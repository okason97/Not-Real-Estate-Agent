import streamlit as st
import requests
from streamlit.logger import get_logger

logger = get_logger(__name__)

# Set up the page configuration
st.set_page_config(page_title="Not-Real-Estate-Agent", layout="centered")
st.title("Not-Real-State-Agent is NOT A REAL ESTATE AGENT!")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# AWS Lambda function URL - replace with your actual Lambda URL
LAMBDA_URL = "http://127.0.0.1:3000/"

# Get user input
user_input = st.chat_input("Ask about what you want to rent or buy...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Show a spinner while waiting for the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare data for Lambda
            payload = {
                "prompt": user_input
            }
            
            # Make POST request to Lambda function
            try:
                response = requests.post(
                    LAMBDA_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                # Process the response
                if response.status_code == 200:
                    logger.info(response)
                    llm_response = response.json().get("result", "Sorry, I couldn't process that.")
                    logger.info(llm_response)
                    st.write(llm_response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": llm_response})
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to Lambda: {str(e)}")