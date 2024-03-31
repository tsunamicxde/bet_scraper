import time
import sqlite3
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

from automation.changing_the_coefficient import changing_the_coefficient
from config import file_name
from bet_api.send_message_to_api import send_message_to_api
from automation.write_to_file import write_to_file

game = "DOTA 2"


class DotaUpcomingScraper:

    def __init__(self):
        self.conn = sqlite3.connect('matches_data.db')
        self.cursor = self.conn.cursor()

    def setup_method(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Edge(options=chrome_options)
        self.vars = {}
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS dota (
                                id INTEGER PRIMARY KEY,
                                left_team_name TEXT,
                                right_team_name TEXT,
                                league_name TEXT,
                                common TEXT,
                                r1 TEXT,
                                r2 TEXT,
                                r3 TEXT
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS all_matches_data (
                                id INTEGER PRIMARY KEY,
                                left_team_name TEXT,
                                right_team_name TEXT,
                                league_name TEXT,
                                game TEXT,
                                common TEXT,
                                r1 TEXT,
                                r2 TEXT,
                                r3 TEXT,
                                date TIMESTAMP DEFAULT(datetime('now', 'localtime'))
                    )''')
        self.conn.commit()

    def teardown_method(self):
        try:
            self.driver.quit()
            self.conn.close()
        except KeyboardInterrupt:
            print("Программа остановлена пользователем.")
        except Exception:
            pass

    def scrape(self):
        self.driver.get("https://rbvn3.com/")
        time.sleep(5)
        self.driver.set_window_size(1552, 832)

        try:
            close_button = self.driver.find_element(By.CSS_SELECTOR, ".popup-close")
            close_button.click()
        except NoSuchElementException:
            pass

        time.sleep(6)
        self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(2)").click()

        while True:
            time.sleep(2)
            match_cards = self.driver.find_elements(By.CSS_SELECTOR, ".match-card")
            index = 0
            time.sleep(2)
            if len(match_cards) == 0:
                continue
            while index < len(match_cards):
                try:
                    match_card = match_cards[index]

                    time.sleep(2)

                    button = match_card.find_element(By.CSS_SELECTOR, "button.play-count")
                    time.sleep(2)
                    button.click()
                    time.sleep(2)
                    left_team_name_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                      "section.match-team.left-team .team-name")
                    right_team_name_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                       "section.match-team.right-team .team-name")
                    time.sleep(2)

                    live_match_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                                    'section.match-status-content.content-live')

                    if live_match_elements:
                        self.driver.get("https://rbvn3.com/")
                        time.sleep(3)
                        self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(2)").click()
                        time.sleep(2)
                        match_cards = self.driver.find_elements(By.CSS_SELECTOR, ".match-card")
                        index += 1
                        continue
                    else:
                        match_status = "PRE LIVE"

                    league_name_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                   '.announcement-card .card-title')

                    if league_name_element.text == "":
                        league_name_element = self.driver.find_element(By.CSS_SELECTOR,
                                                                       ".match-title span:nth-of-type(2)")
                        league_name = league_name_element.text
                    else:
                        league_name = league_name_element.text

                    left_team_name = left_team_name_element.text
                    right_team_name = right_team_name_element.text
                    is_r2_available = True
                    is_r3_available = True

                    self.driver.find_element(By.CSS_SELECTOR,
                                             ".v-tabs__container--centered > .v-tabs__div:nth-child(3) .tab-item").click()

                    try:
                        self.driver.find_element(By.CSS_SELECTOR, ".v-tabs__div:nth-child(4) .tab-item").click()
                    except NoSuchElementException:
                        is_r2_available = False

                    time.sleep(2)
                    try:
                        self.driver.find_element(By.CSS_SELECTOR, ".v-tabs__div:nth-child(5) .tab-item").click()
                    except NoSuchElementException:
                        is_r3_available = False

                    result_dict = {'left_team_name': left_team_name, 'right_team_name': right_team_name, 'common': [],
                                   'r1': [], 'r2': [], 'r3': []}

                    count_of_pairs = 0
                    group_sections = self.driver.find_elements(By.CSS_SELECTOR, ".group-list")

                    for group_section in group_sections:
                        if "Đội thắng" in group_section.text:
                            count = 0
                            coefficients = []
                            odds_buttons = group_section.find_elements(By.CSS_SELECTOR, ".odds-button")

                            for button in odds_buttons:
                                try:
                                    odds = button.find_element(By.CSS_SELECTOR, ".bet-odds").text
                                    coefficients.append(odds)
                                    count += 1
                                    if count == 2:
                                        break
                                except Exception:
                                    coefficients.append(0)
                                    count += 1
                                    if count == 2:
                                        break
                                    else:
                                        continue

                            if count_of_pairs == 0:
                                result_dict['common'] = coefficients
                            elif count_of_pairs < 4:
                                result_dict['r1'] = coefficients
                            elif count_of_pairs < 6:
                                if is_r2_available:
                                    result_dict['r2'] = coefficients
                            else:
                                if is_r3_available:
                                    result_dict['r3'] = coefficients

                            count_of_pairs += 2

                    current_time = datetime.now()

                    formatted_time = current_time.strftime("%d.%m.%y %H:%M")

                    time.sleep(2)

                    message = f"[{formatted_time}] " \
                              f"{result_dict}. Статус: {match_status}"
                    print(message)
                    write_to_file(file_name, message)

                    if len(result_dict['common']) < 2:
                        result_dict['common'] = [0, 0]
                    if len(result_dict['r1']) < 2:
                        result_dict['r1'] = [0, 0]
                    if len(result_dict['r2']) < 2:
                        result_dict['r2'] = [0, 0]
                    if len(result_dict['r3']) < 2:
                        result_dict['r3'] = [0, 0]

                    new_common = result_dict['common'] if result_dict['common'] else [0, 0]
                    new_r1 = result_dict['r1'] if result_dict['r1'] else [0, 0]
                    new_r2 = result_dict['r2'] if result_dict['r2'] else [0, 0]
                    new_r3 = result_dict['r3'] if result_dict['r3'] else [0, 0]

                    try:
                        query = '''
                                    SELECT common, r1, r2, r3 
                                    FROM dota
                                    WHERE left_team_name = ? AND right_team_name = ?
                                '''

                        self.cursor.execute(query, (left_team_name, right_team_name))
                        results = self.cursor.fetchall()[0]

                        old_common, old_r1, old_r2, old_r3 = results
                        old_common = old_common.split(',')
                        old_r1 = old_r1.split(',')
                        old_r2 = old_r2.split(',')
                        old_r3 = old_r3.split(',')

                        title = f"{left_team_name} vs {right_team_name}\n{game} - {league_name} (RAYBET)" \
                                f"\nСтатус: {match_status}\n"
                        message = title

                        changing_the_coefficient_message = changing_the_coefficient(left_team_name, right_team_name,
                                                                                    new_common, new_r1, new_r2,
                                                                                    new_r3,
                                                                                    old_common, old_r1, old_r2,
                                                                                    old_r3)

                        if changing_the_coefficient_message != "":
                            message += changing_the_coefficient_message
                            send_message_to_api(message, left_team_name, right_team_name)

                    except Exception :
                        pass

                    common_values = ','.join(map(str, result_dict['common'])) if result_dict['common'] else "0,0"
                    r1_values = ','.join(map(str, result_dict['r1'])) if result_dict['r1'] else "0,0"
                    r2_values = ','.join(map(str, result_dict['r2'])) if result_dict['r2'] else "0,0"
                    r3_values = ','.join(map(str, result_dict['r3'])) if result_dict['r3'] else "0,0"

                    try:
                        self.cursor.execute(''' 
                            UPDATE dota
                            SET common = ?,
                                r1 = ?,
                                r2 = ?,
                                r3 = ?
                            WHERE left_team_name = ? AND right_team_name = ?
                        ''', (
                            common_values,
                            r1_values,
                            r2_values,
                            r3_values,
                            left_team_name,
                            right_team_name
                        ))
                        self.conn.commit()
                    except Exception:
                        pass
                        self.conn.rollback()

                    try:
                        self.cursor.execute(''' 
                                                INSERT INTO dota (left_team_name, right_team_name, league_name, common, r1, r2, r3)
                                                SELECT ?, ?, ?, ?, ?, ?, ?
                                                WHERE NOT EXISTS (
                                                    SELECT 1 FROM dota
                                                    WHERE left_team_name = ? AND right_team_name = ?
                                                )
                                            ''', (left_team_name, right_team_name, league_name, common_values, r1_values, r2_values,
                                                  r3_values, left_team_name, right_team_name))
                        self.conn.commit()
                    except Exception:
                        self.conn.rollback()

                    try:
                        self.cursor.execute('''
                                SELECT * FROM all_matches_data 
                                WHERE left_team_name = ? AND right_team_name = ? 
                                ORDER BY id DESC 
                                LIMIT 1
                            ''', (left_team_name, right_team_name))

                        existing_record = self.cursor.fetchone()

                        if existing_record is None:
                            self.cursor.execute('''
                                    INSERT INTO all_matches_data 
                                    (left_team_name, right_team_name, league_name, game, common, r1, r2, r3) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (left_team_name, right_team_name, league_name, game, common_values, r1_values, r2_values, r3_values))
                        else:
                            last_common, last_r1, last_r2, last_r3 = existing_record[5:9]
                            if last_common != common_values or last_r1 != r1_values or last_r2 != r2_values or last_r3 != r3_values:
                                self.cursor.execute('''
                                        INSERT INTO all_matches_data 
                                        (left_team_name, right_team_name, league_name, game, common, r1, r2, r3) 
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (left_team_name, right_team_name, league_name, game, common_values, r1_values, r2_values, r3_values))
                        self.conn.commit()
                    except Exception as e:
                        
                        self.conn.rollback()

                    self.driver.get("https://rbvn3.com/")
                    time.sleep(3)
                    self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(2)").click()
                    time.sleep(2)
                    match_cards = self.driver.find_elements(By.CSS_SELECTOR, ".match-card")
                    index += 1

                except (NoSuchElementException, StaleElementReferenceException):
                    break
