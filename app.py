import streamlit as st
from google import genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="GameDevGPT - Seu Copiloto de Jogos",
    page_icon="🤖",
    layout="wide"
)

# --- CHAVE DA API ---
API_KEY = "SUA_CHAVE_AQUI"  # Substitua pela sua API Key do Google AI Studio

# Inicializa o cliente se houver chave cadastrada
client = genai.Client(api_key=API_KEY) if API_KEY and API_KEY != "SUA_CHAVE_AQUI" else None

# --- CONFIGURAÇÃO DA SESSÃO / ESTADO ---
LIMITE_GRATUITO = 3

if "messages" not in st.session_state:
    st.session_state.messages = []

if "usos_hoje" not in st.session_state:
    st.session_state.usos_hoje = 0

if "plano_vip" not in st.session_state:
    st.session_state.plano_vip = False

# --- BARRA LATERAL (CONFIGURAÇÕES E PLANO) ---
with st.sidebar:
    st.title("🤖 GameDevGPT")
    st.caption("O ChatGPT especializado em Game Dev & Narrative Design")
    
    st.markdown("---")
    st.subheader("⚙️ Configurações do Projeto")
    
    engine_foco = st.selectbox(
        "Sua Engine / Foco principal:",
        ["Unity (C#)", "Godot (GDScript)", "Roblox (Lua)", "Unreal (C++)", "Roteiro / Lore / Diálogos"]
    )
    
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # Status do Plano / Créditos
    if st.session_state.plano_vip:
        st.success("🌟 **Plano PRO Ativo** (Acesso Ilimitado)")
    else:
        usos_restantes = LIMITE_GRATUITO - st.session_state.usos_hoje
        st.metric(label="Créditos Diários Grátis", value=f"{usos_restantes}/{LIMITE_GRATUITO}")
        
        st.markdown("### 🚀 Assine o Plano PRO")
        st.write("• Mensagens Ilimitadas")
        st.write("• Respostas Otimizadas e Mais Rápidas")
        st.write("• Suporte Direto")
        
        if st.button("💳 Testar Plano PRO (Simular)", use_container_width=True):
            st.session_state.plano_vip = True
            st.success("Plano PRO ativado!")
            st.rerun()

# --- TÍTULO PRINCIPAL ---
st.title("💬 GameDevGPT")
st.caption(f"Foco atual: **{engine_foco}**. Peça scripts, sistemas ou histórias!")

# --- EXIBIÇÃO DO HISTÓRICO DE MENSAGENS (ESTILO CHATGPT) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CAMPO DE ENTRADA DA MENSAGEM (CHAT INPUT) ---
if prompt := st.chat_input("Digite o script ou dúvida que precisa para o seu jogo..."):
    
    # Validações antes de enviar
    if not client:
        st.error("⚠️ Insira sua API Key do Google AI Studio no arquivo `app.py` para conversar com a IA!")
    elif not st.session_state.plano_vip and st.session_state.usos_hoje >= LIMITE_GRATUITO:
        st.error("❌ Você usou seus 3 créditos grátis de hoje! Assine o Plano PRO na barra lateral para continuar.")
    else:
        # 1. Mostra a mensagem do usuário no chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Gera a resposta da IA
        with st.chat_message("assistant"):
            with st.spinner("Pensando e codificando..."):
                
                system_prompt = f"""
                Você é o GameDevGPT, um especialista em desenvolvimento de jogos e narrativa.
                Foco atual selecionado pelo usuário: {engine_foco}.
                
                Diretrizes de resposta:
                1. Se o usuário pedir código, entregue código bem estruturado, limpo e comentado em português.
                2. Se for narrativa/diálogo, estruture com formatação clara para roteiro de jogo.
                3. Responda de forma direta, amigável e profissional.
                
                Pedido do usuário: {prompt}
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=system_prompt,
                    )
                    
                    resposta_texto = response.text
                    st.markdown(resposta_texto)
                    
                    # Salva no histórico do chat
                    st.session_state.messages.append({"role": "assistant", "content": resposta_texto})
                    
                    # Desconta crédito se não for VIP
                    if not st.session_state.plano_vip:
                        st.session_state.usos_hoje += 1

                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {e}")