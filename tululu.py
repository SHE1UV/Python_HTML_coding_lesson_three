import os
import argparse
import sys
import logging
from time import sleep

from urllib.parse import urljoin, urlsplit, unquote
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


logger = logging.getLogger()


def fetch_book_ids():
    parser = argparse.ArgumentParser(description='Скрипт для скачивания книг с сайта tululu.org')
    parser.add_argument('-s', '--start_id', help='ID, с которого надо скачивать книги', default=1, type=int)
    parser.add_argument('-e', '--end_id', help='ID, до которого надо скачивать книги', default=10, type=int)
    args = parser.parse_args()
    return args.start_id, args.end_id


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, payload, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        check_for_redirect(response)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Failed to download {filename}: {response.status_code} {response.reason}")
        return None

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath
    

def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(f"{filename}"))

    try:
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Failed to download {filename}: {response.status_code} {response.reason}")
        return None

    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath
    

def handle_http_error(book_id, response):
    logger.warning(f"Redirect. The book {book_id} not found")


def handle_connection_error(connect_err, first_reconnection):
    if first_reconnection:
        logger.warning('Connection is down!')
        logger.warning(connect_err)
        logger.warning('Retry in 5 seconds')
        sleep(5)
    else:
        logger.warning('Connection is still down!')
        logger.warning('Retry in 15 seconds')
        sleep(15)
        

def parse_book_page(html, base_url):
    soup = BeautifulSoup(html, 'lxml')
    title_tag = soup.find('h1')
    book_title, book_author = title_tag.text.split("::")
    image_tag = soup.find('div', class_='bookimage')
    image_url = urljoin(base_url, image_tag.find('img')['src'])
    comments_tag = soup.find_all('div', class_='texts')
    comments = [comment_tag.find('span', class_='black').text 
                for comment_tag in comments_tag]
    genre_tags = soup.find('span', class_='d_book').find_all("a")
    genres = [tag.text for tag in genre_tags]
    return {"title": book_title, "author": book_author, "image": image_url, "comments": comments, "genres": genres}


def print_about_book(book):
    print("Заголовок:", book['title'])
    print(book['comments'])


def download_book(book_id):
    first_reconnection = True
    while True:
        try:
            url = f"https://tululu.org/b{book_id}/"
            response = requests.get(url)

            response.raise_for_status()
            check_for_redirect(response)

            book = parse_book_page(response.text, response.url)

            if not book:
                break

            book_title = book['title']
            image_url = book['image']
            filename = f'{book_id}. {book_title}'
            payload = {"id": book_id}
            download_url = f'https://tululu.org/txt.php'

            if not download_txt(download_url, payload, filename):
                break

            filename = unquote(urlsplit(image_url).path).split("/")[-1]
            download_image(image_url, filename)
            print_about_book(book)

            if not first_reconnection:
                logger.warning('Connection is restored.')

        except requests.exceptions.HTTPError as http_err:
            handle_http_error(book_id, response)
            break
        except requests.exceptions.ConnectionError as connect_err:
            handle_connection_error(connect_err, first_reconnection)
            first_reconnection = False


def main():
    logging.basicConfig(level=logging.INFO, filename='error.log', filemode='w')
    start_id, end_id = fetch_book_ids()

    try:
        for book_id in range(start_id, end_id + 1):
            download_book(book_id)
    except KeyboardInterrupt:
        logger.info("Script execution interrupted by the user.")
    except Exception as e:
        logger.exception("An unhandled exception occurred:")


if __name__ == "__main__":
    main()
