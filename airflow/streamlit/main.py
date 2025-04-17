from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import os
import polars as pl
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
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
            # result = conn.execute(text("SELECT * FROM public.shots_data limit 5;"))
            query = '''
                    SELECT 
                        p.player_name, s.season, p.shots, s.x, s.y, s.xg, s.result,
                        s.situation, s.shottype, s.h_team, s.a_team
                    FROM public.player_stats p
                    LEFT JOIN public.shots_data s ON s.player_id = p.id
                    LIMIT 10000;
                    '''
            df = pd.read_sql(query, con=conn.connection)

        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return None 



df = load_data()   

if df is None or df.empty:
    st.warning("No data loaded. Check your database connection or query.")
    st.stop()

# st.write(df.head())
st.sidebar.header("🎯 Shot Map Filters")
player_search = st.sidebar.text_input("🔍 Search Player")
player_options = sorted(df[df['player_name'].str.contains(player_search, case=False, na=False)]['player_name'].unique()) if player_search else sorted(df['player_name'].dropna().unique())
player_filter = st.sidebar.selectbox("Select Player", player_options)
player_df = df[df['player_name'] == player_filter]

# Sidebar: Optional Shot Types
# all_shot_types = sorted(player_df['shottype'].dropna().unique())
# selected_shot_types = st.sidebar.multiselect("Shot Types (optional)", options=all_shot_types, default=all_shot_types)


all_result_types = sorted(player_df['result'].dropna().unique())
selected_result_types = st.sidebar.multiselect("Result Types (optional)", options=all_result_types, default=all_result_types)

# Sidebar: Optional Team filter (home/away)
opponent_teams = sorted(pd.concat([player_df['h_team'], player_df['a_team']]).dropna().unique())
opponent_filter = st.sidebar.selectbox("Opponent Team (optional)", ["All"] + opponent_teams)

# Sidebar: Optional Season filter
seasons = sorted(player_df['season'].dropna().unique())
season_filter = st.sidebar.selectbox("Season (optional)", ["All"] + seasons)

# Apply filters
filtered_df = player_df.copy()
# filtered_df = filtered_df[filtered_df['shottype'].isin(selected_shot_types)]
filtered_df = filtered_df[filtered_df['result'].isin(selected_result_types)]


if opponent_filter != "All":
    filtered_df = filtered_df[(filtered_df['h_team'] == opponent_filter) | (filtered_df['a_team'] == opponent_filter)]

if season_filter != "All":
    filtered_df = filtered_df[filtered_df['season'] == season_filter]

# Result colors
result_colors = {
    'Goal': '#2ca02c',
    'Missed': '#d62728',
    'Saved': '#1f77b4',
    'Blocked': '#ff7f0e',
    'Post': '#9467bd',
    'Off T': '#8c564b',
    'Other': '#7f7f7f'
}

# Plot


pitch = VerticalPitch(pad_bottom = 1, half = True, goal_type = 'box', goal_alpha = 0.8,
                      pitch_type = 'custom', pitch_length = 99.5, pitch_width = 100)
fig, ax = pitch.draw(figsize=(15, 10))
fig.set_facecolor('#22312b')
ax.patch.set_facecolor('#22312b')

markers = ['o', 's', '^', 'D', 'P', '*', 'X', 'v', '<', '>']
shot_types_unique = sorted(filtered_df['result'].dropna().unique())
marker_map = {shot: markers[i % len(markers)] for i, shot in enumerate(shot_types_unique)}


color_palette = plt.cm.tab10.colors 
shot_type_colors = {shot: color_palette[i % len(color_palette)] for i, shot in enumerate(shot_types_unique)}

legend_handles = []
legend_labels = []

# Plot shots by shot type
for shot_type in shot_types_unique:
    sub_df = filtered_df[filtered_df['result'] == shot_type]
    
    # For each shot type, plot with separate markers for goals vs. non-goals
    # for result_type in sub_df['result'].dropna().unique():
    # result_df = sub_df[(sub_df['result'] == result_type) & (sub_df['shottype']== shot_type)]
    # marker = marker_map[shot_type]
    # color = result_colors.get(result_type, '#7f7f7f')


        
    # Skip if there are no shots of this type and result
    # if result_df.empty:
    #     continue
    
    # Use shot type for marker and color, result for edgecolor
    # marker = marker_map[shot_type]
    face_color = shot_type_colors[shot_type]
    # edge_color = result_colors.get(result_type, '#303030')

    
    # Create label: Shot Type (Result)
    # label = f"{result_type}"
    
    # Plot the shots
    scatter = pitch.scatter(
        sub_df['x'].astype(float) * 100,
        sub_df['y'].astype(float) * 100,
        s=sub_df['xg'].astype(float) * 720,
        c=face_color,
        edgecolors='#303030',
        linewidths=2,
        marker='o',
        ax=ax,
        alpha=0.7
    )
    


# Plot title
title_text = f"{player_filter} Shot Map"
subtitle_parts = []
if season_filter != "All":
    subtitle_parts.append(f"Season: {season_filter}")
if opponent_filter != "All":
    subtitle_parts.append(f"vs {opponent_filter}")
subtitle = " | ".join(subtitle_parts)

ax.text(
    x=50,
    y=105,
    s=f"{title_text}\n{subtitle}" if subtitle else title_text,
    size=25,
    color='white',
    ha='center'
)
shot_type_handles = []
for shot_type in shot_types_unique:
    color = shot_type_colors[shot_type]
    shot_handle = mlines.Line2D([], [], color=color, marker='o', 
                              markersize=10, label=shot_type, linestyle='None')
    shot_type_handles.append(shot_handle)

# Create custom legend for xG sizes
xg_sizes = [0.1, 0.3, 0.5, 0.7, 0.9]
xg_handles = []
for xg in xg_sizes:
    size = xg * 720 / 5  # Divide by a factor to make the legend less overwhelming
    xg_handle = mlines.Line2D([], [], color='white', marker='o', 
                            markersize=size**0.5, label=f'xG: {xg}', linestyle='None')
    xg_handles.append(xg_handle)

# Position legends
shot_legend = ax.legend(handles=shot_type_handles, loc='upper right', 
                       title='Shot Types', frameon=False, fontsize=10, 
                       bbox_to_anchor=(1.1, 1.05),
                       labelcolor='white', title_fontsize=12)
ax.add_artist(shot_legend)

# Add xG legend below the shot type legend
xg_legend = ax.legend(handles=xg_handles, loc='upper center', 
                     bbox_to_anchor=(1.05, 0.8), frameon=False, fontsize=10, 
                     labelcolor='white', title='Expected Goals (xG)', title_fontsize=12)

# Add explanation text
# ax.text(
#     x=5, 
#     y=5, 
#     s="Color = Shot Type\nSize = Expected Goals (xG)",
#     color='white',
#     fontsize=12,
#     ha='left',
#     va='bottom'
# )

st.pyplot(fig)