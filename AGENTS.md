# Agent guide

Read this before changing anything. `README.md` explains what the product does.

## Commands

```bash
make install            # uv sync and pnpm install
make up | make down     # the whole stack in Docker: UI :8088, API :8011
make infra migrate      # Postgres and Redis in Docker, Alembic upgrade
make api | make worker | make web
make run IDEA='...'     # the whole pipeline in one process, no DB needed
make check              # must be green before a task is done
make types              # after any API change
```

Tests use the stand-ins in `tests/fakes`; never call OpenRouter from tests. Every run of the app is a paid OpenRouter run.

`examples/` holds four real runs committed on purpose and loaded by `make migrate`; do not edit them by hand. New runs go to `runs/`, which git ignores.

## Invariants that must never break

1. The text of a line is written once, by the screenwriter. Quoted speech from the idea is copied by code, by index.
2. After the script check no step may change a line. LLM schemas after that point have no field for dialogue text; code inserts it and `verify_lines_unchanged` guards every handoff.
3. The Wan prompt is built by `app/pipeline/adapters/wan.py`, never by a model.
4. A take passes only with zero word errors, the right speaker and a valid format.
5. Retries are capped: script 20 rewrites (text is cheap), portraits 5 redraws, scene 3 takes. Then the graph pauses for a person.

## Backend style

- Layers: `api/routers` call `services`; services use `repository` and the pipeline; routers never touch the database directly.
- Every function and method is fully typed; `mypy --strict` must pass.
- Constants shared by two or more files live in `app/constants/`; a constant used in one file sits at the top of that file. No magic strings or numbers in code.
- Enums live in `app/enums/`. Pydantic models of run files live in `app/pipeline/contracts/`.
- Early return instead of `else` after `return`. Functions stay short; split anything longer than about 30 lines.
- No comments in code. Names and small functions carry the meaning.

## Frontend style

- `src/consts`, `src/types`, `src/enums` with barrel exports; local constants at the top of the file.
- One component per file, PascalCase names, at most about 250 lines.
- SCSS modules with flat BEM: one block per component, `block__element--modifier`, no tag or id selectors, no combinators.
- All user-facing text goes through i18next (`src/locales/en.json`, one nesting level).
- No `typeof x === '...'`, no `else` after `return`, no `console.log`.
- `src/api/schema.ts` is generated; do not edit it by hand.

## Definition of done

- `make check` is green.
- New behavior has a test (unit for rules and checks, graph test on fakes for flows).
- API changes are reflected in regenerated frontend types.
