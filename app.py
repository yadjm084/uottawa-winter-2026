import uuid
import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow
import json
import os


# Load JSON key from Streamlit secrets
service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

# Write it to a temporary file
with open("key.json", "w") as f:
    json.dump(service_account_info, f)

# Point Dialogflow to this file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

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

# Replace this with your actual Google Cloud project ID
PROJECT_ID = "narq-chatbot-lttf"

# Dialogflow needs a session ID to keep conversation context.
# We create one unique ID per Streamlit session.
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ------------------------------------------------------------
# Function to send user text to Dialogflow ES
# ------------------------------------------------------------

def detect_intent_text(project_id: str, session_id: str, text: str, language_code: str = "en") -> str:
    """
    Send a text query to Dialogflow ES and return the chatbot response.
    
    Parameters:
        project_id (str): Google Cloud project ID
        session_id (str): Unique session ID for the conversation
        text (str): User input text
        language_code (str): Language of the query
        
    Returns:
        str: Fulfillment text returned by Dialogflow
    """

    # Create a session client
    session_client = dialogflow.SessionsClient()

    # Build the session path
    session = session_client.session_path(project_id, session_id)

    # Convert user text into Dialogflow text input format
    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    # Wrap text input in a QueryInput object
    query_input = dialogflow.QueryInput(text=text_input)

    # Send request to Dialogflow
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    # Return the text response from Dialogflow
    return response.query_result.fulfillment_text


# ------------------------------------------------------------
# Chat history state
# ------------------------------------------------------------

# Store conversation messages in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------------------------------------
# Display existing chat history
# ------------------------------------------------------------

st.subheader("Chat Interface")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ------------------------------------------------------------
# Chat input box
# ------------------------------------------------------------

user_input = st.chat_input("Describe the patient's symptoms or ask a question...")

if user_input:
    # Save and show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        # Get response from Dialogflow
        bot_reply = detect_intent_text(
            project_id=PROJECT_ID,
            session_id=st.session_state.session_id,
            text=user_input,
            language_code="en"
        )

        # Fallback if Dialogflow returns empty response
        if not bot_reply:
            bot_reply = "I understood your message, but I do not have a response configured yet."

    except Exception as e:
        bot_reply = f"Error connecting to Dialogflow: {e}"

    # Save and show bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)


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