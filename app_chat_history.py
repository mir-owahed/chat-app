
import streamlit as st
import requests

# --- Extract assistant message from API response ---
def extract_message_text(response):
    try:
        return response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError) as e:
        return f"Error: Could not extract message text. Details: {e}"

# --- Setup page ---
st.set_page_config(page_title="Chat with Assistant", layout="wide")
st.title("💬 Chat with Assistant")

# --- Initialize session state ---
if "chats" not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat_id = "chat_1"
    st.session_state.chats["chat_1"] = {"name": "Untitled", "messages": []}

# --- Sidebar: Start new chat ---
st.sidebar.header("📂 Chat Sessions")
if st.sidebar.button("➕ New Chat"):
    new_id = f"chat_{len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = {"name": "Untitled", "messages": []}
    st.session_state.current_chat_id = new_id

# --- Sidebar: Chat selector ---
chat_ids = list(st.session_state.chats.keys())
chat_titles = {cid: st.session_state.chats[cid]["name"] for cid in chat_ids}
selected_id = st.sidebar.radio(
    "Select a chat",
    options=chat_ids,
    format_func=lambda cid: chat_titles[cid],
    index=chat_ids.index(st.session_state.current_chat_id)
)
st.session_state.current_chat_id = selected_id

# --- Access current chat ---
chat = st.session_state.chats[st.session_state.current_chat_id]
chat_history = chat["messages"]

# --- Show chat history ---
for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input ---
user_input = st.chat_input("Ask your question...")

if user_input:
    # 🧠 Rename Untitled immediately on first input
    if chat["name"] == "Untitled" and len(chat_history) == 0:
        short_title = " ".join(user_input.strip().split()[:6])
        if len(user_input.strip().split()) > 6:
            short_title += "..."
        chat["name"] = short_title

    # Save user message
    chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    url = "http://10.72.22.142:7860/api/v1/run/7672edb6-a126-4291-9b6f-43421cee7838"
    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat"
    }
    headers = {"Content-Type": "application/json"}

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                assistant_reply = extract_message_text(response.json())
            except Exception as e:
                assistant_reply = f"Error: {e}"

            st.markdown(assistant_reply)
            chat_history.append({"role": "assistant", "content": assistant_reply})
