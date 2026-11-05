#!/usr/bin/env python3
"""Gera os verbetes da Wiki a partir dos protocolos: trechos copiados sem alteração.

    .venv/bin/python ferramentas/gerar_verbetes.py

Lê ferramentas/verbetes.json (o que vai em cada verbete) e ferramentas/protocolos.json (onde
está o protocolo.json de cada protocolo). Escreve docs/Wiki/<verbete>.md e docs/Wiki/Siglas.md.

Regra: o verbete não tem texto clínico próprio. Cada trecho sai do protocolo.json pelos mesmos
conversores da página do protocolo, com o número do item, do quadro e das referências do
protocolo e um link para a seção de origem. Quando o protocolo é revisado, rode de novo:
o verbete acompanha. Um seletor que não encontra o trecho interrompe a geração.
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import json_para_md as conv  # noqa: E402

RAIZ = os.path.dirname(AQUI)
WIKI = os.path.join(RAIZ, 'docs', 'Wiki')


class Protocolo:
    def __init__(self, titulo, cfg):
        self.titulo = titulo
        self.pasta = os.path.expanduser(cfg['pasta'])
        self.codigo, self.prefixo = cfg['codigo'], cfg['prefixo']
        self.d = json.load(open(os.path.join(self.pasta, 'protocolo.json'), encoding='utf-8'))
        self.revisao = self.d['cabecalho']['revisao']
        self.entradas = []      # (chave_secao, bloco, rótulo do item, título âncora, nível)
        for i, (chave, nome) in enumerate(conv.SECOES, 1):
            sub = subsub = 0
            loc = (f'{i}', f'{i}. {nome}', nome)
            for b in self.d['secoes'].get(chave, []):
                t = b.get('tipo') if isinstance(b, dict) else 'paragrafo'
                if t == 'subtitulo':
                    sub += 1; subsub = 0
                    loc = (f'{i}.{sub}', f'{i}.{sub}. {b["texto"]}', b['texto'])
                    self.entradas.append((chave, b, loc, 2))
                elif t == 'subsubtitulo':
                    subsub += 1
                    loc = (f'{i}.{sub}.{subsub}', f'{i}.{sub}.{subsub}. {b["texto"]}', b['texto'])
                    self.entradas.append((chave, b, loc, 3))
                else:
                    self.entradas.append((chave, b, loc, 9))

    def preparar(self):
        """Estado global do conversor para este protocolo (numeração e remissões)."""
        conv.rotulos.clear(); conv.numero_de.clear()
        conv.numerar_rotulos(self.d['secoes'])
        conv.REF_PAGINA = self.titulo
        return conv.Conversor(self.pasta, self.prefixo)

    # ---------------------------------------------------------------- seletores
    def selecionar(self, s):
        """Devolve [(bloco, loc, filtro, item)] para um seletor; erro se não achar."""
        tipo, achados = s['tipo'], []
        texto = lambda b: b if isinstance(b, str) else b.get('texto', '')  # noqa: E731
        for k, (chave, b, loc, nivel) in enumerate(self.entradas):
            if tipo in ('quadro', 'figura') and isinstance(b, dict) and b.get('tipo') == tipo and b.get('id') == s['id']:
                achados = [(b, loc, s.get('linhas'), None, k)]
            elif chave != s.get('secao'):
                continue
            elif tipo == 'secao' and nivel < 9 and texto(b).startswith(s['inicio']):
                achados = []
                for k2, (chave2, b2, loc2, nivel2) in enumerate(self.entradas[k + 1:], k + 1):
                    if chave2 != chave or nivel2 <= nivel:
                        break
                    if nivel2 == 9:
                        achados.append((b2, loc2, None, None, k2))
            elif tipo == 'paragrafo' and nivel == 9 and (isinstance(b, str) or b.get('tipo') == 'paragrafo') \
                    and texto(b).startswith(s['inicio']):
                achados = [(b, loc, None, None, k)]
                if s.get('com_lista'):
                    seguinte = self.entradas[k + 1][1]
                    if not (isinstance(seguinte, dict) and seguinte.get('tipo') == 'lista'):
                        sys.exit(f'{s}: o parágrafo não é seguido de lista')
                    achados.append((seguinte, loc, None, None, k + 1))
            elif tipo == 'destaque' and isinstance(b, dict) and b.get('tipo') == 'destaque' and b['texto'].startswith(s['inicio']):
                achados = [(b, loc, None, None, k)]
            elif tipo == 'item' and isinstance(b, dict) and b.get('tipo') == 'lista':
                for j, it in enumerate(b['itens']):
                    if texto(it).startswith(s['inicio']):
                        achados = [(b, loc, None, it, k + j / 1000)]
            if achados:
                return achados
        sys.exit(f'trecho não encontrado em "{self.titulo}": {s}')


def textos(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for i in o:
            yield from textos(i)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in ('tipo', 'id', 'imagem', 'larguras', 'alinhamento', 'cor_cabecalho', 'largura_cm'):
                yield from textos(v)


def citacoes(texto):
    nums = set()
    for grupo in re.findall(r'\[(\d+(?:\s*[-,]\s*\d+)*)\]', texto):
        for parte in grupo.split(','):
            a, _, b = parte.strip().partition('-')
            nums.update(range(int(a), int(b or a) + 1))
    return nums


def yaml_lista(xs):
    return '[' + ', '.join(conv.yaml_str(x) for x in xs) + ']'


def gerar_verbete(v, protocolos):
    partes, refs, fontes = [], {}, []
    por_protocolo = {}
    for s in v['trechos']:
        por_protocolo.setdefault(s['protocolo'], []).append(s)

    for nome, seletores in por_protocolo.items():
        p = protocolos[nome]
        c = p.preparar()
        fontes.append(p)
        partes += [f'## {p.titulo}', '',
                   f'<small>{p.codigo} · revisão {p.revisao}</small>', '']
        loc_atual, usados = None, set()
        trechos = sorted((t for s in seletores for t in p.selecionar(s)), key=lambda t: t[4])   # ordem do protocolo
        for b, loc, filtro, item, _ in trechos:
            if True:
                chave_uso = (id(b), id(item) if item is not None else None, tuple(filtro or ()))
                if chave_uso in usados:
                    continue
                usados.add(chave_uso)
                if loc != loc_atual:
                    rotulo, ancora, titulo = loc
                    nome_item = f'Item {rotulo}' if '.' in rotulo else f'Seção {rotulo}'
                    partes += [f'### {nome_item} — {conv.inline(titulo)}', '',
                               f'<small>[[{p.titulo}#{ancora}|Ver no protocolo ›]]</small>', '']
                    loc_atual = loc
                if item is not None:
                    partes += conv.bloco_lista([item]); bruto = item
                elif filtro:
                    partes += c.quadro(b, b['tipo'], filtro)
                    bruto = [b['cabecalho'], [ln for ln in b['linhas'] if isinstance(ln, list)
                                              and any(str(ln[0]).startswith(f) for f in filtro)],
                             b.get('fonte', ''), b.get('nota', '')]
                else:
                    partes += c.bloco(b); bruto = b
                partes.append('')
                for n in citacoes(' '.join(textos(bruto))):
                    refs[(p.titulo, n)] = p.d['secoes']['referencias'][n - 1]

    origem = ', '.join(f'[[{p.titulo}]] ({p.codigo}, revisão {p.revisao})' for p in fontes)
    topo = ['---', f'title: {conv.yaml_str(v["titulo"])}', 'tipo: verbete',
            f'aliases: {yaml_lista(v.get("aliases", []))}',
            f'descricao: {conv.yaml_str(v["descricao"])}',
            'fontes:'] + [f'  - {conv.yaml_str("[[" + p.titulo + "]]")}' for p in fontes] + [
            '---', '',
            '%% Gerado por ferramentas/gerar_verbetes.py a partir de ferramentas/verbetes.json. Não edite aqui. %%', '',
            '> [!info] Transcrição do protocolo',
            f'> Trechos copiados sem alteração de {origem}. A numeração de itens, quadros e referências '
            'é a do protocolo. Em caso de divergência, vale o protocolo.', '']
    if refs:
        partes += ['## Referências', '']
        multiplos = len(fontes) > 1
        for (prot, n), r in sorted(refs.items()):
            partes.append(f'- [{n}] {conv.inline(r)}' + (f' <small>({prot})</small>' if multiplos else ''))
        partes.append('')
    texto = re.sub(r'\n{3,}', '\n\n', '\n'.join(topo + partes))
    with open(os.path.join(WIKI, v['titulo'] + '.md'), 'w', encoding='utf-8') as f:
        f.write(texto)
    return texto


def gerar_siglas(siglas, protocolos):
    linhas = ['---', 'title: Siglas', 'tipo: verbete', 'descricao: "Siglas usadas nos protocolos, com o significado escrito no próprio protocolo."',
              '---', '',
              '%% Gerado por ferramentas/gerar_verbetes.py. Não edite aqui. %%', '',
              'Passe o mouse (ou toque) sobre uma sigla em qualquer página do site para ver o significado.', '',
              '| Sigla | Significado | Protocolo |', '|---|---|---|']
    for sigla, significado, prot in sorted(siglas, key=lambda x: x[0].lower()):
        corpo = ' '.join(textos(protocolos[prot].d['secoes'])).lower()
        if significado.lower() not in corpo or sigla.lower() not in corpo:
            sys.exit(f'sigla {sigla}: "{significado}" não aparece no protocolo {prot}')
        linhas.append(f'| {sigla} | {significado} | [[{prot}]] |')
    with open(os.path.join(WIKI, 'Siglas.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas) + '\n')


def main():
    cfg = json.load(open(os.path.join(AQUI, 'protocolos.json'), encoding='utf-8'))
    spec = json.load(open(os.path.join(AQUI, 'verbetes.json'), encoding='utf-8'))
    protocolos = {t: Protocolo(t, c) for t, c in cfg.items()}
    os.makedirs(WIKI, exist_ok=True)
    for v in spec['verbetes']:
        gerar_verbete(v, protocolos)
        print('ok:', v['titulo'])
    gerar_siglas(spec['siglas'], protocolos)
    print('ok: Siglas')


if __name__ == '__main__':
    main()
