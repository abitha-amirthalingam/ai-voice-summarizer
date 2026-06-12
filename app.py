import streamlit as st
import google.generativeai as genai

# Set up page layout and title
st.set_page_config(page_title="AI Voice Summarizer", page_icon="🎤", layout="centered")

st.title("🎤 AI Voice Summarizer")
st.caption("Speak or upload audio in Tamil to get an instant English translation and summary.")

# 🔑 FETCH SECRET KEY USING THE FRESH VARIABLE NAME
GEMINI_KEY = st.secrets.get("GEMINI_KEY", "")

if not GEMINI_KEY:
    st.warning("⚠️ Please configure your 'GEMINI_KEY' in Streamlit Secrets to activate the pipeline.")
    st.stop()

# Initialize the Gemini SDK
genai.configure(api_key=GEMINI_KEY)

# Sidebar or Tips Box
st.info("""
**Tips for best accuracy:**
1. Speak clearly into your microphone in a quiet room.
2. Try to record for at least 5 to 10 seconds.
""")

# Streamlit native recording block
audio_file = st.audio_input("Record your Tamil voice here:")

if audio_file is not None:
    with st.spinner("⚡ Gemini is analyzing your voice track instantly..."):
        try:
            # Read raw byte streams directly from the web widget buffer
            audio_bytes = audio_file.read()
            
            # Use the fast, native multimodal Gemini 2.5 Flash model
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Explicit, structured prompt layout to extract all three features safely
            prompt = """
            You are an expert AI Voice Engineer. Analyze the attached audio file data which contains Tamil speech.
            Provide the output strictly using the structural headers below:
            
            ---TAMIL_TRANSCRIPT---
            [Provide the exact text transcription of the Tamil speech spoken in the audio here]
            
            ---ENGLISH_TRANSLATION---
            [Translate that Tamil transcription accurately into natural English text here]
            
            ---SUMMARY---
            [Provide a brief, concise 1-2 sentence summary of the translation here]
            """
            
            # Pass data directly as an inline media dictionary block
            response = model.generate_content([
                {
                    "mime_type": "audio/webm",
                    "data": audio_bytes
                },
                prompt
            ])
            
            response_text = response.text
            
            # Parse response data structures to match your original front-end design
            if "---TAMIL_TRANSCRIPT---" in response_text:
                parts = response_text.split("---")
                tamil_text = parts[1].replace("TAMIL_TRANSCRIPT---\n", "").strip()
                english_text = parts[2].replace("ENGLISH_TRANSLATION---\n", "").strip()
                summary_text = parts[3].replace("SUMMARY---\n", "").strip()
                
                st.success("🎉 Processing Completed Successfully!")
                
                st.subheader("🎤 Tamil Transcript")
                st.info(tamil_text)
                    
                st.subheader("🌍 English Translation")
                st.success(english_text)
                    
                st.subheader("📝 Summary")
                st.warning(summary_text)
            else:
                # Direct structural output fallback
                st.subheader("🤖 Gemini Analysis")
                st.write(response_text)
                    
        except Exception as e:
            st.error(f"Transcription pipeline broke: {str(e)}")
