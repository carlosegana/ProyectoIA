import os
import sys
import time

# Permite ejecutar tanto con `python -m src.evaluacion_modelos` como `python src/evaluacion_modelos.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import consumir_gemini
from src.consumir_gemini import PRECIOS


def evaluar_modelo(nombre_modelo, pregunta, precio_entrada, precio_salida, repeticiones=4):
    """
    Ejecuta 'repeticiones' veces la misma petición para un modelo.
    Imprime latencia, costo y respuesta de cada intento y devuelve el resumen.
    """
    print("=" * 70)
    print(f" EVALUANDO MODELO: {nombre_modelo}")
    print("=" * 70)

    latencias = []
    costos = []

    for i in range(1, repeticiones + 1):
        print(f"\n--- Intento {i} de {repeticiones} ({nombre_modelo}) ---")
        url, body = consumir_gemini.armar_peticion(nombre_modelo, pregunta, "Eres un asistente útil.")

        try:
            inicio = time.perf_counter()
            datos = consumir_gemini.con_reintento(lambda: consumir_gemini.enviar_peticion(url, body))
            latencia = time.perf_counter() - inicio

            costo = consumir_gemini.calcular_costo(datos, precio_entrada, precio_salida)
            respuesta = consumir_gemini.extraer_texto(datos)
        except (ValueError, RuntimeError, TimeoutError) as error:
            print(f"Intento fallido: {error}")
            continue

        latencias.append(latencia)
        costos.append(costo)
        print(f"Latencia:  {latencia:.2f} segundos")
        print(f"Costo:     ${costo:.6f} USD")
        print(f"Respuesta: {respuesta}")

    if not latencias:
        print(f"\n{nombre_modelo}: ningún intento exitoso.\n")
        return {"modelo": nombre_modelo, "exitos": 0, "latencia_promedio": None, "costo_total": None}

    resumen = {
        "modelo": nombre_modelo,
        "exitos": len(latencias),
        "latencia_promedio": sum(latencias) / len(latencias),
        "costo_total": sum(costos),
    }
    print("\n" + "-" * 40)
    print(f" RESUMEN {nombre_modelo}:")
    print(f" Éxitos: {resumen['exitos']}/{repeticiones}")
    print(f" Latencia promedio: {resumen['latencia_promedio']:.2f} segundos")
    print(f" Costo acumulado: ${resumen['costo_total']:.6f} USD")
    print("-" * 40 + "\n")
    return resumen


PREGUNTA_PRUEBA = "Confirma la conexion"
# Los precios viven en consumir_gemini.PRECIOS (un solo lugar)
MODELOS = list(PRECIOS)


def main():
    resumenes = []
    for nombre in MODELOS:
        precio_entrada, precio_salida = PRECIOS[nombre]
        resumenes.append(evaluar_modelo(nombre, PREGUNTA_PRUEBA, precio_entrada, precio_salida, repeticiones=4))

    print("=" * 70)
    print(" COMPARACIÓN FINAL")
    print("=" * 70)
    for r in resumenes:
        if r["latencia_promedio"] is None:
            print(f"{r['modelo']:<24} sin resultados")
        else:
            print(f"{r['modelo']:<24} {r['latencia_promedio']:>6.2f}s  ${r['costo_total']:.6f}  ({r['exitos']} éxitos)")


if __name__ == "__main__":
    main()
