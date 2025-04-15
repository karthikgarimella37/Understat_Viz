import os
import json
import requests
import psycopg2 as psy
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def postgres_credentials(file_path):
    load_dotenv(file_path)
    sql_username = os.getenv("sql_username")
    sql_password = os.getenv("sql_password")
    sql_host = os.getenv("sql_host")
    sql_port = os.getenv("sql_port")
    sql_database = os.getenv("sql_database")

    return sql_username, sql_password, sql_host, sql_port, sql_database


def postgres_connection(file_path):
    sql_username, sql_password, sql_host, sql_port, sql_database = postgres_credentials(file_path)
    connection_string = f'postgresql+psycopg2://{sql_username}:{sql_password}@{sql_host}:{sql_port}/{sql_database}'
    engine = create_engine(connection_string)

    return engine


def create_all_tables_sequences(engine):
    with engine.connect() as conn:
        conn.execute(text("""\
        CREATE TABLE IF NOT EXISTS player_stats (
    id               INT PRIMARY KEY,
    player_name      VARCHAR (255),
    games            INT,
    time             INT,
    goals            INT,
    xG               FLOAT,
    assists          INT,
    xA               FLOAT,
    shots            INT,
    key_passes       INT,
    yellow_cards     INT,
    red_cards        INT,
    position         VARCHAR (255),
    team_title       VARCHAR (255),
    npg              BIGINT,
    npxG             FLOAT,
    xGChain          FLOAT,
    xGBuildup        FLOAT
);
                
                          
CREATE TABLE IF NOT EXISTS shots_data (
    id                 INT PRIMARY KEY,
    minute             INT,
    result             VARCHAR (255),
    X                  FLOAT,
    Y                  FLOAT,
    xG                 FLOAT,
    player             VARCHAR (255),
    h_a                VARCHAR (255),
    player_id          INT,
    situation          VARCHAR (255),
    season             INT,
    shotType           VARCHAR (255),
    match_id           INT,
    h_team             VARCHAR (255),
    a_team             VARCHAR (255),
    h_goals            INT,
    a_goals            INT,
    date               TIMESTAMP,
    player_assisted    VARCHAR (255),
    lastAction         VARCHAR (255),
    FOREIGN KEY (player_id) REFERENCES player_stats(id)
);

    
                        """))



def run_table_creation():
    file_path = os.path.join(os.path.dirname(__file__), '../../.env')
    engine = postgres_connection(file_path)
    create_all_tables_sequences(engine)
    
    print("Tables and Sequences Created!")

if __name__ == "__main__":
    run_table_creation()