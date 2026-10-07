import matplotlib.pyplot as plt
from database import conectar_mongo

# 1. Conectar a MongoDB
db, colecciones = conectar_mongo()

def inicializar_riesgos():
    """Carga los riesgos éticos obligatorios de la rúbrica en MongoDB."""
    if not colecciones or "riesgos_eticos" not in colecciones:
        print("❌ Error de conexión a BD.")
        return

    col_riesgos = colecciones["riesgos_eticos"]
    
    # Riesgos extraídos directamente de las instrucciones de tu profesor
    riesgos_base = [
        {
            "modulo": "LLM Clasificador",
            "descripcion": "Alucinaciones del LLM al extraer datos inexistentes del correo.",
            "categoria": "Confiabilidad",
            "probabilidad": 3,
            "impacto": 4,
            "mitigacion": "Validación estricta con Pydantic y plan de respaldo por reglas.",
            "riesgo_residual": 12 # Probabilidad * Impacto
        },
        {
            "modulo": "LLM Clasificador",
            "descripcion": "Sesgo en correos con ortografía informal (discriminación).",
            "categoria": "Sesgo/Equidad",
            "probabilidad": 4,
            "impacto": 3,
            "mitigacion": "Proporcionar contexto neutro al LLM; auditar falsos positivos.",
            "riesgo_residual": 12
        },
        {
            "modulo": "Motor de Acceso",
            "descripcion": "Privacidad de datos de salud y personales del conductor.",
            "categoria": "Privacidad",
            "probabilidad": 2,
            "impacto": 5,
            "mitigacion": "Retención mínima de datos en MongoDB y accesos cifrados.",
            "riesgo_residual": 10
        },
        {
            "modulo": "Sistema General",
            "descripcion": "Dependencia excesiva de la automatización (operadores no revisan).",
            "categoria": "Operativo",
            "probabilidad": 4,
            "impacto": 4,
            "mitigacion": "Forzar revisión humana en incidentes críticos o discrepancias.",
            "riesgo_residual": 16
        }
    ]

    # Limpiamos la colección antes de insertar para no duplicar datos en las pruebas
    col_riesgos.delete_many({})
    col_riesgos.insert_many(riesgos_base)
    print("✅ Matriz de riesgos éticos inicializada y guardada en MongoDB.")

def graficar_riesgos():
    """Genera una gráfica de dispersión Impacto vs Probabilidad."""
    if not colecciones or "riesgos_eticos" not in colecciones:
        return

    riesgos = list(colecciones["riesgos_eticos"].find())
    
    probabilidades = [r["probabilidad"] for r in riesgos]
    impactos = [r["impacto"] for r in riesgos]
    descripciones = [r["categoria"] for r in riesgos]

    plt.figure(figsize=(9, 6))
    plt.style.use('dark_background') # Estilo oscuro para que combine con tu interfaz
    
    # Asignar colores tipo semáforo según la gravedad del riesgo
    colores = ['red' if (p*i) >= 15 else 'yellow' if (p*i) >= 10 else 'green' for p, i in zip(probabilidades, impactos)]

    # Crear gráfico de dispersión
    plt.scatter(probabilidades, impactos, s=300, c=colores, alpha=0.8, edgecolors='white')

    # Añadir las etiquetas al lado de cada punto
    for i, desc in enumerate(descripciones):
        plt.annotate(desc, (probabilidades[i], impactos[i]), xytext=(10, 5), textcoords='offset points', fontsize=10, color='white')

    plt.title('Matriz de Riesgos Éticos (Impacto vs Probabilidad)', fontsize=14, color='#58a6ff')
    plt.xlabel('Probabilidad (1-5)', fontsize=12)
    plt.ylabel('Impacto (1-5)', fontsize=12)
    plt.xlim(0, 6)
    plt.ylim(0, 6)
    plt.grid(True, linestyle='--', alpha=0.3)
    
    print("📊 Abriendo interfaz gráfica de la matriz de riesgos...")
    plt.show()

if __name__ == "__main__":
    print("\n--- INICIANDO MÓDULO DE RIESGOS ---")
    inicializar_riesgos()
    graficar_riesgos()

