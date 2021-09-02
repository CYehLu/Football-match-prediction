# This model is just use the average home/away goals of last season to predict the future goals.

import pandas as pd
from scipy.stats import poisson


class HomeAwayModel:
    """
    find the average home/away goals from the previous season
    and use this result to predict the future matchs
    """
    
    def __init__(self, season, team, team_home=True):
        """e.g. season = '1920', team = 'Liverpool' """
        self.team_home = team_home
        
        last_season = f'{int(season[:2])-1:02d}{int(season[2:])-1:02d}'
        df_table = pd.read_csv(f'table/{last_season}.csv')
        
        team_idx = df_table['Team'] == team       
        
        if team_idx.sum() == 0:
            # maybe `team` is from Championship League
            df_table = pd.read_csv(f'table/Championship/csv/{last_season}.csv')
            team_idx = df_table['Name'] == team
            
            if team_idx.sum() == 0:
                raise ValueError(f"Wrong name of the team! ({team})")
                
        self.avg_goal_home = df_table.loc[team_idx, 'GoalsHome'].map(lambda s: int(s.split(':')[0])).values / 19
        self.avg_goal_away = df_table.loc[team_idx, 'GoalsAway'].map(lambda s: int(s.split(':')[0])).values / 19
        self.mu = self.avg_goal_home[0] if self.team_home else self.avg_goal_away[0]
        
    def calc(self):
        if self.team_home:
            return self.avg_goal_home[0]
        else:
            return self.avg_goal_away[0]
            
    def pmf(self, lower=0, upper=None):
        if upper is None:
            upper = 6
        k = list(range(lower, upper+1))
        return poisson.pmf(k, self.mu)