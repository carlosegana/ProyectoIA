import json
import os
import re
import time
from typing import Any, Callable

import requests
from dotenv import load_dotenv

#carga el .env de la raíz del proyecto
_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_RAIZ_PROYECTO, ".env"))

#Constantes
MODELO = "gemini-3.5-flash-lite"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")
TIMEOUT_SEGUNDOS = 60

#precio por token en USD (entrada, salida), sacados de la página de precios de Gemini
#los de 3.6 y 3.8 suben el 1 de enero de 2027 (1.50 / 7.50 por millón)
PRECIOS = {
    "gemini-3.8-flash": (0.75 / 1_000_000, 3.75 / 1_000_000),
    "gemini-3.6-flash": (0.75 / 1_000_000, 3.75 / 1_000_000),
    "gemini-3.5-flash-lite": (0.30 / 1_000_000, 2.50 / 1_000_000),
    "gemini-3.1-flash-lite": (0.25 / 1_000_000, 1.50 / 1_000_000),
    "gemini-2.5-flash": (0.30 / 1_000_000, 2.50 / 1_000_000),
    "gemini-2.5-flash-lite": (0.10 / 1_000_000, 0.40 / 1_000_000),
    "gemini-2.5-pro": (1.25 / 1_000_000, 10.00 / 1_000_000),
}


#función para crear la solicitud. La key ya no va en la url, se manda por header en enviar_peticion
def armar_peticion(modelo, pregunta, system_instruction, response_schema=None):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")
    url = f"{URL_BASE}{modelo}:generateContent"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}

    #si el system_instruction viene vacío mejor no mandarlo
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body


#función envía la petición
def enviar_peticion(url, body):
    if not API_KEY:
        raise ValueError("No hay GEMINI_API_KEY. Revisa tu archivo .env")

    headers = {"x-goog-api-key": API_KEY}
    try:
        respuesta = requests.post(url, json=body, headers=headers, timeout=TIMEOUT_SEGUNDOS)
    except requests.exceptions.Timeout:
        raise TimeoutError("Se agotó el tiempo. Intenta de nuevo en unos momentos.") from None
    except requests.exceptions.ConnectionError:
        raise TimeoutError("No se pudo conectar con el servicio. Intenta de nuevo en unos momentos.") from None

    #el body de la respuesta dice la causa real, lo guardo para el mensaje
    detalle = respuesta.text[:300]

    if respuesta.status_code in (401, 403):
        raise ValueError(f"Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY. Detalle: {detalle}")
    #Gemini devuelve 400 (no 401) cuando la key es inválida
    if respuesta.status_code == 400 and "API key" in respuesta.text:
        raise ValueError(f"Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY. Detalle: {detalle}")
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


#reintenta solo si falla con TimeoutError (429, 5xx, conexión). Cada intento espera el doble
def con_reintento(funcion: Callable[[], Any], intentos: int = 3, espera_segundos: float = 2) -> Any:
    if intentos < 1:
        raise ValueError("intentos tiene que ser al menos 1")
    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError as error:
            if intento == intentos - 1:
                raise
            espera = espera_segundos * (2 ** intento)
            print(f"Intento {intento + 1} de {intentos} falló por límite de uso/servidor ({error}). Reintentando en {espera:.0f}s...")
            time.sleep(espera)


#funcion procesa y extrae dato
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        #si Gemini bloquea la respuesta, finishReason dice por qué
        try:
            motivo = datos["candidates"][0].get("finishReason")
        except (KeyError, IndexError, TypeError, AttributeError):
            motivo = None
        raise RuntimeError(f"La respuesta no recibe el texto generado en el lugar definido. (finishReason: {motivo})") from None


def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos.get("usageMetadata", {})
    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)
    #thoughtsTokenCount no viene si el modelo no razonó, por eso el .get
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
    return (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)


def parsear_respuesta_json(texto, claves_requeridas=None):
    #claves_requeridas = ["categoria", "nivel"]
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)
    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido") from None

    if claves_requeridas:
        if not isinstance(datos, dict):
            raise ValueError("La respuesta no tiene la estructura esperada.")
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError(f"La respuesta no tiene la estructura esperada. Faltan: {faltantes}")
    return datos


def obtener_dato_de_prueba(pregunta, modelo=MODELO):
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING", "description": "Sistema afectado: frenos, motor, suspensión, etc."},
            "nivel": {"type": "NUMBER", "description": "Urgencia de 1 (baja) a 5 (crítica)"},
        },
        "required": ["categoria", "nivel"],
    }
    system_instruction = "Eres un asistente de taller mecánico y clasificas fallas de autos. Respondes breve."
    url, body = armar_peticion(modelo, pregunta, system_instruction, response_schema)

    inicio = time.perf_counter() #Empezar el contador
    datos = con_reintento(lambda: enviar_peticion(url, body))
    latencia = time.perf_counter() - inicio #Termina el contador
    print(f"Latencia: {latencia:.2f} segundos")

    if modelo in PRECIOS:
        costo = calcular_costo(datos, *PRECIOS[modelo])
        print(f"Costo de la petición: ${costo:.6f} USD")
    else:
        print(f"No tengo el precio de '{modelo}', agrégalo a PRECIOS.")

    texto = extraer_texto(datos)
    return parsear_respuesta_json(texto, ["categoria", "nivel"])


if __name__ == "__main__": #solo se ejecuta si corro este archivo directo, no en imports
    try:
        print(obtener_dato_de_prueba("Mi auto hace un ruido metálico al frenar y el pedal se siente blando"))
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación: ", error)
