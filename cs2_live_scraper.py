import time
import sqlite3
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options

from config import file_name, write_to_file


class CsScraper:

    def __init__(self):
        self.conn = sqlite3.connect('matches_data.db')
        self.cursor = self.conn.cursor()

    def setup_method(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Edge(options=chrome_options)
        self.vars = {}
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cs (
                                id INTEGER PRIMARY KEY,
                                left_team_name TEXT,
                                right_team_name TEXT,
                                common TEXT,
                                r1 TEXT,
                                r2 TEXT,
                                r3 TEXT
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
        self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(3)").click()

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
                        match_status = "LIVE"
                    else:
                        self.driver.get("https://rbvn3.com/")
                        time.sleep(3)
                        self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(3)").click()
                        time.sleep(2)
                        break

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

                    if not is_r2_available:
                        result_dict['r2'] = [0, 0]
                    if not is_r3_available:
                        result_dict['r3'] = [0, 0]

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

                            if len(coefficients) == 0:
                                coefficients[0] = 0
                                coefficients[1] = 0
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

                    if len(result_dict['r3']) == 0:
                        result_dict['r3'] = [0, 0]
                    elif len(result_dict['r2']) == 0:
                        result_dict['r2'] = [0, 0]
                    elif len(result_dict['r1']) == 0:
                        result_dict['r1'] = [0, 0]
                    elif len(result_dict['common']) == 0:
                        result_dict['common'] = [0, 0]

                    current_time = datetime.now()

                    formatted_time = current_time.strftime("%d.%m.%y %H:%M:%S")

                    time.sleep(2)

                    message = f"[{formatted_time}] " \
                              f"{result_dict}. Статус: {match_status}"
                    print(message)
                    write_to_file(file_name, message)

                    new_common = result_dict['common']
                    new_r1 = result_dict['r1']
                    if not is_r2_available:
                        new_r2 = [0, 0]
                    else:
                        new_r2 = result_dict['r2']
                    if not is_r3_available:
                        new_r3 = [0, 0]
                    else:
                        new_r3 = result_dict['r3']

                    try:
                        query = '''
                                    SELECT common, r1, r2, r3 
                                    FROM cs 
                                    WHERE left_team_name = ? AND right_team_name = ?
                                '''

                        self.cursor.execute(query, (left_team_name, right_team_name))
                        results = self.cursor.fetchall()

                        for row in results:
                            old_common, old_r1, old_r2, old_r3 = row
                            old_common = old_common.split(',')
                            old_r1 = old_r1.split(',')
                            old_r2 = old_r2.split(',')
                            old_r3 = old_r3.split(',')

                            title = f"{left_team_name} vs {right_team_name} CS 2 (RAYBET)\n\n"
                            message = title

                            if float(new_common[0]) < float(old_common[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по общему упал с {old_common[0]} " \
                                           f"до {new_common[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title
                            elif float(new_common[0]) > float(old_common[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по общему поднялся с {old_common[0]} " \
                                           f"до {new_common[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r1[0]) < float(old_r1[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по r1 упал с {old_r1[0]} " \
                                           f"до {new_r1[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title
                            elif float(new_r1[0]) > float(old_r1[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по r1 поднялся с {old_r1[0]} " \
                                           f"до {new_r1[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r2[0]) < float(old_r2[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по r2 упал с {old_r2[0]} " \
                                           f"до {new_r2[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            elif float(new_r2[0]) > float(old_r2[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по r2 поднялся с {old_r2[0]} " \
                                           f"до {new_r2[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r3[0]) < float(old_r3[0]):
                                message += f"{formatted_time} " \
                                           f"\nКоэффициент для команды {left_team_name} по r3 упал с {old_r3[0]} " \
                                           f"до {new_r3[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)

                            elif float(new_r3[0]) > float(old_r3[0]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {left_team_name} по r3 поднялся с {old_r3[0]} " \
                                           f"до {new_r3[0]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)

                            message = title

                            if float(new_common[1]) < float(old_common[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по общему упал с {old_common[1]} " \
                                           f"до {new_common[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            elif float(new_common[1]) > float(old_common[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по общему поднялся с {old_common[1]} " \
                                           f"до {new_common[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r1[1]) < float(old_r1[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r1 упал с {old_r1[1]} " \
                                           f"до {new_r1[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            elif float(new_r1[1]) > float(old_r1[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r1 поднялся с {old_r1[1]} " \
                                           f"до {new_r1[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r2[1]) < float(old_r2[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r2 упал с {old_r2[1]} " \
                                           f"до {new_r2[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            elif float(new_r2[1]) > float(old_r2[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r2 поднялся с {old_r2[1]} " \
                                           f"до {new_r2[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)
                                message = title

                            if float(new_r3[1]) < float(old_r3[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r3 упал с {old_r3[1]} " \
                                           f"до {new_r3[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)

                            elif float(new_r3[1]) > float(old_r3[1]):
                                message += f"\n{formatted_time} " \
                                           f"Коэффициент для команды {right_team_name} по r3 поднялся с {old_r3[1]} " \
                                           f"до {new_r3[1]}. Статус: {match_status}\n"
                                print(message)
                                write_to_file(file_name, message)

                    except Exception :
                        pass

                    try:
                        self.cursor.execute(''' 
                            UPDATE cs
                            SET common = ?,
                                r1 = ?,
                                r2 = ?,
                                r3 = ?
                            WHERE left_team_name = ? AND right_team_name = ?
                        ''', (
                            ','.join(map(str, result_dict['common'])),
                            ','.join(map(str, result_dict['r1'])),
                            ','.join(map(str, result_dict['r2'])),
                            ','.join(map(str, result_dict['r3'])),
                            left_team_name,
                            right_team_name
                        ))
                        self.conn.commit()
                    except Exception :
                        pass
                        self.conn.rollback()

                    try:
                        common_values = ','.join(map(str, result_dict['common'])) if result_dict['common'] else None
                        r1_values = ','.join(map(str, result_dict['r1'])) if result_dict['r1'] else None
                        r2_values = ','.join(map(str, result_dict['r2'])) if result_dict['r2'] else None
                        r3_values = ','.join(map(str, result_dict['r3'])) if result_dict['r3'] else None

                        self.cursor.execute(''' 
                                                INSERT INTO cs (left_team_name, right_team_name, common, r1, r2, r3)
                                                SELECT ?, ?, ?, ?, ?, ?
                                                WHERE NOT EXISTS (
                                                    SELECT 1 FROM cs
                                                    WHERE left_team_name = ? AND right_team_name = ?
                                                )
                                            ''', (left_team_name, right_team_name, common_values, r1_values, r2_values, r3_values,
                                                  left_team_name, right_team_name))
                        self.conn.commit()
                    except Exception :
                        pass
                        self.conn.rollback()

                    self.driver.get("https://rbvn3.com/")
                    time.sleep(3)
                    self.driver.find_element(By.CSS_SELECTOR, ".game-item:nth-child(3)").click()
                    time.sleep(2)
                    match_cards = self.driver.find_elements(By.CSS_SELECTOR, ".match-card")
                    index += 1

                except (NoSuchElementException, StaleElementReferenceException):
                    break
