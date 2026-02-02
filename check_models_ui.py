import os
import google.generativeai as genai
from dotenv import load_dotenv

# Try to find API key from environment or input
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Look for it in app.py's secrets if possible, or just ask user to input it in the real app.
    # For this script, we'll try to rely on the environment variable if set by the user previously,
    # or we might need to rely on the app's context. 
    # Since I cannot easily interactively ask in this script execution, I will try to read it from a temporary file if I could,
    # but for now let's assume I need to guide the user or use a hardcoded key for testing if I had one (I don't).
    # Wait, the Streamlit app has the key in the session state. 
    pass

# To make this useful, I'll write a script that can be run via `streamlit run` or just python if the key is env var.
# But the user inputs the key in the UI. 
# So I will creating a small streamlit utility to check models using the key the user inputs.

import streamlit as st

st.title("Debug: Check Available Models")

api_key = st.text_input("Enter your Gemini API Key", type="password")

if st.button("Check Models"):
    if not api_key:
        st.error("Please enter an API Key")
    else:
        try:
            genai.configure(api_key=api_key)
            models = list(genai.list_models())
            st.write("### Available Models")
            found_generate_content = []
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    found_generate_content.append(m.name)
                    st.write(f"- **{m.name}**")
                    # st.json(m.to_dict()) # caused error
            
            st.write("### Recommended List for app.py")
            st.code(json.dumps([m.replace('models/', '') for m in found_generate_content], indent=2))
            
        except Exception as e:
            st.error(f"Error: {e}")
