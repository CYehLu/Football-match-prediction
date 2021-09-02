# `raw_txt` from: https://www.sofascore.com/tournament/football/england/championship/18

import os
import re
import glob
import numpy as np
import pandas as pd


def create_table(season):
    dfs_dict = dict()
    
    for table_type in ['all', 'home', 'away']:
        path = f'table/Championship/raw_txt/{table_type}/{season}'
        with open(path) as file:
            content = file.readlines()
            
        df = pd.DataFrame(
            np.array(content).reshape(-1, 9),
            columns=['Rank', 'FullName', 'Name', 'PlayedMatchs', 'Win', 'Draw', 'Loss', 'Goals', 'Points']
        )
        df = df.applymap(lambda s: s.strip())
        intcol = ['PlayedMatchs', 'Win', 'Draw', 'Loss', 'Points']
        df[intcol] = df[intcol].applymap(lambda s: int(s))
        
        dfs_dict[table_type] = df
        
    df_final = dfs_dict['all'].copy()
    df_home = dfs_dict['home'].copy()
    df_away = dfs_dict['away'].copy()
    
    df_final = df_final.merge(
        df_home[['FullName', 'Win', 'Draw', 'Loss', 'Goals']], 
        on='FullName', 
        suffixes=('', 'Home')
    ).merge(
        df_away[['FullName', 'Win', 'Draw', 'Loss', 'Goals']], 
        on='FullName',
        suffixes=('', 'Away')
    )
    
    df_final['Name'] = df_final['Name'].str.replace('Wolverhampton', 'Wolves')
    return df_final
    
    
if __name__ == '__main__':
    seasons = list(filter(lambda s: s.endswith('.txt'), os.listdir('table/Championship/raw_txt/all/')))

    for season in seasons:
        print(f'season {season} -- ', end='')
        table = create_table(season)
        table.to_csv(f'table/Championship/csv/{season.replace("txt", "csv")}', index=False)
        print('[done]')