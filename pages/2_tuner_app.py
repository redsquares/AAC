import streamlit as st
import numpy as np
import soundfile as sf
import io

# Function to generate a tone with harmonics
def generate_tone(frequency, duration=2, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = (
        0.5 * np.sin(2 * np.pi * frequency * t) +
        0.25 * np.sin(2 * np.pi * 2 * frequency * t) +
        0.125 * np.sin(2 * np.pi * 3 * frequency * t)
    )
    return waveform

# Function to repeat waveform data to simulate looping
def repeat_waveform(waveform, repeat_count=5):
    return np.tile(waveform, repeat_count)

# Define the standard tuning frequencies for guitar (inverted order)
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

# State to track which tone is currently playing
if 'current_note' not in st.session_state:
    st.session_state.current_note = None

# Function to play or stop tone
def toggle_tone(note):
    if st.session_state.current_note == note:
        st.session_state.current_note = None
    else:
        st.session_state.current_note = note

# Create buttons for each string
for note_name, frequency in reversed(notes.items()):  # Inverted order
    if st.button(note_name):
        toggle_tone(note_name)
        if st.session_state.current_note:
            waveform = generate_tone(notes[st.session_state.current_note])
            waveform_looped = repeat_waveform(waveform)  # Repeat waveform to simulate looping
            audio_buffer = io.BytesIO()
            sf.write(audio_buffer, waveform_looped, 44100, format='wav')
            audio_buffer.seek(0)
            st.audio(audio_buffer, format='audio/wav', start_time=0.0, autoplay=True)
        else:
            st.audio(None)  # Stop playback by setting audio to None
