import glob
import pandas as pd


class ParseRawData:
    def __init__(self, filename):
        with open(filename) as file:
            self.content = file.readlines()
            
    def _is_date(self, line):
        day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return any(map(lambda d: d in line, day))
    
    def _parse_date(self, line_date):
        """
        e.g. line_date = 'Sunday 22 May 2011\n' 
        return : ('2011-05-22', 'Sunday')
        """
        weekday = line_date.split()[0]
        date = pd.to_datetime(line_date).strftime('%Y-%m-%d')
        return date, weekday
    
    def _parse_match(self, i):
        """
        e.g.
        ====
        Chelsea     <---- i should be here
        2-0 
        Wolves

         Stamford Bridge, 
        London
                    <---- returned i is here

        Crystal Palace
        1-1 
        Spurs

         Selhurst Park, 
        London
        """
        content = self.content
        match_info = []    # List: [HomeTeam, Result, AwayTeam, Stadium, City]
        
        while len(match_info) < 5 and i < len(content):
            line = content[i]
            if line.strip():
                match_info.append(line.strip())
            i += 1
                
        home_team = match_info[0]
        away_team = match_info[2]
        home_score, away_score = match_info[1].split('-')
        stadium = match_info[3]
        city = match_info[4]
        
        if home_score > away_score:
            winner = home_team
        elif home_score < away_score:
            winner = away_team
        elif home_score == away_score:
            winner = 'Draw'
        
        # returned match info
        rmatch_info = [home_team, int(home_score), int(away_score), away_team, winner, stadium.strip(','), city]
        
        return i, rmatch_info
        
    def parse(self):
        content = self.content
        length = len(content)
        
        matchs_info = []    # List_matchs[List[str]]
        i = 0
        while i < length:
            line = content[i]
            
            if line.strip():
                
                if self._is_date(line):
                    date, weekday = self._parse_date(line)
                    i += 1

                else:
                    i, match_info = self._parse_match(i)
                    matchs_info.append([date, weekday] + match_info)
                    
            else:
                i += 1
                
        df = pd.DataFrame(matchs_info)
        df.columns = ['Date', 'Weekday', 'HomeTeam', 'HomeScore', 'AwayScore', 'AwayTeam', 'Winner', 'Stadium', 'City']
        return df
    
    
if __name__ == '__main__':
    # test the parse result
    test = ParseRawData('./raw_data/1920.txt').parse()
    print('Test parsing 1920 season raw data')
    print('---------------------------------')
    print(test)
    print()
    
    print('Start to parse all data')
    print('----------------')
    allseason = sorted(glob.glob('raw_data/*.txt'))

    for season in allseason:
        print(season)

        # e.g. \\raw_data\\1011.txt -> 1011.csv
        savefilename = season.split('\\')[1].replace('txt', 'csv')

        df = ParseRawData(season).parse()
        df.to_csv(f'./clean_data/{savefilename}')