# Парсер книг с сайта [tululu.org](https://tululu.org)

Программа предназначена для удобного скачивания книг с веб-сайта [tululu.org](https://tululu.org). Скрипт предоставляет функции для загрузки текстовых файлов книг и изображений обложек. Кроме того, выводит информацию о названиях, авторах, комментариях и жанрах. Вся информация о полученных книгах хранится в файле `books.json`.

## Как установить
Создайте и активируйте виртуальное окружение

```
python -m venv venv
source ./venv/Scripts/activate  #для Windows
source ./venv/bin/activate      #для Linux и macOS
```

Python3 должен быть уже установлен. Затем используйте pip (или pip3, есть конфликт с Python2)

Для установки зависимостей:

```
pip install -r requirements.txt
```

## Запуск

Запустить скрипт можно используя команду:

```
python tululu.py
```

Можно использовать сокращенную запись:

```
python tululu.py -s 1 -e 10
```

Если параметры `--start_id` и `--end_id` не указаны, по умолчанию будут скачиваться страницы с 1 по 10. В случае успешного выполнения скрипт не выводит никаких сообщений.

Можно также изменять финальную папку, где окажутся все файлы:

```
python tululu.py --dest_folder Название папки

```

## Доступные параметры:

`--start_id` - Индекс, начиная с какой страницы скачивать книги. По умолчанию: 1

`--end_id` - Индекс, по какую страницу скачивать книги (включительно). По умолчанию: 10

## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).







