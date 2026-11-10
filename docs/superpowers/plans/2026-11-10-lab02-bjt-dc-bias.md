# Lab 02 BJT DC Bias Web App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-file Flask web application that calculates and displays the DC operating point of an NPN common-emitter voltage-divider BJT circuit with validation, region warnings, automated tests, and reproducible docs.

**Architecture:** `dc_bias.py` owns all engineering math, validation helpers, and region classification (no Flask/HTML). `app.py` owns HTTP routes and form parsing/unit conversion, rendering `templates/index.html` with `static/style.css`. Tests use `unittest` (`tests/test_dc_bias.py`, `tests/test_web.py`) and `flask.testing.FlaskClient`. Execution is split into Round A (correct, testable, demoable) then Round B (3-column/SVG/unit-selector polish).

**Tech Stack:** Python 3.12, Flask 3.1.x, Jinja2 templates, vanilla HTML/CSS/SVG, `unittest` (`python -m unittest discover -s tests -v`).

**Spec:** `docs/design-note.md`

## Global Constraints

- Deliverable scope: DC bias only (no Bode/AC, transient, signal generator, overlay animation, SPICE).
- Multi-file Flask app per lab spec: `app.py`, `dc_bias.py`, `templates/index.html`, `static/style.css`, `tests/`, `requirements.txt`, `README.md`, `AGENTS.md`, `docs/design-note.md`, `docs/validation.md`, `docs/reflection.md`.
- `dc_bias.py` MUST NOT import Flask or know HTML/HTTP. `templates/index.html` MUST NOT embed physics equations.
- App must run via local server: `python -m flask --app app run --debug` (not `file://`).
- Inputs: `VCC, R1, R2, RC, RE, β, VBE`. Outputs: `VB, VE, VC, VCE, IC` (and `IB, IE`) with units and Operating Region.
- Forward-Active approximation only (β constant, VBE constant). Results outside assumption must show warning and must not be presented as trustworthy without warning.
- Input validation: R≤0, β≤0, VCC≤0, missing/non-numeric → clear error, no crash (HTTP 200 with error UI or 400 with rendered error page; prefer user-visible errors in page).
- Reference case (must match independent calc): VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V → VTH=2.16393442623 V, RTH=18032.7868852459 Ω, IB=1.22985814626e-05 A, IC=0.00122985814626 A, IE=0.00124215672772 A, VB=1.94215672772 V, VE=1.24215672772 V, VC=9.29431207823 V, VCE=8.0521553505 V, Region Active.
- Test command: `python -m unittest discover -s tests -v`. Minimum: ≥3 automated engineering-math tests and ≥1 Flask test-client test.
- Do not commit `.venv/`, secrets, or machine-specific junk. Use project-local `.venv` created at workspace root for development if needed; keep repo clean.

## Review Focus

- **Cutoff boundary (`VTH <= VBE`):** UI must show Operating Region warning and must not claim Forward-Active approximation is valid; values must not be presented as trustworthy DC bias.
- **Saturation boundary (low/negative `VCE`, e.g. VCE <= 0.2 V):** same — explicit warning/limitation, region marked Saturation.
- **Unit conversion correctness:** kΩ/MΩ selectors (or multipliers) must convert to ohms before math; submitting `R1=100, unit=kΩ` must equal 100000 Ω (reference case).
- **Invalid/missing input resilience:** R≤0, β≤0, VCC≤0, empty, or non-numeric input returns a clear, field-specific or summary error and does not raise 500.
- **Reference accuracy:** displayed/calculated VB,VE,VC,VCE,IC,IB,IE for the spec reference case match independent values within reasonable tolerance and include units.

---
### Task 1: Project scaffolding and reproducibility files

**Files:**
- Create: `transistor-simulator/requirements.txt`
- Create: `transistor-simulator/README.md`
- Create: `transistor-simulator/AGENTS.md`
- Create: `transistor-simulator/.gitignore`
- Create: `transistor-simulator/docs/validation.md`
- Create: `transistor-simulator/docs/reflection.md`
- Create: `transistor-simulator/app.py` (minimal placeholder)
- Create: `transistor-simulator/dc_bias.py` (placeholder)
- Create: `transistor-simulator/templates/index.html` (placeholder)
- Create: `transistor-simulator/static/style.css` (placeholder)
- Create: `transistor-simulator/tests/__init__.py`

**Interfaces:**
- Produces: runnable project skeleton; `README.md` documents install/run/test commands using `.venv` or system Python and `python -m unittest discover -s tests -v`.

- [ ] **Step 1: Write/refresh skeleton files**
  - `requirements.txt`: include `Flask>=3.0,<4` (and no unnecessary deps).
  - `.gitignore`: `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.DS_Store`, instance/db artifacts if any.
  - `README.md`: title, purpose, setup (`python -m venv .venv`, activate, `pip install -r requirements.txt`), run (`python -m flask --app app run --debug` then open `http://127.0.0.1:5000/`), test command, brief note on Forward-Active assumption/warnings.
  - `AGENTS.md`: coding/testing conventions (logic in `dc_bias.py`, no physics in template, run unittest before claiming done).
  - `docs/validation.md`, `docs/reflection.md`: headings/placeholders to be filled in Task 6.
  - Minimal `app.py`: Flask app object and `GET /` returning simple 200 response so server can start.
  - Minimal `templates/index.html`, `static/style.css`.

- [ ] **Step 2: Verify skeleton runs**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest discover -s tests -v`
  - Expected: `Ran 0 tests` / OK (no failures).
  - Run: `..\.venv\Scripts\python.exe -m flask --app app routes` (or quick import check `..\.venv\Scripts\python.exe -c "import app; print('ok')"`)
  - Expected: no import errors.

- [ ] **Step 3: Commit scaffold (if git available)**
  - `git add transistor-simulator` (or relevant paths) and commit `chore: scaffold lab02 flask project` (skip commit step if git not usable; note in progress).

### Task 2: DC bias math engine — reference/active case (TDD)

**Files:**
- Modify: `transistor-simulator/dc_bias.py`
- Create: `transistor-simulator/tests/test_dc_bias.py`

**Interfaces:**
- Consumes: numeric SI inputs `vcc, r1, r2, rc, re, beta, vbe` (floats, ohms/volts).
- Produces: `calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe=0.7) -> dict` with keys at least `vth,rth,ib,ic,ie,vb,ve,vc,vce,region,warnings` (numeric values in SI; `region` string e.g. `"active"`; `warnings` list). Exact key names must remain stable for template/tests.

- [ ] **Step 1: Write failing unit tests for reference case**
  - `test_reference_case_active_region`: call `calculate_dc_bias(12, 100000, 22000, 2200, 1000, 100, 0.7)` and assert approximate equality (e.g. `assertAlmostEqual`) for VB=1.94215672772, VE=1.24215672772, VC=9.29431207823, VCE=8.0521553505, IC=0.00122985814626, IB=1.22985814626e-05, IE=0.00124215672772, VTH=2.16393442623, RTH=18032.7868852459; assert region is active and warnings empty/falsey for active case.
  - `test_returns_expected_keys`: assert required output keys exist.

- [ ] **Step 2: Run tests to verify they fail**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
  - Expected: FAIL (missing function/keys).

- [ ] **Step 3: Implement minimal math in `dc_bias.py`**
  - Implement formulas from Global Constraints/spec; compute VTH,RTH,IB,IC,IE,VE,VB,VC,VCE; return dict with SI values. Include region/warnings placeholders sufficient for active case.

- [ ] **Step 4: Run tests to verify they pass**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
  - Expected: PASS.

- [ ] **Step 5: Commit**
  - `git add dc_bias.py tests/test_dc_bias.py` and commit `feat: add dc bias calculation for active region`.

### Task 3: Regions, warnings, and input validation (TDD)

**Files:**
- Modify: `transistor-simulator/dc_bias.py`
- Modify: `transistor-simulator/tests/test_dc_bias.py`

**Interfaces:**
- Produces: `calculate_dc_bias(...)` sets `region` to `active`/`cutoff`/`saturation` (or clearly equivalent labels) and populates `warnings`/`warning_messages` when outside Forward-Active assumptions.
- Produces: validation helper(s), e.g. `validate_dc_inputs(values: dict) -> (clean: dict|None, errors: list)` or `parse_and_validate(...)`, that reject missing/non-numeric and `VCC<=0, R1<=0, R2<=0, RC<=0, RE<=0, beta<=0` with clear field-specific messages; reusable by `app.py`.

- [ ] **Step 1: Write failing tests for edge cases and validation**
  - `test_cutoff_when_vth_not_greater_than_vbe`: e.g. VCC=12, R1=100k, R2=1k, RC=2.2k, RE=1k, β=100, VBE=0.7 (VTH≈0.1188 V) → region cutoff and warnings indicate outside Forward-Active/not trustworthy.
  - `test_saturation_when_vce_low`: e.g. VCC=12, R1=100k, R2=22k, RC=100k, RE=1k, β=100, VBE=0.7 (VCE very negative) → region saturation and warning present.
  - `test_validate_rejects_non_positive_and_missing`: R<=0, β<=0, VCC<=0, missing key, non-numeric string → errors returned and no clean result.

- [ ] **Step 2: Run tests to verify they fail**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
  - Expected: FAIL on new cases.

- [ ] **Step 3: Implement region logic and validation**
  - In `calculate_dc_bias`: detect cutoff (`vth <= vbe` or equivalent) and saturation (`vce <= 0.2` or documented threshold); set region and append human-readable warnings stating Forward-Active approximation limitation; do not claim trustworthy results in those cases.
  - Implement validation helper with explicit messages (Thai/English-friendly text acceptable) and unit-agnostic numeric checks on parsed values.

- [ ] **Step 4: Run tests to verify they pass**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest tests.test_dc_bias -v`
  - Expected: PASS (≥3 meaningful math/logic cases total).

- [ ] **Step 5: Commit**
  - `git add dc_bias.py tests/test_dc_bias.py` and commit `feat: add bias regions, warnings, and validation`.

### Task 4: Flask routes and functional HTML (Round A, TDD)

**Files:**
- Modify: `transistor-simulator/app.py`
- Modify: `transistor-simulator/templates/index.html`
- Modify: `transistor-simulator/static/style.css` (basic usable styling)
- Create: `transistor-simulator/tests/test_web.py`

**Interfaces:**
- Consumes: Task 2/3 (`calculate_dc_bias`, validation helper) from `dc_bias.py`.
- Produces: `GET /` returns HTTP 200 with input form fields `vcc,r1,r2,rc,re,beta,vbe` (and unit fields for resistors if included now; at minimum functional). `POST /calculate` parses form, converts units to SI, validates, computes, and renders same template with results/errors/warnings/region; invalid input must not 500.

- [ ] **Step 1: Write failing Flask client tests**
  - `test_get_index_returns_200_and_form`: GET `/` → 200, contains form/action and input names.
  - `test_post_calculate_reference_case_shows_results`: POST `/calculate` with reference values/units → 200, response contains key outputs (e.g. `1.942`, `8.052`, `1.229` mA-equivalent or SI text) and `Active`.
  - `test_post_invalid_input_shows_error_no_crash`: POST with `r1=0` or empty/non-numeric → 200 (or 400) and error message text, no exception.

- [ ] **Step 2: Run tests to verify they fail**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest tests.test_web -v`
  - Expected: FAIL.

- [ ] **Step 3: Implement routes and basic template**
  - `app.py`: define Flask `app`; route `GET /` renders `index.html`; route `POST /calculate` reads form, applies unit multipliers (Ω/kΩ/MΩ for R1-R4 if present), validates via `dc_bias`, calls `calculate_dc_bias`, passes `inputs/results/errors/warnings/region` to template. No math in template.
  - `templates/index.html`: functional form posting to `/calculate`, results table/list for VB,VE,VC,VCE,IB,IC,IE with units, region display, warning and error blocks; include basic structure usable without polish.

- [ ] **Step 4: Run tests to verify they pass**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest discover -s tests -v`
  - Expected: PASS (all existing tests).

- [ ] **Step 5: Commit**
  - `git add app.py templates/index.html static/style.css tests/test_web.py` and commit `feat: add flask routes and functional dc bias UI`.

### Task 5: UI/UX polish — 3-column layout, SVG circuit, bilingual labels (Round B)

**Files:**
- Modify: `transistor-simulator/templates/index.html`
- Modify: `transistor-simulator/static/style.css`
- (Optional) Modify: `transistor-simulator/app.py` only if needed to pass display values/units back to template (no new math)
- Modify: `transistor-simulator/tests/test_web.py` only if selectors/text changes break assertions (keep intent: GET form, valid calc, invalid error)

**Interfaces:**
- Consumes: same route/result contract from Task 4.
- Produces: user-facing page with header ("Computer Programming for Electrical Engineers"), 3-column card layout (left inputs + unit selectors Ω/kΩ/MΩ for R1-R4 and Calculate button; center SVG NPN CE voltage-divider circuit diagram with ANSI zigzag resistors and annotated values; right results VB,VE,VC,VCE,IB,IC,IE + Operating Region status box), footer Week 2 Goal banner, bilingual Thai+English labels, light responsive styling, inline/summary errors, warning box on cutoff/saturation, assumption note.

- [ ] **Step 1: Update/adjust tests if needed for stable UI hooks**
  - Prefer asserting on stable tokens/values (numbers, field names, region words) rather than fragile layout strings.

- [ ] **Step 2: Implement 3-column responsive template and CSS**
  - Semantic sections/cards, accessible labels, form controls keep `name` attributes expected by `app.py`.
  - SVG circuit: static correct topology with text nodes bound to current/input values via Jinja where practical.

- [ ] **Step 3: Verify tests still pass and page renders key content**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest discover -s tests -v`
  - Expected: PASS.

- [ ] **Step 4: Manual smoke check**
  - Run server: `..\.venv\Scripts\python.exe -m flask --app app run --debug`
  - Open `http://127.0.0.1:5000/`, submit reference case, confirm results/Active, submit invalid case, confirm error/warning UX.

- [ ] **Step 5: Commit**
  - `git add templates/index.html static/style.css app.py tests/test_web.py` and commit `feat: polish 3-column circuit UI and bilingual layout`.

### Task 6: Validation docs, reflection, README, and final verification

**Files:**
- Modify: `transistor-simulator/docs/validation.md`
- Modify: `transistor-simulator/docs/reflection.md`
- Modify: `transistor-simulator/README.md`
- (Verify) all required files present

**Interfaces:**
- Consumes: implemented app and passing tests.
- Produces: documented independent calculation vs app results, reflection text, complete run/test instructions, acceptance checklist evidence.

- [ ] **Step 1: Write `docs/validation.md`**
  - Show independent calculation for reference case (formulas + numeric steps/values) and compare to app/test output; include at least one warning case (cutoff or saturation) behavior.

- [ ] **Step 2: Write `docs/reflection.md` and finalize `README.md`**
  - Reflection: brief learning/AI-use/process notes per course expectations (concise). README: exact clone/setup/run/test steps, assumptions, limitations.

- [ ] **Step 3: Run full verification**
  - Run: `cd transistor-simulator; ..\.venv\Scripts\python.exe -m unittest discover -s tests -v`
  - Expected: all tests PASS (≥3 math in `test_dc_bias.py`, ≥1 HTTP in `test_web.py`).
  - Quick import/sanity: `..\.venv\Scripts\python.exe -c "import app, dc_bias; print('imports-ok')"`.

- [ ] **Step 4: Acceptance checklist self-review**
  - Confirm A1–A6 locally demonstrable; A7 requires git/GitHub (note blocker if git unavailable in session and provide exact commands for user).

- [ ] **Step 5: Commit**
  - `git add docs README.md AGENTS.md` (and any touched files) and commit `docs: add validation, reflection, and final instructions`.
