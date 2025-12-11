import customtkinter as ctk
import keyboard
import threading
import time
import sys
import os

# --- CORREÇÃO DO DIRETÓRIO ---
pasta_do_script = os.path.dirname(os.path.abspath(__file__))
os.chdir(pasta_do_script)
sys.path.append(pasta_do_script)

# --- Importação do Backend ---
try:
    from Backend import iniciar_chat
    MODELO = "gemini-2.0-flash"
    BACKEND_CARREGADO = True
except Exception as e:
    BACKEND_CARREGADO = False
    ERRO_BACKEND = f"Erro no Backend: {e}"

# --- Interface Gráfica ---
ctk.set_appearance_mode("Dark")

class QuickPrompt(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela
        self.overrideredirect(True) 
        self.attributes('-topmost', True)
        self.geometry("600x70")
        self.center_window()
        
        self.grid_columnconfigure(0, weight=1)

        # Widgets
        self.entry = ctk.CTkEntry(self, placeholder_text="Y Assistant", height=50, font=("Arial", 16), border_width=0, fg_color="#2b2b2b")
        self.entry.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.entry.bind("<Return>", self.on_submit)
        self.entry.bind("<Escape>", self.hide_window)

        self.response_label = ctk.CTkLabel(self, text="", font=("Arial", 14), text_color="#dce4ee", wraplength=580, justify="left")
        self.response_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        # Estado Inicial
        self.chat_session = None
        self.withdraw()
        self.is_visible = False
        
        # Inicia a primeira sessão
        self.reset_session()

    def center_window(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (600/2)
        y = (hs/3) - (120/2)
        self.geometry(f"+{int(x)}+{int(y)}")

    # --- NOVA FUNÇÃO DE RESET ---
    def reset_session(self):
        """Força a criação de uma nova sessão limpa"""
        if BACKEND_CARREGADO:
            try:
                # Cria uma NOVA sessão do zero
                self.chat_session = iniciar_chat(MODELO, False)
                print("Sessão reiniciada (Memória limpa).")
            except Exception as e:
                self.response_label.configure(text=f"Erro ao resetar: {e}")
        else:
            self.chat_session = None

    def toggle_visibility(self):
        if self.is_visible:
            self.hide_window()
        else:
            self.show_window()

    def show_window(self):
        self.deiconify()
        self.entry.focus_set()
        self.entry.delete(0, 'end')
        self.response_label.configure(text="")
        self.geometry("600x70")
        self.is_visible = True

    def hide_window(self, event=None):
        self.withdraw()
        self.is_visible = False
        # LIMPEZA AQUI: Reseta a sessão ao fechar
        self.reset_session()

    def on_submit(self, event=None):
        texto = self.entry.get()
        if not texto: return
        self.entry.delete(0, 'end') 

        self.response_label.configure(text="...")
        self.geometry("600x120")
        self.update()

        resposta_final = ""
        
        if self.chat_session:
            try:
                # Usa a sessão interna (self.chat_session)
                response = self.chat_session.send_message(texto)
                resposta_final = response.text
            except Exception as e:
                resposta_final = f"Erro na IA: {e}"
        elif not BACKEND_CARREGADO:
            resposta_final = ERRO_BACKEND
        else:
            resposta_final = "Erro: Sessão não inicializada."

        self.response_label.configure(text=resposta_final)
        
        # Ajuste dinâmico de altura
        altura = 80 + (len(str(resposta_final)) // 80 * 20) + 40
        self.geometry(f"600x{min(altura, 600)}")

def run_hotkey(app):
    while True:
        # Seu atalho escolhido
        if keyboard.is_pressed('Alt+p'):
            app.after(0, app.toggle_visibility)
            time.sleep(0.3)
        time.sleep(0.05)

if __name__ == "__main__":
    app = QuickPrompt()
    t = threading.Thread(target=run_hotkey, args=(app,), daemon=True)
    t.start()
    app.mainloop()