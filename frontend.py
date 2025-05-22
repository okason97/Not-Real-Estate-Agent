import streamlit as st
import requests
from streamlit.logger import get_logger

logger = get_logger(__name__)

# Set up the page configuration
st.set_page_config(page_title="Not-Real-Estate-Agent", layout="centered")
st.title("Not-Real-State-Agent is NOT A REAL ESTATE AGENT!")

# Sidebar for model configuration
st.sidebar.header("🔧 Configuration")

# Model selection
available_providers = [
    "Ollama-remote",
    "OpenAI", 
    "Anthropic",
    "Google",
]

available_models = {
    "Ollama-remote": "gemma3:12b",
    "OpenAI": "o3-mini",
    "Anthropic": "claude-3-5-sonnet-latest",
    "Google": "gemini-2.5-flash-preview-04-17"
}

selected_model = st.sidebar.selectbox(
    "Select Model Provider:",
    available_providers,
    index=0,  # Default to first model
    help="Choose the AI model provider to use for responses"
)

# API Key input
if selected_model != "Ollama-remote":
    api_key = st.sidebar.text_input(
        "API Key:",
        type="password",
        placeholder="Enter your API key",
        help="Your API key for the selected model"
    )

# Display current configuration
st.sidebar.markdown("---")
st.sidebar.markdown("**Current Settings:**")
st.sidebar.markdown(f"Model: `{available_models[selected_model]}`")
if selected_model != "Ollama-remote":
    st.sidebar.markdown(f"API Key: {'✅ Set' if api_key else '❌ Not set'}")

# Warning if API key is not set
if selected_model != "Ollama-remote" and not api_key:
    st.sidebar.warning("⚠️ Please enter your API key to use the chat")


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
    # Check if API key is provided
    if selected_model != "Ollama-remote" and not api_key:
        st.error("Please enter your API key in the sidebar before sending messages.")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Show a spinner while waiting for the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare data for Lambda
            payload = {
                "prompt": user_input,
                "model": selected_model.lower(),
                "api_key": api_key
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
                    llm_response = str(llm_response)
                    logger.info(llm_response)
                    st.markdown(llm_response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": llm_response})
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to Lambda: {str(e)}")