import os
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, exc
import logging
import time

BASE_URL = "https://understat.com"
DEFAULT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../../.env')
SEASON = 2024
LEAGUE  ="EPL"

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


def fetch_url_content(url):

    resp = requests.get(url)
    player_string = BeautifulSoup(resp.content, features="lxml").find_all('script')[3].string

    ind_start = player_string.index("('")+2 
    ind_end = player_string.index("')") 
    json_data = player_string[ind_start:ind_end] 
    json_data = json_data.encode('utf8').decode('unicode_escape')
    # df = pd.read_json(json_data)
    
    return json_data

def player_league_stats(league=LEAGUE, season=SEASON):

    url = f"{BASE_URL}/league/{league}/{season}"
    json_data = fetch_url_content(url)
    parsed_data = json.loads(json_data)
    df = pd.DataFrame(parsed_data)
    df.rename(columns={
                'xG': 'xg', 'xA': 'xa', 'npxG': 'npxg',
                'xGChain': 'xgchain', 'xGBuildup': 'xgbuildup'
            }, inplace=True)
    df['id'] = pd.to_numeric(df['id'], errors='coerce')


    return df


def get_player_shot_data(player_id):
    url = f"{BASE_URL}/player/{player_id}"
    json_data = fetch_url_content(url)
    if json_data:
        parsed_data = json.loads(json_data)
        df = pd.DataFrame(parsed_data)
        df.rename(columns={
                    'X': 'x', 'Y': 'y', 'xG': 'xg',
                    'shotType': 'shottype', 'lastAction': 'lastaction'
                }, inplace=True)
        if int(df.shape[0]) != 0:
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df['player_id'] = pd.to_numeric(df['player_id'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
    else:
        return pd.DataFrame()

    return df


def insert_player_stats(engine, df_players):

    inserted_count = 0
    error_count = 0
    

    sql_query = text("""
        INSERT INTO player_stats (id, player_name, games, time, goals, xg, assists, xa, shots, key_passes, yellow_cards, red_cards, position, team_title, npg, npxg, xgchain, xgbuildup)
        VALUES (:id, :player_name, :games, :time, :goals, :xg, :assists, :xa, :shots, :key_passes, :yellow_cards, :red_cards, :position, :team_title, :npg, :npxg, :xgchain, :xgbuildup)
        ON CONFLICT (id) DO UPDATE SET
            player_name = EXCLUDED.player_name,
            games = EXCLUDED.games,
            time = EXCLUDED.time,
            goals = EXCLUDED.goals,
            xg = EXCLUDED.xg,
            assists = EXCLUDED.assists,
            xa = EXCLUDED.xa,
            shots = EXCLUDED.shots,
            key_passes = EXCLUDED.key_passes,
            yellow_cards = EXCLUDED.yellow_cards,
            red_cards = EXCLUDED.red_cards,
            position = EXCLUDED.position,
            team_title = EXCLUDED.team_title,
            npg = EXCLUDED.npg,
            npxg = EXCLUDED.npxg,
            xgchain = EXCLUDED.xgchain,
            xgbuildup = EXCLUDED.xgbuildup;
    """)

    data_to_insert = df_players.astype(object).where(pd.notnull(df_players), None).to_dict(orient='records')
    for record in data_to_insert:
        record['xg'] = record.pop('xg')
        record['xa'] = record.pop('xa')
        record['npxg'] = record.pop('npxg')
        record['xgchain'] = record.pop('xgchain')
        record['xgbuildup'] = record.pop('xgbuildup')


    with engine.connect() as conn:
        with conn.begin():
                for record in data_to_insert:
                    try:
                        result = conn.execute(sql_query, record)
                        inserted_count += 1
                    except exc.SQLAlchemyError as e:
                        logging.error(f"Error inserting/updating player ID {record.get('id', 'N/A')}: {e}")
                        error_count += 1
    print(f"Inserted Count {inserted_count}")
    return inserted_count


def insert_shots_data(engine, df_players):

    inserted_count = 0
    error_count = 0
    

    sql_query = text("""
        INSERT INTO shots_data (id, minute, result, x, y, xg, player, h_a, player_id, situation, season, shottype, match_id, h_team, a_team, h_goals, a_goals, date, player_assisted, lastaction)
        VALUES (:id, :minute, :result, :x, :y, :xg, :player, :h_a, :player_id, :situation, :season, :shottype, :match_id, :h_team, :a_team, :h_goals, :a_goals, :date, :player_assisted, :lastaction)
        ON CONFLICT (id) DO NOTHING;
    """)

    data_to_insert = df_players.astype(object).where(pd.notnull(df_players), None).to_dict(orient='records')

    with engine.connect() as conn:
        with conn.begin():
                for record in data_to_insert:
                    try:
                        result = conn.execute(sql_query, record)
                        inserted_count += 1
                    except exc.SQLAlchemyError as e:
                        logging.error(f"Error inserting/updating player ID {record.get('id', 'N/A')}: {e}")
                        error_count += 1
    print(f"Inserted Count {inserted_count}")
    return inserted_count
    
def run_etl(league=LEAGUE, season=SEASON, env_path=DEFAULT_ENV_PATH):
    engine = postgres_connection(env_path)


    df_players = player_league_stats(league, season)
    if not df_players.empty:
            insert_player_stats(engine, df_players)

            total_shots_inserted = 0
            player_ids = df_players['id'].unique()
            for i, player_id in enumerate(player_ids):
                logging.info(f"Processing player {i+1}/{len(player_ids)}: ID {player_id}")
                df_shots = get_player_shot_data(player_id)
                if not df_shots.empty:
                    df_shots_filtered = df_shots[df_shots['player_id'] == player_id].copy()
                    if not df_shots_filtered.empty:
                         inserted = insert_shots_data(engine, df_shots_filtered)
                         total_shots_inserted += inserted
                    else:
                        logging.info(f"No shots data specifically for player {player_id} found in the fetched data.")

                else:
                    logging.warning(f"Could not retrieve or parse shot data for player ID: {player_id}")

                time.sleep(0.5) # Sleep for 500ms between player requests

            print(f"Total new shot records inserted: {total_shots_inserted}")

    else:
        print("No player data fetched. Cannot proceed to fetch shots.")



if __name__ == "__main__":
    
    run_etl()