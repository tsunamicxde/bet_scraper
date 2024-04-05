def check_r3(left_team_name, right_team_name, new_r3, old_r3):
    message = ""
    type_of_coefficient = "r3"

    if float(new_r3[0]) < float(old_r3[0]):

        message += f"\nКоэффициент для команды {left_team_name} по r3 упал с {old_r3[0]} " \
                   f"до {new_r3[0]}.\n\n"
        print(message)

    elif float(new_r3[0]) > float(old_r3[0]):

        message += f"Коэффициент для команды {left_team_name} по r3 поднялся с {old_r3[0]} " \
                   f"до {new_r3[0]}.\n\n"
        print(message)

    if float(new_r3[1]) < float(old_r3[1]):

        message += f"Коэффициент для команды {right_team_name} по r3 упал с {old_r3[1]} " \
                   f"до {new_r3[1]}.\n\n"
        print(message)

    elif float(new_r3[1]) > float(old_r3[1]):

        message += f"Коэффициент для команды {right_team_name} по r3 поднялся с {old_r3[1]} " \
                   f"до {new_r3[1]}.\n\n"
        print(message)

    return message, type_of_coefficient
