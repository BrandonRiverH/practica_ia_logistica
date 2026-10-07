import tkinter as tk
from tkinter import scrolledtext
import ollama
import threading

class AsistenteLLM:
    def __init__(self, root):
        self.root = root
        self.root.title("Asistente LLM - Llama 3.2")
        self.root.geometry("600x700")
        self.root.configure(bg="#0d1117")

        # 1. Cambiar la configuración del sistema (Nuevo Contexto)
        self.historial = [
            {
                "role": "system", 
                "content": "Eres un asistente experto en logística de transporte y seguridad. Responde de forma concisa, profesional y en español."
            }
        ]

        # 2. Interfaz Gráfica (GUI)
        tk.Label(root, text="TUTOR LLM - LOGÍSTICA", font=("Helvetica", 14, "bold"), bg="#0d1117", fg="#58a6ff").pack(pady=10)

        # Área de chat
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25, bg="#161b22", fg="#c9d1d9", font=("Consolas", 10), bd=0, padx=10, pady=10)
        self.chat_display.pack(padx=20, pady=5)
        self.chat_display.config(state=tk.DISABLED)

        # Campo de entrada
        self.entrada_texto = tk.Entry(root, width=58, font=("Consolas", 11), bg="#010409", fg="white", insertbackground="white")
        self.entrada_texto.pack(side=tk.LEFT, padx=(20, 5), pady=20, ipady=5)
        self.entrada_texto.bind("<Return>", lambda event: self.enviar_mensaje())

        # Botón Enviar
        self.btn_enviar = tk.Button(root, text="Enviar", bg="#238636", fg="white", bd=0, font=("Helvetica", 10, "bold"), command=self.enviar_mensaje)
        self.btn_enviar.pack(side=tk.LEFT, padx=5, pady=20, ipady=3)

        # 3. Botón para Resumen de Historial
        self.btn_resumen = tk.Button(root, text="Resumir Historial", bg="#8957e5", fg="white", bd=0, font=("Helvetica", 10, "bold"), command=self.generar_resumen)
        self.btn_resumen.pack(side=tk.LEFT, padx=5, pady=20, ipady=3)

        self.mostrar_mensaje("Sistema", "Asistente de logística iniciado. Escribe tu consulta.")

    def mostrar_mensaje(self, remitente, mensaje, color="#c9d1d9"):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{remitente}]: ", "bold")
        self.chat_display.insert(tk.END, f"{mensaje}\n\n")
        
        # Colores personalizados
        self.chat_display.tag_config("bold", font=("Consolas", 10, "bold"), foreground="#58a6ff" if remitente=="Tú" else "#3fb950")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def procesar_respuesta_llm(self, mensaje_usuario):
        try:
            # Enviar todo el historial a Llama 3.2 local
            respuesta = ollama.chat(model='llama3.2', messages=self.historial)
            contenido_respuesta = respuesta['message']['content']
            
            # Guardar en el historial
            self.historial.append({"role": "assistant", "content": contenido_respuesta})
            
            # Mostrar en GUI
            self.mostrar_mensaje("Llama 3.2", contenido_respuesta)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Asegúrate de que Ollama esté ejecutándose. Detalles: {str(e)}")
        finally:
            self.btn_enviar.config(state=tk.NORMAL)
            self.btn_resumen.config(state=tk.NORMAL)

    def enviar_mensaje(self):
        texto = self.entrada_texto.get().strip()
        if not texto:
            return

        self.entrada_texto.delete(0, tk.END)
        self.btn_enviar.config(state=tk.DISABLED)
        self.btn_resumen.config(state=tk.DISABLED)
        
        self.mostrar_mensaje("Tú", texto)
        self.historial.append({"role": "user", "content": texto})

        # Ejecutar en hilo separado para no congelar la GUI
        threading.Thread(target=self.procesar_respuesta_llm, args=(texto,), daemon=True).start()

    def generar_resumen(self):
        """Solicita al LLM que resuma la conversación actual sin agregarlo al flujo principal del chat."""
        if len(self.historial) <= 1:
            self.mostrar_mensaje("Sistema", "No hay historial suficiente para resumir.")
            return

        self.btn_enviar.config(state=tk.DISABLED)
        self.btn_resumen.config(state=tk.DISABLED)
        self.mostrar_mensaje("Sistema", "Generando resumen del historial...")

        def hilo_resumen():
            try:
                # Creamos un prompt temporal solo para resumir
                prompt_resumen = self.historial.copy()
                prompt_resumen.append({
                    "role": "user", 
                    "content": "Por favor, haz un resumen muy breve en una sola frase de lo que hemos hablado hasta ahora."
                })
                
                respuesta = ollama.chat(model='llama3.2', messages=prompt_resumen)
                resumen = respuesta['message']['content']
                self.mostrar_mensaje("Resumen", resumen)
            except Exception as e:
                self.mostrar_mensaje("Error", "No se pudo generar el resumen.")
            finally:
                self.btn_enviar.config(state=tk.NORMAL)
                self.btn_resumen.config(state=tk.NORMAL)

        threading.Thread(target=hilo_resumen, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AsistenteLLM(root)
    root.mainloop()
