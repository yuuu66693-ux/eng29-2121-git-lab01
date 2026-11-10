# Lab 02 — BJT DC Bias Web App (Voltage-Divider Bias)

Flask web application for ENG29 2121 (Computer Programming for Electrical Engineers), Week 2.  
It calculates the DC operating point of an **NPN Common-Emitter amplifier with voltage-divider bias** using a Python backend.

## Scope
- DC bias analysis only (Forward-Active approximation, constant β and constant VBE)
- Inputs: `VCC, R1, R2, RC, RE, β, VBE`
- Outputs: `VB, VE, VC, VCE, IC` (and `IB, IE`) with Operating Region and warnings
- No AC/transient/signal generator/SPICE in this lab

## Project structure
```
transistor-simulator/
├── app.py                  # Flask routes (GET /, POST /calculate)
├── dc_bias.py              # Engineering calculations (no HTML/HTTP)
├── templates/index.html    # Jinja template (form + results)
├── static/style.css        # UI styling
├── tests/
│   ├── test_dc_bias.py     # Engineering/unit tests
│   └── test_web.py         # Flask HTTP tests
├── docs/
│   ├── design-note.md
│   ├── validation.md
│   └── reflection.md
├── requirements.txt
├── AGENTS.md
└── README.md
```

## Setup
From the project directory:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

python -m pip install -r requirements.txt
```

> If a shared virtual environment already exists one level above this folder, you may use it instead (adjust paths accordingly).

## Run
```bash
python -m flask --app app run --debug
```
Open: <http://127.0.0.1:5000/>

Do **not** open `templates/index.html` via `file://` — calculation is performed by the Flask/Python backend.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Engineering assumptions & limitations
- Model: NPN BJT, Forward-Active approximation with constant `β` and constant `VBE`.
- If the operating point is outside Forward-Active assumptions (e.g. cutoff/saturation), the app reports warnings/region and results must not be treated as trustworthy DC bias predictions.
- This is not a SPICE/ngspice simulation.

## Reference case (for validation)
`VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V`  
Expected (independent calculation): `VB≈1.942 V, VE≈1.242 V, VC≈9.294 V, VCE≈8.052 V, IC≈1.230 mA` (Active).
See `docs/validation.md` for full comparison.
