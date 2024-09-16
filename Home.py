import streamlit as st

def authenticate():
    # Display the logo on the top of the page
    st.image("logo_aac.png", width=100)

    # Check if the user is already authenticated
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # If the user is already authenticated, switch to "1_Next_Match"
    if st.session_state.authenticated:
        st.switch_page("pages/1_Next_Match.py")  # Switch to the "Next Match" page
        st.stop()

    # Authentication form
    with st.form(key='login_form'):
        password = st.text_input('Enter Password:', type='password')
        login_button = st.form_submit_button('Login')
        
        if login_button:  # Trigger when form is submitted
            if password == 'aac':
                st.session_state.authenticated = True
                st.success('Successfully logged in!')
                # Switch to "1_Next_Match"
                st.switch_page("pages/1_Next_Match.py")
            else:
                st.error('Incorrect password.')

# Call the authentication function when the script is run
authenticate()
