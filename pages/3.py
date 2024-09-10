import streamlit as st

# Function to display notebook
def display_notebook():
    with open("EDA.html", "r") as file:
        html_content = file.read()
    st.markdown(html_content, unsafe_allow_html=True)

'''
# Sidebar navigation
pages = {
    "Home": home_page,
    "Projects": projects_page,
    "Contact": contact_page,
    "Notebook": display_notebook
}

# Create sidebar with radio buttons
selection = st.sidebar.radio("Navigate", list(pages.keys()))

# Call the selected page function
pages[selection]()
'''