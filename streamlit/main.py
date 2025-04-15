from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import os
from matplotlib.colors import ListedColormap
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen, add_image)
fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                       'rubikmonoone/RubikMonoOne-Regular.ttf')
import streamlit as st

DEFAULT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../../.env')

def postgres_credentials(file_path=DEFAULT_ENV_PATH):
    load_dotenv(file_path)
    sql_username = os.getenv("sql_username")
    sql_password = os.getenv("sql_password")
    sql_host = os.getenv("sql_host")
    sql_port = os.getenv("sql_port")
    sql_database = os.getenv("sql_database")

    return sql_username, sql_password, sql_host, sql_port, sql_database


def postgres_connection(file_path=DEFAULT_ENV_PATH):
    sql_username, sql_password, sql_host, sql_port, sql_database = postgres_credentials(file_path)
    connection_string = f'postgresql+psycopg2://{sql_username}:{sql_password}@{sql_host}:{sql_port}/{sql_database}'
    engine = create_engine(connection_string)

    return engine

@st.cache_data
def load_data():
    engine = postgres_connection()
    query = text("SELECT * FROM players_stats p\
                 left join shots_data s on s.player_id = p.id;")  # Or a refined SELECT query
    df = pd.read_sql(query, engine)
    return df


df = load_data()


st.sidebar.header("Filters")
season_filter = st.sidebar.selectbox("Season", sorted(df['season'].unique()), index=0)
league_filter = st.sidebar.selectbox("League", sorted(df['league'].unique()), index=0)
team_filter = st.sidebar.selectbox("Team", sorted(df[df['league'] == league_filter]['h_team'].unique()), index=0)
player_filter = st.sidebar.selectbox("Player", sorted(df[df['h_team'] == team_filter]['player'].unique()), index=0)

# --- Filter the DataFrame ---

filtered_df = df[
    (df['season'] == season_filter) &
    (df['league'] == league_filter) &
    ((df['h_team'] == team_filter) | (df['a_team'] == team_filter)) &
    (df['player'] == player_filter)
]   

pitch = VerticalPitch(
    pad_bottom=1,
    half=True,
    goal_type='line',
    goal_alpha=0.8,
    pitch_type='custom',
    pitch_length=99.5,
    pitch_width=100
)
fig, ax = pitch.draw(figsize=(15, 15))
fig.set_facecolor('#22312b')
ax.patch.set_facecolor('#22312b')

# Scatter plot for shots
sc = pitch.scatter(
    filtered_df['x'].astype(float) * 100,
    filtered_df['y'].astype(float) * 100,
    s=filtered_df['xg'].astype(float) * 720,
    c='#6CABDD',
    edgecolors='#606060',
    marker='o',
    ax=ax
)

ax.text(
    x=50,
    y=65,
    s=f'{player_filter} ShotMap\nfor {team_filter} in {season_filter}',
    size=30,
    color='white',
    va='center',
    ha='center'
)

# Display the figure
st.pyplot(fig)