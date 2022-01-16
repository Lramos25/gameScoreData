import requests
from bs4 import BeautifulSoup
import re
import pandas as pd #used duing the intial building to help see output, no longer needed so feel free to remove it.
import sys
import pyodbc as odbc

for page in range(100):
    
    data = 'https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page='+str(page)

    user_agent = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62'}
    response = requests.get(data, headers = user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')

    allGameData = []

    for game in soup.find_all('td', class_ = 'clamp-summary-wrap'):
        
        name = game.find('h3').text.strip()

        platform = game.find('span', class_='data').text.strip()
        
        releaseDate = game.select('div.clamp-details span')[2].text

        # critic score - data can be in different classes 
        score_list = [
        game.find('div', class_='metascore_w large game positive'),
        game.find('div', class_='metascore_w large game mixed'),
        game.find('div', class_='metascore_w large game negative')
        ]
        
        # Filtering "not none" element in the score_list
        criticScore = [s.text for s in score_list if s is not None][0]
        criticScore = float(criticScore)

        # Same process for user score as for critic score
        score_list =[
        game.find('div', class_='metascore_w user large game positive'),
        game.find('div', class_='metascore_w user large game mixed'),
        game.find('div', class_='metascore_w user large game negative'),
        game.find('div', class_='metascore_w user large game tbd')
        ]
    #Addresses scores of "tbd"
        userScore = [s.text for s in score_list if s is not None][0]
        if userScore == 'tbd':
            userScore = 0
        else:
            userScore = userScore

        userScore = float(userScore)

         
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
  
        else:
            developer = 'No info'  

        # Get genre info (multiple genres are separated in our entry)
        genres = soup_info.find('li', class_ = 'summary_detail product_genre')
        
        if genres is not None:
            genres = genres.find('span', class_='data').text.strip()
        else:
            genres = 'No info'

        fullGameData = [name,
                        platform,
                        releaseDate,
                        criticScore,
                        userScore,
                        developer,
                        genres
                        ]

        allGameData.append(fullGameData)


    DRIVER = 'SQL Server'
    SERVER_NAME = 'DESKTOP-RJHR8U1\SQLEXPRESS'
    DATABASE_NAME = 'GameData'

    conn_string = f"""
        Driver={{{DRIVER}}};
        Server={SERVER_NAME};
        Database={DATABASE_NAME};
        Trust_Connection=yes;
    """

    try:
        conn = odbc.connect(conn_string)
    except Exception as e:
        print(e)
        print('task is terminated')
        sys.exit()
    else:
        cursor = conn.cursor()


    insert_statement = """
        INSERT INTO gameData
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    try:
        for record in allGameData:
            print(record)
            cursor.execute(insert_statement, record)        
    except Exception as e:
        cursor.rollback()
        print(e.value)
        print('transaction rolled back')
    else:
        print('records inserted successfully')
        cursor.commit()
        cursor.close()

    print('connection closed')
    conn.close()
