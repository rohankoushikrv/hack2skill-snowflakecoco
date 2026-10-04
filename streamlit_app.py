import os
import json
import math
import streamlit as st

st.set_page_config(
    page_title="Rohan Health Copilot — Patient & Member 360",
    page_icon=":hospital:",
    layout="wide",
)

conn = st.connection("snowflake")

AGENT_FQN = "HEALTH_COPILOT_DB.DATA_LAYER.HEALTH_COPILOT_AGENT"

SUGGESTIONS = {
    ":blue[:material/favorite:] High-risk patients": "Which patients are high risk and why?",
    ":green[:material/science:] Cardiac history": "What does the clinical note say about Patient P001's cardiac history?",
    ":orange[:material/policy:] HIPAA rules": "What are the HIPAA rules for disclosing patient information?",
    ":red[:material/medication:] Drug interactions": "What drug interactions should I watch for in elderly patients on warfarin?",
    ":violet[:material/bar_chart:] Cost by plan": "What is the total claims cost by insurance plan?",
}


@st.cache_data(ttl=300)
def get_patient_summary():
    return conn.query("""
        SELECT PATIENT_ID, FIRST_NAME, LAST_NAME, AGE, GENDER,
               RISK_SCORE, INSURANCE_PLAN, TOTAL_CLAIMS,
               TOTAL_CLAIM_AMOUNT, ACTIVE_MEDICATIONS, ABNORMAL_LAB_COUNT
        FROM HEALTH_COPILOT_DB.DATA_LAYER.PATIENT_360_VIEW
        ORDER BY RISK_SCORE DESC
    """)


def safe_int(val):
    try:
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return 0
        return int(val)
    except (ValueError, TypeError):
        return 0


def risk_badge(score):
    if score >= 0.70:
        return f":red-background[HIGH {score:.2f}]"
    elif score >= 0.40:
        return f":orange-background[MOD {score:.2f}]"
    return f":green-background[LOW {score:.2f}]"


def call_agent(question):
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": question}],
            }
        ]
    })
    result = conn.query(
        f"SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN('{AGENT_FQN}', $${payload}$$, TRUE) AS response",
        ttl=0,
    )
    return json.loads(result.iloc[0]["RESPONSE"])


def extract_response_text(agent_response):
    if "content" not in agent_response:
        return agent_response.get("message", "An error occurred.")
    parts = []
    for item in agent_response["content"]:
        if item.get("type") == "text":
            parts.append(item["text"])
    return "\n\n".join(parts) if parts else "No response generated."


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Patient Dashboard")
    df = get_patient_summary()
    for _, row in df.iterrows():
        badge = risk_badge(row["RISK_SCORE"])
        with st.expander(f"{row['FIRST_NAME']} {row['LAST_NAME']} ({row['PATIENT_ID']})"):
            st.markdown(f"**Risk:** {badge}")
            st.markdown(f"**Age:** {row['AGE']}  |  **Gender:** {row['GENDER']}")
            st.markdown(f"**Plan:** {row['INSURANCE_PLAN']}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Claims", safe_int(row["TOTAL_CLAIMS"]))
            col2.metric("Meds", safe_int(row["ACTIVE_MEDICATIONS"]))
            col3.metric("Abn Labs", safe_int(row["ABNORMAL_LAB_COUNT"]))
            amt = row["TOTAL_CLAIM_AMOUNT"]
            if amt is not None and not (isinstance(amt, float) and math.isnan(amt)):
                st.markdown(f"**Total Cost:** ${amt:,.2f}")

    st.divider()
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN ---
st.title(":hospital: Rohan Health Copilot")
st.caption("Patient & Member 360 | Clinical & Regulatory Document Q&A with Cited Evidence")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    selected = st.pills(
        "Try asking:",
        list(SUGGESTIONS.keys()),
        label_visibility="collapsed",
    )
    if selected:
        prompt = SUGGESTIONS[selected]
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

if prompt := st.chat_input("Ask about patients, clinical notes, regulations, or drug safety..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consulting structured data and clinical documents..."):
            try:
                agent_resp = call_agent(prompt)
                answer = extract_response_text(agent_resp)
            except Exception as e:
                answer = f"**Error:** {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
