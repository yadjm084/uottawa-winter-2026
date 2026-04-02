import time
import uuid
import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account


# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(
    page_title="Neurodegenerative Diseases Q&A Chatbot",
    page_icon="🧠",
    layout="wide"
)


# ------------------------------------------------------------
# Dialogflow config
# ------------------------------------------------------------
PROJECT_ID = "narq-chatbot-lttf"


@st.cache_resource
def get_dialogflow_client():
    """
    Create and cache the Dialogflow client once.
    This avoids rebuilding the client on every message.
    """
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return dialogflow.SessionsClient(credentials=credentials)


def detect_intent_text(project_id: str, session_id: str, text: str, language_code: str = "en") -> str:
    """
    Send the user query to Dialogflow ES and return the fulfillment text.
    """
    session_client = get_dialogflow_client()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input
        },
        timeout=20,
    )

    return response.query_result.fulfillment_text


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "open_chat" not in st.session_state:
    st.session_state.open_chat = False


# ------------------------------------------------------------
# Custom CSS
# ------------------------------------------------------------
st.markdown("""
<style>
/* General page background */
.stApp {
    background-color: #f6f3ee;
    color: #2f2a26;
}

/* Main block width */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    max-width: 1250px;
}

/* Top fake nav */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0 1rem 0;
    border-bottom: 1px solid #d8d0c7;
    margin-bottom: 2rem;
}

.brand-wrap {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.brand-title {
    font-size: 2.1rem;
    font-weight: 600;
    color: #2f7d5a;
    letter-spacing: 0.5px;
    margin: 0;
}

.brand-subtitle {
    font-size: 1rem;
    color: #7a6f66;
    line-height: 1.2;
    margin: 0;
}

.nav-center {
    display: flex;
    gap: 2rem;
    font-size: 1.05rem;
    color: #6e6259;
}

.nav-right {
    font-size: 0.95rem;
    color: #7a6f66;
}

/* Hero */
.eyebrow {
    color: #4d9b79;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

.hero-title {
    font-size: 4rem;
    line-height: 1.08;
    font-weight: 500;
    color: #2f2a26;
    margin-bottom: 1.2rem;
}

.hero-accent {
    color: #2f7d5a;
    font-style: italic;
}

.hero-desc {
    font-size: 1.25rem;
    color: #7a6f66;
    line-height: 1.7;
    max-width: 900px;
    margin-bottom: 1.5rem;
}

.info-pill {
    background: #dcefdc;
    border: 1px solid #b7d8bc;
    color: #2f7d5a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-size: 1.05rem;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 2.5rem;
}

/* Section title */
.section-title {
    font-size: 2rem;
    font-weight: 500;
    color: #2f2a26;
    margin-top: 2rem;
    margin-bottom: 0.35rem;
}

.section-subtitle {
    color: #7a6f66;
    font-size: 1.05rem;
    margin-bottom: 1.25rem;
}

/* Condition cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(220px, 1fr));
    gap: 0;
    border: 1px solid #d8d0c7;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.8rem;
}

.condition-card {
    background: #fbfaf8;
    padding: 1.25rem 1.3rem;
    border-right: 1px solid #d8d0c7;
    border-bottom: 1px solid #d8d0c7;
    min-height: 115px;
}

.condition-card:nth-child(3n) {
    border-right: none;
}

.condition-name {
    font-size: 1.25rem;
    font-weight: 500;
    margin-bottom: 0.7rem;
    color: #2f2a26;
}

.condition-meta {
    color: #8a7f75;
    font-size: 0.98rem;
}

/* Ask table */
.ask-table {
    border: 1px solid #d8d0c7;
    border-radius: 14px;
    overflow: hidden;
    background: #fbfaf8;
    margin-bottom: 2rem;
}

.ask-row {
    display: grid;
    grid-template-columns: 70px 280px 1fr;
    border-bottom: 1px solid #d8d0c7;
}

.ask-row:last-child {
    border-bottom: none;
}

.ask-cell {
    padding: 1rem 1.1rem;
    font-size: 1.02rem;
}

.ask-number {
    color: #7a6f66;
}

.ask-type {
    font-weight: 600;
    color: #2f2a26;
}

.ask-example {
    color: #8a7f75;
    font-style: italic;
}

/* Chat box section */
.chat-box {
    background: #fbfaf8;
    border: 1px solid #d8d0c7;
    border-radius: 16px;
    padding: 1rem 1rem 0.5rem 1rem;
    margin-top: 1rem;
}

/* Floating chat button */
.chat-float {
    position: fixed;
    bottom: 22px;
    right: 22px;
    z-index: 9999;
}

div.stButton > button {
    border-radius: 999px;
    border: 1px solid #2f7d5a;
    background-color: #2f7d5a;
    color: white;
    font-weight: 600;
    padding: 0.55rem 1rem;
}

div.stButton > button:hover {
    border-color: #256348;
    background-color: #256348;
    color: white;
}

/* Chat input area tweaks */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 0.4rem 0.7rem;
    border: 1px solid #e0d8cf;
}

/* Hide default Streamlit menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Top header / navigation
# ------------------------------------------------------------
st.markdown("""
<div class="topbar">
    <div class="brand-wrap">
        <div class="brand-title">NARQ</div>
        <div class="brand-subtitle">
            Neurodegenerative Disease<br>Reasoning Agent
        </div>
    </div>
    <div class="nav-center">
        <div><strong style="color:#2f7d5a;">Agent</strong></div>
        <div>Documentation</div>
        <div>Ontology</div>
    </div>
    <div class="nav-right">DTI5125 — Group 2</div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# Tabs for page sections
# ------------------------------------------------------------
tab_agent, tab_docs, tab_ontology = st.tabs(["Agent", "Documentation", "Ontology"])


# ------------------------------------------------------------
# Agent tab
# ------------------------------------------------------------
with tab_agent:
    st.markdown("""
    <div class="eyebrow">Neurodegenerative Disease — Diagnostic Support Agent</div>
    <div class="hero-title">
        Learn about <span class="hero-accent">neurodegenerative</span><br>
        symptoms, risks, and diagnostic<br>
        differentiation with <span class="hero-accent">NARQ</span>.
    </div>
    <div class="hero-desc">
        A knowledge-based conversational agent for educational support, covering Alzheimer’s disease,
        Parkinson’s disease, and ALS with symptoms, triage logic, overlapping signs, risk factors,
        lifestyle factors, and clinical differentiation.
    </div>
    <div class="info-pill">💬 Open the chat below or use the floating button at the bottom-right to get started.</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Covered conditions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The agent has structured knowledge on the three diseases below.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card-grid">
        <div class="condition-card">
            <div class="condition-name">Alzheimer’s Disease</div>
            <div class="condition-meta">Cognitive decline · Memory impairment · Reasoning and language changes</div>
        </div>
        <div class="condition-card">
            <div class="condition-name">Parkinson’s Disease</div>
            <div class="condition-meta">Motor symptoms · Tremor · Bradykinesia · Rigidity</div>
        </div>
        <div class="condition-card">
            <div class="condition-name">ALS</div>
            <div class="condition-meta">Muscle weakness · Bulbar dysfunction · Respiratory impairment</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">What you can ask</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The agent understands six main types of questions.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ask-table">
        <div class="ask-row">
            <div class="ask-cell ask-number">1</div>
            <div class="ask-cell ask-type">Symptoms</div>
            <div class="ask-cell ask-example">“What are the symptoms of Parkinson’s disease?”</div>
        </div>
        <div class="ask-row">
            <div class="ask-cell ask-number">2</div>
            <div class="ask-cell ask-type">Diagnosis support</div>
            <div class="ask-cell ask-example">“I have tremor and slow movement. What disease could I have?”</div>
        </div>
        <div class="ask-row">
            <div class="ask-cell ask-number">3</div>
            <div class="ask-cell ask-type">Differentiation</div>
            <div class="ask-cell ask-example">“How do I differentiate between ALS and Alzheimer’s?”</div>
        </div>
        <div class="ask-row">
            <div class="ask-cell ask-number">4</div>
            <div class="ask-cell ask-type">Overlapping symptoms</div>
            <div class="ask-cell ask-example">“What symptoms overlap between ALS and Parkinson’s?”</div>
        </div>
        <div class="ask-row">
            <div class="ask-cell ask-number">5</div>
            <div class="ask-cell ask-type">Risk factors</div>
            <div class="ask-cell ask-example">“What are the risk factors for Alzheimer’s disease?”</div>
        </div>
        <div class="ask-row">
            <div class="ask-cell ask-number">6</div>
            <div class="ask-cell ask-type">Lifestyle factors</div>
            <div class="ask-cell ask-example">“What lifestyle factors affect Parkinson’s disease?”</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Ask a question below.</div>', unsafe_allow_html=True)

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)

    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Describe the patient's symptoms or ask a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    bot_reply = detect_intent_text(
                        project_id=PROJECT_ID,
                        session_id=st.session_state.session_id,
                        text=user_input,
                        language_code="en"
                    )

                    if not bot_reply:
                        bot_reply = "I understood your message, but I do not have a response configured yet."

                except Exception as e:
                    bot_reply = f"Error connecting to Dialogflow: {type(e).__name__}: {e}"

                st.markdown(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------
# Documentation tab
# ------------------------------------------------------------
with tab_docs:
    st.markdown('<div class="section-title">Documentation</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-desc">
        This chatbot was built as a knowledge-based diagnostic support tool for three neurodegenerative
        diseases. It combines Dialogflow ES, a webhook layer, and an ontology-driven knowledge base.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    - **Goal:** help users explore symptoms, triage logic, overlapping signs, and risk factors.
    - **Knowledge source:** simplified ontology inspired by the Neurodegenerative Disease Risk Factor Ontology (NDDRFO).
    - **Reasoning logic:** diseases are linked to primary symptoms, overlapping symptoms, risk factors, and lifestyle factors.
    - **Deployment:** Streamlit frontend + Dialogflow ES + webhook.
    """)


# ------------------------------------------------------------
# Ontology tab
# ------------------------------------------------------------
with tab_ontology:
    st.markdown('<div class="section-title">Ontology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero-desc">
        The ontology organizes knowledge into diseases, symptoms, symptom categories, and risk factors.
        It allows the chatbot to reason over structured relationships rather than simply matching keywords.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Main classes**
    - NeurodegenerativeDisease
    - Symptom
    - SymptomCategory
    - RiskFactorCategory

    **Main relations**
    - hasPrimarySymptom
    - hasSymptom
    - hasOverlappingSymptom
    - isRiskFactorFor
    - isProtectiveFactorFor
    - belongsToCategory
    """)


# ------------------------------------------------------------
# Floating chat open button
# ------------------------------------------------------------
st.markdown('<div class="chat-float">', unsafe_allow_html=True)
if st.button("Open Chat"):
    st.session_state.open_chat = True
st.markdown('</div>', unsafe_allow_html=True)