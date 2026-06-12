import streamlit as st
import google.generativeai as genai

# Set up page layout and title
st.set_page_config(page_title="AI Voice Summarizer", page_icon="🎤", layout="centered")

st.title("🎤 AI Voice Summarizer")
st.caption("Speak or upload audio in Tamil to get an instant English translation and summary.")

# 🔑 FETCH SECRET KEY
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
            
            # Bulletproof prompt explicitly telling Gemini exactly how to structure the text chunks
            prompt = """
            Analyze the attached audio file which contains Tamil speech. 
            You must provide three distinct outputs. Separate them exactly using these exact tags:

            [TAMIL_START]
            Write the exact text transcription of the Tamil speech spoken in the audio here.
            [TAMIL_END]

            [ENGLISH_START]
            Translate that Tamil transcription completely and accurately into natural English here.
            [ENGLISH_END]

            [SUMMARY_START]
            Provide a brief, concise 2-sentence summary of the English translation here.
            [SUMMARY_END]
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
            
            # 🔍 SAFELY EXTRACT TEXT SECTIONS USING TAG LOCATIONS
            try:
                tamil_text = response_text.split("[TAMIL_START]")[1].split("[TAMIL_END]")[0].strip()
                english_text = response_text.split("[ENGLISH_START]")[1].split("[ENGLISH_END]")[0].strip()
                summary_text = response_text.split("[SUMMARY_START]")[1].split("[SUMMARY_END]")[0].strip()
                
                st.success("🎉 Processing Completed Successfully!")
                
                st.subheader("🎤 Tamil Transcript")
                st.info(tamil_text)
                    
                st.subheader("🌍 English Translation")
                st.success(english_text)
                    
                st.subheader("📝 Summary")
                st.warning(summary_text)
                
            except Exception as parse_error:
                # Fallback display layout if tags don't match exactly
                st.success("🎉 Analysis Received!")
                st.subheader("🤖 Generated Content Pipeline")
                st.write(response_text)
                    
        except Exception as e:
            st.error(f"Transcription pipeline broke: {str(e)}")
