def check_r1(left_team_name, right_team_name, new_r1, old_r1):
    message = ""
    type_of_coefficient = "r1"

    if float(new_r1[0]) < float(old_r1[0]):

        message += f"Коэффициент для команды {left_team_name} по r1 упал с {old_r1[0]} " \
                   f"до {new_r1[0]}.\n\n"
        print(message)
    elif float(new_r1[0]) > float(old_r1[0]):

        message += f"Коэффициент для команды {left_team_name} по r1 поднялся с {old_r1[0]} " \
                   f"до {new_r1[0]}.\n\n"
        print(message)

    if float(new_r1[1]) < float(old_r1[1]):

        message += f"Коэффициент для команды {right_team_name} по r1 упал с {old_r1[1]} " \
                   f"до {new_r1[1]}.\n\n"
        print(message)

    elif float(new_r1[1]) > float(old_r1[1]):

        message += f"Коэффициент для команды {right_team_name} по r1 поднялся с {old_r1[1]} " \
                   f"до {new_r1[1]}.\n\n"
        print(message)

    return message, type_of_coefficient
