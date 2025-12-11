import streamlit as st
import Backend 

# --- CONFIGURAÇÃO DA PÁGINA ---
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
    
    # 2. INTERRUPTOR DE MEMÓRIA
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
    
    # 3. LIMPAR TELA
    if st.button("Limpar Tela"):
        st.session_state.messages = []
        st.rerun()

    # 4. UPLOAD DE ARQUIVOS (NOVO)
    st.divider()
    st.header("👀 Arquivos aqui")
    arquivos_upload = st.file_uploader(
        "Mostre algo para o Y:", 
        type=["png", "jpg", "jpeg", "pdf", "txt", "py", "md"], 
        accept_multiple_files=True
    )

# --- INICIALIZAÇÃO DO CHAT ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = Backend.iniciar_chat(modelo_escolhido, usar_memoria)

# --- CARREGA HISTÓRICO VISUAL ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Só carrega do arquivo se a memória estiver LIGADA
    if usar_memoria:
        historico_antigo = Backend.charge_memory()
        for msg in historico_antigo:
            role = "assistant" if msg["role"] == "model" else "user"
            # Proteção para garantir que msg["parts"] seja lida corretamente
            conteudo = msg["parts"][0] if isinstance(msg["parts"], list) else msg["parts"]
            st.session_state.messages.append({"role": role, "content": conteudo})

# --- RENDERIZA MENSAGENS NA TELA ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LOOP DE INTERAÇÃO (CHAT) ---
prompt = st.chat_input("Diga algo para o Y...")

if prompt:
    # 1. Mostra mensagem do usuário
    with st.chat_message("user"):
        st.markdown(prompt)
        # Se tiver arquivos, mostra aviso visual
        if arquivos_upload:
            st.info(f"📎 {len(arquivos_upload)} arquivo(s) anexado(s)")
            
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Processamento e Resposta do Y
    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            chat = st.session_state.chat_session
            
            try:
                # --- LÓGICA DE VISÃO ---
                anexos_processados = []
                if arquivos_upload:
                    # Chama o Backend para converter os arquivos em formato que a IA aceita
                    anexos_processados = Backend.processar_anexos(arquivos_upload)

                # --- CORREÇÃO AQUI ---
                # Enviamos o texto (prompt) e os arquivos separadamente.
                # O Backend se encarrega de juntar tudo na lista correta.
                response = chat.send_message(prompt, arquivos=anexos_processados)
                
                texto = response.text
                custo = Backend.calc_cost(response)
                
                st.markdown(texto)
                st.caption(f"_{custo}_")
                
                # Salva na memória se estiver ativada
                if usar_memoria:
                    Backend.save_memory(chat.history)
                
                st.session_state.messages.append({"role": "assistant", "content": texto})
                
            except Exception as e:
                st.error(f"Erro no processamento: {e}")