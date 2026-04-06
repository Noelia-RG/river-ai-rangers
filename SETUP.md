# 🌊 River AI Rangers — App Setup

## What you need

- Python 3.10 or above
- [Ollama](https://ollama.com/download) installed and running

---

## Step 1 — Install Ollama and pull a model

Download Ollama from https://ollama.com/download then run:

```bash
ollama pull mistral
```

---

## Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Step 3 — Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at http://localhost:8501

---

## Using your own river data

Upload a CSV file with these columns:

| Column | Example |
|---|---|
| site_name | Upstream woodland |
| pH | 7.2 |
| nitrates_mg_per_L | 2.1 |
| phosphates_mg_per_L | 0.04 |

A sample file is available in `../data/sample-readings.csv`

---

## Troubleshooting

**"Can't connect to Ollama"** — Make sure Ollama is running:
```bash
ollama serve
```

**Slow responses** — Mistral works well on most laptops. 
If it's too slow, try `phi3` which is lighter:
```bash
ollama pull phi3
```
Then select phi3 in the app sidebar.
