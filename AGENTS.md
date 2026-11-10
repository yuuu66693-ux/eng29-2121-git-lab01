# AGENTS.md — Lab 02 BJT DC Bias Web App

## Architecture rules
- `dc_bias.py`: pure engineering logic only (math, validation helpers, region/warnings). **No Flask, no HTML, no request/response objects.**
- `app.py`: HTTP routing, form parsing, unit conversion glue, template rendering. **No circuit equations.**
- `templates/index.html`: presentation and form/results rendering only (Jinja). **No embedded physics formulas.**
- `static/style.css`: styling only.

## Coding conventions
- Keep functions small and testable; prefer explicit names and SI units inside calculation logic.
- Return structured results/errors from `dc_bias.py` so routes and tests can consume them consistently.
- Preserve user-entered form values on errors/results when practical.

## Testing & verification
- Use `unittest`.
- Run: `python -m unittest discover -s tests -v`
- Add/update tests before or alongside behavior changes; do not claim tests pass without running them.
- Minimum expectation: ≥3 engineering-math tests in `tests/test_dc_bias.py` and ≥1 Flask client test in `tests/test_web.py`.

## UI/UX notes
- Bilingual labels (Thai + English) are acceptable/preferred per design.
- Clearly display units, Operating Region, and warnings when outside Forward-Active assumptions.
- Invalid input must produce clear feedback and must not crash the app.

## Safety/reproducibility
- Do not commit `.venv/`, credentials, or secrets.
- Keep `README.md` and `docs/validation.md` aligned with actual behavior and commands.
