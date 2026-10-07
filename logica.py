from database import conectar_mongo
from datetime import datetime

# 1. Conectamos a la BD usando tu archivo database.py
db, colecciones = conectar_mongo()

def evaluar_acceso(placa, P, Q, R, S, V, H, operador="Admin"):
    """
    Evalúa las reglas lógicas y guarda el resultado en MongoDB.
    """
    # Reglas base del profesor
    A_base = P and S and not Q
    E_base = P and (R or Q)

    # Ampliación de Reglas (Requisito 2.2)
    # Para cualquier acceso, la certificación (V) debe estar vigente.
    # Para acceso normal (A), debe ser en horario permitido (H).
    resultado_A = A_base and V and H
    resultado_E = E_base and V

    # Generar explicación paso a paso (Requisito 2.2)
    explicacion = f"Análisis para {placa}:\n"
    explicacion += f"Premisas: P={P}, Q={Q}, R={R}, S={S}, V={V}, H={H}\n"
    
    if resultado_A:
        decision = "Autorizado (A)"
        explicacion += "-> Aprobado por regla A: Tiene ID (P), Cita (S), NO tiene material peligroso (Q), Certificación vigente (V) y Horario correcto (H)."
    elif resultado_E:
        decision = "Especial (E)"
        explicacion += "-> Aprobado por regla E: Tiene ID (P), Carga Especial/Permiso (R o Q) y Certificación vigente (V)."
    else:
        decision = "Denegado"
        explicacion += "-> Denegado: No cumple simultáneamente los requisitos para A ni para E."

    # Armar la bitácora para la Base de Datos
    bitacora = {
        "placa": placa,
        "P": P, "Q": Q, "R": R, "S": S,
        "V": V, "H": H, 
        "resultado_A": resultado_A,
        "resultado_E": resultado_E,
        "decision": decision,
        "explicacion": explicacion,
        "marca_de_tiempo": datetime.now(),
        "operador": operador
    }

    # 2. Guardar en la colección 'accesos' de MongoDB
    if colecciones and "accesos" in colecciones:
        colecciones["accesos"].insert_one(bitacora)
        print(f"✅ ¡Guardado en MongoDB! Placa: {placa} -> {decision}")
    else:
        print("❌ Fallo en la conexión. No se guardó.")

    return bitacora

# Bloque de Pruebas
if __name__ == "__main__":
    print("\n--- INICIANDO MOTOR DE REGLAS ---")
    
    # Prueba 1: Todo perfecto -> Debería dar Autorizado (A)
    evaluar_acceso("CAM-101", P=True, Q=False, R=False, S=True, V=True, H=True)
    
    # Prueba 2: Trae material peligroso (Q) -> Debería dar Especial (E)
    evaluar_acceso("CAM-102", P=True, Q=True, R=False, S=False, V=True, H=True)
    
    # Prueba 3: Todo bien, pero el chofer tiene la certificación vencida (V=False) -> Denegado
    evaluar_acceso("CAM-103", P=True, Q=False, R=False, S=True, V=False, H=True)
    
    print("\n¡Pruebas finalizadas! Los datos se enviaron a la nube del profesor.")
