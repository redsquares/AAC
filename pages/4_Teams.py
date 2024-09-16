import streamlit as st
import sqlite3
import pandas as pd

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the Home page.")
    st.stop()

# Initialize session state variables
if 'edit_team_id' not in st.session_state:
    st.session_state.edit_team_id = None

# Function to fetch all teams from the database
def fetch_teams():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM teams", conn)
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching teams: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Functions to add, update, and delete teams
def add_team(name):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO teams (name) VALUES (?)', (name,))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding the team: {e}")

def update_team(team_id, new_name):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE teams SET name = ? WHERE id = ?', (new_name, team_id))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while updating the team: {e}")

def delete_team(team_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM teams WHERE id = ?', (team_id,))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the team: {e}")

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Show the form to add a new team at the top
st.write("### Add New Team")
with st.form(key='add_team_form'):
    new_team_name = st.text_input('Team Name')
    if st.form_submit_button('Add'):
        if new_team_name.strip():
            add_team(new_team_name.strip())
            st.success(f"Team '{new_team_name}' added successfully!")
            st.rerun()

# Fetch the current list of teams
teams_df = fetch_teams()

# Display the list of teams in a tabular format
st.write("### Team List")

# Display each team's data in the columns
if not teams_df.empty:
    for index, row in teams_df.iterrows():
        # Main container for each team
        with st.container():
            # Display team name
            st.write(f"**{row['name']}**")

            # Create columns for the buttons, adjusting the width
            button_col1, button_col2, space_col3 = st.columns([2, 2, 8])
            
            with button_col1:
                if st.button("Edit", key=f"edit_team_{row['id']}"):
                    st.session_state.edit_team_id = row['id']
                    st.rerun()
            
            with button_col2:
                if st.button("Delete", key=f"delete_team_{row['id']}"):
                    delete_team(row['id'])
                    st.success(f"Team '{row['name']}' deleted successfully!")
                    st.rerun()

            with space_col3:
                pass
else:
    st.write("No teams found. Please add teams using the form above.")

st.markdown("---")

# Show the edit form if a team ID is set
if st.session_state.edit_team_id is not None:
    team_id = st.session_state.edit_team_id
    team_row = teams_df[teams_df['id'] == team_id]
    team_name = team_row['name'].values[0]

    st.write("### Edit Team")
    with st.form(key='edit_team_form'):
        new_name = st.text_input('Edit Team Name', value=team_name)
        if st.form_submit_button('Update'):
            update_team(team_id, new_name.strip())
            st.session_state.edit_team_id = None
            st.success(f"Team '{new_name}' updated successfully!")
            st.rerun()
