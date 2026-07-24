import streamlit as st
from openai import OpenAI

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

# --- CHAVE DA API OPENAI ---
if "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    OPENAI_API_KEY = "SUA_CHAVE_OPENAI_AQUI"

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OPENAI_API_KEY != "SUA_CHAVE_OPENAI_AQUI" else None

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
    st.caption("Seu Copiloto AI para Criar Jogos (Powered by OpenAI)")
    
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

# --- SUGGESTION CARDS ---
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

if st.session_state.prompt_sugerido:
    user_prompt = st.session_state.prompt_sugerido
    st.session_state.prompt_sugerido = None
else:
    user_prompt = prompt_input

if user_prompt:
    if not client:
        st.error("⚠️ Insira sua API Key da OpenAI nos Secrets do Streamlit!")
    elif not st.session_state.plano_vip and st.session_state.usos_hoje >= LIMITE_GRATUITO:
        st.error("❌ Você usou seus 3 créditos grátis de hoje! Faça upgrade para o **Plano PRO** na barra lateral.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Prepara a chamada para a OpenAI
        messages_for_api = [
            {
                "role": "system",
                "content": f"Você é o CoreAI, um Programador Senior e Game Designer especialista. Engine foco: {engine_foco}. Nível de código: {nivel_codigo}."
            }
        ]
        
        for msg in st.session_state.messages[-6:]:
            messages_for_api.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("⚡ Programando e gerando solução..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_for_api
                    )
                    
                    resposta_texto = response.choices[0].message.content
                    st.markdown(resposta_texto)
                    
                    st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                    
                    if not st.session_state.plano_vip:
                        st.session_state.usos_hoje += 1

                except Exception as e:
                    st.error(f"Erro na API da OpenAI: {e}")
