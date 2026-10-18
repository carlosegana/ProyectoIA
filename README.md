 <p align="center">
  <img src="https://www.skillnest.com/wp-content/uploads/2025/01/Skillnest_blanca-1.png" alt="Skillnest" width="200"/>
</p>

<h1 align="center">Proyecto IA</h1>

---

## Cómo empezar

Completa estos pasos progresivamente durante la Unidad U1.2.

### 01. Inicializar el repositorio

Descarga y descomprime el archivo comprimido proporcionado en la plataforma. Inicializa Git en la carpeta y registra un primer commit con la estructura original, antes de realizar modificaciones.

### 02. Crear el entorno virtual

Crea y activa un entorno virtual de Python, por ejemplo, utilizando `venv`.

### 03. Registrar las dependencias

Instala las librerías necesarias y actualiza `requirements.txt` para reflejar las dependencias del proyecto.

### 04. Configurar las credenciales

Copia `.env.example` a un archivo llamado `.env` y añade las credenciales necesarias. El archivo `.env` debe permanecer excluido del control de versiones mediante `.gitignore`.

---

## Estructura del proyecto

```text
ProyectoIA/
├── src/                 # Código fuente
├── docs/                # Documentación técnica
├── tests/               # Pruebas del código
├── requirements.txt     # Dependencias de Python
├── .env.example         # Plantilla de variables de entorno
├── .gitignore           # Archivos excluidos de Git
└── README.md            # Documentación del proyecto
```

## Componentes

| Archivo o carpeta | Descripción |
|---|---|
| `src/` | Código fuente del proyecto. |
| `docs/` | Diagramas, decisiones de arquitectura y notas técnicas. |
| `tests/` | Pruebas del código. |
| `requirements.txt` | Dependencias necesarias para reconstruir el entorno. |
| `.env.example` | Plantilla de variables de entorno sin credenciales reales. |
| `.gitignore` | Configuración de archivos y carpetas excluidos de Git. |

---

## Reglas del proyecto

- **Protección de credenciales:** no incluir contraseñas, API keys ni tokens directamente en el código o en archivos subidos al repositorio.
- **Aislamiento de dependencias:** utilizar un entorno virtual independiente para cada proyecto.
- **Control de versiones:** mantener el trabajo del programa en un repositorio de GitHub.

---
