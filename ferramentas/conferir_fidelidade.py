#!/usr/bin/env python3
"""Confere se todo trecho de texto do protocolo.json aparece, idêntico, na página publicada.

    .venv/bin/python ferramentas/conferir_fidelidade.py "<pasta do protocolo>" site/protocolos/<slug>/index.html
"""
import html, json, re, sys

pasta, pagina = sys.argv[1], sys.argv[2]
p = open(pagina, encoding='utf-8').read()
corpo = p[p.find('<article'):p.find('</article>')]
corpo = re.sub(r'</?(strong|em|b|i|a|sup|sub|span|code|mark)\b[^>]*>', '', corpo)
texto = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', corpo)))

d = json.load(open(f'{pasta}/protocolo.json', encoding='utf-8'))
IGNORAR = {'tipo', 'id', 'imagem', 'larguras', 'alinhamento', 'cor_cabecalho', 'largura_cm', 'manter_junto'}


def textos(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, list):
        for i in o:
            yield from textos(i)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k not in IGNORAR:
                yield from textos(v)


n = faltando = 0
for s in list(textos(d['secoes'])) + list(textos(d['revisoes'])) + list(textos(d['rodape'])):
    for frag in re.split(r'\n+', s):
        f = re.sub(r'\*\*|\*|\^|~', '', frag)
        f = re.sub(r'\{(quadro|figura|tabela):[^}]+\}', '', f)
        for trecho in re.split(r'\s*\b(?:Quadro|Figura|Tabela)\s*', re.sub(r'\s+', ' ', f).strip()):
            trecho = trecho.strip(' ,.;()')
            if len(trecho) < 4:
                continue
            n += 1
            if trecho not in texto:
                faltando += 1
                print('NÃO ACHADO:', trecho[:200])
print(f'{n} trechos conferidos, {faltando} faltando')
sys.exit(1 if faltando else 0)
