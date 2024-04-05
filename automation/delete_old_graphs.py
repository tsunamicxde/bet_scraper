import os


def delete_old_graphs():
    directory = 'graphics/'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print("Ошибка при удалении файла:", e)