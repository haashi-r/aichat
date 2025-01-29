import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Hugging Face API details
HUGGINGFACE_API_URL = os.getenv("HUGGINGFACE_API_URL")
API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not API_KEY:
    st.error("API error: Please check your .env file")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Initialize Streamlit app
st.title("Chatbot")

# Initialize session state if not exists
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "no_count" not in st.session_state:
    st.session_state.no_count = 0
if "last_input" not in st.session_state:
    st.session_state.last_input = None  # To track if the input has already been processed

def query_huggingface_api(user_query):
    """Query the Hugging Face API and return the response."""
    try:
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=HEADERS,
            json={"inputs": user_query}
        )
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list) and len(response_data) > 0:
                return response_data[0].get('generated_text', '').strip()
            else:
                return None
        else:
            st.error("Error with the Hugging Face API.")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Display chat history
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.write(f"*You:* {chat['message']}")
    else:
        st.write(f"*Bot:* {chat['message']}")

# Input box for user query
user_input = st.text_input("Type your message:", key="user_input")

# Process user input on button click
if st.button("Send"):
    if user_input.strip() and user_input != st.session_state.last_input:
        st.session_state.last_input = user_input.strip()  # Update last processed input
        user_query = user_input.strip().lower()
        st.session_state.chat_history.append({"role": "user", "message": user_query})

        # Handle special cases
        if user_query in ["hi", "hello"]:
            bot_response = "Hello, how can I assist you?"
        elif user_query == "no":
            if st.session_state.no_count == 0:
                st.session_state.no_count += 1
                bot_response = "Please ask another question."
            else:
                st.session_state.no_count = 0
                bot_response = "Please connect to our agent: [Agent Link](http://www.agentlink.com)\nIs this useful?"
        elif user_query == "yes":
            st.session_state.no_count = 0
            bot_response = "Thank you! Have a nice day."
        else:
            # Query the Hugging Face API for other inputs
            bot_response = query_huggingface_api(user_query)
            if not bot_response:
                bot_response = "This is not in my context. Please connect to our agent: [Agent Link](http://www.agentlink.com)"
            else:
                bot_response += "\n\nIs this useful? Please let me know if further assistance is needed!"

        # **Fixed the error in this line by removing non-breaking space**
        st.session_state.chat_history.append({"role": "bot", "message": bot_response})
