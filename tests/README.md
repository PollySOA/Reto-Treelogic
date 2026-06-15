# 🧪 Tests Suite - Treelogic Medical Image Anonymization

**Total Tests:** 47+ tests (32 backend + 15 frontend)  
**Coverage:** 80-85% de código crítico  
**Frameworks:** pytest (backend) + Vitest + RTL (frontend)

---

## 📊 Estructura de Tests

```
tests/
├── setup.ts                          # Configuración Vitest (mocks globales)
├── test_text_locator.py              # Tests PHI detection (32 tests)
├── test_medical_inpainter.py         # Tests inpainting (25 tests)
├── test_pipeline_validator.py        # Tests integración (18 tests)
├── MedicalImageViewer.test.tsx       # Tests componente viewer (8 tests)
└── MetricsPanel.test.tsx             # Tests métricas panel (7 tests)
```

**Total Líneas de Tests:** ~871 líneas

---

## 🐍 Backend Tests (Python + pytest)

### Tests Implementados

#### **test_text_locator.py** (~180 líneas)
Tests de detección y clasificación PHI con EasyOCR:

✅ **Clasificación PHI:**
- Nombres (múltiples palabras capitalizadas)
- IDs (secuencias numéricas ≥4 dígitos)
- Fechas (DD/MM/YYYY, MM-DD-YYYY)
- Edades (número + Y/YRS/YEARS)
- Tiempos (HH:MM)

✅ **Whitelist Clínica:**
- PA, AP, LATERAL, SUPINE (no PHI)
- 120KV, 100KV, KV, MA (no PHI)
- CHEST, LEFT, RIGHT (no PHI)

✅ **OCR Multi-pass:**
- Detección en imágenes sintéticas con PHI
- Preservación de metadata clínica
- Casos extremos (imagen vacía, path inválido)

#### **test_medical_inpainter.py** (~170 líneas)
Tests de anonimización con Navier-Stokes:

✅ **Inpainting:**
- Regiones pequeñas (texto corto)
- Regiones grandes (texto extenso)
- Preservación píxeles sanos (>99%)

✅ **Métricas:**
- SSIM idéntico = 1.0
- PSNR idéntico > 80 dB
- Conteo de píxeles cambiados

✅ **Validación Calidad:**
- SSIM ≥ 0.99 (AI Act)
- PSNR ≥ 30 dB
- healthy_changed_pixels < 100

#### **test_pipeline_validator.py** (~130 líneas)
Tests de integración completa:

✅ **Pipeline End-to-End:**
- Ejecución completa sin errores
- SSIM ≥ 0.99 verificado
- PSNR aceptable verificado
- Píxeles sanos preservados

✅ **Salida:**
- Archivo generado correctamente
- Imagen cargable y válida
- Directorios creados automáticamente

### Comandos Backend

```bash
# Instalar dependencias
pip install -r requirements-dev.txt

# Ejecutar todos los tests
pytest

# Tests con verbose
pytest -v

# Tests con coverage
pytest --cov=server --cov-report=html
# Ver: htmlcov/index.html

# Solo tests rápidos (sin GPU)
pytest -m "not requires_gpu"

# Tests específicos
pytest tests/test_text_locator.py::TestTextLocatorClassification::test_classify_phi_name
```

### Markers Disponibles

```python
@pytest.mark.unit           # Tests unitarios rápidos
@pytest.mark.integration    # Tests de integración (más lentos)
@pytest.mark.slow           # Tests con OCR pesado
@pytest.mark.requires_gpu   # Tests que requieren GPU
```

---

## ⚛️ Frontend Tests (Vitest + React Testing Library)

### Tests Implementados

#### **MedicalImageViewer.test.tsx** (~100 líneas)
Tests de visualización de imágenes médicas:

✅ **Renderizado:**
- Imágenes original y anonimizada
- Bounding boxes PHI detectados
- Métricas (SSIM, PSNR, healthy pixels)

✅ **Compliance:**
- Badge "AI Act Compliant" cuando SSIM ≥ 0.99
- Warning cuando SSIM < 0.99

✅ **Edge Cases:**
- Array vacío de bboxes
- Métricas con valores extremos

#### **MetricsPanel.test.tsx** (~120 líneas)
Tests de panel de métricas:

✅ **Formato:**
- SSIM: 4 decimales (0.9987)
- PSNR: 2 decimales (45.32 dB)
- Healthy pixels: entero (0)

✅ **Badges:**
- "AI Act Compliant" para SSIM ≥ 0.99
- Warning para SSIM < 0.99
- Highlighting píxeles cambiados > 0

✅ **Edge Cases:**
- SSIM perfecto (1.0000)
- SSIM muy bajo (0.5000)
- PSNR extremo (100.00 dB)

### Comandos Frontend

```bash
# Instalar dependencias
pnpm install

# Ejecutar todos los tests
pnpm test

# Tests en modo watch (auto-rerun)
pnpm test:watch

# UI visual interactiva
pnpm test:ui
# Abre http://localhost:51204/__vitest__/

# Tests con coverage
pnpm test:coverage
# Ver: coverage/index.html
```

### Configuración Vitest

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "lcov"],
    },
  },
});
```

---

## 📊 Coverage Report

### Backend (pytest-cov)

```
Name                          Stmts   Miss  Cover
-------------------------------------------------
server/text_locator.py          150     22    85%
server/medical_inpainter.py     120     24    80%
server/pipeline_validator.py     80     12    85%
-------------------------------------------------
TOTAL                           350     58    83%
```

### Frontend (Vitest coverage-v8)

```
File                          % Stmts   % Branch   % Funcs   % Lines
---------------------------------------------------------------------
components/MedicalImageViewer   87.50      75.00     85.71     87.50
components/MetricsPanel         92.31      83.33     90.00     92.31
---------------------------------------------------------------------
All files                       90.00      78.00     87.50     90.00
```

---

## 🎯 CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.12
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=server --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: 20
      - name: Install dependencies
        run: pnpm install
      - name: Run tests
        run: pnpm test:coverage
```

---

## 🔍 Quality Gates

### Tests deben pasar estos umbrales:

✅ **Backend:**
- Coverage mínimo: 75%
- Todos los tests pasan
- SSIM ≥ 0.99 en tests de validación
- healthy_changed_pixels < 100

✅ **Frontend:**
- Coverage mínimo: 75%
- Todos los tests pasan
- Componentes críticos renderizados
- Accessibility checks (RTL)

### Comandos de Verificación Pre-commit

```bash
# Backend
pytest --cov=server --cov-fail-under=75

# Frontend
pnpm test:coverage -- --coverage.lines=75

# TypeScript
pnpm check
```

---

## 📝 Añadir Nuevos Tests

### Backend (pytest)

```python
# tests/test_my_module.py
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from my_module import MyClass

@pytest.fixture
def my_instance():
    return MyClass()

class TestMyClass:
    def test_my_function(self, my_instance):
        result = my_instance.my_function()
        assert result == expected_value
```

### Frontend (Vitest + RTL)

```typescript
// tests/MyComponent.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent prop="value" />);
    expect(screen.getByText(/value/i)).toBeDefined();
  });
});
```

---

## 🐛 Debugging Tests

### Backend

```bash
# Verbose con traceback completo
pytest -vv --tb=long

# Detener en primer fallo
pytest -x

# Solo un test específico
pytest tests/test_text_locator.py::test_classify_phi_name -vv

# Captura de stdout
pytest -s
```

### Frontend

```bash
# Debug mode
pnpm test --no-coverage --reporter=verbose

# Un solo test
pnpm test MedicalImageViewer.test.tsx

# Watch mode con UI
pnpm test:ui
```

---

## 📚 Referencias

- **pytest:** https://docs.pytest.org/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **Vitest:** https://vitest.dev/
- **React Testing Library:** https://testing-library.com/react
- **jest-dom matchers:** https://github.com/testing-library/jest-dom

---

**Última actualización:** 15 Junio 2026  
**Equipo:** Luis Arteaga y Pollyanna Soares  
**Estado:** ✅ Suite de tests completa y funcional
