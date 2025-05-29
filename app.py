import streamlit as st
import requests

# Function to extract message text from the API response
def extract_message_text(response):
    try:
        return response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError) as e:
        return f"Error: Could not extract message text. Details: {e}"

st.title("Chat with Assistant")

# Initialize chat history in session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.chat_input("Ask your question...")

# If user submitted a message
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare and send API request
    url = "http://127.0.0.1:7860/api/v1/run/f4913f39-8bc8-4480-a407-ed5b15ef29ca"
    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat"
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        api_response = response.json()
        message_text = extract_message_text(api_response)
    except requests.exceptions.RequestException as e:
        message_text = f"API Error: {e}"
    except ValueError as e:
        message_text = f"Parsing Error: {e}"

    # Add assistant message to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": message_text})

    # Show assistant message
    with st.chat_message("assistant"):
        st.markdown(message_text)

# Display entire chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
