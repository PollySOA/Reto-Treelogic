# Treelogic Medical Image De-identification System

Medical image de-identification system compliant with AI Act (EU), GDPR, and HIPAA. End-to-end pipeline with OCR-based text detection, PHI classification, and surgical anonymization preserving clinical utility (SSIM ≥0.99, zero healthy tissue modification).

---

## Documentation

| Category | Document | Link |
|----------|----------|------|
| **Hackathon** | Requirements Compliance (21/21) | [docs/hackathon/CUMPLIMIENTO.md](docs/hackathon/CUMPLIMIENTO.md) |
| | Presentation Guide (5 min) | [docs/hackathon/PRESENTACION.md](docs/hackathon/PRESENTACION.md) |
| | Pitch Video (3-5 min) | [docs/hackathon/PITCH_VIDEO.md](docs/hackathon/PITCH_VIDEO.md) |
| **Technical** | Code Analysis | [docs/technical/ANALISIS_CODIGO.md](docs/technical/ANALISIS_CODIGO.md) |
| | PHI Detection | [docs/technical/PHI_DETECTOR.md](docs/technical/PHI_DETECTOR.md) |
| | Inpainting | [docs/technical/INPAINTING.md](docs/technical/INPAINTING.md) |
| | User Interface | [docs/technical/INTERFAZ_USUARIO.md](docs/technical/INTERFAZ_USUARIO.md) |
| | Monitoring | [docs/MONITORING_OBSERVABILITY.md](docs/MONITORING_OBSERVABILITY.md) |
| **Project** | Branding | [docs/project/BRANDING.md](docs/project/BRANDING.md) |
| | Issues & Solutions | [docs/project/PROBLEMAS_SOLUCIONES.md](docs/project/PROBLEMAS_SOLUCIONES.md) |
| | Metrics | [docs/project/DATOS_EXTRAIDOS.md](docs/project/DATOS_EXTRAIDOS.md) |

---

## Pipeline Architecture

```
Medical Image → OCR Detection → PHI Classification → Anonymization → Validation
```

**Stage 1: OCR Detection (EasyOCR)**
- Multi-pass strategy (original, CLAHE, sharpening)
- Detection rate: ~95%

**Stage 2: PHI Classification**
- DICOM whitelist (PA, KV, technique, anatomy)
- 5 PHI categories: name, id, age, date, time

**Stage 3: Anonymization**
- Strict inpainting method (AI Act compliant)
- Zero healthy pixel modification

**Stage 4: Validation**
- SSIM: 0.9987 (>0.99 threshold)
- PSNR: 45.32 dB
- Healthy pixels changed: 0

---

## Quick Start

### Prerequisites
- Node.js 20+, pnpm 10+, Python 3.12+

### Installation

```bash
# Backend
cd server
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ..
pnpm install
```

### Run

```bash
# Terminal 1: Backend
cd server && source ../.venv/bin/activate && python main.py

# Terminal 2: Frontend
pnpm dev

# Access: http://localhost:3000
```

### Verify

```bash
curl http://localhost:8000/health | jq .
curl http://localhost:8000/metrics
```

---

## Technical Stack

**Backend:** FastAPI, Python 3.12+, EasyOCR, OpenCV, scikit-image  
**Frontend:** React 19, TypeScript, Vite 7, Tailwind CSS 4  
**Monitoring:** Prometheus, structured JSON logging  
**Testing:** pytest (95+ tests), Vitest (15+ tests)

---

## Performance Metrics

| Metric | Value | Status |
|--------|-------|--------|
| SSIM | 0.9987 | Exceeds 0.99 threshold |
| PSNR | 45.32 dB | Excellent (>40 dB) |
| Healthy pixels modified | 0 | Perfect preservation |
| PHI detection rate | ~95% | High accuracy |
| Processing time | 3.42s | Acceptable |
| Test coverage | 80-85% | Good |

---

## Compliance

**AI Act (EU):** SSIM ≥0.99 with bit-level validation  
**GDPR:** Irreversible anonymization, Privacy by Design  
**HIPAA:** Local processing, Zero-Trust architecture

---

## Project Structure

```
├── client/                  # React frontend
│   ├── src/pages/          # Application pages
│   ├── src/components/     # UI components
│   └── public/             # Static assets
├── server/                 # Python backend
│   ├── main.py            # FastAPI app
│   ├── monitoring.py      # Observability
│   ├── text_locator.py    # PHI detection
│   ├── medical_inpainter.py # Anonymization
│   └── pipeline_validator.py # Validation
├── tests/                  # Test suite (115+ tests)
└── docs/                   # Documentation (18 files)
```

---

## Testing

```bash
pytest tests/ -v                    # All backend tests
pytest --cov=server --cov-report=html  # With coverage
pnpm test                           # Frontend tests
```

**Results:** 115+ automated tests, 80-85% backend coverage, 100% monitoring module coverage

---

## Monitoring Endpoints

- **Health:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics (Prometheus format)
- **Logs:** Structured JSON for analysis

---

## Status

**Production-ready for Treelogic Hackathon submission**

- 100% functional (backend + frontend)
- 21/21 requirements fulfilled
- AI Act, GDPR, HIPAA compliant
- 115+ automated tests
- Production monitoring enabled
- Complete documentation (18 files)

---

**Developed for:** Treelogic Computer Vision Challenge  
**Team:** Luis Arteaga and Pollyanna Soares  
**Date:** June 15, 2026  
**Version:** 2.1.0
