import streamlit as st
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import threading

# Show title and description.
st.title("💬 Multi-User Chatbot")
st.write(
    "This is a multi-user chatroom where one participant is an AI chatbot. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Initialize ThreadPoolExecutor.
    executor = ThreadPoolExecutor(max_workers=10)
    lock = threading.Lock()

    # Initialize or retrieve the session state for chat messages.
    if "chatroom_messages" not in st.session_state:
        st.session_state.chatroom_messages = []

    # Function to generate and store chatbot responses.
    def generate_response(prompt):
        with lock:
            st.session_state.chatroom_messages.append({"role": "user", "content": prompt})
        # Generate a response using the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chatroom_messages
            ],
        )["choices"][0]["message"]["content"]

        with lock:
            st.session_state.chatroom_messages.append({"role": "assistant", "content": response})

    # Display all chatroom messages.
    for message in st.session_state.chatroom_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field for user input.
    if prompt := st.chat_input("What's on your mind?"):
        # Submit user input to the thread pool for processing.
        executor.submit(generate_response, prompt)
