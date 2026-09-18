# Datasets

## demo_documents/

All files in `demo_documents/` are **100% synthetic, programmatically generated
placeholder images**, created by `generate_demo_assets.py` in this folder.

- No real person's photograph, name, or identity data is used anywhere.
- No real government document template, security feature, hologram, or
  official layout is reproduced. These are simplified illustrative mockups
  (a bordered card with a title bar, a few text fields, and a placeholder
  photo box) sufficient to exercise the OCR → extraction → validation →
  tampering → risk pipeline end-to-end.
- Document numbers, names, and dates used (e.g. "Aarav Sharma", "ABCDE1234F")
  are placeholder values chosen only to match the *format* of real Indian
  identity document numbers for validation-testing purposes. They do not
  correspond to any real, issued document or real individual.
- Every generated image includes a visible "SYNTHETIC SAMPLE — NOT A REAL
  DOCUMENT" watermark.

### Regenerating the demo assets

```bash
cd datasets
python3 generate_demo_assets.py
```

This will (re)create all files in `demo_documents/`.

### Using your own test data

If you want to test with your own images, you have two options:

1. **Upload through the UI** — go to "New Screening" and upload any JPG,
   PNG, or PDF. Only use documents you have the right to use (your own
   documents, consented test data, or synthetic/mock documents). Do not
   upload other people's real government-issued identity documents without
   their consent.
2. **Add a new demo scenario** — drop a new synthetic image into
   `demo_documents/`, add its OCR ground-truth text to `DEMO_OCR_TEXT` in
   `backend/app/services/demo_data.py`, and register a new entry in
   `DEMO_SCENARIOS`.

### Important

This system does **not** require, request, or connect to any government
identity database. It never performs real-time verification against
Aadhaar/UIDAI, PAN/Income Tax Department, Passport Seva, or any other
official record system. All "validation" performed is limited to document
**format** and **internal logical consistency** checks — see the
`disclaimer` field returned by every validation API response.
