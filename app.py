import os
import torch
import streamlit as st
import whisper
from deep_translator import GoogleTranslator

# Local Windows path injection (Keeps your home computer setup working perfectly)
if os.name == 'nt':
    FFMPEG_DIR = r"C:\ffmpeg\ffmpeg-8.1.1-essentials_build\bin"
    if FFMPEG_DIR not in os.environ["PATH"]:
        os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

# Set up page layout and title
st.set_page_config(page_title="AI Voice Summarizer", page_icon="🎤", layout="centered")

st.title("🎤 AI Voice Summarizer")
st.caption("Speak or upload audio in Tamil to get an instant English translation and summary.")

# Cache the heavy whisper model so it only loads ONCE on startup
@st.cache_resource
def load_whisper_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Streamlit Cloud gives 1GB RAM. We use 'base' for CPU stability so it never crashes!
    model_size = "turbo" if device == "cuda" else "base"
    st.write(f"⚙️ Running model tier: `{model_size.upper()}` on `{device.upper()}`")
    return whisper.load_model(model_size, device=device)

model = load_whisper_model()

def translate_and_summarize(tamil_text):
    try:
        english = GoogleTranslator(source="ta", target="en").translate(tamil_text)
        sentences = [s.strip() for s in english.split(".") if len(s.strip()) > 5]
        if len(sentences) <= 2:
            summary = english
        else:
            summary = ". ".join(sentences[:2]) + "."
        return english, summary
    except Exception as e:
        return f"Translation error: {str(e)}", "Summary unavailable"

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
    with st.spinner("Processing audio track... please wait..."):
        filename = "recording.webm"
        try:
            # Save the uploaded byte stream to a temporary local file
            with open(filename, "wb") as f:
                f.write(audio_file.read())
            
            # Execute Whisper transcription pipeline
            result = model.transcribe(
                filename,
                language="ta",
                temperature=0,
                initial_prompt="வணக்கம், இது தெளிவான தமிழ் பேச்சு.",
                no_speech_threshold=0.5
            )
            
            tamil_text = result["text"].strip()
            
            if not tamil_text:
                st.error("No speech detected. Please speak closer to the mic.")
            else:
                # Run the translation and summary functions
                english_text, summary = translate_and_summarize(tamil_text)
                
                st.success("🎉 Processing Completed Successfully!")
                
                # Display output cards beautifully using native styled headers
                st.subheader("🎤 Tamil Transcript")
                st.info(tamil_text)
                    
                st.subheader("🌍 English Translation")
                st.success(english_text)
                    
                st.subheader("📝 Summary")
                st.warning(summary)
                    
        except Exception as e:
            st.error(f"Transcription pipeline broke: {str(e)}")
            
        finally:
            # Secure disk file cleanup
            if os.path.exists(filename):
                os.remove(filename)