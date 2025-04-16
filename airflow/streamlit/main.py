from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import os
import polars as pl
from matplotlib.colors import ListedColormap
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, Sbopen, add_image)
fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                       'rubikmonoone/RubikMonoOne-Regular.ttf')
import streamlit as st

DEFAULT_ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')

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
    engine = create_engine(connection_string, future=True,  pool_pre_ping=True)
    print(f"Connecting to: postgresql+psycopg2://{sql_username}:{sql_password}@{sql_host}:{sql_port}/{sql_database}")

    if not all([sql_username, sql_password, sql_host, sql_port, sql_database]):
        st.error("One or more environment variables are missing.")
        st.text(f"User: {sql_username}, Host: {sql_host}, Port: {sql_port}, DB: {sql_database}")
        
    return engine

@st.cache_data
def load_data():
    
    try:
        engine = postgres_connection(DEFAULT_ENV_PATH)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM public.shots_data limit 5;"))
            # result = conn.execute(text("""SELECT * FROM players_stats p LIMIT 5"""))
            query = 'SELECT p.player_name, s.season, p.shots,' \
            's.x, s.y, s.xg, s.h_team, s.a_team' \
            '  FROM public.player_stats p ' \
            'left join public.shots_data s on s.player_id = p.id' \
            ' limit 10000;'
            # # conn.commit()
            # for row in result:
            #     st.write("tables:", row)
            df = pd.read_sql(query, con=conn.connection)

        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return None 



df = load_data()    

if df is not None and not df.empty:
    st.sidebar.header("Filters")
    season_filter = st.sidebar.selectbox("Season", sorted(df['season'].dropna().unique()))
    team_filter = st.sidebar.selectbox("Team", sorted(df['h_team'].dropna().unique()))
    player_filter = st.sidebar.selectbox(
    "Player", 
    sorted(df[df['h_team'] == team_filter]['player_name'].dropna().unique())
    )

    # --- Filter the DataFrame ---

    filtered_df = df[
        (df['season'] == season_filter) &
        # (df['league'] == league_filter) &
        ((df['h_team'] == team_filter) | (df['a_team'] == team_filter)) &
        (df['player_name'] == player_filter)
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

else:
    st.warning("No data loaded. Check your database connection or query.")