from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# 1. Credenciales y cadena de conexión
USER = "hector1985"
PASS = "Aime131985"
CLUSTER = "utvt.qqqotrr.mongodb.net"
DB_NAME = "Brandon_hr_D73"

MONGO_URI = f"mongodb+srv://{USER}:{PASS}@{CLUSTER}/?retryWrites=true&w=majority"

def conectar_mongo():
    """
    Establece la conexión con MongoDB Atlas y devuelve la base de datos
    junto con un diccionario de las colecciones requeridas.
    """
    try:
        print("⏳ Conectando al clúster de MongoDB...")
        # serverSelectionTimeoutMS=5000 hace que no se quede colgado infinitamente si no hay internet
        cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Hacemos un 'ping' forzado para comprobar que la conexión es real
        cliente.admin.command('ping')
        print("✅ ¡Conexión exitosa a MongoDB Atlas!")
        
        # Conectar a tu base de datos específica
        db = cliente[DB_NAME]
        
        # Preparar las 5 colecciones que pide la práctica (Punto 2.1)
        colecciones = {
            "camiones": db["camiones"],
            "accesos": db["accesos"],
            "incidentes": db["incidentes"],
            "riesgos_eticos": db["riesgos_eticos"],
            "evaluaciones_llm": db["evaluaciones_llm"]
        }
        
        return db, colecciones
        
    except ConnectionFailure:
        print("❌ Error crítico: No se pudo conectar al servidor. Verifica tu conexión a internet.")
        return None, None
    except OperationFailure as e:
        print(f"❌ Error de autenticación (Revisa usuario/contraseña): {e}")
        return None, None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None, None

# Bloque de prueba (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    base_datos, cols = conectar_mongo()
    
    if base_datos is not None:
        print("-" * 40)
        print(f"📁 Base de datos activa: {base_datos.name}")
        print("📚 Colecciones inicializadas:")
        for nombre in cols.keys():
            print(f"   - {nombre}")
        print("-" * 40)
