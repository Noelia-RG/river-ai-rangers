# ============================================================
# RIVER AI RANGERS — AI Assistant (Cloud Version)
# ============================================================
# Runs on Streamlit Community Cloud.
# AI powered by Anthropic Claude (claude-haiku-4-5-20251001).
# River data loaded from CSV uploaded by the river group.
#
# Deploy: push to GitHub → connect to share.streamlit.io
# Add secret: ANTHROPIC_API_KEY in Streamlit Cloud app settings
# ============================================================

import streamlit as st
import requests
import json
import pandas as pd
import io

# ============================================================
# CONFIGURATION
# ============================================================

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"  # fast and cheap for classroom use
                                      # upgrade to "claude-sonnet-4-6" for richer answers

st.set_page_config(
    page_title="River AI Rangers",
    page_icon="🌊",
    layout="wide",
)

# ============================================================
# ANTHROPIC API KEY
# ============================================================
# On Streamlit Cloud: add ANTHROPIC_API_KEY in App Settings → Secrets
# Locally: create .streamlit/secrets.toml with ANTHROPIC_API_KEY = "your-key"

def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None

# ============================================================
# SYSTEM PROMPT
# ============================================================
# Rebuilt on every message so river readings are always current.

def build_system_prompt(river_name, ph, nitrates, phosphates, extra_columns=None):
    extra = ""
    if extra_columns:
        extra = "\nADDITIONAL READINGS FROM THE RIVER GROUP:\n"
        for col, val in extra_columns.items():
            extra += f"- {col}: {val}\n"

    return f"""You are a river science assistant for the River AI Rangers project.
You are helping secondary school students aged 11 to 16 investigate the health of their local river.

TODAY'S RIVER READINGS for {river_name}:
- pH: {ph}
- Nitrates: {nitrates} mg/L
- Phosphates: {phosphates} mg/L{extra}

YOUR ROLE:
- Explain what these numbers mean for river life in clear, precise language
- Help students understand where pollution comes from and what they can do about it
- Encourage students to question your answers and think for themselves
- Always connect your answer back to the real river readings above

YOUR RULES:
- Use language appropriate for secondary school students — clear and precise, not over-simplified
- Never invent data or pretend to know things you don't know
- If you are unsure, say so and suggest the student consults a real river scientist
- Keep answers to 3–5 sentences. Students can ask follow-up questions.
- Remind students you are a tool to help them think, not an expert who is always right

HEALTHY RANGES:
- pH: 6.5 to 8.5 is healthy
- Nitrates: below 10 mg/L is healthy
- Phosphates: below 0.1 mg/L is healthy

Remember: the student is the scientist. You are the tool."""


# ============================================================
# CLAUDE API CALL
# ============================================================

def ask_claude(system_prompt, messages, api_key):
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL,
        "system": system_prompt,
        "messages": messages,
        "stream": True,
        "max_tokens": 400,
        "temperature": 0.5,
    }
    return requests.post(CLAUDE_API_URL, headers=headers, json=payload, stream=True, timeout=30)


# ============================================================
# CSV LOADER
# ============================================================

def load_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        return df, None
    except Exception as e:
        return None, str(e)

def get_latest_readings(df):
    date_cols = [c for c in df.columns if "date" in c]
    if date_cols:
        df = df.sort_values(date_cols[0], ascending=False)
    latest = df.iloc[0].to_dict()
    return latest

def extract_reading(row, *possible_names):
    for name in possible_names:
        for col in row:
            if name in col.lower():
                try:
                    return float(row[col])
                except (ValueError, TypeError):
                    pass
    return None


# ============================================================
# SIDEBAR — river data + CSV upload
# ============================================================

with st.sidebar:
    st.image("https://em-content.zobj.net/source/twitter/376/water-wave_1f30a.png", width=60)
    st.title("River AI Rangers")
    st.caption("Powered by Anthropic Claude · Open-source · Free to use")
    st.divider()

    st.subheader("📂 Upload River Data")
    st.caption("Upload a CSV from your river group. Needs columns for pH, nitrates, phosphates.")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    extra_columns = {}

    if uploaded_file:
        df, err = load_csv(uploaded_file)
        if err:
            st.error(f"Could not read CSV: {err}")
            df = None
        else:
            st.success(f"✅ Loaded {len(df)} readings")
            st.caption(f"Columns found: {', '.join(df.columns)}")

            latest = get_latest_readings(df)

            csv_ph         = extract_reading(latest, "ph")
            csv_nitrates   = extract_reading(latest, "nitrate")
            csv_phosphates = extract_reading(latest, "phosphate")

            standard_keys = {"ph", "nitrate", "phosphate", "date", "site", "river", "location"}
            for col, val in latest.items():
                if not any(k in col for k in standard_keys):
                    extra_columns[col] = val

            st.caption("Using most recent entry from CSV.")
    else:
        csv_ph = csv_nitrates = csv_phosphates = None

    st.divider()

    st.subheader("📊 River Readings")
    st.caption("Pre-filled from CSV if uploaded. Edit to override.")

    river_name  = st.text_input("River name", value="Our Local River")
    ph          = st.number_input("pH", 0.0, 14.0,
                                  value=float(csv_ph) if csv_ph else 7.2, step=0.1,
                                  help="Healthy: 6.5 – 8.5")
    nitrates    = st.number_input("Nitrates (mg/L)", 0.0, 100.0,
                                  value=float(csv_nitrates) if csv_nitrates else 5.0, step=0.5,
                                  help="Healthy: below 10 mg/L")
    phosphates  = st.number_input("Phosphates (mg/L)", 0.0, 10.0,
                                  value=float(csv_phosphates) if csv_phosphates else 0.08, step=0.01,
                                  help="Healthy: below 0.1 mg/L")

    st.divider()
    st.subheader("🩺 Health Check")
    st.write(f"pH {ph}: {'✅ Healthy' if 6.5 <= ph <= 8.5 else '⚠️ Outside range'}")
    st.write(f"Nitrates {nitrates} mg/L: {'✅ Healthy' if nitrates < 10 else '⚠️ Outside range'}")
    st.write(f"Phosphates {phosphates} mg/L: {'✅ Healthy' if phosphates < 0.1 else '⚠️ Outside range'}")

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("☁️ AI runs via Anthropic Claude. River readings stay in your browser session.")


# ============================================================
# MAIN AREA — prompt cards + chat
# ============================================================

st.title("🌊 River AI Rangers")
st.markdown(
    f"**River:** {river_name} &nbsp;|&nbsp; "
    f"pH: `{ph}` &nbsp;|&nbsp; "
    f"Nitrates: `{nitrates} mg/L` &nbsp;|&nbsp; "
    f"Phosphates: `{phosphates} mg/L`"
)
st.divider()

st.subheader("💬 Ask a question")
st.caption("Click a card to get started, or type your own question below.")

col1, col2, col3, col4, col5 = st.columns(5)

if "prefill" not in st.session_state:
    st.session_state.prefill = ""

with col1:
    st.markdown("**🔵 The numbers**")
    if st.button(f"Is pH {ph} healthy?", use_container_width=True):
        st.session_state.prefill = f"Our river has a pH of {ph}. Is that healthy for the fish and invertebrates living there? Please explain clearly."
    if st.button(f"Nitrates at {nitrates} mg/L?", use_container_width=True):
        st.session_state.prefill = f"Our river's nitrate level is {nitrates} mg/L. What does that mean for the river? Is it safe?"
    if st.button(f"Phosphates at {phosphates}?", use_container_width=True):
        st.session_state.prefill = f"Our river has {phosphates} mg/L of phosphates. What causes phosphates to get into rivers, and is our level worrying?"

with col2:
    st.markdown("**🟢 Wildlife**")
    if st.button("What lives in our river?", use_container_width=True):
        st.session_state.prefill = f"If a river has pH {ph}, nitrates {nitrates} mg/L, and phosphates {phosphates} mg/L, what animals and plants might live in it?"
    if st.button("Most sensitive animals?", use_container_width=True):
        st.session_state.prefill = "Which animals are most sensitive to pollution in rivers? Would they survive in our river?"
    if st.button("What is an algae bloom?", use_container_width=True):
        st.session_state.prefill = "What is an algae bloom and why is it bad for rivers? Could it happen in our river?"

with col3:
    st.markdown("**🟡 Pollution**")
    if st.button("Where does pollution come from?", use_container_width=True):
        st.session_state.prefill = "Where do nitrates and phosphates in rivers usually come from? Can you give me some examples?"
    if st.button("How do farms affect rivers?", use_container_width=True):
        st.session_state.prefill = "How do farms affect river water quality? What is fertiliser run-off?"
    if st.button("What is sewage overflow?", use_container_width=True):
        st.session_state.prefill = "What is sewage overflow and how does it affect rivers?"

with col4:
    st.markdown("**🔴 Take action**")
    if st.button("Who is responsible?", use_container_width=True):
        st.session_state.prefill = "Who is responsible for keeping rivers clean? What can ordinary people do?"
    if st.button("Help me write a letter", use_container_width=True):
        st.session_state.prefill = "I want to write a letter to my local council about our river's water quality. What should I include?"
    if st.button("What is citizen science?", use_container_width=True):
        st.session_state.prefill = "What is citizen science? How do ordinary people help monitor rivers?"

with col5:
    st.markdown("**🟣 Question the AI**")
    if st.button("How sure are you?", use_container_width=True):
        st.session_state.prefill = "How confident are you about what you just told me? Could any of it be wrong?"
    if st.button("How could I check?", use_container_width=True):
        st.session_state.prefill = "Where does this information come from? How could I check if it's true?"
    if st.button("What don't you know?", use_container_width=True):
        st.session_state.prefill = "Is there anything you don't know about this topic that I should find out from a real scientist?"

st.divider()


# ============================================================
# CHAT LOOP
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question about our river...")

if st.session_state.prefill and not user_input:
    user_input = st.session_state.prefill
    st.session_state.prefill = ""

if user_input:
    api_key = get_api_key()

    if not api_key:
        st.error(
            "⚠️ No API key found. "
            "Add ANTHROPIC_API_KEY to your Streamlit Cloud app secrets, "
            "or create .streamlit/secrets.toml locally with: ANTHROPIC_API_KEY = 'your-key'"
        )
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system_prompt = build_system_prompt(river_name, ph, nitrates, phosphates, extra_columns)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = ask_claude(system_prompt, st.session_state.messages, api_key)

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        try:
                            chunk = json.loads(data)
                            if chunk.get("type") == "content_block_delta":
                                text = chunk.get("delta", {}).get("text", "")
                                full_response += text
                                placeholder.markdown(full_response + "▌")
                        except json.JSONDecodeError:
                            pass

            placeholder.markdown(full_response)

        except requests.exceptions.Timeout:
            full_response = "⚠️ The request timed out. Please try again."
            placeholder.warning(full_response)
        except Exception as e:
            full_response = f"⚠️ Something went wrong: {str(e)}"
            placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
