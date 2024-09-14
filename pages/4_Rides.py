import streamlit as st
import pandas as pd
import sqlite3

# Set up database connection
conn = sqlite3.connect('ride_management.db', check_same_thread=False)
c = conn.cursor()

# Initialize tables if they don't exist
def init_db():
    # Matches table with added 'address' column
    c.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place TEXT,
            date TEXT,
            home_team TEXT,
            address TEXT
        )
    ''')
    # Ensure 'address' column exists
    c.execute("PRAGMA table_info(matches)")
    match_columns = [info[1] for info in c.fetchall()]
    if 'address' not in match_columns:
        c.execute("ALTER TABLE matches ADD COLUMN address TEXT")
        conn.commit()

    # Athletes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT
        )
    ''')

    # Cars table
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            available_places INTEGER
        )
    ''')

    # Match cars table (associate cars with matches)
    c.execute('''
        CREATE TABLE IF NOT EXISTS match_cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            car_id INTEGER,
            FOREIGN KEY(match_id) REFERENCES matches(id),
            FOREIGN KEY(car_id) REFERENCES cars(id)
        )
    ''')

    # Assignments table with 'match_id' and 'seat_number' columns
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            car_id INTEGER,
            seat_number INTEGER,
            athlete_id INTEGER,
            FOREIGN KEY(match_id) REFERENCES matches(id),
            FOREIGN KEY(car_id) REFERENCES cars(id),
            FOREIGN KEY(athlete_id) REFERENCES athletes(id)
        )
    ''')
    # Ensure 'match_id' and 'seat_number' columns exist
    c.execute("PRAGMA table_info(assignments)")
    assignment_columns = [info[1] for info in c.fetchall()]
    if 'match_id' not in assignment_columns:
        c.execute("ALTER TABLE assignments ADD COLUMN match_id INTEGER")
    if 'seat_number' not in assignment_columns:
        c.execute("ALTER TABLE assignments ADD COLUMN seat_number INTEGER")
    conn.commit()

init_db()

# Authentication function
def authenticate():
    st.sidebar.title("Login")
    password = st.sidebar.text_input("Password", type="password")
    if password == "aac":  # Default password set to "aac"
        return True
    elif password != "":
        st.sidebar.error("Incorrect password")
        return False

# Functions for database manipulation
def add_match(place, date, home_team, address):
    c.execute('''
        INSERT INTO matches (place, date, home_team, address) VALUES (?, ?, ?, ?)
    ''', (place, date, home_team, address))
    conn.commit()

def update_match(match_id, place, date, home_team, address):
    c.execute('''
        UPDATE matches SET place = ?, date = ?, home_team = ?, address = ? WHERE id = ?
    ''', (place, date, home_team, address, match_id))
    conn.commit()

def delete_match(match_id):
    c.execute('DELETE FROM matches WHERE id = ?', (match_id,))
    conn.commit()

def add_athlete(name, contact):
    c.execute('''
        INSERT INTO athletes (name, contact) VALUES (?, ?)
    ''', (name, contact))
    conn.commit()

def update_athlete(athlete_id, name, contact):
    c.execute('''
        UPDATE athletes SET name = ?, contact = ? WHERE id = ?
    ''', (name, contact, athlete_id))
    conn.commit()

def delete_athlete(athlete_id):
    c.execute('DELETE FROM athletes WHERE id = ?', (athlete_id,))
    conn.commit()

def add_car(name, contact, available_places):
    c.execute('''
        INSERT INTO cars (name, contact, available_places) VALUES (?, ?, ?)
    ''', (name, contact, available_places))
    conn.commit()
    return c.lastrowid  # Return the id of the inserted car

def add_car_to_match(match_id, car_id):
    c.execute('''
        INSERT INTO match_cars (match_id, car_id) VALUES (?, ?)
    ''', (match_id, car_id))
    conn.commit()

def remove_car_from_match(match_id, car_id):
    c.execute('DELETE FROM match_cars WHERE match_id = ? AND car_id = ?', (match_id, car_id))
    conn.commit()

def assign_athlete_to_car(match_id, car_id, seat_number, athlete_id):
    c.execute('''
        INSERT INTO assignments (match_id, car_id, seat_number, athlete_id) VALUES (?, ?, ?, ?)
    ''', (match_id, car_id, seat_number, athlete_id))
    conn.commit()

def remove_athlete_from_car(match_id, car_id, seat_number):
    c.execute('DELETE FROM assignments WHERE match_id = ? AND car_id = ? AND seat_number = ?', (match_id, car_id, seat_number))
    conn.commit()

def get_next_match():
    next_match_df = pd.read_sql_query("""
        SELECT * FROM matches WHERE date >= DATE('now') ORDER BY date LIMIT 1
    """, conn)
    return next_match_df

def get_match_cars(match_id):
    cars_df = pd.read_sql_query("""
        SELECT c.id, c.name, c.contact, c.available_places
        FROM match_cars mc
        JOIN cars c ON mc.car_id = c.id
        WHERE mc.match_id = ?
    """, conn, params=(match_id,))
    return cars_df

def get_car_assignments(match_id, car_id):
    assignments_df = pd.read_sql_query("""
        SELECT seat_number, a.name FROM assignments ass
        LEFT JOIN athletes a ON ass.athlete_id = a.id
        WHERE ass.match_id = ? AND ass.car_id = ?
    """, conn, params=(match_id, car_id))
    return assignments_df

def get_available_athletes(match_id):
    assigned_athletes_df = pd.read_sql_query("""
        SELECT athlete_id FROM assignments WHERE match_id = ?
    """, conn, params=(match_id,))
    assigned_athlete_ids = assigned_athletes_df['athlete_id'].tolist()
    if assigned_athlete_ids:
        placeholders = ','.join('?' * len(assigned_athlete_ids))
        athletes_df = pd.read_sql_query(f"""
            SELECT id, name FROM athletes
            WHERE id NOT IN ({placeholders})
        """, conn, params=assigned_athlete_ids)
    else:
        athletes_df = pd.read_sql_query("SELECT id, name FROM athletes", conn)
    return athletes_df

# Show the next match information with formatted display
def show_next_match():
    st.subheader("Next Match")
    next_match_df = get_next_match()
    if not next_match_df.empty:
        match = next_match_df.iloc[0]
        match_id = match['id']
        date_formatted = pd.to_datetime(match['date']).strftime('%d/%m/%Y')
        st.markdown(f"""
        <div style="background-color:#808080; padding:10px; border-radius: 10px;">
            <table style="width:100%; border-collapse: collapse; border: none;">
                <tr style="border: none;">
                    <td style="border: none;"><b>Date:</b> {date_formatted}</td>
                    <td style="border: none;"><b>Place:</b> {match['place']}</td>
                    <td style="border: none;">
                        <a href="{match['address'] if match['address'] else 'https://www.google.com/maps/search/?api=1&query=' + match['place']}" target="_blank">
                            <button style="background-color:#4CAF50; color:white; padding:5px 10px; border:none; border-radius:5px; cursor:pointer;">
                            See in Google Maps
                            </button>
                        </a>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        show_match_cars(match_id)
    else:
        st.write("No upcoming matches found.")

# Show cars and manage assignments for a match
def show_match_cars(match_id):
    st.subheader("Cars and Athletes for This Match")
    cars_df = get_match_cars(match_id)

    # Add Car to Match
    st.write("Add a Car to this Match")
    with st.form(key=f"add_car_to_match_form_{match_id}"):
        name = st.text_input("Car Name")
        contact = st.text_input("Contact")
        available_places = st.number_input("Available Places", min_value=1, step=1)
        submit_button = st.form_submit_button("Add Car to Match")
        if submit_button:
            # Add car to the cars table and get car_id
            car_id = add_car(name, contact, available_places)
            # Associate car with match
            add_car_to_match(match_id, car_id)
            st.success(f"Car {name} added to match.")
            # Refresh the app
            st.experimental_rerun()

    cars_df = get_match_cars(match_id)

    for _, car_row in cars_df.iterrows():
        car_id = car_row['id']
        st.markdown(f"""
        <div style="background-color:#808080; padding:10px; border-radius: 10px;">
            <b>Car:</b> {car_row['name']}<br>
            <b>Contact:</b> {car_row['contact']}<br>
            <b>Total Seats:</b> {car_row['available_places']}
        </div>
        """, unsafe_allow_html=True)

        # List assigned athletes with seat numbers
        assignments_df = get_car_assignments(match_id, car_id)
        seats = {}
        for i in range(1, car_row['available_places'] + 1):
            seats[i] = "Empty"

        for _, assignment in assignments_df.iterrows():
            seats[assignment['seat_number']] = assignment['name'] if assignment['name'] else "Empty"

        st.write("Seats:")
        cols = st.columns(len(seats))
        for idx, seat_num in enumerate(seats.keys()):
            with cols[idx]:
                if seats[seat_num] == "Empty":
                    available_athletes_df = get_available_athletes(match_id)
                    options = ["Empty"] + available_athletes_df['name'].tolist()
                    selected_athlete = st.selectbox(f"Seat {seat_num}", options, key=f"seat_{match_id}_{car_id}_{seat_num}")
                    if selected_athlete != "Empty":
                        athlete_id = available_athletes_df[available_athletes_df['name'] == selected_athlete]['id'].values[0]
                        assign_athlete_to_car(match_id, car_id, seat_num, athlete_id)
                        st.success(f"Athlete {selected_athlete} assigned to seat {seat_num}")
                        st.experimental_rerun()
                else:
                    st.write(f"Seat {seat_num}: {seats[seat_num]}")
                    if st.button("Remove", key=f"remove_{match_id}_{car_id}_{seat_num}"):
                        remove_athlete_from_car(match_id, car_id, seat_num)
                        st.success(f"Athlete removed from seat {seat_num}")
                        st.experimental_rerun()

        # Remove Car from Match
        if st.button(f"Remove {car_row['name']} from Match", key=f"remove_car_{match_id}_{car_id}"):
            # Confirmation prompt
            if st.confirm(f"Are you sure you want to remove {car_row['name']} from the match?"):
                remove_car_from_match(match_id, car_id)
                st.success(f"Car {car_row['name']} removed from match.")
                st.experimental_rerun()

        st.write("---")

# Manage Athletes
def manage_athletes():
    st.subheader("Manage Athletes")
    display_athletes()

def display_athletes():
    athletes_df = pd.read_sql_query("SELECT id, name, contact FROM athletes", conn)
    if not athletes_df.empty:
        athletes_df = athletes_df.reset_index(drop=True)
        athletes_df.index += 1  # Start index from 1 instead of 0
        for idx, row in athletes_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
            col1.write(row['name'])
            col2.write(row['contact'])
            # Edit Button
            if col3.button("Edit", key=f"edit_athlete_{row['id']}"):
                edit_athlete(row['id'])
                return
            # Delete Button
            if col4.button("Delete", key=f"delete_athlete_{row['id']}"):
                # Confirmation prompt
                if st.checkbox(f"Confirm delete athlete {row['name']}?", key=f"confirm_delete_{row['id']}"):
                    delete_athlete(row['id'])
                    st.success(f"Athlete {row['name']} deleted.")
                    st.experimental_rerun()
    else:
        st.write("No athletes available.")

    # Add spacing
    st.write("")
    st.write("")

    # Add Athlete
    st.write("Add New Athlete")
    with st.form(key="add_athlete_form"):
        name = st.text_input("Name (First and Last)")
        contact = st.text_input("Contact")
        submit_button = st.form_submit_button("Add Athlete")
        if submit_button:
            add_athlete(name, contact)
            st.success("Athlete added successfully!")
            st.experimental_rerun()

def edit_athlete(athlete_id):
    athlete = pd.read_sql_query("SELECT * FROM athletes WHERE id = ?", conn, params=(athlete_id,)).iloc[0]
    with st.form(key=f"edit_athlete_form_{athlete_id}"):
        name = st.text_input("Name (First and Last)", value=athlete['name'])
        contact = st.text_input("Contact", value=athlete['contact'])
        submit_button = st.form_submit_button("Update Athlete")
        if submit_button:
            update_athlete(athlete_id, name, contact)
            st.success("Athlete updated successfully!")
            st.experimental_rerun()

# View and Edit Matches
def view_matches():
    st.subheader("View and Manage Matches")

    # Add New Match
    st.write("Add New Match")
    with st.form(key="add_match_form"):
        place = st.text_input("Place")
        date = st.date_input("Date")
        home_team = st.text_input("Home Team")
        address = st.text_input("Google Maps Address")
        submit_button = st.form_submit_button("Add Match")
        if submit_button:
            add_match(place, date.strftime('%Y-%m-%d'), home_team, address)
            st.success("Match added successfully!")
            st.experimental_rerun()

    matches_df = pd.read_sql_query("SELECT id, date, place, home_team, address FROM matches ORDER BY date", conn)
    if not matches_df.empty:
        matches_df['Date'] = pd.to_datetime(matches_df['date']).dt.strftime('%d/%m/%Y')
        matches_df['Google Maps Link'] = matches_df.apply(lambda x: x['address'] if x['address'] else f"https://www.google.com/maps/search/?api=1&query={x['place']}", axis=1)
        display_df = matches_df[['id', 'Date', 'place', 'home_team', 'Google Maps Link']]
        display_df.columns = ['id', 'Date', 'Place', 'Team', 'Google Maps Link']
        display_df = display_df.reset_index(drop=True)

        for idx, row in display_df.iterrows():
            st.markdown(f"""
            <div style="background-color:#808080; padding:10px; border-radius: 10px;">
                <b>Date:</b> {row['Date']}<br>
                <b>Place:</b> {row['Place']}<br>
                <b>Team:</b> {row['Team']}<br>
                <a href="{row['Google Maps Link']}" target="_blank">
                    <button style="background-color:#4CAF50; color:white; padding:5px 10px; border:none; border-radius:5px; cursor:pointer;">
                    See in Google Maps
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
            match_id = row['id']
            edit_match_button = st.button("Edit Match", key=f"edit_match_{match_id}")
            if edit_match_button:
                edit_match(match_id)
                return
            st.write("---")
    else:
        st.write("No matches available.")

def edit_match(match_id):
    match = pd.read_sql_query("SELECT * FROM matches WHERE id = ?", conn, params=(match_id,)).iloc[0]
    with st.form(key=f"edit_match_form_{match_id}"):
        place = st.text_input("Place", value=match['place'])
        date = st.date_input("Date", value=pd.to_datetime(match['date']))
        home_team = st.text_input("Home Team", value=match['home_team'])
        address = st.text_input("Google Maps Address", value=match['address'] if match['address'] else '')
        submit_button = st.form_submit_button("Update Match")
        if submit_button:
            update_match(match_id, place, date.strftime('%Y-%m-%d'), home_team, address)
            st.success("Match updated successfully!")
            st.experimental_rerun()

    delete_match_button = st.button("Delete Match", key=f"delete_match_{match_id}")
    if delete_match_button:
        st.warning(f"Are you sure you want to delete the match on {match['date']} at {match['place']}?")
        confirm_delete = st.button("Yes, Delete Match", key=f"confirm_delete_match_{match_id}")
        cancel_delete = st.button("Cancel", key=f"cancel_delete_match_{match_id}")
        if confirm_delete:
            delete_match(match_id)
            st.success("Match deleted.")
            st.experimental_rerun()
        elif cancel_delete:
            st.info("Delete action cancelled.")

# Main function to display the home screen and menu options
def main():
    st.image("logo_aac.png", width=100)  # Display logo

    if authenticate():
        st.title("Andeboleias")

        menu = st.sidebar.selectbox("Menu", [
            "Next Match", "Manage Athletes", "View Matches"
        ])

        if menu == "Next Match":
            show_next_match()

        elif menu == "Manage Athletes":
            manage_athletes()

        elif menu == "View Matches":
            view_matches()

if __name__ == "__main__":
        main()
