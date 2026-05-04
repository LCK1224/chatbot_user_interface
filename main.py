import streamlit as st
import time
import pandas as pd
from io import StringIO
import ollama 

class GemmaBot:
    def __init__(self, model_name="gemma4:e4b", system_message=None):
        self.model_name = model_name
        self.messages = []
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def send_request(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        response = ollama.chat(
            model=self.model_name,
            messages=self.messages,
            stream=True,
        )
        return response

st.markdown(
    """
<style>
div.stButton > button:first-child {
    height: auto;
    padding: 10px 20px !important;
    width: 80px !important; 
}

[data-testid="stFileUploader"] section button {
    width: auto !important; 
    min-width: 100px; 
    padding: 5px 10px !important;
}


[data-testid="stFileUploader"] {
    font-size: 14px;
}

textarea {
    width: 500px !important;
    height: auto;
}
</style>
""",
    unsafe_allow_html=True,
)

if "themes" not in st.session_state:
    st.session_state.themes = {
        "current_theme": "light",
        "refreshed": True,
        "light": {"theme.base": "dark", "theme.backgroundColor": "black", "theme.primaryColor": "#c98bdb", 
                  "theme.secondaryBackgroundColor": "1e2e48", "theme.textColor": "white", "button_face": "🌜"},
        "dark": {"theme.base": "light", "theme.backgroundColor": "white", "theme.primaryColor": "#5591f5", 
                 "theme.secondaryBackgroundColor": "#82E1D7", "theme.textColor": "#0a1464", "button_face": "🌞"},
    }

def ChangeTheme():
    previous_theme = st.session_state.themes["current_theme"]
    tdict = st.session_state.themes["light"] if st.session_state.themes["current_theme"] == "light" else st.session_state.themes["dark"]
    for vkey, vval in tdict.items():
        if vkey.startswith("theme"):
            st._config.set_option(vkey, vval)
    st.session_state.themes["refreshed"] = False
    st.session_state.themes["current_theme"] = "light" if previous_theme == "dark" else "dark"


with st.sidebar:
    st.title("Navigation")
    menu = st.radio(
        "Main Menu",
        ["Gemma4", "Home Page", "Contact"],
        index=0,
        help="Select a page to navigate"
    )
    
    st.divider()
    
    if menu == "Gemma4":
        st.info("🤖 Model: Gemma 4")
    elif menu == "Home Page":
        st.page_link('github.com', label="Go to Github", icon="🌐")
    elif menu == "Contact":
        st.write("📧 leechunkit24@gmail.com")

def clear_text():
    st.session_state.messages = []
    if "my_instance" in st.session_state:
        st.session_state.my_instance.messages = []

def chat_func(input_text):
    with inside_container:
        with st.chat_message("user"):
            st.markdown(input_text)
        st.session_state.messages.append({"role": "user", "content": input_text})

        response_stream = st.session_state.my_instance.send_request(input_text)
        with st.chat_message("AI"):
            ai_text = st.write_stream(chunk['message']['content'] for chunk in response_stream)

        st.session_state.my_instance.messages.append({"role": "assistant", "content": ai_text})
        st.session_state.messages.append({"role": "AI", "content": ai_text})


st.header("Gemma4")

upper_container = st.container()
inside_container = st.container(border=True, height=500)

col1, col2 = st.columns([2, 12])
with col2:
    input_text = st.chat_input("Ask Gemma4 something...")
with col1:
    if st.button("Clear"):
        clear_text()
        st.rerun()

with upper_container:
    col1, col2 = st.columns([2, 12])
    with col2:
        with st.expander("Upload file"):
            uploaded_file = st.file_uploader("Choose a file", type=["txt", "csv"])
            if uploaded_file:
                if uploaded_file.name.endswith(".txt"):
                    data = uploaded_file.getvalue().decode("utf-8")
                else:
                    df = pd.read_csv(uploaded_file)
                    data = f"Context from CSV:\n{df.head().to_string()}"
                if st.button("Send"):
                    input_text = data

    with col1:
        btn_face = st.session_state.themes[st.session_state.themes["current_theme"]]["button_face"]
        st.button(btn_face, on_click=ChangeTheme)
        if not st.session_state.themes["refreshed"]:
            st.session_state.themes["refreshed"] = True
            st.rerun()

with inside_container:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "my_instance" not in st.session_state:
        st.session_state.my_instance = GemmaBot(system_message="")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if input_text:
        chat_func(input_text)