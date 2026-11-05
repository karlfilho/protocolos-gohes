#!/usr/bin/env python3
"""Confere, depois do build, que cada verbete da Wiki só contém texto dos protocolos.

    .venv/bin/python ferramentas/conferir_verbetes.py

Cada linha de texto visível do verbete (fora a moldura de navegação gerada) precisa aparecer,
idêntica, no protocolo.json de origem. Sai com erro se achar texto que não veio do protocolo.
"""
import glob, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
cfg = json.load(open(os.path.join(AQUI, 'protocolos.json'), encoding='utf-8'))
spec = json.load(open(os.path.join(AQUI, 'verbetes.json'), encoding='utf-8'))


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


def norm(t):
    t = re.sub(r'\*\*|\*|\^|~', '', t)
    return re.sub(r'\s+', ' ', t).strip()


sys.path.insert(0, AQUI)
import json_para_md as conv  # noqa: E402

fonte, moldura_nomes = {}, set(cfg) | {nome for _, nome in conv.SECOES}
for titulo, c in cfg.items():
    d = json.load(open(os.path.join(os.path.expanduser(c['pasta']), 'protocolo.json'), encoding='utf-8'))
    conv.rotulos.clear(); conv.numerar_rotulos(d['secoes'])
    t = ' '.join(textos(d))
    t = re.sub(r'\{(quadro|tabela|figura):([^}]+)\}', lambda m: str(conv.rotulos[f'{m.group(1)}:{m.group(2)}']), t)
    fonte[titulo] = norm(t)

MOLDURA = [r'^Item [\d.]+ — ', r'^Seção \d+ — ', r'^Ver no protocolo ›$', r'^PRI-[\w-]+ · revisão \d+$',
           r'^Transcrição do protocolo$', r'^Trechos copiados sem alteração de .*vale o protocolo\.$',
           r'^Referências$', r'^Atenção$', r'^Citado em:', r'^(Quadro|Tabela|Figura) \d+ – ', r'^Fonte: ',
           r'^\[\d+\] ', r'^Passe o mouse', r'^Sigla Significado Protocolo$']
problemas = 0
for v in spec['verbetes']:
    slug = re.sub(r'[^a-z0-9]+', '-', __import__('unicodedata').normalize('NFKD', v['titulo']).encode('ascii', 'ignore').decode().lower()).strip('-')
    h = open(os.path.join(RAIZ, 'site', 'wiki', slug, 'index.html'), encoding='utf-8').read()
    art = h[h.find('<article'):h.find('</article>')]
    art = re.sub(r'<h1.*?</h1>', '', art, flags=re.S)
    art = re.sub(r'<a class="headerlink".*?</a>', '', art)
    art = re.sub(r'</?(strong|em|b|i|a|sup|sub|span|code|mark|abbr|small)\b[^>]*>', '', art)
    art = re.sub(r'<(td|th)[^>]*>', ' \n', art)
    linhas = [norm(html.unescape(x)) for x in re.sub(r'<[^>]+>', '\n', art).split('\n')]
    corpo = ' '.join(fonte[t['protocolo']] for t in v['trechos'])
    for ln in linhas:
        ln = re.sub(r'^Item [\d.]+ — |^Seção \d+ — ', '', ln)
        if len(ln) < 3 or ln in moldura_nomes or any(re.match(p, ln) for p in MOLDURA[2:]):
            continue
        ln = re.sub(r'^(Quadro|Tabela|Figura) \d+ – ', '', ln).replace(' (linhas selecionadas)', '')
        if ln not in corpo and ln.rstrip(':') not in corpo:
            problemas += 1
            print(f'{v["titulo"]}: texto que não veio do protocolo → {ln[:150]}')
print('verbetes conferidos:', len(spec['verbetes']), '· problemas:', problemas)
sys.exit(1 if problemas else 0)
