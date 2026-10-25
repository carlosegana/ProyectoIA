<p align="center">
  <img src="https://www.skillnest.com/wp-content/uploads/2025/01/Skillnest_blanca-1.png" alt="Skillnest" width="200"/>
</p>

<h1 align="center">Proyecto IA</h1>
<h2 align="center">Carlos Egaña</h2>

---

## Qué es

Una miniaplicación en Python que consume la API de Gemini para un asistente de taller mecánico. Arma la petición, la envía, extrae el texto de la respuesta y valida que el JSON venga con la estructura esperada. Incluye un banco de prompts con su prueba de consistencia y una comparación de modelos que justifica cuál usar.

## Requisitos

- Python 3 (probado con 3.11)
- Una API key de Gemini (se saca en Google AI Studio)

## Instalación

```bash
git clone https://github.com/carlosegana/ProyectoIA.git
cd ProyectoIA
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Después abre `.env` y reemplaza `tu_api_key_aqui` por tu key. La key va solo en `.env`, nunca en `.env.example`.

## Cómo ejecutarlo

Siempre desde la raíz del proyecto y con el entorno virtual activado:

| Comando | Qué hace |
|---|---|
| `python cliente.py` | Hace una pregunta de ejemplo y muestra la respuesta del modelo |
| `python -m src.consumir_gemini` | Prueba con salida JSON y muestra latencia, costo y el dato parseado |
| `python -m src.consistencia` | Corre cada prompt del banco 3 veces y guarda `src/prompts/registro_resultados.json` |
| `python -m src.evaluacion_modelos` | Compara los modelos candidatos (12 llamadas reales) y guarda `docs/comparacion_modelos.md` |
| `python -m unittest discover -s tests` | Corre los tests, no llaman a la API |

## Estructura del proyecto

```text
ProyectoIA/
├── cliente.py                       # Punto de entrada: una consulta de ejemplo
├── src/
│   ├── consumir_gemini.py           # armar_peticion, enviar_peticion, extraer_texto, costo, reintentos
│   ├── consistencia.py              # Prueba de consistencia del banco de prompts
│   ├── evaluacion_modelos.py        # Comparación de modelos (latencia y costo)
│   └── prompts/
│       ├── banco.py                 # Banco de prompts
│       └── registro_resultados.json # Resultado de la prueba de consistencia
├── docs/
│   ├── arquitectura.png / .svg      # Diagrama de arquitectura
│   ├── decision-arquitectura.md     # Decisión de modelo
│   └── comparacion_modelos.md       # Datos crudos de la comparación
├── tests/                           # Tests unitarios
├── requirements.txt                 # Dependencias
├── .env.example                     # Plantilla de variables de entorno, sin valores reales
└── .gitignore
```

## Arquitectura

![Arquitectura de la miniaplicación](docs/arquitectura.png)

## Decisión de modelo

El modelo elegido es `gemini-3.5-flash-lite`. La comparación y las razones están en [docs/decision-arquitectura.md](docs/decision-arquitectura.md).

## Seguridad

- `.env` está en `.gitignore` y `.env.example` solo trae un valor de ejemplo.
- La key se manda en el header `x-goog-api-key`, no en la url.
- Si corres `git log --all --oneline -- .env` aparecen 2 commits: `b6bc47b` agregó un `.env` vacío y `e4d62a8` lo eliminó. Nunca tuvo credenciales: `git show b6bc47b:.env | wc -c` devuelve 0.
