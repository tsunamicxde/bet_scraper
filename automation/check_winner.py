def check_winner(left_team_name, right_team_name, new_common, old_common):
    message = ""
    type_of_coefficient = "common"

    if float(new_common[0]) < float(old_common[0]):

        message += f"Коэффициент для команды {left_team_name} по общему упал с {old_common[0]} " \
                   f"до {new_common[0]}.\n\n"
        print(message)
    elif float(new_common[0]) > float(old_common[0]):

        message += f"Коэффициент для команды {left_team_name} по общему поднялся с {old_common[0]} " \
                   f"до {new_common[0]}.\n\n"
        print(message)

    if float(new_common[1]) < float(old_common[1]):

        message += f"Коэффициент для команды {right_team_name} по общему упал с {old_common[1]} " \
                   f"до {new_common[1]}.\n\n"
        print(message)

    elif float(new_common[1]) > float(old_common[1]):

        message += f"Коэффициент для команды {right_team_name} по общему поднялся с {old_common[1]} " \
                   f"до {new_common[1]}.\n\n"
        print(message)

    return message, type_of_coefficient
