import json, os


import streamlit as st

from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

                            


with open("config.json") as f:
    config = json.load(f)

st.set_page_config(
    page_title="Fitness Consultant AI",
    page_icon="💪",
    layout="centered",
)




# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


@tool
def hitung_bmi(berat: float, tinggi: float) -> str:
    """Hitung BMI berdasarkan berat (kg) dan tinggi (cm)."""
    tinggi_m = tinggi / 100
    bmi = berat / (tinggi_m ** 2)
    if bmi < 18.5:
        kategori = "Kurus"
    elif bmi < 25:
        kategori = "Normal"
    elif bmi < 30:
        kategori = "Kelebihan berat badan"
    else:
        kategori = "Obesitas"
    return f"BMI Anda adalah {bmi:.1f} ({kategori})."

# chatbot page

st.title("💪 Fitness Consultant Chatbot")
st.caption("Halo! Saya asisten kebugaran Anda. Saya bisa bantu buatkan rencana latihan, nutrisi, atau saran kebugaran yang sesuai dengan tujuan Anda. 👇")

prompt = '''
    Kamu adalah seorang konsultan kebugaran profesional yang membantu pengguna 
    membuat rencana latihan, nutrisi, dan gaya hidup sehat. 
    Gunakan tools bila diperlukan (misalnya untuk menghitung BMI). 
    Selalu jawab dengan gaya ramah, positif, dan profesional seperti personal trainer.
'''

os.environ["GOOGLE_API_KEY"] = config["GOOGLE_API_KEY"]

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

agent = create_react_agent(
    model=model,
    tools=[hitung_bmi],
    prompt=prompt
)

# Initialize session & system prompt

# Simpan agent di session
if "agent_state" not in st.session_state:
    st.session_state.agent_state = agent

# Simpan history percakapan
if "messages" not in st.session_state:
    st.session_state.messages = [("assistant", "Halo! Saya FitBot, konsultan kebugaran virtual Anda. 💪 Apa tujuan fitness kamu hari ini?")]

# Tampilkan history chat
for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content)

# Input pengguna
user_input = st.chat_input("Tulis pertanyaan fitness Anda...")
if user_input:
    # Tambahkan pesan user ke history dan tampilkan
    st.session_state.messages.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    # Jalankan agent dengan seluruh riwayat chat
    conversation = [("system", prompt)] + st.session_state.messages
    result = st.session_state.agent_state.invoke({"messages": conversation})

    # Ambil jawaban terakhir
    assistant_message = result["messages"][-1]
    content = assistant_message.content

    # Perbaiki format output LangGraph (jika berupa list)
    if isinstance(content, list):
        text = ""
        for block in content:
            if block.get("type") == "text":
                text += block.get("text", "")
    else:
        text = str(content)

    # Tambahkan ke history dan tampilkan
    st.session_state.messages.append(("assistant", text))
    with st.chat_message("assistant"):
        st.markdown(text)