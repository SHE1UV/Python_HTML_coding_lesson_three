import os
import sys
import logging
from time import sleep

import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, unquote  
from pathvalidate import sanitize_filename


logger = logging.getLogger()


def fetch_book_ids():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_id', default=1, type=int)
    parser.add_argument('-e', '--end_id', default=10, type=int)
    args = parser.parse_args()
    return args.start_id, args.end_id


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, payload, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, sanitize_filename(filename))
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')
    h1 = soup.find('h1')
    title, author = h1.text.split('::')
    img_tag = soup.find('div', class_='bookimage')
    img_url = urljoin(url, img_tag.find('img')['src'])
    comments = [span.text for span in soup.find_all('span', 'black')] 
    genres = [a.text for a in soup.find('span', 'd_book').find_all('a')]
    return {
        'title': title,
        'author': author,
        'img_url': img_url,
        'comments': comments,
        'genres': genres
        }


def print_book_info(book):
    print(f"Title: {book['title']}")
    print(f"Comments: {book['comments']}")


def download_book(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    book = parse_book_page(response.text)
    filename = f"{book_id}. {book['title']}"
    txt_url = 'https://tululu.org/txt.php'
    payload = {'id': book_id}
    txt_path = download_txt(txt_url, payload, filename)
    img_name = unquote(urlsplit(book['img_url']).path).split("/")[-1]
    img_path = download_image(book['img_url'], img_name)
    print_book_info(book)


def main():
    logging.basicConfig(level=logging.INFO, filename='errors.log', filemode='w')

    try:
        start, end = fetch_book_ids()
    except ValueError:
        logger.error("Invalid book IDs")
        sys.exit(1)

    try:
        for book_id in range(start, end + 1):
            download_book(book_id)
            
    except requests.exceptions.ConnectionError:
        logger.error("Connection error")
        sleep(5)
        
        for book_id in range(start, end + 1):
            try:
                download_book(book_id)
            except requests.exceptions.ConnectionError:
                logger.error("Connection still error")
                sleep(15)
                
                for book_id in range(start, end + 1):
                    download_book(book_id)
                    
    except OSError as err:
        logger.error(f"IO error: {err}")
            
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error: {err}")


if __name__ == '__main__':
    main()
