import os
import streamlit as st
import google.generativeai as genai

# Set up page layout and title
st.set_page_config(page_title="AI Voice Summarizer", page_icon="🎤", layout="centered")

st.title("🎤 AI Voice Summarizer")
st.caption("Speak or upload audio in Tamil to get an instant English translation and summary.")

# 🔑 SECURE API KEY CONFIGURATION
# It reads from Streamlit Secrets in production, fallback to hardcoded string for local testing.
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "PASTE_YOUR_GEMINI_API_KEY_HERE")

if GEMINI_API_KEY == "PASTE_YOUR_GEMINI_API_KEY_HERE" or not GEMINI_API_KEY:
    st.warning("⚠️ Please configure your Gemini API Key to activate the pipeline.")
    st.stop()

# Initialize the Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

# Sidebar or Tips Box
st.info("""
**Tips for best accuracy:**
1. Speak clearly into your microphone in a quiet room.
2. Try to record for at least 5 to 10 seconds.
""")

# Streamlit native recording block
audio_file = st.audio_input("Record your Tamil voice here:")

if audio_file is not None:
    # Processing states
    with st.spinner("⚡ Gemini is analyzing your voice track instantly..."):
        filename = "recording.webm"
        try:
            # Save the uploaded byte stream to a temporary local file
            with open(filename, "wb") as f:
                f.write(audio_file.read())
            
            # 1. Upload the audio file directly to Gemini's API cloud engine
            audio_upload = genai.upload_file(path=filename, mime_type="audio/webm")
            
            # 2. Select the fast, powerful Gemini 2.5 Flash model
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Structuring the prompt ensures Gemini splits the outputs exactly how we want them
            prompt = """
            You are an expert AI Voice Engineer. Analyze the attached audio file which contains Tamil speech.
            Provide the output strictly using the structural headers below:
            
            ---TAMIL_TRANSCRIPT---
            [Provide the exact text transcription of the Tamil speech spoken in the audio here]
            
            ---ENGLISH_TRANSLATION---
            [Translate that Tamil transcription accurately into natural English text here]
            
            ---SUMMARY---
            [Provide a brief, concise 1-2 sentence summary of the translation here]
            """
            
            # Request translation pipeline
            response = model.generate_content([audio_upload, prompt])
            response_text = response.text

            # Clean up the cloud audio asset right after processing
            genai.delete_file(audio_upload.name)
            
            # 3. Parse and display the response into your original frontend elements
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
                # Direct fallback output if string splitting misses
                st.subheader("🤖 Gemini Analysis")
                st.write(response_text)
                    
        except Exception as e:
            st.error(f"Transcription pipeline broke: {str(e)}")
            
        finally:
            # Secure disk file cleanup
            if os.path.exists(filename):
                os.remove(filename)
