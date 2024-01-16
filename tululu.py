import os
import pathlib
import argparse
from time import sleep

import requests
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit
from bs4 import BeautifulSoup


def check_for_redirect(book):
    if book.history:
        raise requests.exceptions.HTTPError


def parse_book_page(response, template_url):
    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.select_one("#content h1")
    title_name, title_author = title_text.text.split(' :: ')
    title_image = soup.select_one(".bookimage img")['src']
    image_url = urljoin(template_url, title_image)

    book_comments = soup.select(".texts")
    book_comments_text = [book_comment.select_one('.black').text for book_comment in book_comments]

    book_genres = [genre_tag.text for genre_tag in soup.select('.d_book a')]

    book_page_params = {
        "title": title_name.strip(),
        "author": title_author.strip(),
        "image_url": image_url,
        "comments": book_comments_text,
        "genres": book_genres,
    }

    return book_page_params


def download_txt(response, filename, dest_folder, folder='books/'):
    full_path = f'{dest_folder}/{folder}'
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(full_path, f'{sanitize_filename(filename)}.txt')
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image(url, dest_folder, folder='images/'):
    full_path = f'{dest_folder}/{folder}'
    pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filename = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join(full_path, filename)
    with open(unquote(filepath), 'wb') as file:
        file.write(response.content)


def main():
    parser = argparse.ArgumentParser(description='Программа получает информацию по книгам с сайта http://tululu.org, а также скачивает их текст и картинку')
    parser.add_argument("-s", "--start_id", type=int, help="Начальная точка скачивания книг", default=1)
    parser.add_argument("-e", "--end_id", type=int, help="Конечная точка скачивания книг", default=10)
    parser.add_argument("--dest_folder", type=str, help="путь к каталогу с результатами парсинга: картинкам, книгам, JSON", default='result')
    args = parser.parse_args()

    book_txt_url = "https://tululu.org/txt.php"
    book_url = 'https://tululu.org/b{}/'

    pathlib.Path(args.dest_folder).mkdir(parents=True, exist_ok=True)

    for book_number in range(args.start_id, args.end_id):
        params = {"id": book_number}
        try:
            response = requests.get(book_txt_url, params)
            response.raise_for_status()
            check_for_redirect(response)

            book_response = requests.get(book_url.format(book_number))
            book_response.raise_for_status()
            check_for_redirect(book_response)

            book_parameters = parse_book_page(book_response, book_url)

            download_txt(response, book_parameters['title'], args.dest_folder)
            download_image(book_parameters['image_url'], args.dest_folder)

        except requests.exceptions.HTTPError:
            print("Такой книги нет")
        except requests.exceptions.ConnectionError:
            print("Повторное подключение к серверу")
            sleep(20)


if __name__ == '__main__':
    main()
