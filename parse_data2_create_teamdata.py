import os
import re
import glob
import numpy as np
import pandas as pd


class MakeTeamData:
    def __init__(self, filename):
        """ e.g. filename = './clean_data/1819.csv' """
        self.df_season = pd.read_csv(filename, index_col=0)
        self.allteams = sorted(self.df_season['HomeTeam'].unique())
        
        # e.g. filename = './clean_data/1819.csv'  -->  foldername = '1819'
        self.foldername = re.findall('.+/([0-9]{4}).csv', filename)[0]
        
        try:
            os.mkdir(f'./team_data/{self.foldername}')
        except FileExistsError:
            pass
        
    def _parse_team(self, team):
        """team: str, return: df of this team"""
        df_team = self.df_season[(self.df_season['HomeTeam'] == team) | (self.df_season['AwayTeam'] == team)].copy()
        df_team['Date'] = pd.to_datetime(df_team['Date'])
        df_team = df_team.sort_values(by='Date')
        df_team = df_team.reset_index(drop=True)
        
        # extract information from df_team to df2_team
        df2_team = df_team[['Date']].copy()

        # round
        df2_team['Round'] = list(range(1, df_team.shape[0]+1, 1))

        # if is home match
        ishome = df_team['HomeTeam'] == team
        df2_team['isHome'] = ishome

        # the rival team
        df2_team['Rival'] = pd.concat((
            df_team.loc[ishome, 'AwayTeam'], 
            df_team.loc[~ishome, 'HomeTeam']
        )).sort_index()
        
        # goals in the match
        df2_team['Goal'] = pd.concat((
            df_team.loc[ishome, 'HomeScore'],
            df_team.loc[~ishome, 'AwayScore']
        )).sort_index()

        # conceded in the match
        df2_team['Conceded'] = pd.concat((
            df_team.loc[ishome, 'AwayScore'],
            df_team.loc[~ishome, 'HomeScore']
        )).sort_index()

        # points earned in the match
        df2_team['Points'] = df_team['Winner']
        df2_team['Points'].replace(to_replace=team, value=3, inplace=True)
        df2_team['Points'].replace(to_replace='Draw', value=1, inplace=True)
        df2_team.loc[df2_team.Points.str.isnumeric() == False, 'Points'] = 0

        # cumulative points including this match
        df2_team['CumPoints'] = df2_team['Points'].cumsum()
        
        # cumulative points excluding this match
        df2_team['bCumPoints'] = df2_team['CumPoints'] - df2_team['Points']
        
        # points earned in the last five matches (excluding this one)
        df2_team['b5MatchPoints'] = df2_team['Points'].rolling(6, min_periods=1).sum() - df2_team['Points']
        
        # normalized points (=1: earned all points in the past five matches) earned in the last five matches (excluding this one)
        b5_max_points = df2_team['Round'].rolling(6, min_periods=1).count() * 3 - 3
        b5_max_points[b5_max_points == 0] = np.nan
        df2_team['b5MatchPointRatio'] = df2_team['b5MatchPoints'] / b5_max_points
        
        # cumulative goals (excluding this matches)
        df2_team['bCumGoal'] = df2_team['Goal'].cumsum() - df2_team['Goal']
        
        # cumulative goals in the past five matches (excluding this one)
        df2_team['b5MatchGoal'] = df2_team['Goal'].rolling(6, min_periods=1).sum() - df2_team['Goal']
        
        # cumulative conceded (excluding this matches)
        df2_team['bCumConceded'] = df2_team['Conceded'].cumsum() - df2_team['Conceded']
        
        # cumulative conceded in the past five matches (excluding this one)
        df2_team['b5MatchConceded'] = df2_team['Conceded'].rolling(6, min_periods=1).sum() - df2_team['Conceded']
        
        ### only consider the matches at home
        # points earned in the last five home matches (excluding this one)
        df2_team_home = df2_team[df2_team.isHome].copy()
        df2_team_home['b5HomeMatchPoints'] = df2_team_home['Points'].rolling(6, min_periods=1).sum() - df2_team_home['Points']
        
        # normalized points earned in the last five home matches (excluding this one)
        b5_max_points = df2_team_home['Round'].rolling(6, min_periods=1).count() * 3 - 3
        b5_max_points[b5_max_points == 0] = np.nan
        df2_team_home['b5HomeMatchPointRatio'] = df2_team_home['b5HomeMatchPoints'] / b5_max_points
        
        # cumulative goals in the home matches (excluding this match)
        df2_team_home['bHomeCumGoal'] = df2_team_home['Goal'].cumsum() - df2_team_home['Goal']
        
        # cumulative conceded in the home matches (excluding this match)
        df2_team_home['bHomeCumConceded'] = df2_team_home['Conceded'].cumsum() - df2_team_home['Conceded']
        
        # cumulative goals in the last five home matches (excluding this match)
        df2_team_home['b5HomeMatchGoal'] = df2_team_home['Goal'].rolling(6, min_periods=1).sum() - df2_team_home['Goal']
        
        # cumulative conceded in the last five home matches (excluding this match)
        df2_team_home['b5HomeMatchConceded'] = df2_team_home['Conceded'].rolling(6, min_periods=1).sum() - df2_team_home['Conceded']
        
        ### only consider the matches at away
        # points earned in the last five away matches (excluding this one)
        df2_team_away = df2_team[~df2_team.isHome].copy()
        df2_team_away['b5AwayMatchPoints'] = df2_team_away['Points'].rolling(6, min_periods=1).sum() - df2_team_away['Points']
        
        # normalized points earned in the last five away matches (excluding this one)
        b5_max_points = df2_team_away['Round'].rolling(5, min_periods=1).count() * 3 - 3
        b5_max_points[b5_max_points == 0] = np.nan
        df2_team_away['b5AwayMatchPointRatio'] = df2_team_away['b5AwayMatchPoints'] / b5_max_points
        
        # cumulative goals in the away matches (excluding this match)
        df2_team_away['bAwayCumGoal'] = df2_team_away['Goal'].cumsum() - df2_team_away['Goal']
        
        # cumulative conceded in the away matches (excluding this match)
        df2_team_away['bAwayCumConceded'] = df2_team_away['Conceded'].cumsum() - df2_team_away['Conceded']
        
        # cumulative goals in the last five away matches (excluding this match)
        df2_team_away['b5AwayMatchGoal'] = df2_team_away['Goal'].rolling(6, min_periods=1).sum() - df2_team_away['Goal']
        
        # cumulative conceded in the last five away matches (excluding this match)
        df2_team_away['b5AwayMatchConceded'] = df2_team_away['Conceded'].rolling(6, min_periods=1).sum() - df2_team_away['Conceded']
        
        ### concat the dataframes
        df2_team = pd.concat(
            [
                df2_team,
                df2_team_home.drop(labels=df2_team.columns, axis=1),
                df2_team_away.drop(labels=df2_team.columns, axis=1)
            ],
            axis=1
        )
        
        return df2_team
        
    def parse(self):
        for team in self.allteams:    
            print(team + ' ...', end=' ')
            df_team = self._parse_team(team)
            df_team.to_csv(f'./team_data/{self.foldername}/{team}.csv', index=False)
            print('[Done]')
            
            
if __name__ == '__main__':
    # test the parse result
    df = MakeTeamData('clean_data/1819.csv')._parse_team('Liverpool')
    print('Test parsing Liverpool data at 1819 season')
    print('------------------------------------------')
    print(df.iloc[:10,:15])
    print()
    
    print('Start to parse all data')
    print('----------------------')
    csvfiles = glob.glob('./clean_data/*.csv')
    csvfiles = list(map(lambda cfile: cfile.replace('\\', '/'), csvfiles))

    for cfile in csvfiles:
        print(f' =========== {cfile} ============')
        MakeTeamData(cfile).parse()
        print()