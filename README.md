# Rohan Health Copilot — Patient & Member 360

A Streamlit app powered by a Snowflake Cortex Agent that unifies structured EHR/claims data with unstructured clinical and regulatory documents.

## Features

- **Patient Dashboard** — sidebar with risk scores, claims, medications, and lab results
- **Cortex Agent Chat** — ask questions about patients, clinical notes, HIPAA regulations, and drug safety
- **Cited Evidence** — responses include source document citations

## Prerequisites

- A Snowflake account with the following objects already created:
  - `HEALTH_COPILOT_DB.DATA_LAYER.HEALTH_COPILOT_AGENT` (Cortex Agent)
  - `HEALTH_COPILOT_DB.DATA_LAYER.PATIENT_360_VIEW` (View)
  - `HEALTH_COPILOT_DB.DATA_LAYER.PATIENT_360_ANALYTICS` (Semantic View)
  - `HEALTH_COPILOT_DB.DATA_LAYER.CLINICAL_DOCS_SEARCH` (Cortex Search Service)
- Python 3.11+

## Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/<your-username>/health-copilot-app.git
   cd health-copilot-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Snowflake credentials:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Edit `.streamlit/secrets.toml` with your Snowflake credentials.

4. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add your Snowflake credentials in the app's Secrets settings (paste the contents of `secrets.toml`)
