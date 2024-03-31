import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch


def draw_graphs(left_team_name, right_team_name):
    conn = sqlite3.connect('matches_data.db')
    cursor = conn.cursor()

    teams = ['common', 'r1', 'r2', 'r3']

    for team in teams:
        query = f"""
            SELECT {team}, strftime('%Y-%m-%d %H:%M', date) AS formatted_date
            FROM all_matches_data
            WHERE left_team_name = ? AND right_team_name = ?
        """
        cursor.execute(query, (left_team_name, right_team_name))

        results = cursor.fetchall()
        common_lists = []
        dates = []
        for row in results:
            try:
                common_str = row[0]
                common_list = list(map(float, common_str.split(',')))
                common_lists.append(common_list)
                dates.append(row[1])
            except Exception:
                continue

        filtered_common_lists = []
        filtered_dates = []

        for common_list, date in zip(common_lists, dates):
            if common_list != [0.0, 0.0]:
                filtered_common_lists.append(common_list)
                filtered_dates.append(date)

        if len(filtered_common_lists) > 0:
            data = {'Date': filtered_dates,
                    left_team_name: [x[0] for x in filtered_common_lists],
                    right_team_name: [x[1] for x in filtered_common_lists]}
            df = pd.DataFrame(data)

            df_melted = df.melt(id_vars=['Date'], var_name='Team', value_name='Coefficient')

            sns.set_style("white")
            plt.figure(figsize=(12, 6))

            sns.lineplot(data=df_melted, x='Date', y='Coefficient', hue='Team', marker='o',
                         palette={left_team_name: '#FFA500', right_team_name: '#6A5ACD'})

            legend_elements = [Patch(facecolor='#FFA500', label=left_team_name),
                               Patch(facecolor='#6A5ACD', label=right_team_name)]
            plt.legend(handles=legend_elements, title='Teams', loc='best')

            sns.despine()

            if team == "common":
                plt.title("Match Winner")
            else:
                plt.title(team)

            plt.xlabel('Дата')
            plt.ylabel('Коэффициенты')

            plt.yticks([i for i in range(int(df_melted['Coefficient'].min()), int(df_melted['Coefficient'].max()) + 1)],
                       [i / 2 for i in range(int(df_melted['Coefficient'].min()), int(df_melted['Coefficient'].max()) + 1)])

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'graphics/{left_team_name}_{right_team_name}_{team}.png')

    conn.close()
