import streamlit as st
import Backend 

# Configuração da página
st.set_page_config(page_title="Y - Assistente", page_icon="🤖")

st.title("🤖 Y")
st.caption("Olá! Sou o Assistente Pessoal do Victor, Como Posso Ajudar?")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuração Cerebral")
    
    # 1. Escolha do Modelo
    modelo_escolhido = st.radio(
        "Versão:",
        ["gemini-2.0-flash", "gemini-3.0-pro-preview"],
        index=0
    )
    
    st.divider()
    
    # 2. INTERRUPTOR DE MEMÓRIA (Padrão: OFF / False)
    # value=False garante que ele comece desligado
    usar_memoria = st.toggle("Ler Memória (Gasta Tokens)", value=False)
    
    # Lógica de Reinício se mudar o toggle
    if "memoria_ativa" not in st.session_state:
        st.session_state.memoria_ativa = usar_memoria
        
    if st.session_state.memoria_ativa != usar_memoria:
        st.session_state.memoria_ativa = usar_memoria
        # Reinicia o backend com a nova configuração
        st.session_state.chat_session = Backend.iniciar_chat(modelo_escolhido, usar_memoria)
        st.session_state.messages = [] # Limpa a tela visual
        st.rerun() # Recarrega a página

    st.divider()
    if st.button("Limpar Tela"):
        st.session_state.messages = []
        st.rerun()

# --- INICIALIZAÇÃO ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = Backend.iniciar_chat(modelo_escolhido, usar_memoria)

# Carrega histórico visual SÓ SE a memória estiver ligada
if "messages" not in st.session_state:
    st.session_state.messages = []
    if usar_memoria:
        historico_antigo = Backend.charge_memory()
        for msg in historico_antigo:
            role = "assistant" if msg["role"] == "model" else "user"
            st.session_state.messages.append({"role": role, "content": msg["parts"][0]})

# Mostra mensagens na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT LOOP ---
prompt = st.chat_input("Diga algo para o Y...")

if prompt:
    # Mostra mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Resposta do Y
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            chat = st.session_state.chat_session
            try:
                response = chat.send_message(prompt)
                texto = response.text
                custo = Backend.calc_cost(response)
                
                st.markdown(texto)
                st.caption(f"_{custo}_")
                
                # SÓ SALVA NO ARQUIVO SE A MEMÓRIA ESTIVER LIGADA
                # Isso protege seu JSON de ser sobrescrito pelo modo econômico
                if usar_memoria:
                    Backend.save_memory(chat.history)
                
                st.session_state.messages.append({"role": "assistant", "content": texto})
                
            except Exception as e:
                st.error(f"Erro: {e}")