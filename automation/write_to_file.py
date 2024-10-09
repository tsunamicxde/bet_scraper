from datetime import datetime


def write_to_file(filename, text):
    timestamp = datetime.today().strftime("%d-%m-%Y %H:%M:%S")
    text = timestamp + text
    try:
        with open(filename, 'a', encoding="utf-8") as file:
            file.write(text + '\n')
    except FileNotFoundError:
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(text + '\n')

