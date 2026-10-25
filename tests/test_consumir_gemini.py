import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.consumir_gemini import (
    armar_peticion,
    calcular_costo,
    con_reintento,
    extraer_texto,
    parsear_respuesta_json,
)


class TestParsear(unittest.TestCase):
    def test_json_valido(self):
        self.assertEqual(parsear_respuesta_json('{"a": 1}', ["a"]), {"a": 1})

    def test_con_fences_markdown(self):
        self.assertEqual(parsear_respuesta_json('```json\n{"a": 1}\n```', ["a"]), {"a": 1})

    def test_json_invalido(self):
        with self.assertRaises(ValueError):
            parsear_respuesta_json("no es json")

    def test_clave_faltante(self):
        with self.assertRaises(ValueError):
            parsear_respuesta_json('{"a": 1}', ["a", "b"])

    def test_lista_en_vez_de_objeto(self):
        with self.assertRaises(ValueError):
            parsear_respuesta_json("[1, 2]", ["a"])


class TestCosto(unittest.TestCase):
    def test_con_razonamiento(self):
        datos = {"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5, "thoughtsTokenCount": 5}}
        self.assertAlmostEqual(calcular_costo(datos, 1, 2), 10 + 2 * 10)

    def test_sin_razonamiento_no_falla(self):
        datos = {"usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5}}
        self.assertAlmostEqual(calcular_costo(datos, 1, 2), 10 + 10)


class TestExtraerTexto(unittest.TestCase):
    def test_ok(self):
        datos = {"candidates": [{"content": {"parts": [{"text": "hola"}]}}]}
        self.assertEqual(extraer_texto(datos), "hola")

    def test_sin_candidatos(self):
        with self.assertRaises(RuntimeError):
            extraer_texto({"promptFeedback": {"blockReason": "SAFETY"}})


class TestPeticion(unittest.TestCase):
    def test_key_no_va_en_la_url(self):
        url, _ = armar_peticion("m", "hola", "")
        self.assertNotIn("key=", url)

    def test_system_instruction_vacia_se_omite(self):
        _, body = armar_peticion("m", "hola", "")
        self.assertNotIn("systemInstruction", body)

    def test_pregunta_vacia(self):
        with self.assertRaises(ValueError):
            armar_peticion("m", "", "x")


class TestReintento(unittest.TestCase):
    def test_reintenta_y_termina(self):
        llamadas = []

        def f():
            llamadas.append(1)
            if len(llamadas) < 3:
                raise TimeoutError("x")
            return "ok"

        self.assertEqual(con_reintento(f, intentos=3, espera_segundos=0), "ok")
        self.assertEqual(len(llamadas), 3)

    def test_agota_intentos(self):
        def f():
            raise TimeoutError("x")

        with self.assertRaises(TimeoutError):
            con_reintento(f, intentos=2, espera_segundos=0)


if __name__ == "__main__":
    unittest.main()
