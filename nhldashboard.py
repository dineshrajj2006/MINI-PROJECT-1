import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pymysql
import streamlit as st
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="13849#Datasci",
    database="proj1"
)

st.title("NHL Dashboard")
st.set_page_config(
    page_title="NHL Analytics",
    page_icon="🏒",
    layout="wide"
)
with st.sidebar:

    selected = option_menu(
        "MENU",
        [
            "Home",
            "Standings",
            "Team Info",
            "Player Search",
            "Game Results",
            "Leaderboards",
            "SQL Query"
        ],
        icons=[
            "house",
            "bar-chart",
            "people",
            "person",
            "calendar",
            "trophy",
            "database"
        ],
        default_index=1
    )
if selected == "Home":   
    st.image("hockey.jpg", width=500)
    st.write("Welcome to the NHL Analytics Hub!")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(" Teams", 32)
    with col2:
        st.metric("Players", 800)
    with col3:
        st.metric("Games", 1312)
    with col4:
        st.metric("Goals", 4500)
elif selected == "Standings":
    st.write("NHL team standings will be displayed here.")
    conference = st.selectbox(
        "Conference",
        ["All", "Eastern", "Western"]
    )
    query = """
        SELECT
            t.team_name,
            t.conference_name,
            s.games_played,
            s.wins,
            s.losses,
            s.ot_losses,
            s.points
        FROM teams t
        JOIN standings s
        ON t.team_id = s.team_id
        WHERE 1=1
    """
    values = []
    if conference != "All":
        query += " AND t.conference_name = %s"
        values.append(conference)
    query += " ORDER BY s.points DESC"
    df = pd.read_sql_query(
        query,
        conn,
        params=values
    )
    df.insert(
        0,
        "Rank",
        range(1, len(df) + 1)
    )
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
elif selected == "Team Info":
    st.write("Team information will be displayed here.")
    teams = pd.read_sql_query(
        "SELECT * FROM teams",
        conn
    )
    team = st.selectbox(
        "Select Team",
        teams["team_name"]
    )
    team_data = teams[
        teams["team_name"] == team
    ]
    st.dataframe(
        team_data,
        hide_index=True
    )
elif selected == "Player Search":
    st.write("player search")
    name = st.text_input("Enter Player Name")
    if name:
        df = pd.read_sql_query(
            "SELECT * FROM players WHERE first_name LIKE %s OR last_name LIKE %s",
            conn,
            params=["%" + name + "%", "%" + name + "%"]
        )
        st.dataframe(df, hide_index=True)
elif selected == "Game Results":
    st.write("Game results will be displayed here.")
    df = pd.read_sql_query(
        """
        SELECT
            g.game_id,
            g.game_date,
            ht.team_name AS home_team,
            at.team_name AS away_team,
            g.home_score,
            g.away_score,
            g.game_state,
            g.venue_name
        FROM games g

        JOIN teams ht
            ON g.home_team_id = ht.team_id

        JOIN teams at
            ON g.away_team_id = at.team_id

        ORDER BY g.game_date DESC
        """,
        conn
    )
    st.dataframe(
        df,
        use_container_width=True
    )
   
elif selected == "Leaderboards":
    st.write("Top NHL players will be displayed here.")
    df = pd.read_sql_query(
        """
        SELECT
            p.first_name,
            p.last_name,
            t.team_name,
            s.goals,
            s.assists,
            s.points
        FROM skater_season_stats s

        JOIN players p
            ON s.player_id = p.player_id

        JOIN teams t
            ON p.team_id = t.team_id

        ORDER BY s.points DESC
        LIMIT 10
        """,
        conn
    )

    st.dataframe(
        df,
        use_container_width=True
    )
elif selected == "SQL Query":
    st.title("SQL Query")
    option = st.selectbox(
        "Select a query",
        (
            "1. Team with Most Goals",
            "2. Top 5 Point Scorers",
            "3. Players with 20+ Goals and 30+ Assists",
            "4. Teams Above Average Points",
            "5. Divisions Above 90 Average Points",
            "6. Teams with Most Wins",
            "7. Top 10 Goal Scorers",
            "8. Team with Highest Average Player Points",
            "9. Top 10 Goalies",
            "10. Games Played by Each Team"
        )
    )
    if option == "1. Team with Most Goals":
        df = pd.read_sql_query(
            """
            SELECT 
                t.team_name,
                s.goals_for
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            ORDER BY s.goals_for DESC
            LIMIT 1
            """,
            conn
        )
    elif option == "2. Top 5 Point Scorers":
        df = pd.read_sql_query(
            """
            SELECT
                p.first_name,
                p.last_name,
                t.team_name,
                s.points
            FROM players p
            JOIN teams t
                ON p.team_id = t.team_id
            JOIN skater_season_stats s
                ON p.player_id = s.player_id
            ORDER BY s.points DESC
            LIMIT 5
            """,
            conn
        )
    elif option == "3. Players with 20+ Goals and 30+ Assists":
        df = pd.read_sql_query(
            """
            SELECT
                p.first_name,
                p.last_name,
                s.goals,
                s.assists
            FROM players p
            JOIN skater_season_stats s
                ON p.player_id = s.player_id
            WHERE s.goals > 20
              AND s.assists > 30
            ORDER BY s.goals DESC
            """,
            conn
        )
    elif option == "4. Teams Above Average Points":

        df = pd.read_sql_query(
            """
            SELECT
                t.team_name,
                s.points
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            WHERE s.points > (
                SELECT AVG(points)
                FROM standings
            )
            ORDER BY s.points DESC
            """,
            conn
        )
    elif option == "5. Divisions Above 90 Average Points":

        df = pd.read_sql_query(
            """
            SELECT
                t.division_name,
                AVG(s.points) AS average_points
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            GROUP BY t.division_name
            HAVING AVG(s.points) > 90
            ORDER BY average_points DESC
            """,
            conn
        )
    elif option == "6. Teams with Most Wins":

        df = pd.read_sql_query(
            """
            SELECT
                t.team_name,
                s.wins
            FROM teams t
            JOIN standings s
                ON t.team_id = s.team_id
            ORDER BY s.wins DESC
            LIMIT 10
            """,
            conn
        )
    elif option == "7. Top 10 Goal Scorers":

        df = pd.read_sql_query(
            """
            SELECT
                p.first_name,
                p.last_name,
                t.team_name,
                s.goals
            FROM players p
            JOIN teams t
                ON p.team_id = t.team_id
            JOIN skater_season_stats s
                ON p.player_id = s.player_id
            ORDER BY s.goals DESC
            LIMIT 10
            """,
            conn
        )
    elif option == "8. Team with Highest Average Player Points":

        df = pd.read_sql_query(
            """
            SELECT
                t.team_name,
                AVG(s.points) AS average_player_points
            FROM teams t
            JOIN players p
                ON t.team_id = p.team_id
            JOIN skater_season_stats s
                ON p.player_id = s.player_id
            GROUP BY t.team_id, t.team_name
            ORDER BY average_player_points DESC
            LIMIT 1
            """,
            conn
        )
    elif option == "9. Top 10 Goalies":
        df = pd.read_sql_query(
            """
            SELECT
                p.first_name,
                p.last_name,
                t.team_name,
                g.save_percentage
            FROM players p
            JOIN teams t
                ON p.team_id = t.team_id
            JOIN goalie_season_stats g
                ON p.player_id = g.player_id
            WHERE g.save_percentage IS NOT NULL
            ORDER BY g.save_percentage DESC
            LIMIT 10
            """,
            conn
        )
    elif option == "10. Games Played by Each Team":
        df = pd.read_sql_query(
            """
            SELECT
                t.team_name,
                COUNT(*) AS games_played
            FROM teams t
            JOIN games g
                ON t.team_id = g.home_team_id
                OR t.team_id = g.away_team_id
            GROUP BY t.team_id, t.team_name
            ORDER BY games_played DESC
            """,
            conn
        )
    st.dataframe(df)