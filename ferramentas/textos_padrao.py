#!/usr/bin/env python3
"""Leva os textos-padrão da pasta de trabalho para o site.

    .venv/bin/python ferramentas/textos_padrao.py

Fonte: ~/Documents/HES/Protocolos/Publicação/textos-padrao/*.md (um arquivo por página).

Formato do arquivo-fonte:

    ---
    titulo: Orientações de alta na perda gestacional precoce
    descricao: uma linha para o índice
    protocolo: Perda gestacional precoce        (opcional)
    situacao: rascunho | aprovado
    atualizado: DD/MM/AAAA
    ---
    Introdução (Markdown, aceita [[wikilinks]]).

    ## Situação 1
    > Nota para o plantonista (Markdown; não é copiada).
    Texto que será copiado para o prontuário, exatamente como está.

    ## Situação 2
    ...

Cada "## " vira um quadro com botão "Copiar". O que vem depois das linhas "> " é o texto copiado,
sem nenhuma transformação. "situacao: rascunho" gera a página em docs/Para revisar/ (só na prévia);
"aprovado" gera em docs/Textos-padrão/. Páginas geradas de fontes apagadas ou renomeadas são removidas.
"""
import html, os, re, sys

FONTE = os.path.expanduser('~/Documents/HES/Protocolos/Publicação/textos-padrao')
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINOS = {'aprovado': os.path.join(RAIZ, 'docs', 'Textos-padrão'),
            'rascunho': os.path.join(RAIZ, 'docs', 'Para revisar')}
MARCA = 'gerado_por: ferramentas/textos_padrao.py'


def ler(caminho):
    s = open(caminho, encoding='utf-8').read().replace('\r\n', '\n')
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
    if not m:
        sys.exit(f'{caminho}: falta o cabeçalho entre ---')
    meta = {}
    for ln in m[1].split('\n'):
        if ':' in ln:
            k, v = ln.split(':', 1)
            meta[k.strip()] = v.strip()
    for k in ('titulo', 'situacao'):
        if not meta.get(k):
            sys.exit(f'{caminho}: falta "{k}" no cabeçalho')
    if meta['situacao'] not in DESTINOS:
        sys.exit(f'{caminho}: situacao deve ser "rascunho" ou "aprovado"')
    return meta, m[2]


def pagina(meta, corpo, nome_fonte):
    partes = re.split(r'^## +(.+)$', corpo, flags=re.M)
    intro, secoes = partes[0].strip(), list(zip(partes[1::2], partes[2::2]))
    if not secoes:
        sys.exit(f'{nome_fonte}: nenhum texto ("## Situação") encontrado')
    yaml = ['---', f'title: {meta["titulo"]}', 'tipo: texto-padrao']
    for k in ('descricao', 'atualizado'):
        if meta.get(k):
            yaml.append(f'{k}: {meta[k]}')
    yaml += [MARCA, f'fonte: {nome_fonte}', '---', '']
    out = yaml + ([intro, ''] if intro else [])
    for titulo, bloco in secoes:
        linhas = bloco.strip('\n').split('\n')
        notas = []
        while linhas and (linhas[0].startswith('>') or not linhas[0].strip()):
            ln = linhas.pop(0)
            if ln.startswith('>'):
                notas.append(re.sub(r'^> ?', '', ln))
        texto = '\n'.join(linhas).strip('\n')
        if not texto:
            sys.exit(f'{nome_fonte}: a seção "{titulo}" não tem texto')
        out += [f'## {titulo.strip()}', '']
        if notas:
            out += ['<p class="tp-nota" markdown="span">' + ' '.join(n for n in notas if n.strip()) + '</p>', '']
        out += ['<div class="texto-padrao" markdown="0">',
                f'<pre class="tp-texto">{html.escape(texto)}</pre>',
                '</div>', '']
    return '\n'.join(out)


def main():
    if not os.path.isdir(FONTE):
        sys.exit(f'pasta não encontrada: {FONTE}')
    gerados = set()
    for nome in sorted(os.listdir(FONTE)):
        if not nome.endswith('.md') or nome.startswith(('.', '_')) or nome.lower() == 'leia-me.md':
            continue
        meta, corpo = ler(os.path.join(FONTE, nome))
        destino = DESTINOS[meta['situacao']]
        os.makedirs(destino, exist_ok=True)
        alvo = os.path.join(destino, meta['titulo'] + '.md')
        novo = pagina(meta, corpo, nome)
        antigo = open(alvo, encoding='utf-8').read() if os.path.exists(alvo) else None
        if novo != antigo:
            open(alvo, 'w', encoding='utf-8').write(novo)
            print(f'{"atualizado" if antigo else "criado"}: {os.path.relpath(alvo, RAIZ)} ({meta["situacao"]})')
        gerados.add(os.path.abspath(alvo))
    for destino in DESTINOS.values():
        if not os.path.isdir(destino):
            continue
        for nome in os.listdir(destino):
            p = os.path.abspath(os.path.join(destino, nome))
            if p in gerados or not nome.endswith('.md'):
                continue
            if MARCA in open(p, encoding='utf-8').read():
                os.remove(p)
                print(f'removido: {os.path.relpath(p, RAIZ)} (fonte apagada, renomeada ou mudou de situação)')


if __name__ == '__main__':
    main()
