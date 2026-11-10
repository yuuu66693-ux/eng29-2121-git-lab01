# Reflection — Lab 02

## What I built
I built a multi-file Flask web application for DC bias analysis of an NPN common-emitter amplifier using voltage-divider bias. The project separates responsibilities clearly:
- `dc_bias.py`: engineering calculations, region detection, and validation (pure Python, no web dependencies)
- `app.py`: HTTP routes (`GET /`, `POST /calculate`), form parsing/unit conversion, and template rendering
- `templates/index.html` + `static/style.css`: user interface (3-column card layout, SVG circuit, form/results, warnings/status)
- `tests/`: automated `unittest` coverage for engineering logic and Flask HTTP behavior

## What I verified
- Automated tests: `python -m unittest discover -s tests -v` → **8 tests passed** (5 engineering/validation, 3 web).
- Reference case (VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.7 V) matches independent calculations: VB≈1.942 V, VE≈1.242 V, VC≈9.294 V, VCE≈8.052 V, IC≈1.230 mA, Region Active.
- Warning/validation behavior: cutoff and saturation cases produce region warnings; invalid inputs (e.g. R1=0, missing/non-numeric) produce clear errors without crashing.
- Browser smoke check: app runs on `http://127.0.0.1:5000/`, accepts form input, calculates via backend, and displays results/region/warnings.

## What I learned
- A real web app needs clear separation between **frontend presentation** (template/CSS), **backend routing** (Flask), and **engineering logic** (Python module). Opening an HTML file directly (`file://`) cannot replace server-side calculation.
- Validation and assumption checks are part of engineering software quality: correct formulas alone are not enough if out-of-region results are shown without warnings.
- Unit handling (Ω/kΩ/MΩ) must be normalized before computation to avoid silent scaling errors.

## AI/tooling note
OpenCode with Superpowers skills was used to follow a structured workflow (brainstorming/design approval → implementation planning → task execution with tests). I reviewed the design, approved the plan, and verified outputs against the lab requirements and independent calculations before treating results as complete. Any generated code and results still require human review and engineering judgment.
