file_name = 'log.txt'


def write_to_file(filename, text):
    try:
        with open(filename, 'a', encoding="utf-8") as file:
            file.write(text + '\n')
    except FileNotFoundError:
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(text + '\n')

