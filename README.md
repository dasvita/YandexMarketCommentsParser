YandexMarketCommentsParser

Парсер на Python. 
С помощью библиотеки BeautifulSoup парсит дату, автора, оценку и текст комментариев с сайта https://market.yandex.ru/product--smartfon-apple-iphone-12-128gb/722974019/reviews?track=tabs, с каждой стараницы по очереди. Записывает распаршенные данные в базу данных Reviews.db. 
Для работы с базой данных использует библиотеку sqlite3.
