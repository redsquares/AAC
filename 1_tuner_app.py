import streamlit as st
import numpy as np
import scipy.io.wavfile as wav
import io

# Function to generate a tone with harmonics
def generate_tone(frequency, duration=2, sample_rate=44100):
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

# Create buttons for each string
for note_name, frequency in reversed(notes.items()):  # Inverted order
    if st.button(note_name):
        waveform = generate_tone(frequency)
        audio_buffer = io.BytesIO()
        wav.write(audio_buffer, 44100, waveform)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format='audio/wav')
