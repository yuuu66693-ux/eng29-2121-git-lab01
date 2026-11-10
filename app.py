from flask import Flask, render_template, request

from dc_bias import calculate_dc_bias, validate_dc_inputs

app = Flask(__name__)

RESISTOR_UNIT_MULTIPLIERS = {
    "ohm": 1.0,
    "Ω": 1.0,
    "kohm": 1000.0,
    "kΩ": 1000.0,
    "k": 1000.0,
    "mohm": 1_000_000.0,
    "MΩ": 1_000_000.0,
    "M": 1_000_000.0,
}

DEFAULT_INPUTS = {
    "vcc": "12",
    "r1": "100",
    "r1_unit": "kΩ",
    "r2": "22",
    "r2_unit": "kΩ",
    "rc": "2.2",
    "rc_unit": "kΩ",
    "re": "1",
    "re_unit": "kΩ",
    "beta": "100",
    "vbe": "0.7",
}


def _parse_form(form):
    raw = {
        "vcc": form.get("vcc", "").strip(),
        "r1": form.get("r1", "").strip(),
        "r1_unit": form.get("r1_unit", "ohm").strip() or "ohm",
        "r2": form.get("r2", "").strip(),
        "r2_unit": form.get("r2_unit", "ohm").strip() or "ohm",
        "rc": form.get("rc", "").strip(),
        "rc_unit": form.get("rc_unit", "ohm").strip() or "ohm",
        "re": form.get("re", "").strip(),
        "re_unit": form.get("re_unit", "ohm").strip() or "ohm",
        "beta": form.get("beta", "").strip(),
        "vbe": form.get("vbe", "").strip(),
    }
    return raw


def _to_si_inputs(raw):
    # Build values for validation/calc in SI ohms/volts.
    values = {
        "vcc": raw.get("vcc", ""),
        "beta": raw.get("beta", ""),
        "vbe": raw.get("vbe", ""),
    }
    for r in ("r1", "r2", "rc", "re"):
        val_str = raw.get(r, "")
        unit = raw.get(f"{r}_unit", "ohm")
        mult = RESISTOR_UNIT_MULTIPLIERS.get(unit, 1.0)
        if val_str == "":
            values[r] = ""
            continue
        try:
            values[r] = float(val_str) * mult
        except (TypeError, ValueError):
            values[r] = val_str  # let validator report non-numeric
    return values


def _format_results(result):
    if not result:
        return None
    return {
        **result,
        "vb_v": result["vb"],
        "ve_v": result["ve"],
        "vc_v": result["vc"],
        "vce_v": result["vce"],
        "ib_ma": result["ib"] * 1000.0,
        "ic_ma": result["ic"] * 1000.0,
        "ie_ma": result["ie"] * 1000.0,
    }


@app.get("/")
def index():
    return render_template(
        "index.html",
        inputs=DEFAULT_INPUTS.copy(),
        results=None,
        errors=[],
        warnings=[],
        region=None,
    )


@app.post("/calculate")
def calculate():
    raw = _parse_form(request.form)
    si_values = _to_si_inputs(raw)
    clean, errors = validate_dc_inputs(si_values)
    if errors:
        return render_template(
            "index.html",
            inputs=raw,
            results=None,
            errors=errors,
            warnings=[],
            region=None,
        )

    result = calculate_dc_bias(
        clean["vcc"],
        clean["r1"],
        clean["r2"],
        clean["rc"],
        clean["re"],
        clean["beta"],
        clean["vbe"],
    )
    view = _format_results(result)
    return render_template(
        "index.html",
        inputs=raw,
        results=view,
        errors=[],
        warnings=result.get("warnings", []),
        region=result.get("region"),
    )


if __name__ == "__main__":
    app.run(debug=True)
