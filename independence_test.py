# check the statistical independence between the goals scored by both teams in the match


import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency


def read_game_result(start, end):
    n_season = int(end[:2]) - int(start[:2]) + 1

    df = []

    for i in range(n_season):
        season = f'{int(start[:2])+i:02d}{int(start[2:])+i:02d}'
        df_iseason = pd.read_csv('clean_data/1011.csv', index_col=0)
        df.append(df_iseason)

    df = pd.concat(df)
    df = df.reset_index(drop=True)
    return df


def convert_contingency(df, max_goals=4):
    df.loc[df.HomeScore >= max_goals, 'HomeScore'] = max_goals
    df.loc[df.AwayScore >= max_goals, 'AwayScore'] = max_goals

    df['tmp'] = 1

    contingency = pd.pivot_table(df, index='HomeScore', columns='AwayScore', values='tmp', aggfunc=np.sum)
    contingency = contingency.fillna(0)
    contingency = contingency.astype(int)

    contingency.columns = list(range(0, max_goals)) + [f'>{max_goals}']
    contingency.columns.name = 'Away goals'
    contingency.index = list(range(0, max_goals)) + [f'>{max_goals}']
    contingency.index.name = 'Home goals'
    return contingency


if __name__ == '__main__':
    df = read_game_result(start='1718', end='1718')
    contingency = convert_contingency(df)
    print('Contingency table:')
    print('-----------------')
    print(contingency)
    print()
    
    chi2, p_value, dof, _ = chi2_contingency(contingency)
    print(f'Chi square statistic = {chi2:.4f}')
    print(f'degree of freedom    = {dof}')
    print(f'p-value              = {p_value:.4f}')