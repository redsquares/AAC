import streamlit as st

st.title("My Portfolio")

# Adding an iframe for LinkedIn profile
st.markdown(
    """
    <iframe src="https://www.linkedin.com/in/nuno-mesquita-184a1515a/" width="100%" height="600" frameborder="0" allowfullscreen></iframe>
    """,
    unsafe_allow_html=True
)