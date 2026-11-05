# Tocoginecologia HES: protocolos, treinamento e wiki

Site estático (MkDocs Material + paleta Nord) publicado no GitHub Pages:
<https://karlfilho.github.io/protocolos-hes/>

Somente o dono do repositório publica. O site não tem login nem botão de edição.

## Como editar

A pasta `docs/` **é um cofre do Obsidian**: abra-a pelo Obsidian em *Open folder as vault*.
O conteúdo é mantido exclusivamente pelo Claude Code. O Obsidian serve só para visualizar
(grafo, backlinks, navegação) e o cofre tem cópia de segurança na nuvem.

| Onde | O quê | Como se edita |
|---|---|---|
| `docs/Protocolos/` | protocolos oficiais | **gerados** a partir do `protocolo.json` (skill protocolo-go-hes). Não edite o texto à mão. |
| `docs/Treinamento/` | tutoriais em texto e vídeo | livre, no Obsidian |
| `docs/Wiki/` | verbetes (fármacos, escores, definições) | livre, no Obsidian |
| `docs/arquivos/` | imagens, PDFs, figuras | o Obsidian salva os anexos aqui |
| `docs/_modelos/` | modelos de página (plugin *Templates*) | não vão para o site |

Sintaxe do Obsidian que o site entende (via `hooks/wiki.py`):

- `[[Página]]`, `[[Página|texto]]`, `[[Página#Seção]]`: links pelo nome do arquivo ou por `aliases`.
- `![[figura.png]]`, `![[figura.png|400]]`, `![[arquivo.pdf]]`, `![[video.mp4]]`: anexos.
- `![](https://youtu.be/…)`: vídeo do YouTube incorporado (prefira YouTube "não listado" a subir vídeo no repositório).
- `> [!warning] Título`: callouts viram quadros coloridos (`+`/`-` = recolhível).
- `%% comentário %%`: não aparece no site.
- `<!-- lista: Pasta -->`: índice automático das páginas da pasta.
- Front matter `descricao:` aparece nos índices; `aliases:` são outros nomes para os wikilinks.

Um link para uma página que ainda não existe aparece com sublinhado tracejado e não quebra o build.

## Protocolo novo ou revisado

```bash
.venv/bin/python ferramentas/json_para_md.py "<pasta do protocolo>" \
    --titulo "Nome da página" --codigo PRI-XXX --prefixo abc --pdf "<pdf oficial>"
.venv/bin/mkdocs build --strict
.venv/bin/python ferramentas/conferir_fidelidade.py "<pasta do protocolo>" site/protocolos/<slug>/index.html
```

Depois, atualize `docs/Novidades.md`.

## Ver localmente e publicar

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # primeira vez
.venv/bin/mkdocs serve        # http://127.0.0.1:8000, recarrega ao salvar
git add -A && git commit -m "…" && git push   # a Action publica em ~2 min
```
