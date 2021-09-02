import os
import re
import glob
import numpy as np
import pandas as pd


for iseason in range(11):
    season = str(1011 + iseason * 101)
    print(f'[{season}] --- ', end='  ')
    
    allteams = [re.findall('([A-Za-z ]+).csv$', t)[0] for t in glob.glob(f'team_data/{season}/*.csv')]
    
    # read df of all teams
    df_allteams_pts = {}
    for team in allteams:
        df_allteams_pts[team] = pd.read_csv(f'team_data/{season}/{team}.csv')['bCumPoints']

    df_allteams_pts = pd.DataFrame(df_allteams_pts).T
    
    # mean / std cumulative points
    mean_pts = df_allteams_pts.mean()
    std_pts = df_allteams_pts.std()

    # result: standardized cumulative points
    # result.index : all teams, result.columns : round (start from 0)
    result = (df_allteams_pts - mean_pts) / std_pts
    
    # insert standardized cumulative points information into team_data
    for team in allteams:
        print(team, end=' / ')
        std_cumpts = result.loc[team,:]
        df_team = pd.read_csv(f'team_data/{season}/{team}.csv')
        df_team['bStdCumPoints'] = std_cumpts
        df_team.to_csv(f'team_data/{season}/{team}.csv', index=False)
    print()