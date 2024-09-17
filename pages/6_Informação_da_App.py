import streamlit as st

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Por favor, faça login a partir da página inicial.")
    st.stop()

# Display the text in Portuguese
st.write("""
### Esta app foi criada por brincadeira, mas deu algum trabalho e ocupou algum tempo.
""")

st.markdown("<br>", unsafe_allow_html=True)

st.write("""
Se achar que mereço um café, pode clicar neste link e "oferecer-me um café" :)
""")

st.markdown("<br>", unsafe_allow_html=True)

st.write("""Obrigado""")

st.write("""Nuno Mesquita""")

# Add extra spacing (adjust the number of <br> tags as needed)
st.markdown("<br>", unsafe_allow_html=True)

# Adjusted "Buy Me a Coffee" button
button_code = '''
<div style="text-align: left; margin-top: 50px;">
    <a href="https://www.buymeacoffee.com/redsquares"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=redsquares&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>
</div>
'''
st.markdown(button_code, unsafe_allow_html=True)
