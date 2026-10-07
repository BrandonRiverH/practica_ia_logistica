import json
import ollama
from pydantic import BaseModel, ValidationError
from database import conectar_mongo
from datetime import datetime

# 1. Conexión a la BD
db, colecciones = conectar_mongo()

# 2. Definición del Esquema Exacto con Pydantic (Requisito 2.3)
# Esto obliga a que los datos tengan exactamente esta estructura, ni más ni menos.
class IncidenteSchema(BaseModel):
    categoria: str
    prioridad: str
    entidades: list[str]
    resumen: str

def clasificar_por_reglas(correo):
    """Plan de respaldo si el LLM falla o devuelve un JSON inválido (Requisito 2.3)"""
    prioridad = "ALTA" if "urgente" in correo.lower() or "accidente" in correo.lower() else "MEDIA"
    categoria = "Seguridad" if "accidente" in correo.lower() or "derrame" in correo.lower() else "Operativo"
    return {
        "categoria": categoria,
        "prioridad": prioridad,
        "entidades": ["Desconocida (Respaldo)"],
        "resumen": "Clasificado por reglas de respaldo debido a error del LLM."
    }

def clasificar_incidente(correo_texto):
    print("\n🔍 Analizando correo con Llama 3.2 (esto puede tomar unos segundos)...")
    
    prompt_sistema = """
    Eres un asistente de logística. Analiza el siguiente correo y extrae la información.
    Devuelve ÚNICAMENTE un objeto JSON válido con exactamente estas 4 claves:
    "categoria" (ej. Seguridad, Retraso, Mantenimiento), 
    "prioridad" (ALTA, MEDIA, BAJA), 
    "entidades" (lista de placas o nombres de personas involucradas), 
    "resumen" (resumen de 1 linea).
    """
    
    try:
        # Petición a Ollama (forzamos la salida en formato JSON)
        respuesta = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': correo_texto}
            ],
            format='json'
        )
        
        contenido = respuesta['message']['content']
        
        # Convertir texto a diccionario Python
        datos_json = json.loads(contenido)
        
        # 3. Validación estricta con Pydantic
        incidente_validado = IncidenteSchema(**datos_json)
        resultado_final = incidente_validado.model_dump()
        metodo = "LLM (Llama 3.2)"
        print("✅ JSON extraído y validado correctamente por Pydantic.")

    except (json.JSONDecodeError, ValidationError) as e:
        print(f"⚠️ Error: El LLM no devolvió el formato correcto. Entrando a plan de respaldo...\nDetalle: {e}")
        resultado_final = clasificar_por_reglas(correo_texto)
        metodo = "Reglas Duras (Respaldo)"

    # 4. Preparar documento para guardar en MongoDB
    documento = {
        "correo_original": correo_texto,
        "clasificacion": resultado_final,
        "estado": "nuevo",  # Requisito de la rúbrica
        "metodo_clasificacion": metodo,
        "fecha_registro": datetime.now()
    }

    # 5. Guardar en MongoDB (colección 'incidentes')
    if colecciones and "incidentes" in colecciones:
        colecciones["incidentes"].insert_one(documento)
        print(f"💾 Incidente guardado en BD con estado 'nuevo'.")
    
    return documento

# Bloque de Pruebas
if __name__ == "__main__":
    # Simulamos un correo de un incidente real en la aduana/almacén
    correo_prueba = "Urgente: El camión con placas CAM-102 acaba de reportar un derrame de líquido tóxico en la rampa 4. El chofer Juan Pérez está bien, pero necesitamos limpieza inmediata."
    
    resultado = clasificar_incidente(correo_prueba)
    
    print("\n📊 Extracción Final:")
    print(json.dumps(resultado["clasificacion"], indent=2, ensure_ascii=False))
