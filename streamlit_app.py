import streamlit as st
from openai import OpenAI
import json
import os
import hashlib
import time

CHAT_HISTORY_FILE = "chat_history.json"

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
        if 'user_icon' not in st.session_state:
            st.session_state.user_icon = user_icon

        # Load the chat history from the file.
        chatroom_messages = read_chat_history()
        
        # Display all chatroom messages.
        chat_display = st.empty()  # Placeholder for chat display
        with chat_display:
            for message in chatroom_messages:
                icon = message.get("icon", "👤")
                content = message.get("content", "")
                role = message.get("role", "user")
                # Format the chat display with the emoji as an icon
                st.markdown(f"""
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 24px; margin-right: 8px;">{icon}</span>
                        <div style="background-color: {'#f1f1f1' if role == 'user' else '#e1f5fe'}; padding: 8px; border-radius: 8px;">
                            {content}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Create a chat input field for user input.
        if prompt := st.chat_input("What's on your mind?"):
            # Add the user's message to the chat history and display it.
            chatroom_messages.append({"role": "user", "icon": st.session_state.user_icon, "content": f"{prompt}"})
            write_chat_history(chatroom_messages)
            
            # Display the new message
            with chat_display:
                st.markdown(f"""
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 24px; margin-right: 8px;">{st.session_state.user_icon}</span>
                        <div style="background-color: #f1f1f1; padding: 8px; border-radius: 8px;">
                            {prompt}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            # Generate a response using the OpenAI API.
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in chatroom_messages
                ],
            )
            assistant_message = response.choices[0].message.content
            
            # Add the assistant's message to the chat history and display it.
            chatroom_messages.append({"role": "assistant", "icon": "🤖", "content": f"{assistant_message}"})
            write_chat_history(chatroom_messages)
            
            # Display the assistant's message
            with chat_display:
                st.markdown(f"""
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 24px; margin-right: 8px;">🤖</span>
                        <div style="background-color: #e1f5fe; padding: 8px; border-radius: 8px;">
                            {assistant_message}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Auto-refresh the chat every few seconds to show new messages.
        while True:
            time.sleep(1)
            new_messages = read_chat_history()
            if new_messages != chatroom_messages:
                chatroom_messages = new_messages
                with chat_display:
                    st.empty()
                    for message in chatroom_messages:
                        icon = message.get("icon", "👤")
                        content = message.get("content", "")
                        role = message.get("role", "user")
                        st.markdown(f"""
                            <div style="display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 8px;">{icon}</span>
                                <div style="background-color: {'#f1f1f1' if role == 'user' else '#e1f5fe'}; padding: 8px; border-radius: 8px;">
                                    {content}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
