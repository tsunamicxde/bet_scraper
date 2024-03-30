from config import file_name
from automation.write_to_file import write_to_file


def changing_the_coefficient(left_team_name, right_team_name, new_common, new_r1, new_r2, new_r3, old_common, old_r1, old_r2, old_r3):
    message = ""

    if float(new_common[0]) < float(old_common[0]):
        message += f"Коэффициент для команды {left_team_name} по общему упал с {old_common[0]} " \
                   f"до {new_common[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)
    elif float(new_common[0]) > float(old_common[0]):
        message += f"Коэффициент для команды {left_team_name} по общему поднялся с {old_common[0]} " \
                   f"до {new_common[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r1[0]) < float(old_r1[0]):
        message += f"Коэффициент для команды {left_team_name} по r1 упал с {old_r1[0]} " \
                   f"до {new_r1[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)
    elif float(new_r1[0]) > float(old_r1[0]):
        message += f"Коэффициент для команды {left_team_name} по r1 поднялся с {old_r1[0]} " \
                   f"до {new_r1[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r2[0]) < float(old_r2[0]):
        message += f"Коэффициент для команды {left_team_name} по r2 упал с {old_r2[0]} " \
                   f"до {new_r2[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_r2[0]) > float(old_r2[0]):
        message += f"Коэффициент для команды {left_team_name} по r2 поднялся с {old_r2[0]} " \
                   f"до {new_r2[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r3[0]) < float(old_r3[0]):
        message += f"\nКоэффициент для команды {left_team_name} по r3 упал с {old_r3[0]} " \
                   f"до {new_r3[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_r3[0]) > float(old_r3[0]):
        message += f"Коэффициент для команды {left_team_name} по r3 поднялся с {old_r3[0]} " \
                   f"до {new_r3[0]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_common[1]) < float(old_common[1]):
        message += f"Коэффициент для команды {right_team_name} по общему упал с {old_common[1]} " \
                   f"до {new_common[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_common[1]) > float(old_common[1]):
        message += f"Коэффициент для команды {right_team_name} по общему поднялся с {old_common[1]} " \
                   f"до {new_common[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r1[1]) < float(old_r1[1]):
        message += f"Коэффициент для команды {right_team_name} по r1 упал с {old_r1[1]} " \
                   f"до {new_r1[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_r1[1]) > float(old_r1[1]):
        message += f"Коэффициент для команды {right_team_name} по r1 поднялся с {old_r1[1]} " \
                   f"до {new_r1[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r2[1]) < float(old_r2[1]):
        message += f"Коэффициент для команды {right_team_name} по r2 упал с {old_r2[1]} " \
                   f"до {new_r2[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_r2[1]) > float(old_r2[1]):
        message += f"Коэффициент для команды {right_team_name} по r2 поднялся с {old_r2[1]} " \
                   f"до {new_r2[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    if float(new_r3[1]) < float(old_r3[1]):
        message += f"Коэффициент для команды {right_team_name} по r3 упал с {old_r3[1]} " \
                   f"до {new_r3[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    elif float(new_r3[1]) > float(old_r3[1]):
        message += f"Коэффициент для команды {right_team_name} по r3 поднялся с {old_r3[1]} " \
                   f"до {new_r3[1]}.\n\n"
        print(message)
        write_to_file(file_name, message)

    return message
