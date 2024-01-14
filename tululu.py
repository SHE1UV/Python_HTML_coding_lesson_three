import os
import sys
import logging
import argparse
from time import sleep
from urllib.parse import urljoin, urlsplit, unquote
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

logger = logging.getLogger(__name__)


def fetch_book_ids():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', default=1, type=int)
    parser.add_argument('-e', default=10, type=int)
    return parser.parse_args()


def parse_book_page(html, url):
    soup = BeautifulSoup(html, 'lxml')

    return {
        "title": title,
        "author": author,
        "image_url": image_url,
        "comments": comments,
        "genres": genres
    }


def download_txt(url, payload, filename, folder):
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))
    with open(filepath, 'wb') as f:
        f.write(requests.get(url, params=payload).content)


def download_image(url, filename, folder):
    filepath = os.path.join(folder, sanitize_filename(f"{filename}"))
    with open(filepath, 'wb') as f:
        f.write(requests.get(url).content)


def print_book_info(book):
    print(book)


def main():
    logging.basicConfig(filename='app.log', level=logging.INFO)

    try:
        start_id, end_id = fetch_book_ids()

        for book_id in range(start_id, end_id+1):
            
            url = f"https://tululu.org/b{book_id}/"
            response = requests.get(url)

            if response.history:
                logger.warning(f"Книга {book_id} не найдена - редирект")
                continue

            book = parse_book_page(response.text, url)

            download_txt(
                "https://tululu.org/txt.php",
                {"id": book_id},
                f"{book_id}. {book['title']}",
                "books"
            )

            download_image(
                book['image_url'], 
                unquote(urlsplit(book['image_url']).path).split("/")[-1],
                "images"
            )

            print_book_info(book)

    except requests.RequestException as e:
        logger.error(f"Ошибка запроса: {e}")
        
    except FileNotFoundError as e:
        logger.error(f"Не найден файл: {e}")

    except OSError as e:
        logger.error(f"Ошибка файловой системы: {e}")


if __name__ == "__main__":
    main()
