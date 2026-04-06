import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="River AI Rangers",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f0f8f5; }

    /* Header */
    .river-header {
        background: linear-gradient(135deg, #0F6E56, #1D9E75);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .river-header h1 { font-size: 2.4rem; margin: 0; }
    .river-header p  { font-size: 1.1rem; margin: 0.5rem 0 0; opacity: 0.9; }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid #e0f0ea;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-label { font-size: 0.8rem; color: #666; margin-bottom: 4px; }
    .metric-value { font-size: 1.8rem; font-weight: bold; }
    .metric-status { font-size: 0.75rem; margin-top: 4px; }
    .good  { color: #0F6E56; }
    .warn  { color: #BA7517; }
    .bad   { color: #A32D2D; }

    /* Chat bubbles */
    .bubble-user {
        background: #0F6E56;
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0 0.5rem 3rem;
        font-size: 0.95rem;
    }
    .bubble-ai {
        background: white;
        color: #1a1a1a;
        padding: 0.8rem 1.2rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem 3rem 0.5rem 0;
        font-size: 0.95rem;
        border: 1px solid #d0e8df;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .bubble-label {
        font-size: 0.75rem;
        color: #888;
        margin-bottom: 2px;
    }

    /* Prompt chips */
    .stButton > button {
        background: white;
        border: 1.5px solid #1D9E75;
        color: #0F6E56;
        border-radius: 20px;
        font-size: 0.85rem;
        padding: 0.3rem 0.9rem;
        transition: all 0.15s;
    }
    .stButton > button:hover {
        background: #0F6E56;
        color: white;
    }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Helper: status colour ─────────────────────────────────────────────────────
def ph_status(v):
    if 6.5 <= v <= 8.5: return "good", "✅ Healthy"
    if 6.0 <= v < 6.5 or 8.5 < v <= 9.0: return "warn", "⚠️ Borderline"
    return "bad", "❌ Concern"

def nitrate_status(v):
    if v < 5:  return "good", "✅ Good"
    if v < 10: return "warn", "⚠️ Moderate"
    return "bad", "❌ High"

def phosphate_status(v):
    if v < 0.1:  return "good", "✅ Good"
    if v < 0.3:  return "warn", "⚠️ Elevated"
    return "bad", "❌ High"

# ── Helper: ask Ollama ────────────────────────────────────────────────────────
def ask_ollama(prompt, model="mistral"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        return response.json().get("response", "Sorry, I could not generate a response.")
    except requests.exceptions.ConnectionError:
        return (
            "🔌 I can't connect to Ollama right now. "
            "Please make sure Ollama is running (`ollama serve`) "
            "and that you have pulled a model (`ollama pull mistral`)."
        )
    except Exception as e:
        return f"Something went wrong: {e}"

# ── Build AI prompt ───────────────────────────────────────────────────────────
def build_prompt(question, site_data):
    readings = "\n".join([
        f"- Site {row['site_name']}: pH {row['pH']}, "
        f"Nitrates {row['nitrates_mg_per_L']} mg/L, "
        f"Phosphates {row['phosphates_mg_per_L']} mg/L"
        for _, row in site_data.iterrows()
    ])
    return f"""You are a friendly river science assistant helping primary school children 
(aged 7-11) learn about river health. Always explain things in simple, 
encouraging language a 9-year-old would understand. Use short sentences.
Mention real animals like fish, mayflies, and kingfishers where relevant.

Current river data:
{readings}

Child's question: {question}

Please give a helpful, age-appropriate answer in 3-5 sentences. 
End with one encouraging sentence about what children can do to help."""

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"site_name": "Upstream woodland",   "pH": 7.2, "nitrates_mg_per_L": 2.1,  "phosphates_mg_per_L": 0.04},
        {"site_name": "Town edge bridge",    "pH": 6.8, "nitrates_mg_per_L": 18.7, "phosphates_mg_per_L": 0.41},
        {"site_name": "Farm outflow",        "pH": 6.5, "nitrates_mg_per_L": 24.3, "phosphates_mg_per_L": 0.68},
    ])

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌊 River AI Rangers")
    st.markdown("---")

    st.markdown("**📊 Load your own data**")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    if uploaded:
        try:
            st.session_state.data = pd.read_csv(uploaded)
            st.success("Data loaded!")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    st.markdown("---")
    st.markdown("**🤖 AI Model**")
    model_choice = st.selectbox(
        "Ollama model",
        ["mistral", "llama3", "phi3", "gemma"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**ℹ️ About**")
    st.markdown(
        "River AI Rangers is a free, open-source toolkit "
        "for primary school teachers. The AI runs entirely "
        "on your device — no data leaves the school.\n\n"
        "[📖 View on GitHub](https://github.com/Noelia-RG/river-ai-rangers)"
    )

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="river-header">
    <h1>🌊 River AI Rangers</h1>
    <p>Ask questions about your river data and discover what it means for wildlife</p>
</div>
""", unsafe_allow_html=True)

# ── DATA DASHBOARD ────────────────────────────────────────────────────────────
st.markdown("### 📊 Today's river readings")

df = st.session_state.data
cols = st.columns(len(df))

for i, (_, row in df.iterrows()):
    with cols[i]:
        ph_cls, ph_lbl   = ph_status(row["pH"])
        no3_cls, no3_lbl = nitrate_status(row["nitrates_mg_per_L"])
        po4_cls, po4_lbl = phosphate_status(row["phosphates_mg_per_L"])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📍 {row['site_name']}</div>
            <div style="margin: 8px 0; border-top: 1px solid #eee; padding-top: 8px;">
                <div class="metric-label">pH</div>
                <div class="metric-value {ph_cls}">{row['pH']}</div>
                <div class="metric-status {ph_cls}">{ph_lbl}</div>
            </div>
            <div style="margin: 8px 0; border-top: 1px solid #eee; padding-top: 8px;">
                <div class="metric-label">Nitrates (mg/L)</div>
                <div class="metric-value {no3_cls}">{row['nitrates_mg_per_L']}</div>
                <div class="metric-status {no3_cls}">{no3_lbl}</div>
            </div>
            <div style="margin: 8px 0; border-top: 1px solid #eee; padding-top: 8px;">
                <div class="metric-label">Phosphates (mg/L)</div>
                <div class="metric-value {po4_cls}">{row['phosphates_mg_per_L']}</div>
                <div class="metric-status {po4_cls}">{po4_lbl}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── CHAT INTERFACE ────────────────────────────────────────────────────────────
st.markdown("### 💬 Ask the River Ranger AI")

# Render existing messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="bubble-label" style="text-align:right">You</div>
        <div class="bubble-user">{msg['content']}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bubble-label">🌊 River Ranger AI</div>
        <div class="bubble-ai">{msg['content']}</div>
        """, unsafe_allow_html=True)

# Suggested prompts
st.markdown("**💡 Try asking:**")
prompt_cols = st.columns(3)
suggestions = [
    "What does the pH at Site C mean for fish?",
    "Why are nitrates so high downstream?",
    "Which site is healthiest and why?",
    "What animals would struggle in Site C?",
    "What can we do to help our river?",
    "Is the water safe for swimming?",
]
for i, suggestion in enumerate(suggestions):
    with prompt_cols[i % 3]:
        if st.button(suggestion, key=f"sug_{i}"):
            with st.spinner("🌊 Thinking..."):
                answer = ask_ollama(
                    build_prompt(suggestion, df),
                    model=model_choice
                )
            st.session_state.messages.append({"role": "user",      "content": suggestion})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

# Free-text input
st.markdown("<br>", unsafe_allow_html=True)
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Your question",
            placeholder="Type your question about the river...",
            label_visibility="collapsed"
        )
    with col2:
        submitted = st.form_submit_button("Ask 🌊", use_container_width=True)

    if submitted and user_input.strip():
        with st.spinner("🌊 Thinking..."):
            answer = ask_ollama(
                build_prompt(user_input, df),
                model=model_choice
            )
        st.session_state.messages.append({"role": "user",      "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

# Clear chat
if st.session_state.messages:
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.rerun()
