import streamlit as st
import sqlite3
import pandas as pd
import os

# Ensure the user is authenticated
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Por favor, faça login a partir da página inicial.")
    st.stop()

# Function to fetch all past matches from the database
def fetch_past_matches():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT * FROM matches WHERE date < DATE('now') ORDER BY date DESC", conn)
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os jogos anteriores: {e}")
        return pd.DataFrame()

# Function to fetch all teams from the database
def fetch_teams():
    try:
        with sqlite3.connect('athletes.db') as conn:
            return pd.read_sql_query("SELECT name FROM teams", conn)['name'].tolist()
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os escalões: {e}")
        return []

# Function to fetch carpool information for a specific match
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
                SELECT a.name, a.contact FROM athletes a
                JOIN assignments ass ON a.id = ass.athlete_id
                WHERE ass.car_id = ?
                ''', conn, params=(car_id,)
            )
    except sqlite3.Error as e:
        st.error(f"Ocorreu um erro ao buscar os atletas atribuídos: {e}")
        return pd.DataFrame()

# Display the logo on the top of the page
st.image("logo_aac.png", width=100)

# Fetch available teams for filtering
team_options = fetch_teams()

# Add filter to select teams
st.write("### Filtrar Jogos Anteriores por Escalão")
selected_teams = st.multiselect('Escolher Escalões', team_options)  # Default to all teams

# Fetch the current list of past matches
past_matches_df = fetch_past_matches()

# Apply team filter to the match list
if not past_matches_df.empty and selected_teams:
    past_matches_df = past_matches_df[past_matches_df['team'].isin(selected_teams)]

# Display the list of past matches
st.write("### Lista de Jogos Anteriores")

# Display match selection dropdown if matches are found
if not past_matches_df.empty:
    match_names = [f"{row['name']} ({row['team']}) - {pd.to_datetime(row['date']).strftime('%d/%m/%Y')}" for index, row in past_matches_df.iterrows()]
    selected_match = st.selectbox('Escolha um Jogo para ver Detalhes', ["Escolha um Jogo"] + match_names)

    # If a match is selected, fetch and display detailed carpooling information
    if selected_match != "Escolha um Jogo":
        match_index = match_names.index(selected_match)
        selected_match_id = past_matches_df.iloc[match_index]['id']

        # Fetch carpooling information for the selected match
        cars_df = fetch_cars_for_match(selected_match_id)

        if not cars_df.empty:
            st.write(f"### Informação para {selected_match}")
            for index, car in cars_df.iterrows():
                with st.container():
                    st.write(f"**Condutor:** {car['driver']} ({car['contact']}) - **Lugares Disponíveis:** {car['seats']}")

                    # Fetch assigned athletes for this car
                    assigned_athletes_df = fetch_assigned_athletes(car['id'])
                    if not assigned_athletes_df.empty:
                        st.write("Atletas:")
                        for _, athlete in assigned_athletes_df.iterrows():
                            st.write(f"- {athlete['name']} ({athlete['contact']})")

                    # Add a divider for each car
                    st.markdown("---")
        else:
            st.write("Nenhuma informação de carpool encontrada para este jogo.")
else:
    st.write("Nenhum jogo anterior encontrado para os escalões selecionados.")
    