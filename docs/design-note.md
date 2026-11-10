# Lab 02 — BJT DC Bias Web App Design Note

## Intent
พัฒนา Flask Web Application สำหรับคำนวณ DC Operating Point ของวงจร **NPN Common-Emitter แบบ Voltage-Divider Bias** ภายในคาบ Lab 02 (ENG29 2121, 2-2569) โดยใช้ OpenCode + Superpowers ตาม workflow ของรายวิชา ผลลัพธ์ต้องเปิดผ่าน `http://127.0.0.1:5000/` คำนวณด้วย Python backend จริง มี automated tests และพร้อม push ขึ้น GitHub

## Goals
- รับค่า `VCC, R1, R2, RC, RE, β, VBE` จากฟอร์มเว็บ และคำนวณ `VB, VE, VC, VCE, IC` (พร้อม `IB, IE`) ด้วยสมการ Forward-Active approximation (β คงที่, VBE คงที่)
- แสดงผลลัพธ์พร้อมหน่วย, Operating Region (Active/Cutoff/Saturation), และ warning เมื่ออยู่นอกสมมติฐาน
- ตรวจสอบ input (ค่าว่าง, ไม่ใช่ตัวเลข, ≤ 0 ตามเงื่อนไข) โดยไม่ทำให้หน้าเว็บล้ม
- มี automated tests: อย่างน้อย 3 unit tests ฝั่ง engineering math และอย่างน้อย 1 test ผ่าน Flask test client
- โครงสร้าง multi-file ตามข้อ 04: logic แยกจาก route/template อย่างชัดเจน

## Non-goals (Lab 02)
- ไม่ทำ Bode/AC, Transient, Signal Generator, Overlay Animation, Full circuit editor
- ไม่ใช้ SPICE/ngspice (ใช้สมการโดยตรง)
- ไม่รองรับ bias type อื่น (Fixed/Emitter/Collector feedback) ในคาบนี้ — เตรียมโครงให้ต่อยอดได้
- ไม่ใช้ JavaScript framework/build step; ใช้ form POST + Jinja rendering

## Constraints (จากไฟล์ Lab)
- เปิดผ่าน local web server (`python -m flask --app app run --debug`) ไม่ใช่ `file://`
- `dc_bias.py` ต้องไม่รู้จัก HTML/HTTP; `templates/index.html` ไม่ฝังสมการฟิสิกส์
- ค่าอยู่นอกสมมติฐาน Forward-Active ต้องแสดง warning และไม่รายงานว่า approximation ใช้ได้
- ต้องมี `requirements.txt`, `README.md`, `AGENTS.md`, `docs/*`, tests, และ commit/push ได้
- Test command เป้าหมาย: `python -m unittest discover -s tests -v`

## Approaches considered
| ทางเลือก | ข้อดี | ข้อเสีย | ตัดสินใจ |
|---|---|---|---|
| Form POST + Jinja render (ไม่มี JS) | ตรงโจทย์, ง่าย, เทสต์ HTTP ตรงไปตรงมา, ไม่ต้อง API แยก | ไม่ real-time | **เลือก** |
| JSON API + fetch/JS | UX ลื่น | เพิ่มงาน, ออกนอกโครงที่โจทย์สื่อ, เสี่ยงเวลา | ไม่เลือก |
| Single-file HTML/inline calc | เร็ว | ขัด A2/A4/A7 และข้อ 04 โดยตรง | ไม่เลือก |

## Architecture & File Structure
```
transistor-simulator/
├── app.py                  # Flask routes: GET /, POST /calculate
├── dc_bias.py              # Engineering calculations + region/warnings (pure Python)
├── templates/
│   └── index.html          # Jinja template: form, circuit, results, messages
├── static/
│   └── style.css           # Card layout, 3-column responsive styling
├── tests/
│   ├── test_dc_bias.py     # unittest: math, regions, validation helpers
│   └── test_web.py         # unittest + Flask test_client: GET/POST flows
├── requirements.txt
├── README.md
├── AGENTS.md
└── docs/
    ├── design-note.md      # (this file)
    ├── validation.md       # comparison vs independent hand calc
    └── reflection.md
```

## Engineering Model (`dc_bias.py`)
- Inputs (SI base inside logic): `vcc_V, r1_ohm, r2_ohm, rc_ohm, re_ohm, beta, vbe_V`
- Equations (exact-form using given β, VBE):
  - `VTH = VCC * R2 / (R1 + R2)`
  - `RTH = R1*R2 / (R1 + R2)`
  - `IB = (VTH - VBE) / (RTH + (β + 1) * RE)`
  - `IC = β * IB`, `IE = (β + 1) * IB`
  - `VE = IE * RE`, `VB = VE + VBE`, `VC = VCC - IC * RC`, `VCE = VC - VE`
- Region/warning logic:
  - **Cutoff**: `VTH <= VBE` (or resulting IB/IC non-physical for forward bias) → warn, report limitation
  - **Saturation risk**: `VCE <= VCE_sat_threshold` (use small threshold, e.g. 0.2 V, documented) → warn, approximation unreliable
  - **Active**: otherwise
  - On cutoff/saturation: still return computed numbers for transparency but mark as not trustworthy / include clear warning text (ไม่ clamp เป็นค่าที่ดู "ถูก" โดยไม่มี warning)
- Validation: missing/non-numeric, `VCC <= 0`, `R* <= 0`, `β <= 0` → structured errors (field + message) consumable by route/template
- Public interface (planned): pure function(s) e.g. `calculate_dc_bias(...) -> result dict` and/or `validate_inputs(...)`; no Flask/HTML imports

**Reference case (ข้อ 06):** VCC=12 V, R1=100 kΩ, R2=22 kΩ, RC=2.2 kΩ, RE=1 kΩ, β=100, VBE=0.70 V
→ VTH=2.163934 V, RTH=18.032787 kΩ, IB=12.298581 µA, IC=1.229858 mA, IE=1.242157 mA, VB=1.942157 V, VE=1.242157 V, VC=9.294312 V, VCE=8.052155 V, Region **Active**.

## Web Layer
- `GET /` → render empty/default form (prefilled with reference values for quick demo) and no results
- `POST /calculate` → parse form (including unit multipliers), validate, call `dc_bias.py`, render `index.html` with inputs, results/errors/warnings preserved
- `app.py` handles HTTP/form parsing/unit conversion presentation glue only; no circuit math

## UI/UX Design (Round B target, Round A minimal-but-working)
- **Layout:** 3-column card layout on wide screens (responsive to single column on narrow)
  - Left: Input Parameters — fields for VCC, R1, R2, RC, RE, β, VBE; R1–R4 with unit selectors (Ω/kΩ/MΩ), V fields in V; prominent Calculate button
  - Center: Circuit Diagram — SVG (ANSI zigzag resistors) of NPN Common-Emitter voltage-divider bias with annotated component values from current inputs
  - Right: DC Bias Results — VB, VE, VC, VCE and IB, IC, IE with units; Operating Region status box; warning/assumption notes
- **Header:** icon/badge + "Computer Programming for Electrical Engineers"
- **Footer:** Week 2 Goal banner summarizing scope
- **Language:** bilingual labels inline (Thai + English) per agreed direction
- **Theme:** light, professional, projector-friendly
- **UX details:** inline field errors + summary on invalid input, warning box when not Active, note "β constant, VBE constant, Forward-Active approximation"
- **Execution split:**
  - **Round A:** working backend + tests + basic functional page (all A1–A7 achievable)
  - **Round B:** polish to full 3-column/SVG/unit-selector design; safe to trim if time runs short

## Testing Plan (`unittest`)
- `tests/test_dc_bias.py` (≥3): reference-case values match independent calc (tolerance documented), cutoff case warns/flags (`VTH <= VBE`), saturation case warns/flags (low VCE), invalid inputs rejected (R≤0, β≤0, VCC≤0, non-numeric/missing as applicable to pure functions)
- `tests/test_web.py` (≥1): `GET /` returns 200 with form; `POST /calculate` with reference inputs returns 200 and contains expected result markers; invalid POST shows error without 500
- Run: `python -m unittest discover -s tests -v`
- `docs/validation.md`: record independent hand calculation vs app/test output

## Risks & Decisions
- **Unit conversion ambiguity:** resolve in UI+route (selectors define multipliers) and pass ohms/volts to `dc_bias.py`
- **Region threshold:** document VCE saturation threshold in code/docs; prioritize clear warning over "correct" saturated numbers
- **Git:** git installed but may be invisible to current OpenCode process; restart required before push step (170–180)
- **Time:** prioritize A1–A7 correctness before visual polish (Round A then B)

## Deliverables checklist (maps to rubric/A1–A7)
- [ ] Multi-file Flask app runs on localhost
- [ ] Correct DC bias + units + region + warnings
- [ ] Input validation and non-crashing error handling
- [ ] ≥3 math unit tests + ≥1 Flask HTTP test, all passing
- [ ] README, AGENTS, docs (design/validation/reflection)
- [ ] GitHub commit/push with reproducible instructions
