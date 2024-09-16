import streamlit as st
import sqlite3
import pandas as pd
import os

# Database initialization
def init_db():
    try:
        if not os.path.exists('athletes.db'):
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

                # Create the cars table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        match_id INTEGER,
                        driver TEXT,
                        contact TEXT,
                        seats INTEGER,
                        FOREIGN KEY(match_id) REFERENCES matches(id)
                    )
                ''')

                # Create the athletes table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS athletes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        contact TEXT
                    )
                ''')

                # Create the assignments table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS assignments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        match_id INTEGER,
                        car_id INTEGER,
                        athlete_id INTEGER,
                        FOREIGN KEY(match_id) REFERENCES matches(id),
                        FOREIGN KEY(car_id) REFERENCES cars(id),
                        FOREIGN KEY(athlete_id) REFERENCES athletes(id)
                    )
                ''')
                conn.commit()
    except sqlite3.Error as e:
        st.error(f"An error occurred while initializing the database: {e}")

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

# Custom CSS for mobile-friendly adjustments
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

# Function to add a car to the database
def add_car(match_id, driver, contact, seats):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO cars (match_id, driver, contact, seats) 
                VALUES (?, ?, ?, ?)
            ''', (match_id, driver, contact, seats))
            conn.commit()
            st.success(f"Car added successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while adding a car: {e}")


# Display the logo on the top of the page
st.image("logo_aac.png", width=100)


# Function to update car information in the database
def update_car(car_id, driver, contact, seats):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE cars 
                SET driver = ?, contact = ?, seats = ? 
                WHERE id = ?
            ''', (driver, contact, seats, car_id))
            conn.commit()
            st.success(f"Car updated successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while updating the car: {e}")

# Function to delete a car from the database
def delete_car(car_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            # Remove all assignments related to this car
            c.execute('DELETE FROM assignments WHERE car_id = ?', (car_id,))
            # Delete the car
            c.execute('DELETE FROM cars WHERE id = ?', (car_id,))
            conn.commit()
            st.success(f"Car deleted successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while deleting the car: {e}")

# Function to assign an athlete to a car
def assign_athlete_to_car(match_id, car_id, athlete_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            # Remove athlete from any other car in the match
            c.execute('DELETE FROM assignments WHERE match_id = ? AND athlete_id = ?', (match_id, athlete_id))
            # Insert new assignment
            c.execute('''
                INSERT INTO assignments (match_id, car_id, athlete_id) 
                VALUES (?, ?, ?)
            ''', (match_id, car_id, athlete_id))
            # Decrease seats by 1
            c.execute('UPDATE cars SET seats = seats - 1 WHERE id = ?', (car_id,))
            conn.commit()
            st.success(f"Athlete assigned successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while assigning the athlete: {e}")

# Function to remove an athlete from a car
def remove_athlete_from_car(car_id, athlete_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            # Remove athlete assignment
            c.execute('DELETE FROM assignments WHERE car_id = ? AND athlete_id = ?', (car_id, athlete_id))
            # Increase seats by 1
            c.execute('UPDATE cars SET seats = seats + 1 WHERE id = ?', (car_id,))
            conn.commit()
            st.success(f"Athlete removed successfully!")
    except sqlite3.Error as e:
        st.error(f"An error occurred while removing the athlete: {e}")

# Function to fetch the next match (nearest date in the future)
def fetch_next_match():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                "SELECT * FROM matches WHERE date >= DATE('now') ORDER BY date LIMIT 1", conn
            )
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching the next match: {e}")
        return pd.DataFrame()

# Function to fetch cars for a specific match
def fetch_cars_for_match(match_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                "SELECT * FROM cars WHERE match_id = ?", conn, params=(match_id,)
            )
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching cars: {e}")
        return pd.DataFrame()

# Function to fetch assigned athletes for a specific car
def fetch_assigned_athletes(car_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                '''
                SELECT a.id, a.name, a.contact FROM athletes a
                JOIN assignments ass ON a.id = ass.athlete_id
                WHERE ass.car_id = ?
                ''', conn, params=(car_id,)
            )
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching assigned athletes: {e}")
        return pd.DataFrame()

# Function to fetch available athletes for the match
def fetch_available_athletes(match_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                '''
                SELECT * FROM athletes
                WHERE id NOT IN (
                    SELECT athlete_id FROM assignments WHERE match_id = ?
                )
                ''', conn, params=(match_id,)
            )
    except sqlite3.Error as e:
        st.error(f"An error occurred while fetching athletes: {e}")
        return pd.DataFrame()

# Initialize the database
init_db()

# State to hold the currently edited car ID
if 'edit_car_id' not in st.session_state:
    st.session_state.edit_car_id = None

# Display the next match
st.title("Next Match")
next_match_df = fetch_next_match()

if not next_match_df.empty:
    # Extract match information
    match_id = next_match_df['id'].values[0]
    match_name = next_match_df['name'].values[0]
    match_date = pd.to_datetime(next_match_df['date'].iloc[0]).strftime('%d/%m/%Y')
    google_maps_link = next_match_df['google_maps_link'].values[0]

    # Display match information
    st.write(f"### {match_name}")
    st.write(f"**Date:** {match_date}")
    st.markdown(f"[Open in Google Maps]({google_maps_link})", unsafe_allow_html=True)

    # Divider above the form
    st.markdown("---")
    
    # Add or edit car form
    st.write("### Add Car")
    with st.form(key='car_form'):
        if st.session_state.edit_car_id is None:
            driver_name = st.text_input('Driver')
            contact_info = st.text_input('Contact')
            seats_available = st.number_input('Available Seats', min_value=1, step=1)
            submit_label = 'Add Car'
        else:
            # Fetch car details for editing
            car_to_edit = fetch_cars_for_match(match_id)[fetch_cars_for_match(match_id)['id'] == st.session_state.edit_car_id]
            driver_name = st.text_input('Driver', value=car_to_edit['driver'].values[0])
            contact_info = st.text_input('Contact', value=car_to_edit['contact'].values[0])
            seats_available = st.number_input('Available Seats', min_value=1, step=1, value=car_to_edit['seats'].values[0])
            submit_label = 'Update Car'
        
        if st.form_submit_button(submit_label):
            if st.session_state.edit_car_id is None:
                add_car(match_id, driver_name.strip(), contact_info.strip(), seats_available)
            else:
                update_car(st.session_state.edit_car_id, driver_name.strip(), contact_info.strip(), seats_available)
                st.session_state.edit_car_id = None
            st.rerun()

    # Divider above available cars
    st.markdown("---")
    
    # Fetch and display cars for this match
    st.write("### Available Cars")
    cars_df = fetch_cars_for_match(match_id)

    if not cars_df.empty:
        for index, car in cars_df.iterrows():
            with st.container():
                # Combine driver and contact information in one line
                st.write(f"**Driver:** {car['driver']} ({car['contact']})")
                st.write(f"**Available Seats:** {car['seats']}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Edit", key=f"edit_car_{car['id']}"):
                        st.session_state.edit_car_id = car['id']
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"delete_car_{car['id']}"):
                        delete_car(car['id'])
                        st.rerun()

                # Display assigned athletes
                assigned_athletes_df = fetch_assigned_athletes(car['id'])
                if not assigned_athletes_df.empty:
                    st.write(f"**Assigned Athletes for {car['driver']}**")
                    for athlete_index, athlete in assigned_athletes_df.iterrows():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"{athlete['name']} ({athlete['contact']})")
                        with col2:
                            if st.button("Remove", key=f"remove_athlete_{athlete['id']}_{car['id']}"):
                                remove_athlete_from_car(car['id'], athlete['id'])
                                st.rerun()

                st.markdown("---")

    # Athlete assignment form
    st.write("### Assign Athlete to a Car")
    available_athletes_df = fetch_available_athletes(match_id)
    if not available_athletes_df.empty and not cars_df.empty:
        # Filter out cars with 0 seats
        available_cars_df = cars_df[cars_df['seats'] > 0]
        if not available_cars_df.empty:
            with st.form(key='assign_athlete_form'):
                selected_athlete_id = st.selectbox('Select Athlete', available_athletes_df['id'], format_func=lambda x: available_athletes_df[available_athletes_df['id'] == x]['name'].values[0])
                selected_car_id = st.selectbox('Select Car', available_cars_df['id'], format_func=lambda x: available_cars_df[available_cars_df['id'] == x]['driver'].values[0])
                if st.form_submit_button('Assign'):
                    assign_athlete_to_car(match_id, selected_car_id, selected_athlete_id)
                    st.rerun()
else:
    st.write("No upcoming matches found.")
