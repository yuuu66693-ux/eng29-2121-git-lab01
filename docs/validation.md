# Validation — Lab 02 DC Bias

## 1. Independent calculation (reference case)
**Inputs:** VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V

**Formulas (Forward-Active approximation, constant β, VBE):**
- VTH = VCC · R2 / (R1 + R2)
- RTH = R1·R2 / (R1 + R2)
- IB = (VTH − VBE) / (RTH + (β + 1)·RE)
- IC = β·IB,  IE = (β + 1)·IB
- VE = IE·RE,  VB = VE + VBE,  VC = VCC − IC·RC,  VCE = VC − VE

**Independent hand/Python cross-check values:**
- VTH = 2.16393442623 V
- RTH = 18032.7868852459 Ω (18.032787 kΩ)
- IB = 12.2985814626 µA (1.22985814626e-05 A)
- IC = 1.22985814626 mA (0.00122985814626 A)
- IE = 1.24215672772 mA (0.00124215672772 A)
- VB = 1.94215672772 V
- VE = 1.24215672772 V
- VC = 9.29431207823 V
- VCE = 8.05215535050 V
- **Operating Region:** Active (VTH > VBE and VCE well above saturation boundary)

## 2. App / automated test comparison
| Quantity | Independent | `dc_bias.calculate_dc_bias` / tests | Match |
|---|---:|---:|:---:|
| VTH (V) | 2.16393442623 | 2.16393442623 | ✅ |
| RTH (Ω) | 18032.7868852459 | 18032.7868852459 | ✅ |
| IB (A) | 1.22985814626e-05 | 1.22985814626e-05 | ✅ |
| IC (A) | 0.00122985814626 | 0.00122985814626 | ✅ |
| IE (A) | 0.00124215672772 | 0.00124215672772 | ✅ |
| VB (V) | 1.94215672772 | 1.94215672772 | ✅ |
| VE (V) | 1.24215672772 | 1.24215672772 | ✅ |
| VC (V) | 9.29431207823 | 9.29431207823 | ✅ |
| VCE (V) | 8.05215535050 | 8.05215535050 | ✅ |
| Region | Active | active | ✅ |

**Automated evidence:** `python -m unittest discover -s tests -v` → 8 tests, all OK (5 engineering/validation tests + 3 Flask HTTP tests).  
Web test posts the reference case and verifies key displayed values (`1.942`, `8.052`, `1.230 mA` equivalent) and `Active`.

## 3. Warning / limitation cases (verified)
| Case | Example inputs | Expected behavior | Verified |
|---|---|---|:---:|
| Cutoff | VCC=12, R1=100kΩ, R2=1kΩ, RC=2.2kΩ, RE=1kΩ, β=100, VBE=0.7 (VTH≈0.119 V ≤ VBE) | Region `cutoff`, warning shown, result not trustworthy under Forward-Active assumption | ✅ (unit test) |
| Saturation | VCC=12, R1=100kΩ, R2=22kΩ, RC=100kΩ, RE=1kΩ, β=100, VBE=0.7 (VCE ≪ 0.2 V) | Region `saturation`, warning shown, result not trustworthy under Forward-Active assumption | ✅ (unit test) |
| Invalid input | R1=0, missing, or non-numeric values | Clear validation error, no server crash | ✅ (unit + web test) |

## 4. Notes
- Calculations are performed by `dc_bias.py` (Python backend), not hard-coded in HTML.
- Unit conversion for resistor inputs (Ω/kΩ/MΩ) is applied before validation/calculation.
- Threshold used for saturation warning in this lab model: `VCE <= 0.2 V` (documented in `dc_bias.py`).
