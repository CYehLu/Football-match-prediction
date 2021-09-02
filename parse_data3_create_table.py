import os
import glob
import re
import pandas as pd


def extract_team_df_info(df):
    win = (df['Points'] == 3).sum()
    draw = (df['Points'] == 1).sum()
    loss = (df['Points'] == 0).sum()
    goals = f'{df["Goal"].sum()}:{df["Conceded"].sum()}'
    points = df['Points'].sum()
    
    idx_home = df['isHome']
    win_home = (df.loc[idx_home, 'Points'] == 3).sum()
    draw_home = (df.loc[idx_home, 'Points'] == 1).sum()
    loss_home = (df.loc[idx_home, 'Points'] == 0).sum()
    goals_home = f'{df.loc[idx_home, "Goal"].sum()}:{df.loc[idx_home, "Conceded"].sum()}'
    
    win_away = (df.loc[~idx_home, 'Points'] == 3).sum()
    draw_away = (df.loc[~idx_home, 'Points'] == 1).sum()
    loss_away = (df.loc[~idx_home, 'Points'] == 0).sum()
    goals_away = f'{df.loc[~idx_home, "Goal"].sum()}:{df.loc[~idx_home, "Conceded"].sum()}'
    
    return_tup = (
        win, draw, loss, goals, points,
        win_home, draw_home, loss_home, goals_home,
        win_away, draw_away, loss_away, goals_away
    )
    return return_tup


def create_table(season):
    print(f'===== Read csv files at team_data/{season}/*.csv =====')
    teams_csv = glob.glob(f'team_data/{season}/*.csv')
    
    table = []    # List[Tuple(team_name, points, home_goals, home_conceded, away_goals, away_conceded)]
    
    for team_csv in teams_csv:        
        df = pd.read_csv(team_csv)     
        info = extract_team_df_info(df)
        #points = df.iloc[-1, df.columns.get_loc('CumPoints')]
        team_name = re.findall('([A-Za-z ]+).csv$', team_csv)[0]
        table.append((team_name, *info))
        
    table = pd.DataFrame(
        table, 
        columns=[
            'Team', 'Win', 'Draw', 'Loss', 'Goals', 'Points',
            'WinHome', 'DrawHome', 'LossHome', 'GoalsHome',
            'WinAway', 'DrawAway', 'LossAway', 'GoalsAway'
        ]
    )
    table = table.sort_values(by='Points', ascending=False, ignore_index=True)
    table.insert(0, 'Rank', table.index+1)
    return table


if __name__ == '__main__':
    allseason = list(filter(lambda f: f.isdigit(), os.listdir('team_data')))
    
    for season in allseason:
        table = create_table(season)
        table.to_csv(f'table/{season}.csv', index=False)
        print(f' Save table at table/{season}.csv')
        print()