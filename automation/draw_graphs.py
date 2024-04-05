import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import ticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D


def draw_graphs(match_id, teams):
    conn = sqlite3.connect('matches_data.db')
    cursor = conn.cursor()

    if teams[0] == "None":
        teams = ['common', 'r1', 'r2', 'r3']

    for team in teams:
        query = '''
                    SELECT left_team_name, right_team_name
                    FROM matches_data 
                    WHERE match_id = ?
                '''

        cursor.execute(query, (match_id,))
        results = cursor.fetchone()
        left_team_name, right_team_name = results

        query = f"""
            SELECT {team}, strftime('%Y-%m-%d %H:%M', date) AS formatted_date, status
            FROM full_matches_data
            WHERE match_id = ?
            ORDER BY date ASC
        """
        cursor.execute(query, (match_id, ))

        results = cursor.fetchall()
        common_lists = []
        dates = []
        statuses = []
        for row in results:
            try:
                common_str = row[0]
                common_list = list(map(float, common_str.split(',')))
                common_lists.append(common_list)
                dates.append(row[1])
                statuses.append(row[2])
            except Exception:
                continue

        filtered_common_lists = []
        filtered_dates = []

        for common_list, date, status in zip(common_lists, dates, statuses):
            if common_list != [0.0, 0.0]:
                filtered_common_lists.append(common_list)
                filtered_dates.append(date)

        for common_list, date, status in zip(common_lists, dates, statuses):
            if common_list != [0.0, 0.0]:
                if status == "LIVE":
                    live_date = date
                    live_index = len(filtered_dates) - 1
                    break

        if len(filtered_common_lists) > 0:
            data = {'Date': filtered_dates,
                    left_team_name: [x[0] for x in filtered_common_lists],
                    right_team_name: [x[1] for x in filtered_common_lists]}
            df = pd.DataFrame(data)

            df_melted = df.melt(id_vars=['Date'], var_name='Team', value_name='Coefficient')

            sns.set_style("white")
            plt.figure(figsize=(12, 6))

            sns.lineplot(data=df_melted, x='Date', y='Coefficient', hue='Team', marker='o',
                         palette={left_team_name: '#FFA500', right_team_name: '#6A5ACD'}, ci=None)

            if 'live_date' in locals():
                plt.axvline(x=live_date, color='#FF1493', linestyle='--', label='First LIVE Match')

            legend_elements = [Patch(facecolor='#FFA500', label=left_team_name),
                               Patch(facecolor='#6A5ACD', label=right_team_name)]
            if 'live_date' in locals():
                legend_elements.append(Line2D([0], [0], color='#FF1493', linestyle='--', label='First LIVE Match'))

            plt.legend(handles=legend_elements, title='Teams', loc='best')

            sns.despine()

            if team == "common":
                plt.title("Match Winner")
            else:
                plt.title(team)

            plt.xlabel('Date')
            plt.ylabel('Coefficients')

            locator = ticker.MultipleLocator(base=3)
            plt.gca().xaxis.set_major_locator(locator)

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f'graphics/{match_id}_{team}.png')

    conn.close()
