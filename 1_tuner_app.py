import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import io

# Function to generate a tone with harmonics
def generate_tone(frequency, duration=8, sample_rate=44100):  # Duration increased to 8 seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = (
        0.5 * np.sin(2 * np.pi * frequency * t) +
        0.25 * np.sin(2 * np.pi * 2 * frequency * t) +
        0.125 * np.sin(2 * np.pi * 3 * frequency * t)
    )
    # Normalize waveform to 16-bit PCM
    waveform = np.int16(waveform / np.max(np.abs(waveform)) * 32767)
    return waveform

# Define the standard tuning frequencies for guitar
notes = {
    'E (High)': 329.63,
    'B': 246.94,
    'G': 196.00,
    'D': 146.83,
    'A': 110.00,
    'E (Low)': 82.41
}

# Streamlit app layout
st.title("Guitar Tuner")

# Initialize session state
if 'current_note' not in st.session_state:
    st.session_state.current_note = None
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = None

# Function to play the tone
def play_tone(note_name):
    frequency = notes[note_name]
    waveform = generate_tone(frequency)
    audio_buffer = io.BytesIO()
    wav.write(audio_buffer, 44100, waveform)
    audio_buffer.seek(0)
    st.session_state.audio_buffer = audio_buffer  # Save buffer to session state

# Create buttons for each string
for note_name in reversed(notes.keys()):  # Inverted order
    if st.button(note_name):
        if st.session_state.current_note == note_name:
            st.session_state.current_note = None
            st.session_state.audio_buffer = None
        else:
            st.session_state.current_note = note_name
            play_tone(note_name)

# Play the audio if there's a buffer
if st.session_state.audio_buffer:
    st.audio(st.session_state.audio_buffer, format='audio/wav', autoplay=True)
