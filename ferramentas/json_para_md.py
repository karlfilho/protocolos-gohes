#!/usr/bin/env python3
"""Converte o protocolo.json (skill protocolo-go-hes) numa página Markdown do site/cofre.

    .venv/bin/python ferramentas/json_para_md.py "<pasta do protocolo>" \
        --titulo "Perda gestacional precoce" --codigo PRI-PROV-01 --prefixo pgp \
        [--pdf "<arquivo.pdf>"] [--relacionado "Gravidez ectópica" ...]

Regra de fidelidade: o texto clínico sai exatamente como está no protocolo.json (que é a
fonte do DOCX oficial). O conversor só troca a marcação (Markdown/Obsidian), recria a
numeração automática do gerador (4.1., Quadro 3, Figura 2) e acrescenta navegação.
Nada é resumido, completado ou reescrito.

Saída:
  docs/Protocolos/<titulo>.md
  docs/arquivos/<prefixo>-fig<N>-<nome>.svg   (figuras; SVG do fluxograma, ou PNG)
  docs/arquivos/<codigo> <titulo> rev<NNN>.pdf (se --pdf)
"""
import argparse
import json
import os
import re
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, 'docs')

SECOES = [
    ('introducao', 'Introdução e justificativa'),
    ('objetivo', 'Objetivo'),
    ('elegibilidade', 'Critérios de elegibilidade'),
    ('conteudo', 'Conteúdo clínico e assistencial'),
    ('fluxograma', 'Fluxograma'),
    ('responsabilidades', 'Responsabilidades'),
    ('indicadores', 'Indicadores'),
    ('referencias', 'Referências bibliográficas'),
    ('anexos', 'Anexos'),
]

rotulos = {}          # 'quadro:id' -> número


def numerar_rotulos(secoes):
    cont = {'quadro': 0, 'tabela': 0, 'figura': 0}
    for chave, _ in SECOES:
        for b in secoes.get(chave, []):
            if isinstance(b, dict) and b.get('tipo') in cont:
                cont[b['tipo']] += 1
                if b.get('id'):
                    rotulos[f'{b["tipo"]}:{b["id"]}'] = cont[b['tipo']]


def inline(t, celula=False):
    """Marcação do gerador → Markdown. **negrito** e *itálico* já são Markdown."""
    t = str(t)
    t = t.replace('|', r'\|') if celula else t
    t = t.replace('_', r'\_')                       # linhas de preenchimento ____ do formulário
    t = re.sub(r'\^([^^]+)\^', r'<sup>\1</sup>', t)
    t = re.sub(r'~([^~]+)~', r'<sub>\1</sub>', t)

    def ref(m):
        tipo, ident = m.group(1), m.group(2)
        n = rotulos.get(f'{tipo}:{ident}')
        if n is None:
            sys.exit(f'referência cruzada sem destino: {m.group(0)}')
        return f'[{n}](#{tipo}-{n})' if not celula else str(n)     # o texto já traz "Quadro"/"Figura"
    t = re.sub(r'\{(quadro|tabela|figura):([^}]+)\}', ref, t)
    t = t.replace('\n\n', '<br><br>').replace('\n', '<br>')
    return t


def bloco_lista(itens, numerada=False, nivel=0):
    out = []
    for i, it in enumerate(itens, 1):
        marca = f'{i}.' if numerada else '-'
        texto, sub = (it.get('texto', ''), it.get('subitens', [])) if isinstance(it, dict) else (it, [])
        out.append('    ' * nivel + f'{marca} {inline(texto)}')
        if sub:
            out.extend(bloco_lista(sub, False, nivel + 1))
    return out


class Conversor:
    def __init__(self, pasta, prefixo):
        self.pasta, self.prefixo = pasta, prefixo
        self.cont = {'quadro': 0, 'tabela': 0, 'figura': 0}
        self.figuras = []        # (origem, destino)

    def quadro(self, b, tipo):
        self.cont[tipo] += 1
        n = self.cont[tipo]
        rot = 'Quadro' if tipo == 'quadro' else 'Tabela'
        ncol = len(b['cabecalho'])
        out = [f'<a id="{tipo}-{n}"></a>', f'**{rot} {n} – {inline(b["titulo"])}**', '']
        out.append('| ' + ' | '.join(inline(c, True) for c in b['cabecalho']) + ' |')
        out.append('|' + '---|' * ncol)
        for ln in b['linhas']:
            if isinstance(ln, dict) and 'mesclada' in ln:
                out.append('| ' + ' | '.join([f'**{inline(ln["mesclada"], True)}**'] + [''] * (ncol - 1)) + ' |')
            else:
                out.append('| ' + ' | '.join(inline(c, True) for c in ln) + ' |')
        if b.get('fonte'):
            out += ['', f'<small>Fonte: {inline(b["fonte"])}</small>']
        if b.get('nota'):
            out += ['', f'<small>{inline(b["nota"])}</small>']
        return out

    def figura(self, b):
        self.cont['figura'] += 1
        n = self.cont['figura']
        png = os.path.join(self.pasta, b['imagem'])
        svg = os.path.splitext(png)[0] + '.svg'
        origem = svg if os.path.exists(svg) else png
        base = re.sub(r'^fig\d+_?', '', os.path.splitext(os.path.basename(origem))[0])
        destino = f'{self.prefixo}-fig{n}-{base}{os.path.splitext(origem)[1]}'.replace('_', '-')
        self.figuras.append((origem, destino))
        out = [f'<a id="figura-{n}"></a>', f'![[{destino}]]', '', f'**Figura {n} – {inline(b["legenda"])}**']
        if b.get('fonte'):
            out += ['', f'<small>Fonte: {inline(b["fonte"])}</small>']
        return out

    def blocos(self, lista, sec_num):
        out, sub, subsub = [], 0, 0
        for b in lista:
            if isinstance(b, str):
                b = {'tipo': 'paragrafo', 'texto': b}
            t = b.get('tipo', 'paragrafo')
            if t == 'paragrafo':
                out += [inline(b['texto'])]
            elif t == 'subtitulo':
                sub += 1; subsub = 0
                out += [f'### {sec_num}.{sub}. {inline(b["texto"])}']
            elif t == 'subsubtitulo':
                subsub += 1
                out += [f'#### {sec_num}.{sub}.{subsub}. {inline(b["texto"])}']
            elif t == 'lista':
                out += bloco_lista(b['itens'])
            elif t == 'lista_numerada':
                out += bloco_lista(b['itens'], numerada=True)
            elif t in ('quadro', 'tabela'):
                out += self.quadro(b, t)
            elif t == 'figura':
                out += self.figura(b)
            elif t == 'destaque':
                out += ['> [!danger] Atenção', '> ' + inline(b['texto'])]
            elif t == 'nota':
                out += ['> ' + inline(b['texto'])]
            elif t == 'quebra_pagina':
                continue
            else:
                sys.exit(f'tipo de bloco desconhecido: {t}')
            out.append('')
        return out


def yaml_str(s):
    return json.dumps(str(s), ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pasta')
    ap.add_argument('--titulo', required=True, help='nome da página (= nome do arquivo e do wikilink)')
    ap.add_argument('--codigo', required=True)
    ap.add_argument('--prefixo', required=True, help='prefixo curto dos arquivos de figura')
    ap.add_argument('--pdf')
    ap.add_argument('--relacionado', action='append', default=[])
    a = ap.parse_args()

    d = json.load(open(os.path.join(a.pasta, 'protocolo.json'), encoding='utf-8'))
    cab, sec = d['cabecalho'], d['secoes']
    numerar_rotulos(sec)
    conv = Conversor(a.pasta, a.prefixo)

    pdf_nome = None
    if a.pdf:
        pdf_nome = f'{a.codigo} {a.titulo} rev{cab["revisao"]}.pdf'

    fm = ['---',
          'tipo: protocolo',
          f'codigo: {yaml_str(a.codigo)}',
          f'assunto: {yaml_str(cab["assunto"])}',
          f'origem: {yaml_str(cab["origem"])}',
          f'revisao: {yaml_str(cab["revisao"])}',
          f'data_revisao: {yaml_str(d["revisoes"][0]["data"])}',
          f'emissao: {yaml_str(d["revisoes"][-1]["data"])}',
          f'elaborado_por: {yaml_str(d["rodape"]["elaborado_por"])}',
          f'aprovado_por: {yaml_str(d["rodape"]["aprovado_por"])}']
    if pdf_nome:
        fm.append(f'pdf: {yaml_str("[[" + pdf_nome + "|PDF oficial · revisão " + cab["revisao"] + "]]")}')
    fm.append('relacionados:' + ('' if a.relacionado else ' []'))
    fm += [f'  - {yaml_str("[[" + r + "]]")}' for r in a.relacionado]
    fm += ['---', '',
           '%% Página gerada a partir do protocolo.json pelo ferramentas/json_para_md.py.',
           'Não edite o texto clínico aqui: altere o protocolo (docx/json) e converta de novo. %%', '']

    corpo = []
    for i, (chave, titulo) in enumerate(SECOES, 1):
        corpo += [f'## {i}. {titulo}', '']
        blocos = sec.get(chave, [])
        if not blocos:
            corpo += ['Não se aplica.', '']
        elif chave == 'referencias':
            corpo += [f'{k}. {inline(r)}' for k, r in enumerate(blocos, 1)] + ['']
        else:
            corpo += conv.blocos(blocos, i)

    corpo += ['## Histórico de revisões', '',
              '| Revisão | Data | Revisão efetuada |', '|---|---|---|']
    corpo += [f'| {r["numero"]} | {r["data"]} | {inline(r["descricao"], True)} |' for r in d['revisoes']]
    corpo.append('')

    texto = '\n'.join(fm + corpo)
    texto = re.sub(r'\n{3,}', '\n\n', texto)

    os.makedirs(os.path.join(DOCS, 'Protocolos'), exist_ok=True)
    os.makedirs(os.path.join(DOCS, 'arquivos'), exist_ok=True)
    destino = os.path.join(DOCS, 'Protocolos', a.titulo + '.md')
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(texto)
    for origem, nome in conv.figuras:
        shutil.copyfile(origem, os.path.join(DOCS, 'arquivos', nome))
    if pdf_nome:
        shutil.copyfile(a.pdf, os.path.join(DOCS, 'arquivos', pdf_nome))
    print(f'ok: {os.path.relpath(destino, RAIZ)} · {len(conv.figuras)} figuras'
          + (f' · PDF {pdf_nome}' if pdf_nome else ''))


if __name__ == '__main__':
    main()
