# codecrafters-shell-python

> Este é o desafio **"Build your own Shell"** da CodeCrafters, em Python. As regras pedagógicas globais de `/home/roberth/Estudos/CLAUDE.md` (método socrático, correção guiada, cobrança por excelência) **valem integralmente aqui** — este arquivo só adiciona contexto técnico específico do projeto.

## O que é este projeto
- Implementação de um shell POSIX-like do zero: builtins, execução de programas externos, PATH lookup, redirecionamento, pipes, etc., em estágios incrementais definidos pela CodeCrafters.
- **Não é pasta de `exercicios/`** — é um projeto real e contínuo. Ainda assim, a regra de "não entregar código pronto" e "correção guiada" se aplica normalmente: o objetivo é aprendizado, o código é meu.
- Progresso e enunciado de cada stage vêm da interface da CodeCrafters (o usuário cola prints/texto do stage atual). Trate cada stage como um enunciado de exercício guiado.

## Estrutura
- `app/main.py` — todo o código do shell vive aqui (por enquanto, um único arquivo; a CodeCrafters testa o entrypoint `python -m app.main`).
- `your_program.sh` — roda o shell localmente via `uv run`. **Não editar** (é usado só localmente; a CodeCrafters usa `.codecrafters/run.sh`).
- `.codecrafters/` — scripts internos da plataforma (não mexer).
- `codecrafters.yml` — config da plataforma (versão do Python etc.).

## Stack e execução
- Python **3.14**, gerenciado via `uv` (ver `pyproject.toml`, `uv.lock`).
- Rodar localmente: `./your_program.sh` (inicia o REPL do shell).
- Sem dependências externas (`dependencies = []`) — o desafio é sobre usar a stdlib bem (`sys`, `os`, `shutil`, `subprocess` etc. conforme o stage pedir).

## Convenções específicas deste projeto
- **Lint:** rodar `ruff check` (e `ruff format --check` se formatação estiver em jogo) antes de considerar qualquer mudança concluída — regra global, reforçada aqui porque o código deste projeto cresce stage a stage e tende a acumular repetição se não for revisado.
- **Evitar duplicação entre builtins:** à medida que builtins (`echo`, `type`, `exit`, `pwd`, `cd`, ...) crescem, fique atento a parsing de comando repetido (ex: `command.split()` chamado múltiltiplas vezes) — é terreno fértil para extrair uma função só. Ao me guiar, aponte a repetição e pergunte como eu extrairia, não extraia por mim.
- **Testado pela CodeCrafters:** a solução precisa se comportar exatamente como o enunciado do stage descreve (mensagens de erro, formato de saída) — atenção a detalhes de string exatos (ex: `"<cmd>: not found"` vs `"<cmd> not found"`), já que o corretor é automatizado e sensível a isso.
- **Commits:** seguir Conventional Commits (regra global). Como cada stage do codecrafters tende a virar um commit (`codecrafters submit`), commits de progresso podem ficar mais descritivos do que o submit automático — mas só quando eu pedir para commitar.
