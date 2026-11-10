"""DC bias calculations for NPN common-emitter voltage-divider bias (Lab 02).

Engineering logic only: no Flask/HTML dependencies.

Model assumptions: NPN transistor, Forward-Active approximation with constant
beta and constant VBE. Results outside these assumptions are flagged.
"""

SATURATION_VCE_THRESHOLD = 0.2  # volts, approximate boundary for this lab model


def calculate_dc_bias(vcc, r1, r2, rc, re, beta, vbe=0.7):
    """Calculate DC operating point for voltage-divider bias.

    Args:
        vcc, vbe: volts
        r1, r2, rc, re: ohms
        beta: current gain (dimensionless)

    Returns:
        dict with SI values and keys:
        vth, rth, ib, ic, ie, vb, ve, vc, vce, region, warnings
    """
    vcc = float(vcc)
    r1 = float(r1)
    r2 = float(r2)
    rc = float(rc)
    re = float(re)
    beta = float(beta)
    vbe = float(vbe)

    vth = vcc * r2 / (r1 + r2)
    rth = (r1 * r2) / (r1 + r2)

    warnings = []
    denom = rth + (beta + 1.0) * re
    ib = (vth - vbe) / denom if denom != 0 else 0.0
    ic = beta * ib
    ie = (beta + 1.0) * ib

    ve = ie * re
    vb = ve + vbe
    vc = vcc - ic * rc
    vce = vc - ve

    if vth <= vbe or ib <= 0 or ic <= 0:
        region = "cutoff"
        warnings.append(
            "Cutoff region detected (VTH <= VBE or non-forward base-emitter bias). "
            "Forward-Active approximation is not valid; results are not trustworthy."
        )
    elif vce <= SATURATION_VCE_THRESHOLD:
        region = "saturation"
        warnings.append(
            "Saturation region detected (VCE is at or below the active-region boundary). "
            "Forward-Active approximation is not valid; results are not trustworthy."
        )
    else:
        region = "active"

    return {
        "vth": vth,
        "rth": rth,
        "ib": ib,
        "ic": ic,
        "ie": ie,
        "vb": vb,
        "ve": ve,
        "vc": vc,
        "vce": vce,
        "region": region,
        "warnings": warnings,
    }


def validate_dc_inputs(values):
    """Validate and parse DC bias inputs.

    Args:
        values: mapping with keys vcc,r1,r2,rc,re,beta,vbe (string or numeric).

    Returns:
        (clean_dict, errors)
        - clean_dict: dict of floats in SI units when valid, else None
        - errors: list of {"field": <name|None>, "message": <str>}
    """
    errors = []
    clean = {}
    specs = {
        "vcc": ("VCC", True, False),   # must be > 0
        "r1": ("R1", True, True),      # must be > 0
        "r2": ("R2", True, True),
        "rc": ("RC", True, True),
        "re": ("RE", True, True),
        "beta": ("beta", True, True),
        "vbe": ("VBE", False, False),  # can be 0? usually >0 but allow numeric; spec states VBE input
    }

    for key, (label, must_be_positive, _is_res) in specs.items():
        if key not in values or values[key] is None or str(values[key]).strip() == "":
            errors.append({"field": key, "message": f"{label} is required."})
            continue
        try:
            num = float(values[key])
        except (TypeError, ValueError):
            errors.append({"field": key, "message": f"{label} must be a number."})
            continue
        if must_be_positive and num <= 0:
            errors.append({"field": key, "message": f"{label} must be greater than 0."})
            continue
        if key == "vbe" and num <= 0:
            errors.append({"field": key, "message": f"{label} must be greater than 0."})
            continue
        clean[key] = num

    if errors:
        return None, errors
    return clean, []
