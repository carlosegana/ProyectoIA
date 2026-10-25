import os
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSeguridad(unittest.TestCase):
    def test_env_example_sin_credenciales(self):
        #si este test falla, pegaste una key real en .env.example
        with open(os.path.join(RAIZ, ".env.example"), encoding="utf-8") as archivo:
            lineas = [l.strip() for l in archivo if l.startswith("GEMINI_API_KEY=")]
        self.assertEqual(lineas, ["GEMINI_API_KEY=tu_api_key_aqui"])

    def test_env_esta_ignorado(self):
        with open(os.path.join(RAIZ, ".gitignore"), encoding="utf-8") as archivo:
            ignoradas = [l.strip() for l in archivo]
        self.assertIn(".env", ignoradas)


if __name__ == "__main__":
    unittest.main()
