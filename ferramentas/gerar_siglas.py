#!/usr/bin/env python3
"""Gera docs/Wiki/Siglas.md a partir de ferramentas/siglas.json.

    .venv/bin/python ferramentas/gerar_siglas.py

O significado de cada sigla precisa estar escrito no próprio protocolo (o script confere).
O hook do site transforma a tabela em dicas ao passar o mouse sobre a sigla em todas as páginas.
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


def textos(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for i in o:
            yield from textos(i)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k != 'tipo':
                yield from textos(v)


cfg = json.load(open(os.path.join(AQUI, 'protocolos.json'), encoding='utf-8'))
siglas = json.load(open(os.path.join(AQUI, 'siglas.json'), encoding='utf-8'))['siglas']
corpos = {}
for t, c in cfg.items():
    d = json.load(open(os.path.join(os.path.expanduser(c['pasta']), 'protocolo.json'), encoding='utf-8'))
    corpos[t] = ' '.join(textos(d['secoes'])).lower()

linhas = ['---', 'title: Siglas', 'tipo: artigo',
          'descricao: "Siglas usadas nos protocolos, com o significado escrito no próprio protocolo."',
          'tags: [Referência rápida]', '---', '',
          '%% Gerado por ferramentas/gerar_siglas.py. Não edite aqui. %%', '',
          'Passe o mouse (ou toque) sobre uma sigla em qualquer página do site para ver o significado.', '',
          '| Sigla | Significado | Protocolo |', '|---|---|---|']
for sigla, significado, prot in sorted(siglas, key=lambda x: x[0].lower()):
    if significado.lower() not in corpos[prot] or sigla.lower() not in corpos[prot]:
        sys.exit(f'sigla {sigla}: "{significado}" não aparece no protocolo {prot}')
    linhas.append(f'| {sigla} | {significado} | [[{prot}]] |')
open(os.path.join(RAIZ, 'docs', 'Wiki', 'Siglas.md'), 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
print('ok: Siglas', len(siglas))
