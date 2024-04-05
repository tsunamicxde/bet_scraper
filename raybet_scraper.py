import requests
import sqlite3
from datetime import datetime
import time

from automation.check_r1 import check_r1
from automation.check_r2 import check_r2
from automation.check_r3 import check_r3
from automation.check_winner import check_winner
from automation.delete_old_graphs import delete_old_graphs
from automation.delete_old_records import delete_old_records
from bet_api.send_message_to_api import send_message_to_api

games = {
    151: "DOTA 2",
    140: "CS 2",
    70: "League Of Legends",
    37480401: "Mobile Legends"
}

conn = sqlite3.connect('matches_data.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS matches_data (
                                id INTEGER PRIMARY KEY,
                                match_id INTEGER,
                                left_team_name TEXT,
                                right_team_name TEXT,
                                league_name TEXT,
                                game TEXT,
                                status TEXT,
                                common TEXT,
                                r1 TEXT,
                                r2 TEXT,
                                r3 TEXT,
                                date TIMESTAMP DEFAULT(datetime('now', 'localtime'))
                            )''')

cursor.execute('''
                    CREATE TABLE IF NOT EXISTS full_matches_data (
                    id INTEGER PRIMARY KEY,
                    match_id INTEGER,
                    left_team_name TEXT,
                    right_team_name TEXT,
                    league_name TEXT,
                    game TEXT,
                    status TEXT,
                    common TEXT,
                    r1 TEXT,
                    r2 TEXT,
                    r3 TEXT,
                    date TIMESTAMP DEFAULT(datetime('now', 'localtime'))
                )''')
conn.commit()


def parse_match(match_id):
    match_url = f"https://vnimpvgameinfo.esportsworldlink.com/v2/odds?match_id={match_id}"
    try:
        match_json = requests.get(match_url)
        match_json.raise_for_status()
    except Exception as e:
        print("Ошибка при прогрузке страницы:", e)
        return

    if match_json.status_code == 200:
        try:
            match_data = match_json.json()
        except Exception as e:
            print("Ошибка при прогрузке страницы:", e)
            return

        game = match_data['result']['game_id']

        if game in games:
            odds = match_data['result']['odds']

            team1 = match_data['result']['team'][0]['team_short_name']
            team2 = match_data['result']['team'][1]['team_short_name']

            team1_id = match_data['result']['team'][0]['team_id']
            team2_id = match_data['result']['team'][1]['team_id']

            status = "LIVE" if match_data['result']['status'] == 2 else "PRE LIVE"
            league_name = match_data['result']['tournament_short_name']

            final_odds = [0, 0]
            r1_odds = [0, 0]
            r2_odds = [0, 0]
            r3_odds = [0, 0]

            for odd in odds:
                if odd['match_id'] is bool:
                    odd['match_id'] = 0

                if odd['match_stage'] == 'final' and odd['group_short_name'] == 'Winner':
                    if odd['team_id'] == team1_id:
                        final_odds[0] = odd['odds']
                    if odd['team_id'] == team2_id:
                        final_odds[1] = odd['odds']

                if (odd['match_stage'] == 'r1' or odd['match_stage'] == 'map1') and odd['group_short_name'] == 'Winner':
                    if odd['team_id'] == team1_id:
                        r1_odds[0] = odd['odds']
                    if odd['team_id'] == team2_id:
                        r1_odds[1] = odd['odds']

                if (odd['match_stage'] == 'r2' or odd['match_stage'] == 'map2') and odd['group_short_name'] == 'Winner':
                    if odd['team_id'] == team1_id:
                        r2_odds[0] = odd['odds']
                    if odd['team_id'] == team2_id:
                        r2_odds[1] = odd['odds']

                if (odd['match_stage'] == 'r3' or odd['match_stage'] == 'map3') and odd['group_short_name'] == 'Winner':
                    if odd['team_id'] == team1_id:
                        r3_odds[0] = odd['odds']
                    if odd['team_id'] == team2_id:
                        r3_odds[1] = odd['odds']

            game = games[game]

            try:
                query = '''
                            SELECT common, r1, r2, r3 
                            FROM matches_data 
                            WHERE match_id = ?
                        '''

                cursor.execute(query, (match_id, ))
                results = cursor.fetchone()

                old_common, old_r1, old_r2, old_r3 = results
                old_common = old_common.split(',')
                old_r1 = old_r1.split(',')
                old_r2 = old_r2.split(',')
                old_r3 = old_r3.split(',')

                title = f"{team1} vs {team2}\n{game} - {league_name} (RAYBET)" \
                        f"\nСтатус: {status}\n"

                message = title

                if status == "PRE LIVE":
                    check_winner_message, type_of_coefficient = check_winner(team1, team2, final_odds,
                                                                             old_common)
                    if check_winner_message != "":
                        message += check_winner_message
                        send_message_to_api(message, type_of_coefficient, match_id)
                        message = title

                    check_r1_message, type_of_coefficient = check_r1(team1, team2, r1_odds,
                                                                     old_r1)
                    if check_r1_message != "":
                        message += check_r1_message
                        send_message_to_api(message, type_of_coefficient, match_id)
                        message = title
                    check_r2_message, type_of_coefficient = check_r2(team1, team2, r2_odds,
                                                                     old_r2)
                    if check_r2_message != "":
                        message += check_r2_message
                        send_message_to_api(message, type_of_coefficient, match_id)
                        message = title
                    check_r3_message, type_of_coefficient = check_r3(team1, team2, r3_odds,
                                                                     old_r3)
                    if check_r3_message != "":
                        message += check_r3_message
                        send_message_to_api(message, type_of_coefficient, match_id)
            except Exception:
                pass

            final_odds = ','.join(map(str, final_odds)) if final_odds else "0,0"
            r1_odds = ','.join(map(str, r1_odds)) if r1_odds else "0,0"
            r2_odds = ','.join(map(str, r2_odds)) if r2_odds else "0,0"
            r3_odds = ','.join(map(str, r3_odds)) if r3_odds else "0,0"

            try:
                cursor.execute(''' 
                                        UPDATE matches_data
                                        SET common = ?,
                                            r1 = ?,
                                            r2 = ?,
                                            r3 = ?
                                        WHERE match_id = ?
                                    ''', (
                    final_odds,
                    r1_odds,
                    r2_odds,
                    r3_odds,
                    match_id
                ))
                conn.commit()
            except Exception:
                conn.rollback()

            try:
                cursor.execute(''' 
                                    INSERT INTO matches_data (match_id, left_team_name, right_team_name, league_name, game, status, common, r1, r2, r3)
                                    SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                    WHERE NOT EXISTS (
                                        SELECT 1 FROM matches_data
                                        WHERE match_id = ?
                                    )
                                ''', (match_id, team1, team2, league_name, game, status, final_odds,
                                      r1_odds, r2_odds, r3_odds, match_id))
                conn.commit()
            except Exception:
                conn.rollback()

            try:
                cursor.execute('''
                    SELECT * FROM full_matches_data 
                    WHERE match_id = ? 
                    ORDER BY id DESC 
                    LIMIT 1
                ''', (match_id, ))

                existing_record = cursor.fetchone()

                if existing_record is None or \
                        (existing_record[6] != final_odds or existing_record[7] != r1_odds or
                         existing_record[8] != r2_odds or existing_record[9] != r3_odds):
                    cursor.execute('''
                        INSERT INTO full_matches_data 
                        (match_id, left_team_name, right_team_name, league_name, game, status, common, r1, r2, r3) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (match_id, team1, team2, league_name, game, status, final_odds, r1_odds, r2_odds, r3_odds))
                else:
                    print("Record exists and no odds have changed. No new record added.")

                conn.commit()
            except Exception as e:
                print(f"An error occurred: {e}")
                conn.rollback()


while True:
    current_time = datetime.now().strftime('%H:%M')
    if current_time == '23:00':
        delete_old_records()
        delete_old_graphs()

    k = 1
    while k <= 5:
        url = f'https://vnimpvgameinfo.esportsworldlink.com/v2/match?page={k}&match_type=2'
        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            print("Ошибка при прогрузке страницы:", e)
            break

        if response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                print("Ошибка при прогрузке страницы:", e)
                time.sleep(60)
                break
            for match in data['result']:
                parse_match(match['id'])

            k += 1
