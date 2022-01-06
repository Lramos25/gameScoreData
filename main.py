import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import sqlite3

conn = sqlite3.connect('gamedata')


def getGameData(url):
    user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}
    response = requests.get(url, headers = user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')

    for game in soup.find_all('td', class_ = 'clamp-summary-wrap'):
        name = game.find('h3').text.strip()

        platform = game.find('span', class_='data').text.strip()
        #platform = platform.replace('\n','')
        #platform = platform.replace(' ','')
        
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
         
        # Into the game page
        # Getting the url of the reviews page:
        url_info = game.find('a', class_='title')['href']
        url_info = 'https://www.metacritic.com'+url_info
        
        # Getting into the game page:
        response_info = requests.get(url_info, headers = user_agent)
        soup_info = BeautifulSoup(response_info.text, 'html.parser')

        # Get developer info
        developer = soup_info.find('li', class_ = 'summary_detail developer')
        
        if developer is not None:
            developer = developer.find('span',class_='data').text.strip()
            #developer = developer.replace('\n','')
            #developer = developer.replace(' ','')  
        else:
            developer = 'No info'  

        # Get genre info (multiple genres are separated in our entry)
        genres = soup_info.find('li', class_ = 'summary_detail product_genre')
        
        if genres is not None:
            genres = genres.find_all('span', class_='data')
            genre=''

            for item in genres:
                if genre:
                    genre = genre + ' / ' + item.text
                else:
                    genre = item.text
        else:
            genres = 'No info'

        print(name)
    return

#adjust for number of pages up to 180 
for page in range(1):
    getGameData('https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page='+str(page))
