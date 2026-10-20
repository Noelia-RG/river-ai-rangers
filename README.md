# 🌊 River AI Rangers

An open-source AI assistant for secondary school students investigating real river water quality data. Built with Anthropic Claude and Streamlit.

**Live app:** [river-ai-rangers.streamlit.app](https://river-ai-rangers.streamlit.app)  
**Landing page:** [noelia-rg.github.io/river-ai-rangers](https://noelia-rg.github.io/river-ai-rangers/)

---

## What it does

Students load a citizen science CSV (Thames21 / Lea Guardians datasets are preloaded, or upload your own), then ask an AI assistant questions about the water quality readings in plain English. The app:

- Aggregates large datasets per site and season so Claude can compare all monitoring sites fairly
- Displays bar charts comparing key indicators (pH, phosphates, ammonia, etc.) across sites
- Shows healthy reference ranges with citations to UK Environment Agency / Water Framework Directive standards
- Guards API costs with a per-session question limit (30 questions) and optional class access code

---

## Files in this repository

| File | Description |
|---|---|
| `app.py` | Main Streamlit application |
| `index.html` | Landing page (served by GitHub Pages) |
| `requirements.txt` | Python dependencies for Streamlit Cloud |
| `ching-river-lesson-data.csv` | Thames21 Ching river 3-site lesson dataset |
| `lea-guardians-readings.csv` | Lea Guardians full monitoring dataset |
| `sample-readings.csv` | Fictional demonstration dataset |
| `tests/test_app.py` | Unit tests for core helper functions |
| `.github/workflows/test.yml` | GitHub Actions CI (runs tests on every push) |

---

## Deployment

### Streamlit Community Cloud (recommended)

1. Fork this repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app pointing to your fork and `app.py`.
3. In **App settings → Secrets**, add:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
ACCESS_CODE = "rangers2024"   # optional — remove this line to disable the access gate
```

The app redeploys automatically on every push to `main`.

> **Note:** Streamlit Community Cloud apps sleep after ~7 days of no visits. The first visit after sleeping takes about 30 seconds to wake up — this is normal.

### Setting a monthly spend limit

To protect against unexpected costs, set a monthly spend limit in the [Anthropic console](https://console.anthropic.com/settings/billing) under **Billing → Usage limits**.

---

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your API key to `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## Running tests

```bash
pip install pandas pytest
pytest tests/ -v
```

Tests cover: label sanitisation, season column detection, CSV aggregation logic, and column selection.

---

## Known limitations

- **No seasonal analysis on datasets without a `season` column.** If your CSV has date columns but no `season` column, the seasonal prompt card is hidden and Claude cannot compare seasons. Add a `season` column to your CSV to unlock this.
- **Large datasets are aggregated.** For datasets with more than 100 rows, Claude works from per-site (and per-season) averages with min/max ranges — not the raw readings. This is necessary because Claude's context window is limited.
- **pH averaging is approximate.** pH is a logarithmic scale. The app flags this in the sidebar and instructs Claude to caveat pH averages, but students should understand that a mean pH is not the same as a stable pH.
- **Free-text student questions go to Anthropic's API.** See the privacy section below.
- **App sleeps after 7 days of inactivity** on the free Streamlit Community Cloud plan. The first visit after sleeping takes ~30 seconds to wake up.
- **Preloaded datasets are fetched from GitHub** on first load. If GitHub is unavailable, the datasets won't load. Results are cached for 1 hour per session.

---

## Data & privacy

- **Student questions** typed in the chat are sent to Anthropic's API to generate AI responses. Students should not enter personal information in the chat.
- **River data** (the CSV readings) is included in each API request as context for the AI.
- Anthropic's privacy policy: [anthropic.com/privacy](https://www.anthropic.com/privacy)
- **Data Protection:** Schools using this tool should consider their obligations under UK GDPR and the Data Protection Act 2018. As student inputs are processed by a third-party AI provider (Anthropic), schools may wish to record this in their Data Protection Impact Assessment (DPIA) or equivalent record of processing activities. We recommend informing students not to enter personal data in the chat interface.
- The preloaded datasets contain volunteer-collected, publicly available citizen science data. No personal data about students is stored by this application.

---

## Curriculum links

- **KS3/KS4 Biology:** ecosystems, biodiversity, human impact on the environment
- **KS3/KS4 Chemistry:** chemical indicators, concentration, pH
- **KS3/KS4 Geography:** rivers, land use, water cycle
- **Cross-curricular:** data literacy, scientific enquiry, citizenship

---

## Contributing

Pull requests welcome. Please open an issue first if you're planning a significant change.

This project is open source. Data kindly provided by [Thames21](https://www.thames21.org.uk/) and Lea Guardians.
