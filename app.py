# ============================================================
# RIVER AI RANGERS — AI Assistant (Cloud Version)
# ============================================================
# Runs on Streamlit Community Cloud.
# AI powered by Anthropic Claude (claude-haiku-4-5-20251001).
# River data: preloaded Thames21 datasets or uploaded CSV.
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

GITHUB_RAW = "https://raw.githubusercontent.com/Noelia-RG/river-ai-rangers/main/"

PRELOADED_DATASETS = {
    "The Ching — 3-site lesson data (Thames21)": "ching-river-lesson-data.csv",
    "Lea Guardians — full dataset (Thames21)": "lea-guardians-readings.csv",
    "Sample data — fictional river (demonstration)": "sample-readings.csv",
}

st.set_page_config(
    page_title="River AI Rangers",
    page_icon="🌊",
    layout="wide",
)

# ============================================================
# ANTHROPIC API KEY
# ============================================================

def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None

# ============================================================
# SYSTEM PROMPT
# ============================================================

def build_system_prompt(df, river_label):
    """Build system prompt from a dataframe — handles multi-site, multi-season data."""
    cols = [c.lower() for c in df.columns]
    has_ph = any("ph" in c for c in cols)
    has_nitrates = any("nitrate" in c for c in cols)
    has_ammonia = any("ammonia" in c for c in cols)
    has_phosphates = any("phosphate" in c for c in cols)
    has_oxygen = any("oxygen" in c or "dissolved" in c for c in cols)
    display_cols = []
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in ["site", "river", "date", "season", "ph", "nitrate",
                                   "phosphate", "ammonia", "oxygen", "turbid",
                                   "temp", "colour", "clarity", "notes"]):
            display_cols.append(c)
    display_df = df[display_cols].copy() if display_cols else df.copy()
    data_summary = display_df.to_string(index=False, max_rows=50)
    ranges = []
    if has_ph:
        ranges.append("- pH: 6.5 to 8.5 is healthy")
    if has_nitrates:
        ranges.append("- Nitrates: below 10 mg/L is healthy")
    if has_ammonia:
        ranges.append("- Ammonia: below 0.5 mg/L is safe for fish; below 0.1 mg/L is ideal")
    if has_phosphates:
        ranges.append("- Phosphates: below 0.1 mg/L is healthy")
    if has_oxygen:
        ranges.append("- Dissolved Oxygen: above 8 mg/L is healthy; below 5 mg/L stresses fish; below 3 mg/L is critical")
    ranges_text = "\n".join(ranges)
    return f"""You are a river science assistant for the River AI Rangers project.
You are helping secondary school students aged 11 to 16 investigate the health of their local river.

DATASET: {river_label}

RIVER DATA:
{data_summary}

YOUR ROLE:
- Help students read, interpret and question this real water-quality data
- Explain what the numbers mean for river life in clear, precise language
- Help students understand where pollution comes from, what the patterns show, and what can be done
- Encourage students to question your answers and think for themselves
- Connect your answers directly back to the data above — refer to specific numbers and sites

YOUR RULES:
- Use language appropriate for secondary school students — clear and precise, not over-simplified
- Never invent data. If a measurement isn't in the dataset, say so
- If you are unsure, say so and suggest the student consults a real river scientist
- Keep answers to 3–5 sentences unless the student asks for more detail
- Remind students you are a tool to help them think, not an expert who is always right
- When comparing sites or seasons, cite the actual numbers

HEALTHY RANGES FOR REFERENCE:
{ranges_text}

IMPORTANT — what this dataset does and does NOT contain:
- Columns present: {', '.join(display_cols)}
- If a student asks about a measurement not in the dataset, tell them it wasn't recorded in this monitoring programme

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
        "max_tokens": 500,
        "temperature": 0.5,
    }
    return requests.post(CLAUDE_API_URL, headers=headers, json=payload, stream=True, timeout=30)

# ============================================================
# CSV LOADER
# ============================================================

def load_csv_from_url(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        return df, None
    except Exception as e:
        return None, str(e)

def load_csv_from_upload(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

def get_quick_stats(df):
    stats = {}
    cols = {c.lower(): c for c in df.columns}
    for key, variants in {
        "ph": ["ph"],
        "phosphates_mg_l": ["phosphate"],
        "ammonia_mg_l": ["ammonia"],
        "nitrates_mg_l": ["nitrate"],
        "dissolved_oxygen_mg_l": ["oxygen", "dissolved"],
    }.items():
        for col_lower, col_orig in cols.items():
            if any(v in col_lower for v in variants):
                vals = pd.to_numeric(df[col_orig], errors="coerce").dropna()
                if len(vals):
                    stats[key] = {"min": vals.min(), "max": vals.max(), "mean": vals.mean()}
                break
    return stats

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.image("https://em-content.zobj.net/source/twitter/376/water-wave_1f30a.png", width=60)
    st.title("River AI Rangers")
    st.caption("Powered by Anthropic Claude · Open-source · Free to use")
    st.divider()
    st.subheader("📂 River Dataset")
    source = st.radio("Data source", ["Load a preloaded dataset", "Upload your own CSV"], index=0)
    df = None
    river_label = "River"
    if source == "Load a preloaded dataset":
        choice = st.selectbox("Choose dataset", list(PRELOADED_DATASETS.keys()))
        filename = PRELOADED_DATASETS[choice]
        url = GITHUB_RAW + filename
        if st.button("Load dataset", use_container_width=True):
            with st.spinner("Loading..."):
                df, err = load_csv_from_url(url)
                if err:
                    st.error(f"Could not load: {err}")
                else:
                    st.session_state["df"] = df
                    st.session_state["river_label"] = choice
                    st.success(f"✅ Loaded {len(df)} rows")
        if "df" in st.session_state:
            df = st.session_state["df"]
            river_label = st.session_state.get("river_label", choice)
    else:
        uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
        if uploaded_file:
            df, err = load_csv_from_upload(uploaded_file)
            if err:
                st.error(f"Could not read CSV: {err}")
                df = None
            else:
                st.session_state["df"] = df
                st.session_state["river_label"] = uploaded_file.name.replace(".csv", "")
                st.success(f"✅ Loaded {len(df)} rows")
                st.caption(f"Columns: {', '.join(df.columns)}")
        if "df" in st.session_state:
            df = st.session_state["df"]
            river_label = st.session_state.get("river_label", "Uploaded river")
    st.divider()
    if df is not None:
        st.subheader("🩺 Dataset Summary")
        stats = get_quick_stats(df)
        if "ph" in stats:
            s = stats["ph"]
            flag = "✅" if 6.5 <= s["mean"] <= 8.5 else "⚠️"
            st.write(f"pH avg: `{s['mean']:.1f}` (range {s['min']:.1f}–{s['max']:.1f}) {flag}")
        if "phosphates_mg_l" in stats:
            s = stats["phosphates_mg_l"]
            flag = "✅" if s["mean"] < 0.1 else "🔴"
            st.write(f"Phosphates avg: `{s['mean']:.2f}` mg/L {flag}")
            st.caption("Healthy: <0.1 mg/L")
        if "ammonia_mg_l" in stats:
            s = stats["ammonia_mg_l"]
            flag = "✅" if s["mean"] < 0.5 else "⚠️"
            st.write(f"Ammonia avg: `{s['mean']:.2f}` mg/L {flag}")
            st.caption("Healthy: <0.5 mg/L for fish")
        if "nitrates_mg_l" in stats:
            s = stats["nitrates_mg_l"]
            flag = "✅" if s["mean"] < 10 else "⚠️"
            st.write(f"Nitrates avg: `{s['mean']:.1f}` mg/L {flag}")
        if "dissolved_oxygen_mg_l" in stats:
            s = stats["dissolved_oxygen_mg_l"]
            flag = "✅" if s["mean"] > 8 else "⚠️"
            st.write(f"Dissolved O₂ avg: `{s['mean']:.1f}` mg/L {flag}")
        st.caption(f"Dataset: {river_label}")
    else:
        st.info("Load or upload a river dataset to begin.")
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("☁️ AI powered by Anthropic Claude. River readings stay in your session.")

# ============================================================
# MAIN AREA
# ============================================================

st.title("🌊 River AI Rangers")
if df is not None:
    st.markdown(f"**Dataset loaded:** {river_label} &nbsp;|&nbsp; `{len(df)} readings` across `{df.shape[1]} columns`")
else:
    st.markdown("**No dataset loaded** — select a preloaded dataset or upload a CSV in the sidebar.")
st.divider()

st.subheader("💬 Ask a question")
st.caption("Click a card to get started, or type your own question below.")
col1, col2, col3, col4, col5 = st.columns(5)
if "prefill" not in st.session_state:
    st.session_state.prefill = ""
with col1:
    st.markdown("**🔵 The numbers**")
    if st.button("What do these readings mean?", use_container_width=True):
        st.session_state.prefill = "Can you explain what the readings in our dataset mean? Which indicator looks most worrying and why?"
    if st.button("Is the phosphate level dangerous?", use_container_width=True):
        st.session_state.prefill = "Looking at the phosphate readings in our dataset, are these levels dangerous for river life? What is the healthy limit?"
    if st.button("What does ammonia tell us?", use_container_width=True):
        st.session_state.prefill = "What does the ammonia level in our river tell us? Where does ammonia in rivers usually come from?"
with col2:
    st.markdown("**🟢 Compare sites**")
    if st.button("Which site is healthiest?", use_container_width=True):
        st.session_state.prefill = "Looking at all the monitoring sites in our dataset, which site has the best water quality and which has the worst? Use the actual numbers to explain."
    if st.button("What changes upstream to downstream?", use_container_width=True):
        st.session_state.prefill = "How do the water quality readings change from the upstream site to the downstream site? What might explain that pattern?"
    if st.button("Do seasons change the readings?", use_container_width=True):
        st.session_state.prefill = "Do the readings change between seasons? Why might phosphate or ammonia levels be higher in summer than winter?"
with col3:
    st.markdown("**🟡 Pollution**")
    if st.button("Where does pollution come from?", use_container_width=True):
        st.session_state.prefill = "Where do the pollutants in our dataset usually come from? What types of land use or human activity cause these readings?"
    if st.button("How do farms affect rivers?", use_container_width=True):
        st.session_state.prefill = "How do farms affect river water quality? What is fertiliser run-off and how does it cause phosphate and ammonia to rise?"
    if st.button("Algae bloom explained", use_container_width=True):
        st.session_state.prefill = "What is an algae bloom and how could it happen in our river based on these readings? What are the consequences?"
with col4:
    st.markdown("**🔴 Take action**")
    if st.button("Who is responsible?", use_container_width=True):
        st.session_state.prefill = "Who is responsible for keeping rivers clean in the UK? Which organisation would I contact about the readings in our dataset?"
    if st.button("Help me write a letter", use_container_width=True):
        st.session_state.prefill = "I want to write a letter to my local council or the Environment Agency about our river's water quality. What should I include, using our actual data?"
    if st.button("What would actually help?", use_container_width=True):
        st.session_state.prefill = "Based on what you can see in our data, what actions would most improve this river's health? Who would need to take those actions?"
with col5:
    st.markdown("**🟣 Question the AI**")
    if st.button("How confident are you?", use_container_width=True):
        st.session_state.prefill = "How confident are you about what you just told me? Could any of it be wrong? What are the limits of using AI to interpret river data?"
    if st.button("What can't you tell me?", use_container_width=True):
        st.session_state.prefill = "What questions about this river can't you answer from this data alone? What extra measurements would a real river scientist want?"
    if st.button("How could I check this?", use_container_width=True):
        st.session_state.prefill = "Where does this information come from? How could I check whether what you told me is accurate?"
st.divider()

# ============================================================
# CHAT LOOP
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
user_input = st.chat_input("Ask a question about the river data...")
if st.session_state.prefill and not user_input:
    user_input = st.session_state.prefill
    st.session_state.prefill = ""
if user_input:
    if df is None:
        st.warning("⚠️ Please load a dataset first — use the sidebar to choose a preloaded dataset or upload a CSV.")
        st.stop()
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ No API key found. Add ANTHROPIC_API_KEY to your Streamlit Cloud app secrets.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    system_prompt = build_system_prompt(df, river_label)
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
