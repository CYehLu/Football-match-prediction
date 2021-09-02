import os
import re
import glob
import numpy as np
import pandas as pd


def merge_rival_info_to_df_team(team, season):
    df_team = pd.read_csv(f'team_data/{season}/{team}.csv')
    rivals = df_team['Rival'].unique()

    df_rivals = []

    for rival in rivals:
        df_rival = pd.read_csv(f'team_data/{season}/{rival}.csv')

        target_cols = df_rival.columns[df_rival.columns.str.startswith('b')]
        target_cols = target_cols.insert(0, 'Date')

        df_rivals.append(
            df_rival.loc[df_rival['Rival'] == team, target_cols]
        )

    df_rivals = pd.concat(df_rivals).sort_values(by='Date')
    df_rivals.columns = df_rivals.columns.str.replace('b', 'bRival')

    df_team = df_team.merge(df_rivals, on='Date')
    return df_team


if __name__ == '__main__':
    for iseason in range(11):
        season = str(1011 + iseason * 101)
        print(f'[{season}] --- ', end='  ')

        allteams = list(
            map(
                lambda s: s.replace('.csv', ''), 
                filter(lambda s: s.endswith('csv'), os.listdir(f'team_data/{season}/'))
            )
        )

        df_team_dict = {}    # Dict[str_team_name, df_team]

        for team in allteams:
            print(team, end=' / ')        
            df_team = merge_rival_info_to_df_team(team, season)
            df_team_dict[team] = df_team
        print()

        for team, df_team in df_team_dict.items():
            df_team.to_csv(f'team_data/{season}/{team}.csv', index=False)