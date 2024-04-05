def check_r2(left_team_name, right_team_name, new_r2, old_r2):
    message = ""
    type_of_coefficient = "r2"

    if float(new_r2[0]) < float(old_r2[0]):

        message += f"Коэффициент для команды {left_team_name} по r2 упал с {old_r2[0]} " \
                   f"до {new_r2[0]}.\n\n"
        print(message)

    elif float(new_r2[0]) > float(old_r2[0]):

        message += f"Коэффициент для команды {left_team_name} по r2 поднялся с {old_r2[0]} " \
                   f"до {new_r2[0]}.\n\n"
        print(message)

    if float(new_r2[1]) < float(old_r2[1]):

        message += f"Коэффициент для команды {right_team_name} по r2 упал с {old_r2[1]} " \
                   f"до {new_r2[1]}.\n\n"
        print(message)

    elif float(new_r2[1]) > float(old_r2[1]):

        message += f"Коэффициент для команды {right_team_name} по r2 поднялся с {old_r2[1]} " \
                   f"до {new_r2[1]}.\n\n"
        print(message)

    return message, type_of_coefficient
