# A Simple model from: https://www.pinnacle.com/en/betting-articles/Soccer/how-to-calculate-poisson-distribution/MD62MLXUMKMXZ6A8
# Only use the `attck strength` and `defence strength` to find the expected goals by poisson distribution.


import pandas as pd
from scipy.stats import poisson


class _StrengthContainer:
    def __init__(self, att_home=None, def_home=None, att_away=None, def_away=None):
        self.att_home = att_home
        self.def_home = def_home
        self.att_away = att_away
        self.def_away = def_away
        

class PoiDistModel:
    def __init__(self, season, team, rival, team_home=True):
        """
        e.g. season = '1920', team = 'Liverpool', rival = 'Spurs'
        team_home = True if Liverpool (arg `team`) is played at home
        
        Attributes / methods :
        self.mu    : the parameter of poisson distribution
        self.pmf() : find the corresponding pmf of self.mu
        """
        df = pd.read_csv(f'team_data/{season}/{team}.csv')
        is_home = df['isHome']
        
        # attack/defence strength of the team
        team_stren = _StrengthContainer(
            att_home=df.loc[is_home, 'SelfAS'].values[0],
            def_home=df.loc[is_home, 'SelfDS'].values[0],
            att_away=df.loc[~is_home, 'SelfAS'].values[0],
            def_away=df.loc[~is_home, 'SelfDS'].values[0]
        )
        
        # strength of the rival
        rival_stren = _StrengthContainer(
            att_home=df.loc[~is_home, 'RivalAS'].values[0],
            def_home=df.loc[~is_home, 'RivalDS'].values[0],
            att_away=df.loc[is_home, 'RivalAS'].values[0],
            def_away=df.loc[is_home, 'RivalDS'].values[0]
        )
        
        # the home/away goals in the entire league
        league_home_goals, league_away_goals = self._calc_league_avg_goals(season)
        
        if team_home:
            self.mu = team_stren.att_home * rival_stren.def_away * league_home_goals
        else:
            self.mu = team_stren.att_away * rival_stren.def_home * league_away_goals
        
    def _calc_league_avg_goals(self, season):
        """calculate the average home/away goals in the entire league"""
        last_season = f'{int(season[:2])-1:02d}{int(season[2:])-1:02d}'
        df_table = pd.read_csv(f'table/{last_season}.csv')
        home_goals = df_table['GoalsHome'].map(lambda s: int(s.split(':')[0])).sum()
        away_goals = df_table['GoalsAway'].map(lambda s: int(s.split(':')[0])).sum()
        return home_goals/380, away_goals/380
    
    def pmf(self, lower=0, upper=None):
        """lower/upper : the bounds of pmf"""
        if upper is None:
            upper = 6
        k = list(range(lower, upper+1))
        return poisson.pmf(k, self.mu)