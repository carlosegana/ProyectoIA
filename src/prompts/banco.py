BANCO_DE_PROMPT = [
    {
        "nombre": "estimar_respuesta_y_tiempo",
        "system_instruction": (
            "Eres asesor de un taller mecánico. Responde únicamente con un JSON con las claves "
            "'respuesta' (texto directo), 'tiempo_estimado' (ej. 'Inmediato', '2-3 horas', "
            "'1-2 días'), 'nivel_complejidad' ('Bajo', 'Medio' o 'Alto') y "
            "'requiere_soporte_humano' (boolean, true si el auto necesita que lo vea un mecánico)."
        ),
        "ejemplo_usuario": (
            "Se me encendió la luz de check engine y el auto vibra al acelerar. "
            "¿Qué debo hacer y cuánto tardaría la revisión?"
        ),
        "claves_esperadas": [
            "respuesta",
            "tiempo_estimado",
            "nivel_complejidad",
            "requiere_soporte_humano",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "respuesta": {"type": "STRING"},
                "tiempo_estimado": {"type": "STRING"},
                "nivel_complejidad": {"type": "STRING"},
                "requiere_soporte_humano": {"type": "BOOLEAN"},
            },
            "required": ["respuesta", "tiempo_estimado", "nivel_complejidad", "requiere_soporte_humano"],
        },
    },
    {
        "nombre": "extraer_entidades",
        "system_instruction": (
            "Extrae del texto las personas, los lugares y las organizaciones "
            "(marcas, concesionarios, talleres) que se mencionen. "
            "Responde únicamente con un JSON con las claves "
            "'personas', 'lugares' y 'organizaciones', cada una con una lista "
            "de textos (vacía si no hay ninguno)."
        ),
        "ejemplo_usuario": (
            "Mariana Soto compró un Toyota Corolla en el concesionario AutoNorte de Santiago "
            "y lo llevó a revisión a Mecánica Rivas, en Valparaíso."
        ),
        "claves_esperadas": ["personas", "lugares", "organizaciones"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "personas": {"type": "ARRAY", "items": {"type": "STRING"}},
                "lugares": {"type": "ARRAY", "items": {"type": "STRING"}},
                "organizaciones": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["personas", "lugares", "organizaciones"],
        },
    },
]
