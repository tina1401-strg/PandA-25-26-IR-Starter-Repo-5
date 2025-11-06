# Part 5 — Starter

This starter builds on Part 4. Two key changes:

1. **Data moved to JSON**: `part5/sonnets.json` replaces the previous `sonnets.py`.
2. **Config file I/O**: Read and write a `config.json` (alongside the package) to persist UI options like `highlight` and `search_mode`.

Students should *carry over* their working logic from Part 4 (the search-mode exercise). Where noted below, copy your previous implementations into the marked regions of `app.py`.

## Run the app

```bash
python -m part5.app
```

## Check against the transcript

```bash
python -m part5.tests.check_transcript
```

## What to implement (ToDos)

- **ToDo 0** — *Search mode (carry-over from Exercise 4)*:
  - Move your implementation of the search mode from part 4 to this repository.

- **ToDo 1** — *Load sonnets from JSON*:
  - Implement `load_sonnets()` in `app.py` to open `part5/sonnets.json` and return the list of sonnets.

- **ToDo 2** — *Read config.json*:
  - Implement `load_config()` to read `config.json` if present (else use defaults).

- **ToDo 3** — *Write config.json*:
  - Implement `save_config(cfg)` to write the current settings (`highlight`, `search_mode`) back to JSON (pretty-printed) whenever the user changes a setting (highlight or search-mode).

## Notes

- Keep the search functionality that we've been working on.
- Use **file I/O** (`open`, `json.load`, `json.dump`) for both `sonnets.json` and `config.json`.
- The config schema reflects the two settings we have up until now:
  ```json
  { "highlight": true, "search_mode": "AND" }
  ```
