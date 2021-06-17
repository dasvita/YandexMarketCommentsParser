from bs4 import BeautifulSoup
import requests
import sqlite3
import time


# Парсит html документ, возвращает спсок кортежей,
# где каждый кортеж имеет вид - (дата, автор, рейтинг, комментарий).
def parse(html_data):
    soup = BeautifulSoup(html_data, "lxml")

    reviews = soup.findAll("div", attrs={"itemprop": "review"})

    results_list = []

    for review in reviews:
        date_content = review.find("meta", attrs={"itemprop": "datePublished"})
        date = date_content["content"]

        author_content = review.find("meta", attrs={"itemprop": "author"})
        author = author_content["content"]

        rating_content = review.find("div", attrs={"itemprop": "reviewRating"})
        rating = rating_content.meta["content"]

        comment_content = review.find("meta", attrs={"itemprop": "description"})
        comment = comment_content["content"]

        review_tuple = (date, author, rating, comment)

        results_list.append(review_tuple)

    return results_list


# Находит на странице указатель на следующую страницу,
# формирует и возвращает ссылку для перехода на следующую страницу.
def get_next_page_url(html_data):
    soup = BeautifulSoup(html_data, "lxml")
    tag = soup.find("a", attrs={"aria-label": "Следующая страница"})
    if tag is None:
        return None
    else:
        return "https://market.yandex.ru/" + tag["href"]


# Добавляет распраршенные данные в базу данных, в таблицу Reviews.
def add_parsed_data_to_db(date, author, rating, comment):
    try:
        sqlite_connection = sqlite3.connect('Reviews.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = """INSERT INTO Reviews
                            (Date, Author, Rating, Comment_text)
                            VALUES (?, ?, ?, ?);"""
        data_tuple = (date, author, rating, comment)
        cursor.execute(sqlite_insert_query, data_tuple)
        sqlite_connection.commit()

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Запись в SQLite закончена")


# Основной цикл программы, вызывающий все остальные части.
# Отправляет get запрос, парсит содержимое ответа функцией parse(),
# записывает данные в базу данных функцией add_parsed_data_to_db(),
# получает слыку на след. страницу функцией get_next_page_url(data),
# выполняется пока получет новый url.
# Принимает на входе url и headers для get запроса.
def main_loop(url, headers):
    while True:
        try:
            response = requests.get(url, headers=headers)
            response.encoding = "UTF-8"
            data = response.text
            parsed_reviews = parse(data)

            for review in parsed_reviews:
                add_parsed_data_to_db(
                    parsed_reviews[parsed_reviews.index(review)][0],
                    parsed_reviews[parsed_reviews.index(review)][1],
                    parsed_reviews[parsed_reviews.index(review)][2],
                    parsed_reviews[parsed_reviews.index(review)][3],
                )

        except TypeError:
            break

        finally:
            time.sleep(6)

            url = get_next_page_url(data)

            if url is None:
                break


url = "https://market.yandex.ru/product--smartfon-apple-iphone-12-128gb/722974019/reviews?track=tabs"

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image\
    /avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
    "Connection": "keep-alive",
    "Host": "market.yandex.ru",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit\
    /537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
}


main_loop(url, headers)
