import time
import uuid
import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="NARQ Chatbot",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 NARQ Diagnostic Support Chatbot")
st.write(
    "This chatbot helps explore symptom patterns related to Alzheimer’s disease, ALS, and Parkinson’s disease."
)

st.info(
    "This tool is for educational and research purposes only. It does not provide a medical diagnosis."
)


# ------------------------------------------------------------
# Dialogflow configuration
# ------------------------------------------------------------
PROJECT_ID = "narq-chatbot-lttf"


# ------------------------------------------------------------
# Cache the Dialogflow client so it is created only once
# ------------------------------------------------------------
@st.cache_resource
def get_dialogflow_client():
    return dialogflow.SessionsClient()


# ------------------------------------------------------------
# Session state
# ------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------------------------------------
# Function to send text to Dialogflow ES
# ------------------------------------------------------------
def detect_intent_text(project_id: str, session_id: str, text: str, language_code: str = "en") -> str:
    session_client = get_dialogflow_client()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={
            "session": session,
            "query_input": query_input
        }
    )

    return response.query_result.fulfillment_text


# ------------------------------------------------------------
# Display chat history
# ------------------------------------------------------------
st.subheader("Chat Interface")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------------------------------------
# Chat input
# ------------------------------------------------------------
user_input = st.chat_input("Describe the patient's symptoms or ask a question...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Show assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                start_time = time.time()

                bot_reply = detect_intent_text(
                    project_id=PROJECT_ID,
                    session_id=st.session_state.session_id,
                    text=user_input,
                    language_code="en"
                )

                elapsed = time.time() - start_time

                if not bot_reply:
                    bot_reply = "I understood your message, but I do not have a response configured yet."

            except Exception as e:
                bot_reply = f"Error connecting to Dialogflow: {e}"
                elapsed = None

            st.markdown(bot_reply)

            # Optional: show response time for debugging
            # if elapsed is not None:
            #     st.caption(f"Response time: {elapsed:.2f} seconds")

    # Save bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})


# ------------------------------------------------------------
# Example questions
# ------------------------------------------------------------
st.subheader("Example questions")
st.markdown("""
- What symptoms are most typical of Parkinson’s disease?
- Which symptoms overlap between ALS and Parkinson’s?
- Is memory impairment more typical of Alzheimer’s disease?
- Which symptoms are motor symptoms?
""")