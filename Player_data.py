import pandas as pd
import requests
from bs4 import BeautifulSoup



class PlayerData:
    def __init__(self):
        self.urlPassing = "https://www.pro-football-reference.com/years/2024/passing.htm"
        self.urlReceiving = "https://www.footballdb.com/statistics/nfl/player-stats/receiving"
        self.urlRushing = "https://www.footballdb.com/statistics/nfl/player-stats/rushing"
        self.urlConversions = "https://www.teamrankings.com/nfl/player-stat/scoring-two-point-conversions"
        self.urlFumbles = "https://www.teamrankings.com/nfl/player-stat/fumbles-lost"
        self.passing = self.load_passing_data()
        self.receiving = self.load_receiving_data()
        self.rushing = self.fetch_rushing_data()
        self.conversions = self.load_conversion_data()
        self.fumbles = self.load_fumble_data()
        self.final_data = self.merge_datasets()


    def load_passing_data(self):
        passing = pd.read_html(self.urlPassing)[0]
        passing.drop(columns=['Age', 'Awards', 'QBR', 'GS', 'QBrec', 'Cmp', 'Att', "Cmp%", 'TD%', 'Int%', '1D', 'Succ%', 'Lng', 'Y/A', 'AY/A', 'Y/C', 'Rate', 'Yds.1', 'Sk%', 'NY/A', 'ANY/A', '4QC', 'GWD'], inplace=True)
        passing.rename(columns={'G': 'Games', 'Yds': 'Passing Yards', 'Pos': 'Position', 'TD' : 'Passing TD'}, inplace=True)
        passing['Player'] = passing['Player'].str.replace(' Jr.', '', regex=False)
        passing.drop(columns=['Team'], inplace=True)
        passing = passing.replace(r'\.', '', regex=True)
        passing.to_excel('passing.xlsx')
        return passing

    def load_receiving_data(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.footballdb.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(self.urlReceiving, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table:
                headers = [header.text.strip() for header in table.find_all('th')]
                data = []
                last_player = None
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells:
                        player_name = cells[0].text.strip()
                        if player_name == "":
                            player_name = last_player
                        else:
                            last_player = player_name
                        # Remove everything after the last period in player names
                        player_name = player_name.rsplit('.', 1)[0]  # Keeps everything before the last period
                        data.append([player_name] + [cell.text.strip() for cell in cells[1:]])
                receiving = pd.DataFrame(data, columns=headers)

                # Remove last letter from the 'Player' column (if this is still needed)
                receiving['Player'] = receiving['Player'].str[:-1]

                # Remove rows where 'Player' column is blank
                receiving = receiving[receiving['Player'].notna() & (receiving['Player'] != "")]

                receiving.drop(columns={'Lg', 'FD', 'Tar', 'YAC', 'Avg', 'YPG'}, inplace=True)
                receiving.rename(columns={'Yds': 'Receiving Yards', 'Gms': 'Games', 'TD' : 'Receiving TD'}, inplace=True)

                # Normalize team names
                team_corrections = {
                    'LV': 'LVR', 'KC': 'KAN', 'GB': 'GNB', 'TB': 'TAM', 'NO': 'NOR',
                    'LA': 'LAR', 'NE': 'NWE', 'SF': 'SFO'
                }
                receiving['Team'] = receiving['Team'].replace(team_corrections)
                receiving['Player'] = receiving['Player'].str.replace(' Jr.', '', regex=False)
                receiving.drop(columns=['Team'], inplace=True)
                # Assuming your DataFrame is named df
                receiving = receiving.replace(r'\.', '', regex=True)
                receiving['Player'] = receiving['Player'].str.replace(r'(Amon-Ra St Brown).*', r'\1', regex=True)
                receiving.to_excel('hello.xlsx')
                return receiving
        raise ValueError('Status code is not right')


    def load_conversion_data(self):
        conversions = pd.read_html(self.urlConversions)[0]
        conversions.drop(columns=['Team', 'Rank', 'Pos'], inplace=True)
        conversions.rename(columns={'Value': '2pt Conversion'}, inplace=True)
        conversions['Player'] = conversions['Player'].str.replace(' Jr.', '', regex=False)
        
        return conversions

    def fetch_rushing_data(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.footballdb.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(self.urlRushing, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table:
                headers = [header.text.strip() for header in table.find_all('th')]
                data = []
                last_player = None
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if cells:
                        player_name = cells[0].text.strip()
                        if player_name == "":
                            player_name = last_player
                        else:
                            last_player = player_name
                        # Remove everything after the last period in player names
                        player_name = player_name.rsplit('.', 1)[0]  # Keeps everything before the last period
                        data.append([player_name] + [cell.text.strip() for cell in cells[1:]])
                rushing = pd.DataFrame(data, columns=headers)

                # Remove last letter from the 'Player' column (if this is still needed)
                rushing['Player'] = rushing['Player'].str[:-1]

                # Remove rows where 'Player' column is blank
                rushing = rushing[rushing['Player'].notna() & (rushing['Player'] != "")]

                rushing.drop(columns=['Lg', 'FD'], inplace=True)
                rushing.rename(columns={'Yds': 'Rush Yards', 'Pos': 'Position', 'Gms': 'Games'}, inplace=True)
                # Normalize team names
                team_corrections = {
                    'LV': 'LVR', 'KC': 'KAN', 'GB': 'GNB', 'TB': 'TAM', 'NO': 'NOR',
                    'LA': 'LAR', 'NE': 'NWE', 'SF': 'SFO'
                }
                rushing['Team'] = rushing['Team'].replace(team_corrections)
                rushing['Player'] = rushing['Player'].str.replace(' Jr.', '', regex=False)
                rushing['Rush Yards'] = rushing['Rush Yards'].str.replace(',', '', regex=False)
                rushing.drop(columns=['Team'], inplace=True)
                rushing = rushing.replace(r'\.', '', regex=True)
                rushing['Player'] = rushing['Player'].str.replace(r'(Amon-Ra St Brown).*', r'\1', regex=True)
                rushing.to_excel('hello1.xlsx')
                return rushing
        raise ValueError('Status code is not right')

    def load_fumble_data(self):
        fumbles = pd.read_html(self.urlFumbles)[0]
        fumbles.drop(columns=['Team', 'Rank'], inplace=True)
        fumbles.rename(columns={'Value' : 'Fmb', 'Pos' : 'Position'}, inplace=True)
        fumbles['Player'] = fumbles['Player'].str.replace(' Jr.', '', regex=False)
        return fumbles

    def merge_datasets(self):
        partial_merge = pd.merge(self.passing, self.receiving, on=['Player'], how='outer')
        final_merged_data = pd.merge(partial_merge, self.rushing, on=['Player'], how='outer')
        final_merged_data2 = pd.merge(final_merged_data, self.conversions, on=['Player'], how='outer')
        final_merged_data2.drop(columns=['Rk'], inplace=True)
        final_merged_data1 = pd.merge(final_merged_data2, self.fumbles, on=['Player'], how='outer')
        final_merged_data1 = final_merged_data1[~final_merged_data1['Player'].str.contains('Player', na=False)]
        final_merged_data1.to_excel('final.xlsx')
        return final_merged_data1


























