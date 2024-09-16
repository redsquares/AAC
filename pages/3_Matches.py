import streamlit as st
import sqlite3
import pandas as pd
import os

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the Home page.")
    # Redirect to Home if not authenticated
    st.markdown("""
        <script>
            window.location.href = "/";
        </script>
        """, unsafe_allow_html=True)
    st.stop()

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
                    team TEXT,
                    google_maps_link TEXT
                )
            ''')
            conn.commit()
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
        color: grey;
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
def add_match(name, date, team, google_maps_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO matches (name, date, team, google_maps_link) VALUES (?, ?, ?, ?)', 
                      (name, date, team, google_maps_link))
            conn.commit()
            st.success(f"Match '{name}' added successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding a match: {e}")

def update_match(match_id, new_name, new_date, new_team, new_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE matches SET name = ?, date = ?, team = ?, google_maps_link = ? WHERE id = ?', 
                      (new_name, new_date, new_team, new_link, match_id))
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

# Display each match's data
for index, row in matches_df.iterrows():
    with st.container():
        # Combine name, date, team, and link into one line
        match_line = f"**{row['name']}** ({row['team']}) - {pd.to_datetime(row['date']).strftime('%d/%m/%Y')}"
        if row['google_maps_link']:
            match_line += f" - [Open Map]({row['google_maps_link']})"
        st.markdown(match_line, unsafe_allow_html=True)

        # Create columns for Edit and Delete buttons
        button_col1, button_col2 = st.columns([1, 1])
        
        with button_col1:
            if st.button("Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_match_id = row['id']
                st.rerun()
        
        with button_col2:
            if st.button("Delete", key=f"delete_{row['id']}"):
                delete_match(row['id'])
                st.rerun()

        # Add a small divider line for spacing between matches
        st.markdown("---")

# Show the form to add a new match
st.write("### Add New Match")
with st.form(key='add_match_form'):
    new_match_name = st.text_input('Match Name')
    new_match_date = st.date_input('Match Date')
    new_team = st.selectbox('Select Team', ["Select a team...", "Minis", "Sub-14", "Sub-16"])
    new_google_maps_link = st.text_input('Google Maps Link')

    if st.form_submit_button('Add'):
        # Check if the match name and team are provided
        if new_match_name.strip() and new_team != "Select a team...":
            add_match(new_match_name.strip(), new_match_date.strftime('%Y-%m-%d'), new_team, new_google_maps_link.strip())
            st.rerun()
        else:
            if not new_match_name.strip():
                st.error("Match name is required.")
            if new_team == "Select a team...":
                st.error("Please select a valid team.")
                
# Show the edit form if a match ID is set
if st.session_state.edit_match_id is not None:
    match_id = st.session_state.edit_match_id
    match_row = matches_df[matches_df['id'] == match_id]
    match_name = match_row['name'].values[0]
    match_date = pd.to_datetime(match_row['date']).values[0]
    match_team = match_row['team'].values[0]
    match_link = match_row['google_maps_link'].values[0]

    st.write("### Edit Match")
    with st.form(key='edit_match_form'):
        new_name = st.text_input('Edit Name', value=match_name)
        new_date = st.date_input('Edit Date', value=match_date)
        new_team = st.selectbox('Edit Team', ["Minis", "Sub-14", "Sub-16"], index=["Minis", "Sub-14", "Sub-16"].index(match_team))
        new_link = st.text_input('Edit Google Maps Link', value=match_link)
        if st.form_submit_button('Update'):
            update_match(match_id, new_name.strip(), new_date.strftime('%Y-%m-%d'), new_team, new_link.strip())
            st.session_state.edit_match_id = None
            st.rerun()
