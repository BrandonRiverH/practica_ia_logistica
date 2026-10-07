import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import json
import ollama

from database import conectar_mongo
import logica
import incidentes
import riesgos

db, colecciones = conectar_mongo()

class MegaDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión Logística - Asistente Inteligente")
        self.root.geometry("950x700")
        
        self.bg_color = "#f4f7f9" 
        self.card_color = "#ffffff" 
        self.text_color = "#2c3e50" 
        self.accent_color = "#3498db" 
        
        self.root.configure(bg=self.bg_color)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#e0e6ed", foreground=self.text_color, padding=[20, 10], font=('Segoe UI', 11, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", self.card_color)], foreground=[("selected", self.accent_color)])
        style.configure("TFrame", background=self.bg_color)

        tk.Label(root, text="👋 Bienvenido al Sistema de Logística Inteligente", font=("Segoe UI", 18, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=15)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tab_accesos = ttk.Frame(self.notebook)
        self.tab_incidentes = ttk.Frame(self.notebook)
        self.tab_chat_rag = ttk.Frame(self.notebook)
        self.tab_riesgos = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_accesos, text="🚦 1. Autorizar Entradas")
        self.notebook.add(self.tab_incidentes, text="✉️ 2. Leer Correos")
        self.notebook.add(self.tab_chat_rag, text="💬 3. Preguntar a la IA")
        self.notebook.add(self.tab_riesgos, text="🛡️ 4. Seguridad del Sistema")

        self.construir_tab_accesos()
        self.construir_tab_incidentes()
        self.construir_tab_chat_rag()
        self.construir_tab_riesgos()

    # ==========================================
    # PESTAÑA 1: CONTROL DE ACCESOS
    # ==========================================
    def construir_tab_accesos(self):
        instrucciones = "Llena este pequeño cuestionario para saber si el camión tiene permiso de entrar a la planta."
        tk.Label(self.tab_accesos, text=instrucciones, font=("Segoe UI", 11), bg=self.bg_color, fg="#596a7b").pack(pady=10)
        
        frame_form = tk.Frame(self.tab_accesos, bg=self.card_color, bd=1, relief="solid", highlightbackground="#e0e6ed")
        frame_form.pack(pady=10, padx=20, fill=tk.X)

        frame_placa = tk.Frame(frame_form, bg=self.card_color)
        frame_placa.pack(pady=15)
        tk.Label(frame_placa, text="Escribe las placas del camión:", font=("Segoe UI", 11, "bold"), bg=self.card_color, fg=self.text_color).pack(side=tk.LEFT, padx=10)
        self.entrada_placa = tk.Entry(frame_placa, font=("Segoe UI", 12), width=15, bg="#f8f9fa")
        self.entrada_placa.pack(side=tk.LEFT)

        self.var_P = tk.BooleanVar()
        self.var_Q = tk.BooleanVar()
        self.var_R = tk.BooleanVar()
        self.var_S = tk.BooleanVar()
        self.var_V = tk.BooleanVar()
        self.var_H = tk.BooleanVar()

        preguntas = [
            ("¿El chofer presentó su identificación oficial vigente?", self.var_P),
            ("¿El camión transporta materiales peligrosos o tóxicos?", self.var_Q),
            ("¿Tienen un permiso especial del gerente para esta carga?", self.var_R),
            ("¿Tenían una cita programada para el día de hoy?", self.var_S),
            ("¿La certificación médica y técnica del chofer está al día?", self.var_V),
            ("¿Llegaron dentro de su horario laboral permitido?", self.var_H)
        ]
        
        frame_preguntas = tk.Frame(frame_form, bg=self.card_color)
        frame_preguntas.pack(pady=5, padx=20, fill=tk.X)

        for i, (texto, var) in enumerate(preguntas):
            tk.Checkbutton(frame_preguntas, text=texto, variable=var, font=("Segoe UI", 11), bg=self.card_color, fg=self.text_color, selectcolor=self.card_color, activebackground=self.card_color).grid(row=i, column=0, sticky="w", pady=5)

        tk.Button(self.tab_accesos, text="Decidir y Guardar Registro", bg="#27ae60", fg="white", bd=0, font=("Segoe UI", 12, "bold"), command=self.ejecutar_logica, cursor="hand2").pack(pady=15, ipady=8, ipadx=20)
        
        self.consola_accesos = scrolledtext.ScrolledText(self.tab_accesos, height=8, bg="#f8f9fa", fg=self.text_color, font=("Segoe UI", 11), bd=1, relief="solid")
        self.consola_accesos.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.consola_accesos.config(state=tk.DISABLED) # Bloqueamos edición

    def ejecutar_logica(self):
        placa = self.entrada_placa.get().strip()
        if not placa: return
        
        bitacora = logica.evaluar_acceso(placa, self.var_P.get(), self.var_Q.get(), self.var_R.get(), self.var_S.get(), self.var_V.get(), self.var_H.get())
        
        decision = bitacora["decision"]
        if "Autorizado" in decision or "Especial" in decision:
            mensaje = f"✅ ¡Todo en orden! El camión {placa} TIENE PERMISO para entrar.\nResumen del sistema: {bitacora['explicacion']}"
        else:
            mensaje = f"⛔ ALTO. El camión {placa} NO PUEDE ENTRAR.\nResumen del sistema: {bitacora['explicacion']}"
            
        # Desbloqueamos para escribir, escribimos y volvemos a bloquear
        self.consola_accesos.config(state=tk.NORMAL)
        self.consola_accesos.insert(tk.END, f"\n{mensaje}\n(Guardado automáticamente en la base de datos)\n{'-'*60}")
        self.consola_accesos.see(tk.END)
        self.consola_accesos.config(state=tk.DISABLED)

        self.root.after(2500, self.limpiar_formulario)

    def limpiar_formulario(self):
        self.entrada_placa.delete(0, tk.END)
        for var in [self.var_P, self.var_Q, self.var_R, self.var_S, self.var_V, self.var_H]:
            var.set(False)

    # ==========================================
    # PESTAÑA 2: INCIDENTES 
    # ==========================================
    def construir_tab_incidentes(self):
        tk.Label(self.tab_incidentes, text="Pega aquí el correo electrónico que te llegó para clasificarlo.", font=("Segoe UI", 11), bg=self.bg_color, fg="#596a7b").pack(pady=(10, 0))
        tk.Label(self.tab_incidentes, text="Ejemplo: 'Hola, soy el chofer del CAM-102. Tuvimos un choque y se regó la mercancía...'", font=("Segoe UI", 9, "italic"), bg=self.bg_color, fg="#7f8c8d").pack(pady=(0, 10))
        
        # Esta caja SÍ es editable porque aquí pegas el correo
        self.texto_correo = scrolledtext.ScrolledText(self.tab_incidentes, height=8, bg=self.card_color, fg=self.text_color, font=("Segoe UI", 11), bd=1, relief="solid")
        self.texto_correo.pack(fill=tk.X, padx=20, pady=5)

        self.btn_clasificar = tk.Button(self.tab_incidentes, text="✨ Enviar correo a IA", bg="#9b59b6", fg="white", bd=0, font=("Segoe UI", 12, "bold"), command=self.ejecutar_clasificador, cursor="hand2")
        self.btn_clasificar.pack(pady=15, ipady=8, ipadx=20)

        self.consola_incidentes = scrolledtext.ScrolledText(self.tab_incidentes, height=10, bg="#f8f9fa", fg=self.text_color, font=("Segoe UI", 11), bd=1, relief="solid")
        self.consola_incidentes.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.consola_incidentes.config(state=tk.DISABLED) # Bloqueamos resultados

    def ejecutar_clasificador(self):
        correo = self.texto_correo.get(1.0, tk.END).strip()
        if not correo: return
        self.btn_clasificar.config(state=tk.DISABLED)
        
        self.consola_incidentes.config(state=tk.NORMAL)
        self.consola_incidentes.insert(tk.END, "\n🤖 La Inteligencia Artificial está leyendo el correo. Dame un momento...\n")
        self.consola_incidentes.see(tk.END)
        self.consola_incidentes.config(state=tk.DISABLED)
        self.root.update()

        def hilo():
            try:
                resultado = incidentes.clasificar_incidente(correo)
                datos = resultado["clasificacion"]
                reporte = f"""
📋 REPORTE GENERADO:
- Prioridad del problema: {datos.get('prioridad', 'No definida')}
- Tipo de problema: {datos.get('categoria', 'Desconocido')}
- Personas/Camiones involucrados: {', '.join(datos.get('entidades', []))}
- Resumen rápido: {datos.get('resumen', '')}

✅ Listo. Este reporte ya se guardó en los archivos de la empresa.
{'-'*60}"""
                self.root.after(0, lambda: self.mostrar_resultado_correo(reporte))
            except Exception as e:
                self.root.after(0, lambda: self.mostrar_resultado_correo(f"❌ Ocurrió un error al analizar: {e}\n"))
        
        threading.Thread(target=hilo, daemon=True).start()

    def mostrar_resultado_correo(self, mensaje):
        self.consola_incidentes.config(state=tk.NORMAL)
        self.consola_incidentes.insert(tk.END, mensaje)
        self.consola_incidentes.see(tk.END)
        self.consola_incidentes.config(state=tk.DISABLED)
        self.btn_clasificar.config(state=tk.NORMAL)
        self.texto_correo.delete(1.0, tk.END) 

    # ==========================================
    # PESTAÑA 3: ASISTENTE RAG 
    # ==========================================
    def construir_tab_chat_rag(self):
        tk.Label(self.tab_chat_rag, text="Si no quieres buscar en los archivos, solo pregúntame qué pasó hoy.", font=("Segoe UI", 11), bg=self.bg_color, fg="#596a7b").pack(pady=10)
        
        self.chat_rag = scrolledtext.ScrolledText(self.tab_chat_rag, height=15, bg=self.card_color, fg=self.text_color, font=("Segoe UI", 11), bd=1, relief="solid")
        self.chat_rag.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.chat_rag.insert(tk.END, "🤖 [Tu Asistente]: ¡Hola! Soy tu asistente virtual. Hablame normal, como si chatearas. ¿Quieres saber sobre algún camión que haya entrado hoy?\n\n")
        self.chat_rag.config(state=tk.DISABLED) # Bloqueamos el historial (Solo lectura)

        frame_input = tk.Frame(self.tab_chat_rag, bg=self.bg_color)
        frame_input.pack(fill=tk.X, padx=20, pady=15)

        # AQUI ES DONDE EL USUARIO DEBE ESCRIBIR SUS PREGUNTAS
        self.entrada_pregunta = tk.Entry(frame_input, font=("Segoe UI", 12), bg=self.card_color, fg=self.text_color)
        self.entrada_pregunta.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        self.entrada_pregunta.bind("<Return>", lambda event: self.ejecutar_rag())

        self.btn_pregunta = tk.Button(frame_input, text="Enviar Pregunta", bg="#3498db", fg="white", bd=0, font=("Segoe UI", 11, "bold"), command=self.ejecutar_rag, cursor="hand2")
        self.btn_pregunta.pack(side=tk.RIGHT, ipady=5, ipadx=15)

    def ejecutar_rag(self):
        pregunta = self.entrada_pregunta.get().strip()
        if not pregunta: return
        
        self.chat_rag.config(state=tk.NORMAL) # Desbloqueamos para insertar texto del sistema
        self.chat_rag.insert(tk.END, f"👤 [Tú]: {pregunta}\n")
        self.chat_rag.insert(tk.END, "🤖 [Tu Asistente]: Pensando y buscando en los archivos... (esto puede tardar unos segundos)\n")
        self.chat_rag.see(tk.END)
        self.chat_rag.config(state=tk.DISABLED) # Volvemos a bloquear
        
        self.entrada_pregunta.delete(0, tk.END)
        self.btn_pregunta.config(state=tk.DISABLED)
        self.root.update()

        def hilo():
            contexto = "No se encontraron accesos recientes en la base de datos."
            try:
                if colecciones and "accesos" in colecciones:
                    ultimos = list(colecciones["accesos"].find().sort("_id", -1).limit(10))
                    if ultimos:
                        contexto = "HISTORIAL RECIENTE DE CAMIONES:\n"
                        for a in ultimos:
                            contexto += f"- Placa: {a.get('placa', '')} | Decisión: {a.get('decision', '')} | Razón: {a.get('explicacion', '')}\n"

                prompt_rag = f"Eres un asistente humano y amable. Responde a la pregunta del usuario basándote SOLO en este historial:\n\n{contexto}\n\nPregunta: {pregunta}\nSi el camión no está en el historial, díselo amablemente."
                
                respuesta = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt_rag}])
                texto_final = respuesta['message']['content']
                
                self.root.after(0, lambda: self.imprimir_respuesta_rag(f"🤖 [Tu Asistente]: {texto_final}\n\n"))
            
            except Exception as e:
                error = f"🤖 [Tu Asistente]: Ups, tuve un problema técnico. Detalle: {str(e)}\n\n"
                self.root.after(0, lambda: self.imprimir_respuesta_rag(error))
            
        threading.Thread(target=hilo, daemon=True).start()

    def imprimir_respuesta_rag(self, texto):
        self.chat_rag.config(state=tk.NORMAL)
        self.chat_rag.insert(tk.END, texto)
        self.chat_rag.see(tk.END)
        self.chat_rag.config(state=tk.DISABLED)
        self.btn_pregunta.config(state=tk.NORMAL)

    # ==========================================
    # PESTAÑA 4: RIESGOS ÉTICOS
    # ==========================================
    def construir_tab_riesgos(self):
        tk.Label(self.tab_riesgos, text="Revisión de Salud y Seguridad de la IA", font=("Segoe UI", 16, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=30)
        
        texto_explicativo = (
            "Para asegurarnos de que la Inteligencia Artificial sea justa y segura,\n"
            "nuestro sistema evalúa automáticamente posibles riesgos éticos.\n\n"
            "Presiona el botón de abajo para ver un mapa visual."
        )
        tk.Label(self.tab_riesgos, text=texto_explicativo, bg=self.bg_color, fg="#596a7b", font=("Segoe UI", 12), justify=tk.CENTER).pack(pady=20)
        tk.Button(self.tab_riesgos, text="🔍 Ver Mapa de Seguridad", bg="#e67e22", fg="white", bd=0, font=("Segoe UI", 13, "bold"), command=riesgos.graficar_riesgos, cursor="hand2").pack(pady=20, ipady=10, ipadx=25)


if __name__ == "__main__":
    root = tk.Tk()
    app = MegaDashboard(root)
    root.mainloop()
