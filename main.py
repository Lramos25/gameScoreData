import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sqlite3

conn = sqlite3.connect('gamedata2')
cur = conn.cursor()

# uncomment to create db table but then recomment out
#cur.execute('''CREATE TABLE gameData2(name TEXT, platform TEXT, releaseDate TEXT, criticScore TEXT, userScore TEXT, developer TEXT, genres TEXT) ''')

def getGameData(url):
    user_agent = {'User-agent': 'Mozilla/5.0 '} # adjust to your computer user agent
    response = requests.get(url, headers = user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')

    for game in soup.find_all('td', class_ = 'clamp-summary-wrap'):
        name = game.find('h3').text.strip()

        platform = game.find('span', class_='data').text.strip()
        
        releaseDate = game.select('div.clamp-details span')[2].text
        
        # critic score - data can be in different classes depending on score
        score_list = [
        game.find('div', class_='metascore_w large game positive'),
        game.find('div', class_='metascore_w large game mixed'),
        game.find('div', class_='metascore_w large game negative')
        ]
        
        # Filtering "not none" element in the score_list
        criticScore = [s.text for s in score_list if s is not None][0]

        # Same process for user score as for critic score
        score_list =[
        game.find('div', class_='metascore_w user large game positive'),
        game.find('div', class_='metascore_w user large game mixed'),
        game.find('div', class_='metascore_w user large game negative'),
        game.find('div', class_='metascore_w user large game tbd')
        ]

        userScore = [s.text for s in score_list if s is not None][0]
         
        # Retrieve url for reviews page:
        url_info = game.find('a', class_='title')['href']
        url_info = 'https://www.metacritic.com'+url_info
        
        response_info = requests.get(url_info, headers = user_agent)
        soup_info = BeautifulSoup(response_info.text, 'html.parser')

        # Developer
        developer = soup_info.find('li', class_ = 'summary_detail developer')
        
        if developer is not None:
            developer = developer.find('span',class_='data').text.strip() 
        else:
            developer = 'No info'  

        # Genre info
        genres = soup_info.find('li', class_ = 'summary_detail product_genre')
        
        if genres is not None:
            genres = genres.find('span', class_='data').text.strip()
        else:
            genres = 'No info'

        #print(name, platform, releaseDate, criticScore, userScore, developer, genres)
        cur.execute('''INSERT INTO gameData2 VALUES(?,?,?,?,?,?,?)''', (name, platform, releaseDate, criticScore, userScore, developer, genres))
    return

#adjust for number of pages up to 180 
for page in range(1):
    try:
        getGameData('https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page='+str(page))
    except:
        pass

conn.commit()

# Read db into dataframe
df = pd.read_sql_query("SELECT * FROM gameData2", conn)
print(df)

conn.close()
