import streamlit as st
from openai import OpenAI

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

    # Initialize or retrieve the session state for chat messages.
    if "chatroom_messages" not in st.session_state:
        st.session_state.chatroom_messages = []

    # Display all chatroom messages.
    for message in st.session_state.chatroom_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field for user input.
    if prompt := st.chat_input("What's on your mind?"):
        # Store and display the current prompt.
        st.session_state.chatroom_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chatroom_messages
            ],
        )

        # Extract the assistant's response from the OpenAI response object.
        assistant_message = response.choices[0].message.content

        # Store and display the bot's response.
        st.session_state.chatroom_messages.append({"role": "assistant", "content": assistant_message})
        with st.chat_message("
