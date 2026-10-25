import os
import sys
import time
from datetime import date
from pathlib import Path

#para poder correrlo desde la raíz o desde src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import consumir_gemini
from src.consumir_gemini import PRECIOS


def evaluar_modelo(nombre_modelo, pregunta, precio_entrada, precio_salida, repeticiones=4):
    """
    Ejecuta 'repeticiones' veces la misma petición para un modelo específico.
    Calcula e imprime Latencia, Costo y Respuesta de cada intento,
    además del promedio de latencia al final.
    """
    print("=" * 70)
    print(f" EVALUANDO MODELO: {nombre_modelo}")
    print("=" * 70)

    latencias = []
    costos = []
    tokens_salida = []
    respuestas = []

    for i in range(1, repeticiones + 1):
        print(f"\n--- Intento {i} de {repeticiones} ({nombre_modelo}) ---")

        # 1. Armar petición
        url, body = consumir_gemini.armar_peticion(nombre_modelo, pregunta, SYSTEM_INSTRUCTION)

        try:
            # 2. Medir latencia
            inicio = time.perf_counter()
            datos = consumir_gemini.con_reintento(lambda: consumir_gemini.enviar_peticion(url, body))
            latencia = time.perf_counter() - inicio

            # 3. Calcular costo
            costo = consumir_gemini.calcular_costo(datos, precio_entrada, precio_salida)

            # 4. Extraer respuesta
            respuesta = consumir_gemini.extraer_texto(datos)
            uso = datos.get("usageMetadata", {})
            salida = uso.get("candidatesTokenCount", 0) + uso.get("thoughtsTokenCount", 0)
        except (ValueError, RuntimeError, TimeoutError) as error:
            #si un intento falla sigo con el siguiente
            print(f"Intento fallido: {error}")
            continue

        latencias.append(latencia)
        costos.append(costo)
        tokens_salida.append(salida)
        respuestas.append(respuesta)

        # 5. Imprimir resultados de la petición actual
        print(f"Latencia:  {latencia:.2f} segundos")
        print(f"Costo:     ${costo:.6f} USD")
        print(f"Respuesta: {respuesta}")

    if not latencias:
        print(f"\n{nombre_modelo}: no salió ningún intento.\n")
        return {"modelo": nombre_modelo, "exitos": 0, "latencia_promedio": None, "costo_total": None,
                "costo_promedio": None, "tokens_salida_promedio": None, "respuesta": None}

    resumen = {
        "modelo": nombre_modelo,
        "exitos": len(latencias),
        "latencia_promedio": sum(latencias) / len(latencias),
        "costo_total": sum(costos),
        "costo_promedio": sum(costos) / len(costos),
        "tokens_salida_promedio": sum(tokens_salida) / len(tokens_salida),
        "respuesta": respuestas[0],
    }

    print("\n" + "-" * 40)
    print(f" RESUMEN {nombre_modelo}:")
    print(f" Intentos exitosos: {resumen['exitos']}/{repeticiones}")
    print(f" Latencia promedio: {resumen['latencia_promedio']:.2f} segundos")
    print(f" Costo acumulado: ${resumen['costo_total']:.6f} USD")
    print("-" * 40 + "\n")
    return resumen


SYSTEM_INSTRUCTION = "Eres un asesor automotriz experto. Responde en máximo 2 frases."
PREGUNTA_PRUEBA = "¿Cada cuántos kilómetros debo cambiar el aceite de un motor a gasolina y qué riesgo hay si me atraso?"
#los 3 con free tier, los precios están en consumir_gemini.PRECIOS
MODELOS = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]


#guarda la tabla en docs/ para usarla en el documento de decisión
RUTA_COMPARACION = Path(__file__).parent.parent / "docs" / "comparacion_modelos.md"


def guardar_comparacion(resumenes, repeticiones, ruta=RUTA_COMPARACION):
    lineas = [
        "# Resultados de la evaluación de modelos",
        "",
        f"- Fecha: {date.today().isoformat()}",
        f"- Pregunta: {PREGUNTA_PRUEBA}",
        f"- Instrucción de sistema: {SYSTEM_INSTRUCTION}",
        f"- Peticiones por modelo: {repeticiones}",
        "",
        "| Modelo | Exitosos | Latencia promedio | Tokens de salida (promedio) | Costo por petición | Costo total |",
        "|---|---|---|---|---|---|",
    ]
    for r in resumenes:
        if r["latencia_promedio"] is None:
            lineas.append(f"| {r['modelo']} | 0/{repeticiones} | sin datos | sin datos | sin datos | sin datos |")
        else:
            lineas.append(
                f"| {r['modelo']} | {r['exitos']}/{repeticiones} | {r['latencia_promedio']:.2f} s "
                f"| {r['tokens_salida_promedio']:.0f} | ${r['costo_promedio']:.6f} | ${r['costo_total']:.6f} |"
            )
    lineas += ["", "## Respuesta de ejemplo de cada modelo", ""]
    for r in resumenes:
        lineas += [f"### {r['modelo']}", "", r["respuesta"] or "sin respuesta", ""]
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
    print(f"Tabla guardada en {ruta}")


def main():
    repeticiones = 4
    resumenes = []
    for nombre in MODELOS:
        precio_entrada, precio_salida = PRECIOS[nombre]
        resumenes.append(evaluar_modelo(nombre, PREGUNTA_PRUEBA, precio_entrada, precio_salida, repeticiones=repeticiones))

    print("=" * 70)
    print(" COMPARACIÓN")
    print("=" * 70)
    for r in resumenes:
        if r["latencia_promedio"] is None:
            print(f"{r['modelo']:<24} sin resultados")
        else:
            print(f"{r['modelo']:<24} {r['latencia_promedio']:>6.2f}s  ${r['costo_total']:.6f}  ({r['exitos']} exitosos)")

    guardar_comparacion(resumenes, repeticiones)

if __name__ == "__main__":
    main()
