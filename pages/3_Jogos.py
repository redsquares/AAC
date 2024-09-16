import streamlit as st
import sqlite3
import pandas as pd
import os

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Por favor, faça login a partir da página inicial.")
    st.stop()

# Initialize session state variables
if 'edit_match_id' not in st.session_state:
    st.session_state.edit_match_id = None

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
                        team TEXT,
                        google_maps_link TEXT
                    )
                ''')
                # Create the teams table if it doesn't exist
                c.execute('''
                    CREATE TABLE IF NOT EXISTS teams (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT
                    )
                ''')
                conn.commit()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao inicializar a base de dados: {e}")

# Function to fetch all matches from the database
def fetch_matches():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM matches", conn)
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os jogos: {e}")
        return pd.DataFrame()

# Function to fetch all teams from the database
def fetch_teams():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT name FROM teams", conn)['name'].tolist()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os escalões: {e}")
        return []

# Functions to add, update, and delete matches
def add_match(name, date, team, google_maps_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO matches (name, date, team, google_maps_link) VALUES (?, ?, ?, ?)', 
                      (name, date, team, google_maps_link))
            conn.commit()
            st.success(f"Jogo '{name}' adicionado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao adicionar um jogo: {e}")

def update_match(match_id, new_name, new_date, new_team, new_link):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('UPDATE matches SET name = ?, date = ?, team = ?, google_maps_link = ? WHERE id = ?', 
                      (new_name, new_date, new_team, new_link, match_id))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao atualizar o jogo: {e}")

def delete_match(match_id):
    try:
        with sqlite3.connect('athletes.db') as conn:
            c = conn.cursor()
            c.execute('DELETE FROM matches WHERE id = ?', (match_id,))
            conn.commit()
            st.success(f"Jogo apagado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao apagar o jogo: {e}")

# Initialize the database
init_db()

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Show the form to add a new match
st.write("### Adicionar Jogo")
with st.form(key='add_match_form'):
    new_match_name = st.text_input('Local')
    new_match_date = st.date_input('Data do Jogo')
    new_team = st.selectbox('Escolher Escalão', ["Escolher um escalão..."] + fetch_teams())
    new_google_maps_link = st.text_input('Link do Google Maps')

    if st.form_submit_button('Confirmar'):
        # Check if the match name and team are provided
        if new_match_name.strip() and new_team != "Escolher um escalão...":
            add_match(new_match_name.strip(), new_match_date.strftime('%Y-%m-%d'), new_team, new_google_maps_link.strip())
            st.rerun()
        else:
            if not new_match_name.strip():
                st.error("O local do jogo é obrigatório.")
            if new_team == "Escolher um escalão...":
                st.error("Por favor, selecione um escalão válido.")

# Add filter to select teams
st.write("### Filtrar Jogos por Escalão")
selected_teams = st.multiselect('Escolher Escalões', fetch_teams())

# Fetch the current list of matches
matches_df = fetch_matches()

# Apply team filter to the match list if any teams are selected
if not matches_df.empty and selected_teams:
    matches_df = matches_df[matches_df['team'].isin(selected_teams)]

# Display the list of matches
st.write("### Lista de Jogos")

# Display each match's data
if not matches_df.empty:
    for index, row in matches_df.iterrows():
        with st.container():
            # Combine name, date, team, and link into one line
            match_line = f"**{row['name']}** ({row['team']}) - {pd.to_datetime(row['date']).strftime('%d/%m/%Y')}"
            if row['google_maps_link']:
                match_line += f" - [Abrir Google Maps]({row['google_maps_link']})"
            st.markdown(match_line, unsafe_allow_html=True)

            # Create columns for Edit and Delete buttons
            button_col1, button_col2 = st.columns([1, 1])
            
            with button_col1:
                if st.button("Editar", key=f"edit_{row['id']}"):
                    st.session_state.edit_match_id = row['id']
                    st.rerun()
            
            with button_col2:
                if st.button("Apagar", key=f"delete_{row['id']}"):
                    delete_match(row['id'])
                    st.rerun()

            # Add a small divider line for spacing between matches
            st.markdown("---")
else:
    st.write("Nenhum jogo encontrado. Por favor, adicione jogos usando o formulário acima.")

# Show the edit form if a match ID is set
if st.session_state.edit_match_id is not None:
    match_id = st.session_state.edit_match_id
    match_row = matches_df[matches_df['id'] == match_id]
    match_name = match_row['name'].values[0]
    match_date = pd.to_datetime(match_row['date']).values[0]
    match_team = match_row['team'].values[0]
    match_link = match_row['google_maps_link'].values[0]

    st.write("### Editar Jogo")
    with st.form(key='edit_match_form'):
        new_name = st.text_input('Editar Local', value=match_name)
        new_date = st.date_input('Editar Data', value=pd.to_datetime(match_date))
        new_team = st.selectbox('Editar Escalão', fetch_teams(), index=fetch_teams().index(match_team))
        new_link = st.text_input('Editar Link para Google Maps', value=match_link)
        if st.form_submit_button('Confirmar'):
            update_match(match_id, new_name.strip(), new_date.strftime('%Y-%m-%d'), new_team, new_link.strip())
            st.session_state.edit_match_id = None
            st.rerun()
