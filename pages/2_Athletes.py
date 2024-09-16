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


# The rest of your existing code for the "Next Match" page

# Database initialization
def init_db():
    try:
        if not os.path.exists('athletes.db'):
            st.write("Creating the database...")

        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            # Create the athletes table with 'contact' column if it doesn't exist
            c.execute('''
                CREATE TABLE IF NOT EXISTS athletes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    contact TEXT
                )
            ''')
            # Check if 'contact' column exists and add it if it doesn't
            c.execute("PRAGMA table_info(athletes)")
            columns = [column[1] for column in c.fetchall()]
            if 'contact' not in columns:
                c.execute('ALTER TABLE athletes ADD COLUMN contact TEXT')
            
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
        color: grey;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# Function to fetch all athletes from the database
def fetch_athletes():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM athletes", conn)
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching athletes: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Functions to add, update, and delete athletes
def add_athlete(name, contact):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO athletes (name, contact) VALUES (?, ?)', (name, contact))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding an athlete: {e}")

def update_athlete(athlete_id, new_name, new_contact):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE athletes SET name = ?, contact = ? WHERE id = ?', (new_name, new_contact, athlete_id))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while updating the athlete: {e}")

def delete_athlete(athlete_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM athletes WHERE id = ?', (athlete_id,))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the athlete: {e}")

# Initialize the database
init_db()

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# State to hold the currently edited athlete ID
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# Fetch the current list of athletes
athletes_df = fetch_athletes()

# Display the list of athletes in a tabular format
st.write("### Athlete List")

# # Add headers for the columns
# col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
# col1.write("**Name**")
# col2.write("**Contact**")

# Display each athlete's data in the columns
for index, row in athletes_df.iterrows():
    # Main container for each athlete
    with st.container():
        # Combine athlete's name and contact information in one line
        st.write(f"**{row['name']}** ({row['contact']})")

        # Create columns for the buttons, adjusting the width
        button_col1, button_col2, space_col3 = st.columns([1,1,8])
        
        with button_col1:
            if st.button("Edit", key=f"edit_{row['id']}"):
                st.session_state.edit_id = row['id']
                st.rerun()
        
        with button_col2:
            if st.button("Del", key=f"delete_{row['id']}"):
                delete_athlete(row['id'])
                st.success(f"Athlete '{row['name']}' deleted successfully!")
                st.rerun()        
        with space_col3:
            pass


st.markdown("---")

# Show the form to add a new athlete
st.write("### Add New Athlete")
with st.form(key='add_athlete_form'):
    new_athlete_name = st.text_input('Name')
    new_athlete_contact = st.text_input('Contact')
    if st.form_submit_button('Add'):
        if new_athlete_name.strip() and new_athlete_contact.strip():
            add_athlete(new_athlete_name.strip(), new_athlete_contact.strip())
            st.success(f"Athlete '{new_athlete_name}' added successfully!")
            st.rerun()

# Show the edit form if an athlete ID is set
if st.session_state.edit_id is not None:
    athlete_id = st.session_state.edit_id
    athlete_row = athletes_df[athletes_df['id'] == athlete_id]
    athlete_name = athlete_row['name'].values[0]
    athlete_contact = athlete_row['contact'].values[0]

    st.write("### Edit Athlete")
    with st.form(key='edit_form'):
        new_name = st.text_input('Edit Name', value=athlete_name)
        new_contact = st.text_input('Edit Contact', value=athlete_contact)
        if st.form_submit_button('Update'):
            update_athlete(athlete_id, new_name.strip(), new_contact.strip())
            st.session_state.edit_id = None
            st.success(f"Athlete '{new_name}' updated successfully!")
            st.rerun()
