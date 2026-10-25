import json
import os
import re
import time
from typing import Any, Callable

import requests
from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (no falla si no existe)
_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_RAIZ_PROYECTO, ".env"))

# Constantes
MODELO = "gemini-2.5-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")
TIMEOUT_SEGUNDOS = 60

# Precios en USD por token (entrada, salida). Fuente: ai.google.dev/gemini-api/docs/pricing
# (tier de pago, prompts <= 200k tokens). Verificar periódicamente: cambian.
PRECIOS = {
    "gemini-2.5-flash": (0.30 / 1_000_000, 2.50 / 1_000_000),
    "gemini-2.5-flash-lite": (0.10 / 1_000_000, 0.40 / 1_000_000),
    "gemini-2.5-pro": (1.25 / 1_000_000, 10.00 / 1_000_000),
}


def armar_peticion(modelo, pregunta, system_instruction, response_schema=None):
    """Devuelve (url, body). La API key NO va en la URL: se envía por header en enviar_peticion."""
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")
    url = f"{URL_BASE}{modelo}:generateContent"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}

    if system_instruction:  # un texto vacío puede provocar 400
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body


def enviar_peticion(url, body):
    if not API_KEY:
        raise ValueError("Falta GEMINI_API_KEY. Defínela en el archivo .env de la raíz del proyecto.")

    headers = {"x-goog-api-key": API_KEY}
    try:
        respuesta = requests.post(url, json=body, headers=headers, timeout=TIMEOUT_SEGUNDOS)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # TimeoutError = error transitorio, reintentable con con_reintento.
        # "from None" evita encadenar la excepción original.
        raise TimeoutError("No se pudo conectar o se agotó el tiempo de espera.") from None

    detalle = respuesta.text[:300]  # la API devuelve la causa real en el body
    if respuesta.status_code in (401, 403):
        raise ValueError(f"Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY. Detalle: {detalle}")
    if respuesta.status_code == 400 and "API key" in respuesta.text:
        # Gemini responde 400 (no 401) cuando la key es inválida
        raise ValueError(f"API key inválida. Revisa tu GEMINI_API_KEY. Detalle: {detalle}")
    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After")
        mensaje = f"Límite excedido. Reintentar en {segundos}s." if segundos else "Límite excedido."
        raise TimeoutError(mensaje)
    if respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintentar")
    if respuesta.status_code != 200:
        raise RuntimeError(f"Error en la petición. Status Code: {respuesta.status_code}. Detalle: {detalle}")

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.") from None


def con_reintento(funcion: Callable[[], Any], intentos: int = 3, espera_segundos: float = 2) -> Any:
    """Reintenta ante TimeoutError (429, 5xx, red) con backoff exponencial."""
    if intentos < 1:
        raise ValueError("intentos debe ser >= 1")
    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError as error:
            if intento == intentos - 1:
                raise
            espera = espera_segundos * (2 ** intento)
            print(f"Intento {intento + 1} de {intentos} falló ({error}). Reintentando en {espera:.0f}s...")
            time.sleep(espera)


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        motivo = None
        try:
            motivo = datos["candidates"][0].get("finishReason")
        except (KeyError, IndexError, TypeError, AttributeError):
            motivo = (datos or {}).get("promptFeedback") if isinstance(datos, dict) else None
        raise RuntimeError(f"La respuesta no trae el texto generado. Motivo: {motivo}") from None


def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos.get("usageMetadata", {})
    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)  # no existe si el modelo no razona
    return (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)


def parsear_respuesta_json(texto, claves_requeridas=None):
    """claves_requeridas = ["categoria", "nivel"]"""
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido") from None

    if claves_requeridas:
        if not isinstance(datos, dict):
            raise ValueError("La respuesta no tiene la estructura esperada (se esperaba un objeto JSON).")
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError(f"La respuesta no tiene la estructura esperada. Faltan: {faltantes}")
    return datos


def obtener_dato_de_prueba(pregunta, modelo=MODELO):
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "nivel": {"type": "NUMBER"},
        },
        "required": ["categoria", "nivel"],
    }
    system_instruction = "Eres un asistente amigable y respondes en máximo 2 palabras."
    url, body = armar_peticion(modelo, pregunta, system_instruction, response_schema)

    inicio = time.perf_counter()
    datos = con_reintento(lambda: enviar_peticion(url, body))
    latencia = time.perf_counter() - inicio
    print(f"Latencia: {latencia:.2f} segundos")

    precio_entrada, precio_salida = PRECIOS[modelo]
    costo = calcular_costo(datos, precio_entrada, precio_salida)
    print(f"Costo de la petición: ${costo:.6f} USD")

    texto = extraer_texto(datos)
    return parsear_respuesta_json(texto, ["categoria", "nivel"])


if __name__ == "__main__":
    try:
        print(obtener_dato_de_prueba("Confirma en una frase corta que esta conexión funciona"))
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)
