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
                        google_maps_link TEXT,
                        team TEXT
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
                        contact TEXT,
                        teams TEXT
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

                # Create the teams table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS teams (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE
                    )
                ''')
                
                conn.commit()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao inicializar a base de dados: {e}")

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Por favor, faça login a partir da página inicial.")
    st.stop()

# Custom CSS for mobile-friendly adjustments
st.markdown(
    """
    <style>
    /* Change the color of titles */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: green;
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
            st.success(f"Carro adicionado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao adicionar o carro: {e}")

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
            st.success(f"Carro atualizado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao atualizar o carro: {e}")

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
            st.success(f"Carro apagado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao apagar o carro: {e}")

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
            st.success(f"Atleta atribuído com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao atribuir o atleta: {e}")

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
            st.success(f"Atleta removido com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao remover o atleta: {e}")

# Function to fetch the next match for a specific team
def fetch_next_match(team):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                "SELECT * FROM matches WHERE team = ? AND date >= DATE('now') ORDER BY date LIMIT 1", 
                conn, params=(team,)
            )
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar o próximo jogo: {e}")
        return pd.DataFrame()

# Function to fetch cars for a specific match
def fetch_cars_for_match(match_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                "SELECT * FROM cars WHERE match_id = ?", conn, params=(match_id,)
            )
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os carros: {e}")
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
        st.error(f"Ocorreu um erro ao buscar os atletas atribuídos: {e}")
        return pd.DataFrame()

# Function to fetch available athletes for the match, filtered by team
def fetch_available_athletes(match_id, team):
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query(
                '''
                SELECT * FROM athletes
                WHERE id NOT IN (
                    SELECT athlete_id FROM assignments WHERE match_id = ?
                ) AND teams LIKE ?
                ''', conn, params=(match_id, f'%{team}%')
            )
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os atletas: {e}")
        return pd.DataFrame()

# Initialize the database
init_db()

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Fetch available teams for the selectbox
def fetch_teams():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT name FROM teams", conn)['name'].tolist()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar as equipas: {e}")
        return []

# Fetch the list of teams
teams = fetch_teams()

# State to hold the currently edited car ID
if 'edit_car_id' not in st.session_state:
    st.session_state.edit_car_id = None

# Team Selector for Filtering Matches
selected_team = st.selectbox('Escolher Escalão', teams)

# Display the next match for the selected team
st.title(f"Próximo jogo dos {selected_team}")
next_match_df = fetch_next_match(selected_team)

if not next_match_df.empty:
    # Extract match information
    match_id = next_match_df['id'].values[0]
    match_name = next_match_df['name'].values[0]
    match_date = pd.to_datetime(next_match_df['date'].iloc[0]).strftime('%d/%m/%Y')
    google_maps_link = next_match_df['google_maps_link'].values[0]

    # Display match information
    st.write(f"### {match_name}")
    st.write(f"**Data:** {match_date}")
    st.markdown(f"[Abrir no Google Maps]({google_maps_link})", unsafe_allow_html=True)

    # Divider above the form
    st.markdown("---")
    
    # Add or edit car form
    st.write("### Adicionar Carro")
    with st.form(key='car_form'):
        if st.session_state.edit_car_id is None:
            driver_name = st.text_input('Condutor')
            contact_info = st.text_input('Contacto')
            seats_available = st.number_input('Lugares Disponíveis', min_value=1, step=1)
            submit_label = 'Adicionar'
        else:
            # Fetch car details for editing
            car_to_edit = fetch_cars_for_match(match_id)[fetch_cars_for_match(match_id)['id'] == st.session_state.edit_car_id]
            driver_name = st.text_input('Condutor', value=car_to_edit['driver'].values[0])
            contact_info = st.text_input('Contacto', value=car_to_edit['contact'].values[0])
            seats_available = st.number_input('Lugares Disponíveis', min_value=1, step=1, value=car_to_edit['seats'].values[0])
            submit_label = 'Atualizar'
        
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
    st.write("### Carros Disponíveis")
    cars_df = fetch_cars_for_match(match_id)

    if not cars_df.empty:
        for index, car in cars_df.iterrows():
            with st.container():
                # Combine driver and contact information in one line
                st.write(f"**Condutor:** {car['driver']} ({car['contact']})")
                st.write(f"**Lugares Disponíveis:** {car['seats']}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Editar", key=f"edit_car_{car['id']}"):
                        st.session_state.edit_car_id = car['id']
                        st.rerun()
                with col2:
                    if st.button("Apagar", key=f"delete_car_{car['id']}"):
                        delete_car(car['id'])
                        st.rerun()

                # Display assigned athletes
                assigned_athletes_df = fetch_assigned_athletes(car['id'])
                if not assigned_athletes_df.empty:
                    st.write(f"**Atletas no carro de {car['driver']}**")
                    for athlete_index, athlete in assigned_athletes_df.iterrows():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"{athlete['name']} ({athlete['contact']})")
                        with col2:
                            if st.button("Remover", key=f"remove_athlete_{athlete['id']}_{car['id']}"):
                                remove_athlete_from_car(car['id'], athlete['id'])
                                st.rerun()

                st.markdown("---")

    # Athlete assignment form
    st.write("### Escolher Carro para o Atleta")
    available_athletes_df = fetch_available_athletes(match_id, selected_team)  # Pass the selected team for filtering

    # Check if there are available athletes and cars
    if not available_athletes_df.empty and not cars_df.empty:
        # Filter out cars with 0 seats
        available_cars_df = cars_df[cars_df['seats'] > 0]
        if not available_cars_df.empty:
            with st.form(key='assign_athlete_form'):
                selected_athlete_id = st.selectbox('Escolher Atleta', available_athletes_df['id'], format_func=lambda x: available_athletes_df[available_athletes_df['id'] == x]['name'].values[0])
                selected_car_id = st.selectbox('Escolher Carro', available_cars_df['id'], format_func=lambda x: available_cars_df[available_cars_df['id'] == x]['driver'].values[0])
                if st.form_submit_button('Confirmar'):
                    assign_athlete_to_car(match_id, selected_car_id, selected_athlete_id)
                    st.rerun()

    # Show message if there are no more athletes to assign
    if available_athletes_df.empty:
        st.write("Não existem mais atletas para o escalão deste jogo.")
else:
    st.write(f"Não foram encontrados próximos jogos dos {selected_team}.")
