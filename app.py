import streamlit as st
import json
import asyncio
from insurance_agent.agent import root_agent # Langsung import agent utama
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
import os
from dotenv import load_dotenv

load_dotenv()

# --- Konfigurasi Lingkungan ---
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT", "eikon-dev-ai-team")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")

# --- Konfigurasi Halaman ---   #
st.set_page_config(
    page_title="Aether Insurance Virtual Agent",
    page_icon="🛡️",
    layout="centered"
)

# --- CSS Kustom untuk Tampilan Chat dengan Light/Dark Mode ---
st.markdown("""
<style>
    /* --- Light Mode (Default) --- */
    :root {
        --bg-color: #f0f2f6;
        --text-color: #212529;
        --title-color: #003366;
        --caption-color: #555555;
        --chat-bg: #ffffff;
        --chat-border: #e6e6e6;
        --card-bg: #ffffff;
        --card-border: #005a9e;
        --card-text: #333333;
        --button-bg: #ffffff;
        --button-text: #003366;
        --button-border: #003366;
        --button-hover-bg: #1c83e1; /* Warna biru untuk hover */
        --button-hover-text: #ffffff;
    }
    
    .stApp { background-color: var(--bg-color); }
    h1 { color: var(--title-color); }
    .stMarkdown, div[data-testid="stMarkdownContainer"] p { color: var(--text-color); }
    [data-testid="stCaption"] { color: var(--caption-color); }
    
    .st-emotion-cache-1c7y2kd {
        background-color: var(--chat-bg);
        border: 1px solid var(--chat-border);
    }
    .st-emotion-cache-1c7y2kd .stMarkdown { color: var(--text-color); }

    .recommendation-card {
        background-color: var(--card-bg);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        transition: 0.3s;
        border-left: 5px solid var(--card-border);
    }
    .recommendation-card:hover { box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2); }
    .recommendation-card h3 {
        margin-top: 0;
        color: var(--title-color);
        border-bottom: 2px solid var(--bg-color);
        padding-bottom: 10px;
    }
    .recommendation-card p { color: var(--card-text); }
    
    .stButton>button {
        font-size: 0.9rem;
        background-color: var(--button-bg);
        color: var(--button-text);
        border: 1px solid var(--button-border);
        border-radius: 5px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: var(--button-hover-bg);
        color: var(--button-hover-text);
        border: 1px solid var(--button-hover-bg);
    }

    /* --- Dark Mode --- */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #0e1117;
            --text-color: #fafafa;
            --title-color: #fafafa;
            --caption-color: #a0a0a0;
            --chat-bg: #262730;
            --chat-border: #31333F;
            --card-bg: #262730;
            --card-border: #1c83e1;
            --card-text: #d1d1d1;
            --button-bg: #262730;
            --button-text: #fafafa;
            --button-border: #fafafa;
            --button-hover-bg: #1c83e1; /* Warna biru untuk hover */
            --button-hover-text: #ffffff; /* Teks putih saat hover */
        }
        
        .recommendation-card {
            border-top: 1px solid #31333F;
            border-right: 1px solid #31333F;
            border-bottom: 1px solid #31333F;
        }
        .recommendation-card h3 {
            border-bottom: 2px solid #31333F;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Setup Runner dan Session Service (di-cache agar tidak dibuat ulang) ---
@st.cache_resource
def setup_adk_runner():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="aether_insurance_app",
        session_service=session_service
    )
    return runner, session_service

runner, session_service = setup_adk_runner()
USER_ID = "streamlit_user"
SESSION_ID = "default_session"

# --- Inisialisasi Sesi ADK (hanya sekali saat aplikasi dimulai) ---
if "session_initialized" not in st.session_state:
    try:
        asyncio.run(session_service.create_session(
            app_name=runner.app_name,
            user_id=USER_ID,
            session_id=SESSION_ID
        ))
        st.session_state.session_initialized = True
    except Exception as e:
        st.error(f"Gagal menginisialisasi sesi percakapan: {e}")
        st.stop()

# --- Fungsi Asinkron untuk Menjalankan Agen ---
async def get_agent_response_async(prompt, runner, user_id, session_id):
    """Menjalankan agen ADK secara asinkron dan mengembalikan respons akhir."""
    content = genai_types.Content(role='user', parts=[genai_types.Part(text=prompt)])
    final_response_text = "Maaf, terjadi kesalahan saat memproses permintaan Anda."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break
    return final_response_text

# --- Judul Utama ---
st.title("🛡️ Aether Insurance Virtual Agent")
st.markdown("Ajukan pertanyaan apa pun tentang kebutuhan asuransi Anda, dan saya akan membantu menemukan produk yang tepat.")

# --- Inisialisasi Riwayat Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa saya bantu untuk merencanakan masa depan Anda?"}]

# --- Fungsi untuk mem-parse dan menampilkan rekomendasi ---
def tampilkan_rekomendasi_dari_teks(teks_respons):
    try:
        json_str_match = teks_respons[teks_respons.find("[") : teks_respons.rfind("]") + 1]
        if not json_str_match:
             json_str_match = teks_respons[teks_respons.find("{") : teks_respons.rfind("}") + 1]

        data_list = json.loads(json_str_match.replace("'", "\""))
        
        if not isinstance(data_list, list):
            data_list = [data_list]

        intro_text = teks_respons.split(json_str_match)[0].strip()
        if intro_text:
            st.markdown(intro_text)

        for produk in data_list:
            nama = produk.get("nama_produk", "Produk Tidak Ditemukan")
            deskripsi = produk.get("deskripsi", "-")
            st.markdown(f"""
            <div class="recommendation-card">
                <h3>{nama}</h3>
                <p>{deskripsi}</p>
            </div>
            """, unsafe_allow_html=True)
    except (json.JSONDecodeError, IndexError, ValueError):
        st.markdown(teks_respons)

# --- Tampilkan Riwayat Chat yang Ada ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        tampilkan_rekomendasi_dari_teks(message["content"])

# --- Logika untuk memproses input baru ---
prompt_to_process = None

if len(st.session_state.messages) == 1:
    st.markdown("---")
    st.caption("Atau, mulai dengan salah satu pertanyaan ini:")
    col1, col2 = st.columns(2)
    placeholders = [
        "Saya butuh asuransi kesehatan untuk keluarga.",
        "Rencanakan dana pendidikan untuk anak 5 tahun.",
        "Bagaimana menyiapkan dana pensiun?",
        "Produk investasi yang cocok untuk saya?"
    ]
    if col1.button(placeholders[0], use_container_width=True):
        prompt_to_process = placeholders[0]
    if col2.button(placeholders[1], use_container_width=True):
        prompt_to_process = placeholders[1]
    if col1.button(placeholders[2], use_container_width=True):
        prompt_to_process = placeholders[2]
    if col2.button(placeholders[3], use_container_width=True):
        prompt_to_process = placeholders[3]

if chat_input_prompt := st.chat_input("Tanyakan tentang asuransi..."):
    prompt_to_process = chat_input_prompt

if prompt_to_process:
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    
    with st.spinner("Aether sedang berpikir..."):
        respons_agen = asyncio.run(get_agent_response_async(
            prompt=prompt_to_process,
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID
        ))
    
    st.session_state.messages.append({"role": "assistant", "content": respons_agen})
    st.rerun()


