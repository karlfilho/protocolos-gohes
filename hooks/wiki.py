"""Camada de wiki para o MkDocs: o site lê o cofre do Obsidian como ele é.

O que este hook faz (nada disso altera o conteúdo das páginas):
  [[Página]], [[Página|texto]], [[Página#Seção]]   → links (resolvidos pelo nome do arquivo ou aliases)
  ![[imagem.svg]], ![[imagem.png|400]]             → imagem (com largura opcional)
  ![[arquivo.pdf]]                                 → botão de download
  ![[video.mp4]]                                   → player de vídeo
  ![](https://youtu.be/…) / youtube.com/watch?v=… → vídeo do YouTube incorporado
  > [!warning] Título  (callouts do Obsidian)     → quadros coloridos do Material
  %% comentário %%                                 → removido do site
  <!-- lista: Pasta -->                            → índice automático das páginas da pasta
  front matter tipo: protocolo                     → cartão com código, revisão, PDF e relacionados
  fim de toda página                               → "Citado em": quem aponta para ela (backlinks)
  nomes de arquivo com espaço/acento               → URLs limpas (Perda gestacional precoce.md → perda-gestacional-precoce/)

Link para página que ainda não existe não quebra o build: vira texto com sublinhado
tracejado e aparece na lista "wikilinks pendentes" no fim do build.
"""
import html
import logging
import posixpath
import re
import unicodedata
from urllib.parse import quote

from mkdocs.utils import meta as meta_util

log = logging.getLogger('mkdocs.hooks.wiki')

EXT_IMAGEM = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.avif'}
EXT_VIDEO = {'.mp4', '.webm', '.mov'}
WIKILINK = re.compile(r'(!?)\[\[([^\[\]\n]+?)\]\]')
CODIGO = re.compile(r'(^(?P<f>```|~~~).*?^(?P=f)[^\n]*$|`[^`\n]+`)', re.S | re.M)
YOUTUBE = re.compile(r'!\[[^\]]*\]\((?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})[^)]*\)')
LISTA = re.compile(r'<!--\s*lista:\s*(.+?)\s*-->')
COMENTARIO = re.compile(r'%%.*?%%', re.S)

paginas = {}        # chave minúscula (nome, alias, caminho) -> File
arquivos = {}       # nome minúsculo do anexo -> File
metas = {}          # src_uri -> front matter
citado_por = {}     # src_uri alvo -> {src_uri origem}
pendentes = {}      # texto do link -> {páginas}
slugify_titulo = None


# ------------------------------------------------------------------ utilidades
def slug(texto):
    t = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-') or 'pagina'


def slug_caminho(src_uri):
    partes = src_uri.split('/')
    *pastas, nome = partes
    raiz, ext = posixpath.splitext(nome)
    return '/'.join([slug(p) for p in pastas] + [slug(raiz) + ext.lower()])


def titulo(f):
    m = metas.get(f.src_uri, {})
    if m.get('title'):
        return m['title']
    raiz = posixpath.splitext(posixpath.basename(f.src_uri))[0]
    if raiz == 'index':
        pasta = posixpath.dirname(f.src_uri)
        return posixpath.basename(pasta) if pasta else 'Início'
    return raiz


def proteger_codigo(md, funcao):
    """Aplica `funcao` só fora de blocos e trechos de código."""
    partes, ultimo = [], 0
    for m in CODIGO.finditer(md):
        partes.append(funcao(md[ultimo:m.start()]))
        partes.append(m.group(0))
        ultimo = m.end()
    partes.append(funcao(md[ultimo:]))
    return ''.join(partes)


def separar(alvo):
    """'Página#Seção|texto' -> ('Página', 'Seção', 'texto')"""
    alvo, _, texto = alvo.partition('|')
    alvo, _, secao = alvo.partition('#')
    return alvo.strip(), secao.strip(), texto.strip()


def resolver_pagina(nome):
    chave = nome.lower().removesuffix('.md')
    return paginas.get(chave)


def link_relativo(origem, destino):
    rel = posixpath.relpath(destino.src_uri, posixpath.dirname(origem.src_uri) or '.')
    return quote(rel, safe='/#.-_~')


# ------------------------------------------------------------------ eventos
def on_config(config):
    global slugify_titulo
    toc = config['mdx_configs'].get('toc', {})
    slugify_titulo = toc.get('slugify')
    if slugify_titulo is None:
        from markdown.extensions.toc import slugify as slugify_titulo  # noqa: F811
    return config


def on_files(files, config):
    paginas.clear(); arquivos.clear(); metas.clear(); citado_por.clear(); pendentes.clear()
    duplicados = set()
    docs = config['docs_dir']
    for f in files:
        if f.src_dir != docs:
            continue
        if f.is_documentation_page():
            _, m = meta_util.get_data(f.content_string)
            metas[f.src_uri] = m or {}
            raiz = posixpath.splitext(f.src_uri)[0]
            chaves = {raiz.lower(), posixpath.basename(raiz).lower()}
            aliases = (m or {}).get('aliases') or []
            chaves |= {str(x).lower() for x in ([aliases] if isinstance(aliases, str) else aliases)}
            if posixpath.basename(raiz) == 'index':
                chaves.discard('index')
                if posixpath.dirname(raiz):
                    chaves.add(posixpath.dirname(raiz).lower())
            for c in chaves:
                if c in paginas and paginas[c] is not f:
                    duplicados.add(c)
                paginas[c] = f
        else:
            arquivos[posixpath.basename(f.src_uri).lower()] = f
        f.dest_uri = slug_caminho(f.dest_uri)
    for c in duplicados:
        log.warning(f'wiki: o nome "{c}" vale para mais de uma página; use o caminho completo no link')

    # backlinks: quem cita quem
    for f in files:
        if f.src_uri not in metas:
            continue
        texto = COMENTARIO.sub('', CODIGO.sub('', f.content_string))
        for m in WIKILINK.finditer(texto):
            if m.group(1):
                continue
            nome, _, _ = separar(m.group(2))
            alvo = resolver_pagina(nome) if nome else None
            if alvo and alvo is not f:
                citado_por.setdefault(alvo.src_uri, set()).add(f.src_uri)
    return files


def on_nav(nav, config, files):
    ordem = config['extra'].get('ordem_menu', [])

    def posicao(item):
        nome = item.title if item.is_section else posixpath.splitext(item.file.src_uri)[0]
        return ordem.index(nome) if nome in ordem else len(ordem)
    nav.items.sort(key=posicao)
    return nav


def on_page_markdown(markdown, page, config, files):
    f = page.file
    m = metas.get(f.src_uri, {})
    markdown = proteger_codigo(markdown, lambda t: transformar(t, f, files))
    topo = cartao_protocolo(m, f) if m.get('tipo') == 'protocolo' else ''
    return topo + markdown + rodape_backlinks(f, files)


def on_post_build(config):
    if pendentes:
        linhas = [f'  [[{n}]] em: {", ".join(sorted(p))}' for n, p in sorted(pendentes.items())]
        log.info('wiki: wikilinks pendentes (páginas ainda não criadas):\n' + '\n'.join(linhas))


# ------------------------------------------------------------------ transformações
def transformar(texto, pagina, files):
    texto = COMENTARIO.sub('', texto)
    texto = callouts(texto)
    texto = YOUTUBE.sub(lambda m: youtube(m.group(1)), texto)
    texto = LISTA.sub(lambda m: lista(m.group(1), pagina), texto)
    return WIKILINK.sub(lambda m: wikilink(m, pagina), texto)


def wikilink(m, pagina):
    embutir, bruto = m.group(1), m.group(2)
    nome, secao, texto = separar(bruto)

    if embutir:
        anexo = arquivos.get(nome.lower())
        if anexo is None:
            pendentes.setdefault(nome, set()).add(pagina.src_uri)
            return f'<span class="wikilink-pendente">{html.escape(nome)}</span>'
        url = link_relativo(pagina, anexo)
        ext = posixpath.splitext(nome)[1].lower()
        if ext in EXT_IMAGEM:
            largura = f'{{ width="{texto}" }}' if texto.isdigit() else ''
            return f'[![{html.escape(texto if not texto.isdigit() else nome)}]({url}){largura}]({url})'
        if ext in EXT_VIDEO:
            return f'<video controls preload="metadata" src="{anexo.url_relative_to(pagina)}"></video>'
        rotulo = texto or nome
        return f'[:material-file-download-outline: {rotulo}]({url}){{ .md-button }}'

    if not nome:                                    # [[#Seção]] na própria página
        return f'[{texto or secao}](#{slugify_titulo(secao, "-")})'
    if nome.lower() in arquivos:                    # [[arquivo.pdf]]: link para o anexo
        anexo = arquivos[nome.lower()]
        icone = ':material-file-pdf-box: ' if nome.lower().endswith('.pdf') else ':material-paperclip: '
        return f'[{icone}{texto or nome}]({link_relativo(pagina, anexo)}){{ .md-button }}'
    alvo = resolver_pagina(nome)
    if alvo is None:
        pendentes.setdefault(nome, set()).add(pagina.src_uri)
        return (f'<span class="wikilink-pendente" title="Página ainda não publicada">'
                f'{html.escape(texto or nome)}</span>')
    url = link_relativo(pagina, alvo)
    if secao:
        url += '#' + slugify_titulo(secao, '-')
    rotulo = texto or (f'{titulo(alvo)} › {secao}' if secao else titulo(alvo))
    return f'[{rotulo}]({url})'


TIPOS_CALLOUT = {'todo': 'info', 'hint': 'tip', 'important': 'tip', 'caution': 'warning',
                 'attention': 'warning', 'error': 'danger', 'cite': 'quote', 'faq': 'question',
                 'help': 'question', 'check': 'success', 'done': 'success', 'fail': 'failure',
                 'missing': 'failure', 'summary': 'abstract', 'tldr': 'abstract'}
INICIO_CALLOUT = re.compile(r'^(?P<ind>[ \t]*)>[ \t]*\[!(?P<tipo>[\w-]+)\](?P<dobra>[+-]?)[ \t]*(?P<titulo>.*)$')


def callouts(texto):
    """> [!tipo]± Título / > conteúdo  →  !!! tipo "Título" / ⎵⎵⎵⎵conteúdo (recursivo)."""
    linhas, out, i = texto.split('\n'), [], 0
    while i < len(linhas):
        m = INICIO_CALLOUT.match(linhas[i])
        if not m:
            out.append(linhas[i]); i += 1
            continue
        ind = m['ind']
        corpo, i = [], i + 1
        while i < len(linhas) and re.match(rf'^{re.escape(ind)}>', linhas[i]):
            corpo.append(re.sub(rf'^{re.escape(ind)}> ?', '', linhas[i]))
            i += 1
        tipo = m['tipo'].lower()
        tipo = TIPOS_CALLOUT.get(tipo, tipo)
        marca = {'': '!!!', '+': '???+', '-': '???'}[m['dobra']]
        titulo_c = m['titulo'].strip().replace('"', '&quot;')
        cab = f'{ind}{marca} {tipo}' + (f' "{titulo_c}"' if titulo_c else '')
        out += ['', cab]
        out += [(ind + '    ' + ln) if ln.strip() else '' for ln in callouts('\n'.join(corpo)).split('\n')]
        out.append('')
    return '\n'.join(out)


def youtube(video_id):
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{video_id}" '
            f'title="Vídeo" allowfullscreen loading="lazy" '
            f'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"></iframe></div>')


def lista(pasta, pagina):
    """Índice automático das páginas de uma pasta (ordem alfabética)."""
    pasta = pasta.strip().strip('/')
    itens = sorted(
        (f for f in {id(v): v for v in paginas.values()}.values()
         if posixpath.dirname(f.src_uri) == pasta and not f.src_uri.endswith('index.md')),
        key=lambda f: titulo(f).lower())
    if not itens:
        return '*Nenhuma página publicada ainda.*'
    if any(metas[f.src_uri].get('codigo') for f in itens):
        linhas = ['| Protocolo | Código | Revisão | Data |', '|---|---|---|---|']
        for f in itens:
            m = metas[f.src_uri]
            linhas.append(f'| [{titulo(f)}]({link_relativo(pagina, f)}) | {m.get("codigo", "")} '
                          f'| {m.get("revisao", "")} | {m.get("data_revisao", "")} |')
        return '\n'.join(linhas)
    linhas = []
    for f in itens:
        desc = metas[f.src_uri].get('descricao', '')
        linhas.append(f'- [{titulo(f)}]({link_relativo(pagina, f)})' + (f' — {desc}' if desc else ''))
    return '\n'.join(linhas)


def links_de_propriedade(valor, pagina):
    """Propriedade do Obsidian com links ("[[A]]" ou lista deles) → links Markdown."""
    valores = valor if isinstance(valor, list) else [valor]
    out = []
    for v in valores:
        for m in WIKILINK.finditer(str(v)):
            out.append(wikilink(m, pagina))
    return out


def cartao_protocolo(m, pagina):
    dados = [('Código', m.get('codigo')), ('Revisão', m.get('revisao')),
             ('Data da revisão', m.get('data_revisao')), ('Emissão', m.get('emissao')),
             ('Elaborado por', m.get('elaborado_por')), ('Aprovado por', m.get('aprovado_por'))]
    celulas = ''.join(f'<div><span>{r}</span><strong>{html.escape(str(v))}</strong></div>'
                      for r, v in dados if v)
    partes = [f'<div class="ficha-protocolo">{celulas}</div>', '']
    if m.get('pdf'):
        partes += [' '.join(links_de_propriedade(m['pdf'], pagina)), '']
    rel = links_de_propriedade(m.get('relacionados') or [], pagina)
    if rel:
        partes += ['**Veja também:** ' + ' · '.join(rel), '']
    partes += ['!!! info "Este protocolo não substitui o julgamento clínico"',
               '    Em caso de divergência, vale o documento oficial (PDF acima).', '']
    return '\n'.join(partes) + '\n'


def rodape_backlinks(f, files):
    fontes = sorted(citado_por.get(f.src_uri, ()), key=lambda s: titulo(files.get_file_from_path(s)).lower())
    if not fontes:
        return ''
    links = [f'[{titulo(files.get_file_from_path(s))}]({link_relativo(f, files.get_file_from_path(s))})'
             for s in fontes]
    return ('\n\n<div class="citado-em" markdown>\n\n**Citado em:** ' + ' · '.join(links) + '\n\n</div>\n')
