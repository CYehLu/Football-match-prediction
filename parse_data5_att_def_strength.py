# calculate attack / defense strength based on the previous season
# reference: https://www.pinnacle.com/en/betting-articles/Soccer/how-to-calculate-poisson-distribution/MD62MLXUMKMXZ6A8

import os
import re
import glob
import numpy as np
import pandas as pd


class Strength:
    """
    Compute attck / defence strength
    """
    
    def __init__(self, season):
        """
        e.g. season=1920
        And it will calculate the attack/defence strength based on the statistics
        of the last (1819) season.
        level = 0 for Premier League, 1 for Championship League
        """
        self.season = season
        
    def _get_all_teams(self, season):
        allteams_path = glob.glob(f'team_data/{season}/*.csv')
        allteams = list(map(lambda s: re.findall('([A-Za-z ]+).csv$', s)[0], allteams_path))
        return allteams
        
    def _read_file(self, level):
        """return df (table of the last season)"""
        y1 = int(self.season[:2])
        y2 = int(self.season[2:])
        last_season = f'{y1-1:02d}{y2-1:02d}'
        
        if level == 0:
            return pd.read_csv(f'table/{last_season}.csv')
        elif level == 1:
            return pd.read_csv(f'table/Championship/csv/{last_season}.csv')
        else:
            raise ValueError('self.level should be 0 (Premier league) or 1 (Championship league)')
        
    def calc_strength(self, level):
        """
        The result is based on the previous season.
        ASH : Attack Strength at Home
        ASA : Attack Strength Away
        DSH : Defence Strength at Home
        DSA : Defence Strength Away
        """
        # table of last season
        df = self._read_file(level)
        
        # e.g. goals = '55:17', return (55, 17)
        split_goals = lambda goals: list(map(lambda s: int(s), goals.split(':')))
        
        dfcalc = pd.concat(
            [
                df['GoalsHome'].map(split_goals).apply(pd.Series),   # (20, 2)
                df['GoalsAway'].map(split_goals).apply(pd.Series)    # (20, 2)
            ],
            axis=1
        )
        dfcalc.columns = ['HomeGoal', 'HomeConceded', 'AwayGoal', 'AwayConceded']
        dfcalc.index = df['Team'] if level == 0 else df['Name']
        dfcalc.insert(0, 'Rank', list(range(1, dfcalc.shape[0]+1)))
        
        # League average...
        lhg = dfcalc['HomeGoal'].sum() / 380      # ...Home Goals
        lhc = dfcalc['HomeConceded'].sum() / 380  # ...Home Conceded
        lag = dfcalc['AwayGoal'].sum() / 380      # ...Away Goals
        lac = dfcalc['AwayConceded'].sum() / 380  # ...Away Conceded
        
        # Teams average...
        tms_hg = dfcalc['HomeGoal'] / 19        # ...Home Goals
        tms_hc = dfcalc['HomeConceded'] / 19    # ...Home Conceded
        tms_ag = dfcalc['AwayGoal'] / 19        # ...Away Goals
        tms_ac = dfcalc['AwayConceded'] / 19    # ...Away Conceded
        
        # Attack Strength at Home/Away
        dfcalc['ASH'] = tms_hg / lhg
        dfcalc['ASA'] = tms_ag / lag
        
        # Defence Strength at Home/Away
        dfcalc['DSH'] = tms_hc / lhc
        dfcalc['DSA'] = tms_ac / lac
        
        return dfcalc
    
    def compute_result(self):
        """
        The result is based on the previous season.
        ASH : Attack Strength at Home
        ASA : Attack Strength Away
        DSH : Defence Strength at Home
        DSA : Defence Strength Away
        isFromCL : True if this team was in Championship League in the previous season
        """
        # strength are calculated based on last season
        df_pl_strength = self.calc_strength(level=0)
        df_cl_strength = self.calc_strength(level=1)
        
        # table of this season
        df = pd.read_csv(f'table/{self.season}.csv')
        
        df_merge_pl = df[['Rank', 'Team', 'Points']].merge(
            df_pl_strength[['ASH', 'ASA', 'DSH', 'DSA']], 
            left_on='Team', right_index=True, 
        )
        df_merge_pl['isFromCL'] = False

        df_merge_cl = df[['Rank', 'Team', 'Points']].merge(
            df_cl_strength[['ASH', 'ASA', 'DSH', 'DSA']], 
            left_on='Team', right_index=True, 
        )
        df_merge_cl['isFromCL'] = True

        # final result
        df_final = pd.concat((df_merge_pl, df_merge_cl), axis=0).sort_values(by='Rank')
        
        return df_final
    
    
def append_strength_to_df_team(df_team, df_strength, team_name):
    """
    append these columns from to df_team:
    SelfAS, SelfDS, SelfFromCL, RivalAS, RivalDS, RivalFromCL
    """
    # deal with the attack/defense strength of the rival team
    # merge the ASH/ASA/DSH/DSA of the rival team
    df_tmp_rvl = df_team[['Round', 'isHome', 'Rival']].merge(
        df_strength[['Team', 'ASH', 'ASA', 'DSH', 'DSA', 'isFromCL']],
        left_on='Rival', right_on='Team', how='left'
    ).drop('Team', axis=1)

    # decide to keep ASH/DSH or ASA/DSA according to the (rival team) home or away match
    df_tmp_rvl = pd.concat(
        [
            df_tmp_rvl[df_tmp_rvl.isHome].drop(['ASH', 'DSH'], axis=1).rename(
                {'ASA': 'RivalAS', 'DSA': 'RivalDS', 'isFromCL': 'RivalFromCL'}, axis=1
            ),
            df_tmp_rvl[~df_tmp_rvl.isHome].drop(['ASA', 'DSA'], axis=1).rename(
                {'ASH': 'RivalAS', 'DSH': 'RivalDS', 'isFromCL': 'RivalFromCL'}, axis=1
            )
        ]
    ).sort_values(by='Round')


    # merge the AS/DS according to the home or away match
    df_tmp_self = df_team[['Round', 'isHome']].copy()
    df_tmp_self['Self'] = team_name

    df_tmp_self = df_tmp_self.merge(
        df_strength[['Team', 'ASH', 'ASA', 'DSH', 'DSA', 'isFromCL']],
        left_on='Self', right_on='Team', how='left'
    ).drop(['Team', 'Self'], axis=1)

    # decide to keep ASH/DSH or ASA/DSA according to the home or away match
    df_tmp_self = pd.concat(
        [
            df_tmp_self[df_tmp_self.isHome].drop(['ASA', 'DSA'], axis=1).rename(
                {'ASH': 'SelfAS', 'DSH': 'SelfDS', 'isFromCL': 'SelfFromCL'}, axis=1
            ),
            df_tmp_self[~df_tmp_self.isHome].drop(['ASH', 'DSH'], axis=1).rename(
                {'ASA': 'SelfAS', 'DSA': 'SelfDS', 'isFromCL': 'SelfFromCL'}, axis=1
            )
        ]
    ).sort_values(by='Round')


    df_tmp_self = df_tmp_self[['SelfAS', 'SelfDS', 'SelfFromCL']]
    df_tmp_rvl = df_tmp_rvl[['RivalAS', 'RivalDS', 'RivalFromCL']]

    df_team = pd.concat(
        [
            df_team,
            df_tmp_self,
            df_tmp_rvl
        ],
        axis=1
    )
    return df_team
    
    
if __name__ == '__main__':
    print('Test computing the attck/defense strength at the 1819 season')
    print('------------------------------------------------------------')
    print(Strength('1819').compute_result())
    print()
    
    print('Test merging strength dataframe to the original team data')
    print('---------------------------------------------------------')
    season = '1920'
    team = 'Man City'
    test_df = append_strength_to_df_team(
        pd.read_csv(f'team_data/{season}/{team}.csv'),
        Strength(season).compute_result(),
        team
    )
    print(test_df.iloc[10,:])
    print()
    
    print('Update team data')
    print('----------------')
    for iseason in range(11):
        season = str(1011 + iseason * 101)
        print(f'[{season}] --- ', end='  ')

        df_strength = Strength(season).compute_result()
        all_teams = df_strength['Team']

        for team in all_teams:
            print(team, end=' / ')
            df_team = pd.read_csv(f'team_data/{season}/{team}.csv')
            df_team = append_strength_to_df_team(df_team, df_strength, team)
            df_team.to_csv(f'team_data/{season}/{team}.csv', index=False)

        print()

    