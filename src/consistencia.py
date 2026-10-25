import json
import os
import sys
import time
from pathlib import Path

#para poder correrlo desde la raíz o desde src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.consumir_gemini import (
    MODELO,
    armar_peticion,
    con_reintento,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)
from src.prompts.banco import BANCO_DE_PROMPT

#ruta fija, así no depende de desde dónde lo ejecute
RUTA_REGISTRO = Path(__file__).parent / "prompts" / "registro_resultados.json"
INTENTOS = 3


def medir_consistencia():
    registro = {}
    try:
        for prompt in BANCO_DE_PROMPT:
            exitos = 0
            for intento in range(INTENTOS):
                url, body = armar_peticion(
                    MODELO,
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt["response_schema"],
                )
                #si un intento falla lo cuento como fallido y sigo con el siguiente
                try:
                    respuesta = con_reintento(lambda: enviar_peticion(url, body))
                    texto = extraer_texto(respuesta)
                    datos = parsear_respuesta_json(texto, prompt["claves_esperadas"])
                    exitos += 1 #exitos++
                    print(f"Respuesta: {datos}")
                except (ValueError, RuntimeError, TimeoutError) as error:
                    print(f" intento {intento + 1} falló: {error}")
                time.sleep(1)
            print(f"{prompt['nombre']}: {exitos}/{INTENTOS} respuestas válidas")
            registro[prompt["nombre"]] = {"exitos": exitos, "intentos": INTENTOS}
    finally:
        #guarda lo que haya en registro_resultados.json, aunque se corte a la mitad
        with open(RUTA_REGISTRO, "w", encoding="utf-8") as archivo:
            json.dump(registro, archivo, indent=2, ensure_ascii=False)
    return registro


if __name__ == "__main__":
    medir_consistencia()
