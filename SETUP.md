# 🌊 River AI Rangers — App Setup

## No installation needed

The River AI Rangers assistant runs in any browser at:

👉 **[river-ai-rangers.streamlit.app](https://river-ai-rangers.streamlit.app)**

No Python, no Ollama, no downloads required. Open the link and start investigating.

---

## Want to run your own instance?

If you want to host your own version (for your school, trust, or river group), follow the steps below.

### What you need

- A free [GitHub](https://github.com) account
- A free [Streamlit Community Cloud](https://share.streamlit.io) account
- An [Anthropic API key](https://console.anthropic.com) (free tier available)

---

## Step 1 — Fork the repository

Go to **https://github.com/Noelia-RG/river-ai-rangers** and click **Fork** to copy it to your own GitHub account.

---

## Step 2 — Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
2. Click **Deploy an app**
3. Select your forked repository and set the main file to `app.py`
4. Click **Deploy**

---

## Step 3 — Add your API key

1. In Streamlit Cloud, open your app's **Settings → Secrets**
2. Add the following:

```toml
ANTHROPIC_API_KEY = "your-key-here"
```

3. Save — the app will restart automatically

Your API key is stored securely in Streamlit Cloud and never appears in the code or on GitHub.

---

## Using your own river data

Upload a CSV file via the sidebar. The app accepts any CSV with columns for pH, nitrates, and phosphates. Column names are flexible — the app recognises common variants automatically.

A sample file is available in the repository: `sample_river_data.csv`

| Column | Example |
|--------|---------|
| date | 2026-07-15 |
| site | Upstream bridge |
| ph | 7.4 |
| nitrates_mg_l | 4.2 |
| phosphates_mg_l | 0.06 |

Extra columns (temperature, dissolved oxygen, turbidity) are automatically passed to the AI as additional context.

---

## Cost

The app uses Anthropic Claude Haiku — approximately **£0.01 per full lesson session**. A typical school pilot costs less than £1 per term.

---

## Licence

MIT — fork, adapt, and redeploy freely. If you build something useful, share it back.

*River AI Rangers — github.com/Noelia-RG/river-ai-rangers*
