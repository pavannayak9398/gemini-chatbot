import streamlit as st
import os
import google.generativeai as genai
import time

# Page config
st.set_page_config(layout="wide", page_title="Gemini Chatbot")

# App Title
st.title("Chatbot with Prompt Engineering")
st.write("Fine-tune your prompts with Gemini models using temperature, top-p, CoT, and token settings.")


# Sidebar-API key input
st.sidebar.title('Chatbot Settings')
api_key_input= st.sidebar.text_input("Enter your Gemini API Key:", type="password")
if api_key_input:
    os.environ["GEMINI_API_KEY"]=api_key_input
    genai.configure(api_key=api_key_input)
    

# Sidebar-Model selection and tuning parameters
AVAILABLE_MODELS = ["gemini-1.5-pro", "gemini-1.0-pro", "gemini-1.5-flash"]
selected_model = st.sidebar.selectbox("Select a Gemini model:", AVAILABLE_MODELS)
temperature = st.sidebar.slider('Temperature', 0.0, 1.0, 0.7, 0.1)
top_p = st.sidebar.slider('Top-p', 0.0, 1.0, 0.9, 0.1)
max_tokens = st.sidebar.slider("Max Output Tokens", 100, 2048, 512, 50)

# Prompting Strategy: Zero-shot, One-shot, Few-shot
prompting_type = st.sidebar.radio('CoT Prompting', options=['Zero-shot', 'One-shot', 'Few-shot'], index=0)
example_prompt = ""
if prompting_type in ["One-shot", "Few-shot"]:
    example_prompt = st.sidebar.text_area(
        "Provide Example(s) for Prompting:",
        value=(
            "Q: What is 19 times 4?\n"
            "A: Let's think step by step...\n"
            "19 x 4 = (20 x 4) - 4 = 80 - 4 = 76\n"
            "So, the answer is 76."
        ))
    
# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Input prompt
prompt = st.text_area("Enter your message:", placeholder="E.g., What is the meaning of dreams vs goals?")

    
# Custom CSS
st.markdown(
    """
    <style>
    
/* Full width override for Streamlit */
.main .block-container { 
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100% !important;
}

/* Use Poppins font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="st"] {
    font-family: 'Poppins', sans-serif;
}

/* Cool AI background */
body {
    background-image: url('https://images.unsplash.com/photo-1629904853716-f0bc54eea481?auto=format&fit=crop&w=1600&q=80');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    color: #ffffff;
}

/* Transparent app container */
.stApp {
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 0px;
    box-shadow: none;
    padding: 2rem;
}

/* Buttons and text areas */
.stTextArea, .stSelectbox, .stButton {
    background-color: #ffffff;
    color: #333;
    border-radius: 10px;
    padding: 0.8rem;
    box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.1);
}

/* Button hover */
.stButton button {
    background-color: #00adb5;
    color: #ffffff;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 10px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.stButton button:hover {
    background-color: #007e85;
}

/* Chat response box */
.response-box {
    background-color: rgba(255, 255, 255, 0.95);
    color: #ffffff;
    padding: 1.5rem;
    border-radius: 10px;
    margin-top: 1rem;
    box-shadow: 0 0 15px rgba(0,0,0,0.2);
}

.user-msg {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    text-align: left;
}

.bot-msg {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    text-align: left;
    box-shadow: 0 2px 5px rgba(255,255,255,0.2);
}

/* Footer styling */
.footer {
    text-align: center;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #ddd;
}
</style>
    """,
    unsafe_allow_html=True
)
                                    

# Send button
if st.button("Send"):
    if not api_key_input:
        st.error('Kindly enter the Gemini API key to proceed', icon="🚨")
    elif not prompt:
        st.warning("Please enter a prompt.")
    else:
        full_prompt = f"{example_prompt}\n{prompt}" if prompting_type != 'Zero-shot' else prompt
        
        try:
            model=genai.GenerativeModel(
                model_name=selected_model,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_tokens
                    )
                )
            
            with st.spinner("🤖 Gemini is thinking..."):
                response = model.generate_content(full_prompt)
            reply = response.text
            time.sleep(1.2)
            
            # Save interaction
            st.session_state.chat_history.append(('You', prompt))
            st.session_state.chat_history.append(('Gemini', reply))
            
        except Exception as e:
            st.error(f"Error:{e}")
        

# Display chat
st.markdown("### 💬 Chat History:")
for sender, message in st.session_state.chat_history:
    css_class = "user-msg" if sender == "You" else "bot-msg"
    avatar = "🧑‍💻" if sender == "You" else "🤖"
    st.markdown(f"<div class='{css_class}'><strong>{avatar} {sender}:</strong><br>{message}</div>", unsafe_allow_html=True)

# Download button
if len(st.session_state.chat_history) > 0:
    all_text = "\n\n".join([f"{s}: {m}" for s, m in st.session_state.chat_history])
    st.download_button("Download Chat", all_text, file_name="chat_history.txt")

# Footer
st.markdown("<div class='footer'>Built by <b>Pavan Naik</b> using Streamlit + Gemini ⚡</div>", unsafe_allow_html=True)

# Auto-scroll
st.markdown("<script>window.scrollTo(0,document.body.scrollHeight);</script>", unsafe_allow_html=True)