import streamlit as st
import sqlite3
import pandas as pd
import os

# Database initialization
def init_db():
    try:
        if not os.path.exists('athletes.db'):
            st.write("Creating the database...")

        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            # Create the matches table if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    date TEXT,
                    google_maps_link TEXT
                )
            ''')
            conn.commit()
            # st.write("Database and table initialized.")
    except sqlite3.Error as e:
        st.error(f"An error occurred while initializing the database: {e}")

# Custom CSS styles
st.markdown(
    """
    <style>
    /* Change the color of titles */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: green;
    }

    /* Change table header row color */
    .stDataFrame table thead th {
        background-color: #17a2b8; /* greenish-blue color */
        color: purple;
    }

    /* Change form titles */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# Function to fetch all matches from the database
def fetch_matches():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM matches", conn)
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching matches: {e}")
        return pd.DataFrame()

# Functions to add, update, and delete matches
def add_match(name, date, google_maps_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO matches (name, date, google_maps_link) VALUES (?, ?, ?)', (name, date, google_maps_link))
            conn.commit()
            st.success(f"Match '{name}' added successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding a match: {e}")

def update_match(match_id, new_name, new_date, new_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE matches SET name = ?, date = ?, google_maps_link = ? WHERE id = ?', (new_name, new_date, new_link, match_id))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while updating the match: {e}")

def delete_match(match_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM matches WHERE id = ?', (match_id,))
            conn.commit()
            st.success(f"Match deleted successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the match: {e}")

# Initialize the database
init_db()

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# State to hold the currently edited match ID
if 'edit_match_id' not in st.session_state:
    st.session_state.edit_match_id = None

# Fetch the current list of matches
matches_df = fetch_matches()

# Display the list of matches
st.write("### Match List")

# Add headers for the columns
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
col1.write("**Name**")
col2.write("**Date**")
col3.write("**Google Maps**")

# Display each match's data in the columns
for index, row in matches_df.iterrows():
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
    with col1:
        st.write(row['name'])
    with col2:
        st.write(row['date'])
    with col3:
        if row['google_maps_link']:
            st.markdown(f"[Open Map]({row['google_maps_link']})", unsafe_allow_html=True)
    with col4:
        if st.button("Edit", key=f"edit_{row['id']}"):
            st.session_state.edit_match_id = row['id']
            st.rerun()
    with col5:
        if st.button("Delete", key=f"delete_{row['id']}"):
            delete_match(row['id'])
            st.rerun()

# Show the form to add a new match
st.write("### Add New Match")
with st.form(key='add_match_form'):
    new_match_name = st.text_input('Match Name')
    new_match_date = st.date_input('Match Date')
    new_google_maps_link = st.text_input('Google Maps Link')
    if st.form_submit_button('Add'):
        if new_match_name.strip() and new_google_maps_link.strip():
            add_match(new_match_name.strip(), new_match_date.strftime('%Y-%m-%d'), new_google_maps_link.strip())
            st.rerun()

# Show the edit form if a match ID is set
if st.session_state.edit_match_id is not None:
    match_id = st.session_state.edit_match_id
    match_row = matches_df[matches_df['id'] == match_id]
    match_name = match_row['name'].values[0]
    match_date = pd.to_datetime(match_row['date'].values[0])
    match_link = match_row['google_maps_link'].values[0]

    st.write("### Edit Match")
    with st.form(key='edit_match_form'):
        new_name = st.text_input('Edit Name', value=match_name)
        new_date = st.date_input('Edit Date', value=match_date)
        new_link = st.text_input('Edit Google Maps Link', value=match_link)
        if st.form_submit_button('Update'):
            update_match(match_id, new_name.strip(), new_date.strftime('%Y-%m-%d'), new_link.strip())
            st.session_state.edit_match_id = None
            st.rerun()
