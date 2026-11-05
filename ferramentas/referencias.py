#!/usr/bin/env python3
"""Preenche as referências (notas de rodapé) dos artigos da Wiki.

    .venv/bin/python ferramentas/referencias.py

Nos artigos, cite com [^chave] (ex.: [^nice], [^febrasgo]). Este script reescreve, no fim de
cada artigo, as definições [^chave]: <referência Vancouver>, tiradas da bibliografia conferida
dos protocolos (campo "refs" de cada protocolo_fonte.json) e de ferramentas/bibliografia.json,
quando existir (referências extras, também conferidas na Crossref).
Chave desconhecida interrompe o script.
"""
import glob, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
MARCA = '%% Referências: geradas por ferramentas/referencias.py. %%'

bib = {}
for c in json.load(open(os.path.join(AQUI, 'protocolos.json'), encoding='utf-8')).values():
    fonte = os.path.join(os.path.expanduser(c['pasta']), 'protocolo_fonte.json')
    bib.update(json.load(open(fonte, encoding='utf-8')).get('refs', {}))
extra = os.path.join(AQUI, 'bibliografia.json')
if os.path.exists(extra):
    bib.update(json.load(open(extra, encoding='utf-8')))

for p in sorted(glob.glob(os.path.join(RAIZ, 'docs', '**', '*.md'), recursive=True)):
    s = open(p, encoding='utf-8').read()
    if not re.search(r'^tipo: artigo$', s, re.M):
        continue
    corpo = s.split('\n' + MARCA)[0].rstrip() + '\n'
    usadas = []
    for k in re.findall(r'\[\^([\w-]+)\](?!:)', corpo):
        if k not in usadas:
            usadas.append(k)
    if not usadas:
        continue
    faltam = [k for k in usadas if k not in bib]
    if faltam:
        sys.exit(f'{os.path.relpath(p, RAIZ)}: chave(s) sem referência: {faltam}')
    defs = '\n'.join(f'[^{k}]: {bib[k]}' for k in usadas)
    open(p, 'w', encoding='utf-8').write(corpo + '\n' + MARCA + '\n\n' + defs + '\n')
    print(f'ok: {os.path.relpath(p, RAIZ)} · {len(usadas)} referências')
