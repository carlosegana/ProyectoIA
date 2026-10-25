from src.consumir_gemini import MODELO, armar_peticion, con_reintento, enviar_peticion, extraer_texto

#se ejecuta desde la raíz del proyecto: python cliente.py
if __name__ == "__main__":
    try:
        url, cuerpo = armar_peticion(
            MODELO,
            "¿Cada cuántos kilómetros debo cambiar el aceite del motor?",
            "Eres un asesor automotriz. Responde en máximo 2 frases.",
        )
        respuesta = con_reintento(lambda: enviar_peticion(url, cuerpo))
        print(extraer_texto(respuesta))
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación: ", error)
