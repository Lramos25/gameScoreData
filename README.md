Video Game Rankings and Sales
Web scraping personal project to see if any correlation between critic scores and user scores and total sales. 

Tasks:
•	Utilize requests and BeautifulSoup4 to scrap for data on each game (game title, game publisher, genre scores etc.) 
•	Clean data and handling of unique cases
•	Create MySQL connection
•	Store scraped data to db
•	Upload and clean sales data from csv file 
•	Analyze and visualize data

Scrap Data  from (https://www.metacritic.com/browse/games/score/metascore/all/all)

	
  I was able to scrap most of the data from the main search results page. The Developer and genre information was on each individual game page. This required using a second scrap after the initial. During the initial scrap the href for each game page was located and a second iteration on the that page was done. Essentially this causes the initial page to get data on the first game, then update the url with the game specific page, go grab that data and then come back to the first page to get the next game. There must be a better method to go about this. 
	
  The user and critic scores are divided into four separate classes. This required a find method for each class and a conditional statement to find the score. Handled a few critic/user scores with text of ‘tbd’ and record these as 0. All scores are converted from text to float for use later. This will need to be accounted for when analyzing the data.
	
  I utilized pandas to create a data frame which allowed me to see the data pulled for QA purposes. This has been removed from the final product.
  
  Creating the connection the MySQL took a bit of research. Once I found the correct information needed it was straight forward. After getting this going all data inserted without issue.
	
  Once the sale data table was created and the data uploaded the initial cleaning started. The first obvious issue was the total sales data. Most games are released on several platforms. The means there are several records for many of the games. Each of these records has their own sales data. I could not delete duplicate records without first getting the total for that game from each platform. Getting the rolling sum is easy with a windows function but updating the table with this method proved to be an issue. I tried several methods but in the end just using a nested function was the best way to go.
	
	UPDATE gameSales
	SET totalSales = 
	(
	SELECT SUM(Global_Sales)
	FROM gameSales as secondTable
	WHERE gameSales.Name = secondTable.Name
	)
	
  This updated the total sales data for every instance of a game without regard to the platform. The current output still has duplicate records for the same games on different platforms but the total sales data is updated for each one. Now I can remove duplicates without the need to ensure the correct record remains. 

((***INSERT PIC HERE***))

  Before moving on with deleting duplicates I like to create a backup of the cleaned data. This will allow me to come back later if I find any discrepancies or allow me to restore the data if I make a mistake. I also run tests on a small “test” table in a separate db as a redundant precaution.  Because this is my db and the data set is just under 17k, I don’t think there are any draw backs to the extra care – and it just provides more chances for me to practice. 

  For reference, here is the test SQL commands:
	
	CREATE TABLE Test
	(
	Rank varchar(max), 
	Name varchar(max), 
	Platform varchar(max), 
	genre varchar(max),
	totalSales float
	)

	INSERT INTO Test VALUES 
	('1', 'first', 'ps', 'action', 100),
	('2', 'second', 'test', 'action', 10),
	('3', 'third', 'test', 'action', 20),
	('4', 'first', 'pc', 'action', 40),
	('5', 'first', 'xbox', 'action', 50),
	('6', 'sixth', 'test', 'action', 15),
	('7', 'seventh', 'test', 'action', 120),
	('8', 'eighth', 'test', 'action', 200),
	('9', 'ninth', 'test', 'action', 45),
	('10', 'tenth', 'test', 'action', 6)


	with CTE_Test
		AS
		(
			SELECT *,
				ROW_NUMBER() OVER(PARTITION BY [Name] ORDER BY [Name]) [RowNumber]
			FROM Test
		)

	DELETE FROM CTE_Test
	WHERE [RowNumber] > 1

	
 	
  After deleting duplicates, I dropped the various regional sales data. I had this data for verification purposes. This data is not important to me for this project.
The final part for cleaning this data is to make sure all game collection sets are marked accordingly. Game collection sets have several older games in one package and I don’t want these to count for any particular game title or genre. I want to keep these as their own so we can look at how these do comparatively. 

  A quick glance shows me the gameData table has 18k rows compared to the 11K rows in game sales. It is obvious I need to go through the gameData table to clean this up as well. 
Once this is done I need to join the two tables but I need to make sure any titles on one but not the other has a default value. After removing duplicates an doing some minor cleaning on game titles there is a difference of 160 records between the two tabels. 


  I now have a clean set of data from reliable sources. It is time to start visualizing and working on the comparison analysis. For this, I am using Microsoft PowerBI. I will want charts to show the how game sales and scores relate by game titles, genre, Platform, Publisher and year. I also want to show the difference between critic score and user score to see if there can be any impact on game sales.
