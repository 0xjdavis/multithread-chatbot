import streamlit as st
from openai import OpenAI
import json
import os
import time
import hashlib

CHAT_HISTORY_FILE = "chat_history.json"
UPDATE_INTERVAL = 1  # seconds

# Initialize the chat history file if it doesn't exist
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([], f)

# Function to read chat history from the file
def read_chat_history():
    with open(CHAT_HISTORY_FILE, "r") as f:
        return json.load(f)

# Function to write chat history to the file
def write_chat_history(messages):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(messages, f)

# Function to generate a unique emoji based on username
def generate_user_icon(username):
    # Hash the username to get a consistent, but unique result
    hash_value = int(hashlib.md5(username.encode()).hexdigest(), 16)
    emoji_index = hash_value % len(EMOJI_LIST)
    return EMOJI_LIST[emoji_index]

# List of emojis to use
EMOJI_LIST = [
    "🙂", "😎", "🤓", "😇", "😂", "😍", "🥳", "😃", "😅", "😎", 
    "😜", "🤗", "🤔", "😴", "😱", "😡", "🤠", "😈", "😇", "👻"
]

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

    # Ask user for their username.
    username = st.text_input("Enter your username:")
    if not username:
        st.info("Please enter a username to continue.", icon="🗣️")
    else:
        # Generate a unique icon for the user.
        user_icon = generate_user_icon(username)

        # Load the chat history from the file.
        chatroom_messages = read_chat_history()

        # Display all chatroom messages.
        for message in chatroom_messages:
            try:
                # Ensure the message contains the 'icon' and 'content' fields
                icon = message.get("icon", "👤")  # Default to a generic icon if not present
                content = message.get("content", "")
                with st.chat_message(message.get("role", "user")):
                    st.markdown(f"{icon} {content}")
            except Exception as e:
                st.error(f"Error displaying message: {e}")

        # Create a chat input field for user input.
        if prompt := st.chat_input("What's on your mind?"):
            # Add the user's message to the chat history and display it.
            chatroom_messages.append({"role": "user", "icon": user_icon, "content": f"{user_icon} {prompt}"})
            with st.chat_message("user"):
                st.markdown(f"{user_icon} {prompt}")

            # Write the updated chat history to the file.
            write_chat_history(chatroom_messages)

            # Generate a response using the OpenAI API.
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in chatroom_messages
                ],
            )

            # Extract the assistant's response from the OpenAI response object.
            assistant_message = response.choices[0].message.content

            # Add the assistant's message to the chat history and display it.
            chatroom_messages.append({"role": "assistant", "icon": "🤖", "content": f"🤖 {assistant_message}"})
            with st.chat_message("assistant"):
                st.markdown(f"🤖 {assistant_message}")

            # Write the updated chat history to the file.
            write_chat_history(chatroom_messages)

            # Rerun the app to update the chat display for all users.
            st.rerun()

        # Auto-refresh the chat every few seconds to show new messages.
        while True:
            time.sleep(UPDATE_INTERVAL)
            new_messages = read_chat_history()
            if new_messages != chatroom_messages:
                st.rerun()
