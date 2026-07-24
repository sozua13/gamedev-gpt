import streamlit as st
from google import genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="CoreAI - Seu Copiloto de Jogos",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CHAVE DA API ---
# Tenta buscar dos Secrets do Streamlit Cloud, senão usa a variável direta
if "API_KEY" in st.secrets:
    API_KEY = st.secrets["API_KEY"]
else:
    API_KEY = "SUA_CHAVE_AQUI"  # Cole sua API Key aqui para testes locais

client = genai.Client(api_key=API_KEY) if API_KEY and API_KEY != "SUA_CHAVE_AQUI" else None

# --- CONFIGURAÇÃO DE SESSÃO ---
LIMITE_GRATUITO = 3

if "messages" not in st.session_state:
    st.session_state.messages = []

if "usos_hoje" not in st.session_state:
    st.session_state.usos_hoje = 0

if "plano_vip" not in st.session_state:
    st.session_state.plano_vip = False

if "prompt_sugerido" not in st.session_state:
    st.session_state.prompt_sugerido = None

# --- BARRA LATERAL (PAINEL DE CONTROLE) ---
with st.sidebar:
    st.title("🎮 CoreAI")
    st.caption("Seu Copiloto AI para Criar Jogos")
    
    st.markdown("---")
    st.subheader("⚙️ Configurações do Projeto")
    
    engine_foco = st.selectbox(
        "Engine / Linguagem:",
        ["Unity (C#)", "Godot 4 (GDScript)", "Roblox (Lua)", "Unreal Engine 5 (C++)", "Roteiro & Lore"]
    )
    
    nivel_codigo = st.select_slider(
        "Nível do Código:",
        options=["Iniciante (Comentado)", "Intermediário", "Avançado (Otimizado/Design Patterns)"]
    )

    st.markdown("---")
    
    # Status do Plano / Créditos
    if st.session_state.plano_vip:
        st.success("🌟 **Plano PRO Ativo** (Acesso Ilimitado)")
    else:
        usos_restantes = LIMITE_GRATUITO - st.session_state.usos_hoje
        st.metric(label="Créditos Diários Grátis", value=f"{usos_restantes}/{LIMITE_GRATUITO}")
        
        st.markdown("### 🚀 Assine o Plano PRO")
        st.write("• Respostas Ilimitadas")
        st.write("• Modelos mais rápidos e precisos")
        st.write("• Suporte Direto")
        
        if st.button("💳 Liberar Plano PRO (Simular)", use_container_width=True):
            st.session_state.plano_vip = True
            st.success("Plano PRO ativado!")
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Nova Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ÁREA PRINCIPAL ---
st.title("💬 CoreAI")
st.caption(f"Foco: **{engine_foco}** | Nível: **{nivel_codigo}**")

# --- SUGGESTION CARDS (EXIBIDOS QUANDO O CHAT ESTÁ VAZIO) ---
if not st.session_state.messages:
    st.markdown("### 💡 O que você deseja criar hoje?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏃‍♂️ Script de Movimentação", use_container_width=True):
            st.session_state.prompt_sugerido = f"Crie um script completo de movimentação de personagem 3D com pulo e corrida para {engine_foco}."
            st.rerun()
            
    with col2:
        if st.button("📜 Diálogo de NPC com Escolhas", use_container_width=True):
            st.session_state.prompt_sugerido = "Crie uma árvore de diálogo interativa entre o jogador e um ferreiro misterioso em uma taverna."
            st.rerun()
            
    with col3:
        if st.button("⚔️ Sistema de Vida e Dano", use_container_width=True):
            st.session_state.prompt_sugerido = f"Crie um sistema modular de Vida, Dano e Cura com eventos/sinais para {engine_foco}."
            st.rerun()

    st.markdown("---")

# --- EXIBIÇÃO DO HISTÓRICO DE MENSAGENS ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE CAPTURA DA ENTRADA DO USUÁRIO ---
prompt_input = st.chat_input("Digite o script, sistema ou narrativa que precisa...")

# Se o usuário clicou em um card de atalho, usa ele como entrada
if st.session_state.prompt_sugerido:
    user_prompt = st.session_state.prompt_sugerido
    st.session_state.prompt_sugerido = None
else:
    user_prompt = prompt_input

if user_prompt:
    
    # Validações antes de enviar
    if not client:
        st.error("⚠️ Insira sua API Key do Google AI Studio no arquivo `app.py` ou no Secrets do Streamlit!")
    elif not st.session_state.plano_vip and st.session_state.usos_hoje >= LIMITE_GRATUITO:
        st.error("❌ Você usou seus 3 créditos grátis de hoje! Faça upgrade para o **Plano PRO** na barra lateral.")
    else:
        # 1. Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # 2. Prepara o histórico recente para dar memória à IA
        historico_contexto = ""
        for msg in st.session_state.messages[-6:]:  # Lida com até as últimas 6 mensagens
            historico_contexto += f"{msg['role'].upper()}: {msg['content']}\n\n"

        # 3. Gera a resposta da IA
        with st.chat_message("assistant"):
            with st.spinner("⚡ Programando e gerando solução..."):
                
                system_prompt = f"""
                Você é o CoreAI, um Programador Senior e Game Designer especialista em desenvolvimento de jogos.
                
                Configurações da sessão:
                - Engine/Foco: {engine_foco}
                - Nível do Código: {nivel_codigo}
                
                Diretrizes:
                1. Se for código, entregue-o limpo, moderno, totalmente funcional e formatado dentro de blocos de código markdown.
                2. Adapte o código ao nível selecionado ({nivel_codigo}).
                3. Leve em consideração o histórico recente de conversa.

                Histórico da conversa:
                {historico_contexto}
                
                Resposta:
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=system_prompt,
                    )
                    
                    resposta_texto = response.text
                    st.markdown(resposta_texto)
                    
                    # Salva no histórico
                    st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                    
                    # Consome crédito se não for VIP
                    if not st.session_state.plano_vip:
                        st.session_state.usos_hoje += 1

                except Exception as e:
                    st.error(f"Erro na IA: {e}")
