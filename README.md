# ◈ PROYECTO IA
### `CARLOS EGAÑA` · AI ENGINEERING LAB

<p align="center">
  <img src="https://img.shields.io/badge/PYTHON-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/STATUS-IN%20DEVELOPMENT-00D4AA?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/FOCUS-API%20%7C%20LLM%20%7C%20AUTOMATION-7C3AED?style=for-the-badge" alt="Focus"/>
</p>

---

> **BUILD. CONNECT. AUTOMATE.**
>
> Un entorno de desarrollo para construir aplicaciones de inteligencia artificial, integrar modelos mediante API y evolucionar hacia soluciones de AI Engineering reproducibles, seguras y escalables.

## `01` / VISIÓN DEL PROYECTO

Este repositorio es la base de un proyecto de inteligencia artificial que evolucionará progresivamente a lo largo del programa, desde la configuración del entorno de desarrollo hasta la construcción de una aplicación funcional.

**Objetivos principales**

- Integrar modelos de IA mediante API.
- Desarrollar módulos de Python reutilizables.
- Implementar gestión segura de credenciales.
- Construir aplicaciones con manejo de errores y respuestas verificables.
- Mantener un entorno reproducible mediante Git y dependencias documentadas.

## `02` / ARQUITECTURA DEL REPOSITORIO

```text
ProyectoIA/
│
├── src/                  # Source code
│   ├── consumir_gemini.py
│   └── ...
│
├── tests/                # Automated tests
│
├── docs/                 # Documentation & evidence
│
├── .env.example          # Environment template
├── .gitignore            # Git exclusion rules
├── requirements.txt      # Python dependencies
└── README.md              # Project documentation
```

| Componente | Responsabilidad |
|---|---|
| `src/` | Código fuente y módulos de la aplicación. |
| `tests/` | Pruebas para verificar el comportamiento del código. |
| `docs/` | Documentación técnica y evidencias de ejecución. |
| `.env.example` | Plantilla de variables de entorno sin secretos. |
| `.gitignore` | Exclusión de credenciales, entornos virtuales y archivos locales. |
| `requirements.txt` | Registro de las dependencias necesarias. |

## `03` / QUICK START

### Requisitos

- Python 3 instalado.
- Git.
- Una API key válida de Google Gemini para ejecutar las pruebas de integración correspondientes.

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd ProyectoIA
```

### 2. Crear y activar el entorno virtual

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
python -m pip install -r requirements.txt
```

Si necesitas registrar una nueva dependencia:

```bash
python -m pip install requests python-dotenv
python -m pip freeze > requirements.txt
```

### 4. Configurar las credenciales

```bash
cp .env.example .env
```

Añade tu API key al archivo `.env` usando el nombre de variable esperado por tu código.

```dotenv
gemini_api_key=YOUR_API_KEY
```

Sustituye `YOUR_API_KEY` por tu credencial real únicamente en el archivo local `.env`.

### 5. Ejecutar el módulo

```bash
python src/consumir_gemini.py
```

El comando anterior presupone que el módulo contiene un punto de entrada ejecutable y que sus dependencias están instaladas.

## `04` / SECURITY PROTOCOL

La seguridad de las credenciales forma parte del diseño del proyecto.

- **No hardcoded secrets:** nunca escribas API keys o tokens directamente en el código.
- **Environment isolation:** utiliza un entorno virtual independiente para este proyecto.
- **Git protection:** `.env` debe permanecer fuera del control de versiones.
- **Safe collaboration:** comparte `.env.example`, nunca el archivo `.env` real.
- **Evidence hygiene:** verifica que las capturas de pantalla no expongan credenciales.

Verifica que Git ignore el archivo de secretos:

```bash
git check-ignore .env
```

Si una credencial real llega a publicarse, revócala y genera una nueva. Eliminarla del último commit no garantiza que desaparezca del historial.

## `05` / DEVELOPMENT WORKFLOW

El desarrollo se gestiona mediante Git, con cambios incrementales y mensajes de commit descriptivos.

```bash
git status
git add <ARCHIVOS>
git commit -m "Describe the implemented change"
git push
```

Antes de subir los cambios, revisa que no incluyan credenciales ni archivos locales innecesarios.

## `06` / ROADMAP

| Etapa | Objetivo |
|---|---|
| U1.2 | Repositorio, entorno virtual, dependencias y primera petición autenticada. |
| U1.3 | Primer módulo Python para consumir una API, procesar respuestas y manejar errores. |
| Gate 1 | Miniaplicación funcional de consumo de modelos mediante API. |
| Gate 3 | Evolución hacia la aplicación final del programa. |

*El alcance y la implementación de cada etapa se ampliarán a medida que avance el proyecto.*

---

<p align="center">
  <code>ENGINEER THE INTELLIGENCE.</code>
  <br/>
  <sub>CARLOS EGAÑA · PROYECTO IA · 2026</sub>
</p>
