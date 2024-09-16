import streamlit as st
import sqlite3
import pandas as pd

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the Home page.")
    st.stop()

# Initialize session state variables
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# Initialize team filter state
if 'selected_teams' not in st.session_state:
    st.session_state.selected_teams = []

# Function to fetch all athletes from the database
def fetch_athletes():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM athletes ORDER BY name ASC", conn)
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching athletes: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Function to fetch available teams for the multiselect
def fetch_teams():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT name FROM teams", conn)['name'].tolist()
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching teams: {e}")
        return []

# Functions to add, update, and delete athletes
def add_athlete(name, contact, teams):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO athletes (name, contact, teams) VALUES (?, ?, ?)', (name, contact, teams))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding an athlete: {e}")

def update_athlete(athlete_id, new_name, new_contact, new_teams):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE athletes SET name = ?, contact = ?, teams = ? WHERE id = ?', (new_name, new_contact, new_teams, athlete_id))
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

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Show the form to add a new athlete at the top
st.write("### Add New Athlete")
with st.form(key='add_athlete_form'):
    new_athlete_name = st.text_input('Name')
    new_athlete_contact = st.text_input('Contact')
    team_options = fetch_teams()  # Fetch team options from the database
    new_athlete_teams = st.multiselect('Teams', team_options)
    if st.form_submit_button('Add'):
        if new_athlete_name.strip() and new_athlete_contact.strip() and new_athlete_teams:
            teams_str = ",".join(new_athlete_teams)  # Store teams as a comma-separated string
            add_athlete(new_athlete_name.strip(), new_athlete_contact.strip(), teams_str)
            st.success(f"Athlete '{new_athlete_name}' added successfully!")
            st.rerun()

# Add filter to select teams (move this section after the form)
st.write("### Filter Athletes by Team")
st.session_state.selected_teams = st.multiselect('Select Teams', team_options, default=st.session_state.selected_teams)

# Fetch the current list of athletes
athletes_df = fetch_athletes()

# Apply team filter to the athlete list if any teams are selected
if not athletes_df.empty:
    if st.session_state.selected_teams:
        # Convert selected teams to set for filtering
        selected_teams_set = set(st.session_state.selected_teams)
        
        # Function to filter athletes by selected teams
        def filter_by_teams(teams_str):
            athlete_teams_set = set(teams_str.split(','))  # Convert athlete's teams string to set
            return not selected_teams_set.isdisjoint(athlete_teams_set)  # Check for common elements

        athletes_df = athletes_df[athletes_df['teams'].apply(filter_by_teams)]

# Display the list of athletes in a tabular format
st.write("### Athlete List")

# Display each athlete's data in the columns
if not athletes_df.empty:
    for index, row in athletes_df.iterrows():
        # Main container for each athlete
        with st.container():
            # Combine athlete's name, contact, and teams information in one line
            st.write(f"**{row['name']}** - {row['contact']} - {row['teams'].replace(',', ' / ')}")

            # Create columns for the buttons, adjusting the width
            button_col1, button_col2, space_col3 = st.columns([2, 2, 8])
            
            with button_col1:
                if st.button("Edit", key=f"edit_{row['id']}"):
                    st.session_state.edit_id = row['id']
                    st.rerun()
            
            with button_col2:
                if st.button("Delete", key=f"delete_{row['id']}"):
                    delete_athlete(row['id'])
                    st.success(f"Athlete '{row['name']}' deleted successfully!")
                    st.rerun()

            with space_col3:
                pass
else:
    st.write("No athletes found. Please add athletes using the form above.")

st.markdown("---")

# Show the edit form if an athlete ID is set
if st.session_state.edit_id is not None:
    athlete_id = st.session_state.edit_id
    athlete_row = athletes_df[athletes_df['id'] == athlete_id]
    athlete_name = athlete_row['name'].values[0]
    athlete_contact = athlete_row['contact'].values[0]
    athlete_teams = athlete_row['teams'].values[0].split(',')  # Convert teams string back to list

    st.write("### Edit Athlete")
    with st.form(key='edit_form'):
        new_name = st.text_input('Edit Name', value=athlete_name)
        new_contact = st.text_input('Edit Contact', value=athlete_contact)
        new_teams = st.multiselect('Edit Teams', team_options, default=athlete_teams)
        if st.form_submit_button('Update'):
            teams_str = ",".join(new_teams)
            update_athlete(athlete_id, new_name.strip(), new_contact.strip(), teams_str)
            st.session_state.edit_id = None
            st.success(f"Athlete '{new_name}' updated successfully!")
            st.rerun()
