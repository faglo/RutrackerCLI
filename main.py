import webbrowser

from rutracker_parser import RutrackerParser
import os
import argparse
from typing import List

LOAD_DIR = "./"
MINI_SEP = "||"
DEFAULT_SEP = "-"

parser = argparse.ArgumentParser(description="Поиск и загрузка торрентов с Rutracker.org")
parser.add_argument('-q', '--query', type=str, help="Поисковый запрос")
parser.add_argument('-m', '--minify', action='store_true', help="Минималистичное отображение")
args = parser.parse_args()


def get_strip():
    strip = ''
    sz = 0
    cols = os.get_terminal_size().columns
    while sz != cols:
        strip += DEFAULT_SEP
        sz += 1
    return strip


def fill(text, size):
    if len(text) < size:
        whitespaces = ''
        for x in range(1, size - len(text)):
            whitespaces += ' '
        return ' ' + text + whitespaces
    elif len(text) > size:
        return text[:size]
    else:
        return text


def make_row(data: List[str]):
    if args.minify:
        sep = " {} ".format(MINI_SEP)
        sb = ''
        sb += fill(data[0], 2) + sep
        sb += fill(data[2], os.get_terminal_size().columns - 80) + sep
        sb += fill(data[3], 10) + sep
        sb += fill(data[4], 5) + sep
        sb += fill(data[5], 5) + sep
        sb += fill(data[6], 5) + sep
        sb += fill(data[7], 20) + sep
        return sb
    else:
        sb = 'ID: {0}\nТопик: {1}\nНазвание: {2}\nРазмер: {3}\nСиды: {4}\nЛичи: {5}\nСкачано: {6} раз(а)\nСоздано: {7}'.format(
            *data
        )
        sb += get_strip()
        return sb


def main():
    print("Проверка на наличие куки...")
    if rp.is_logged_in():
        pass
    else:
        l = input("Введите логин: ")
        p = input("Введите пароль: ")
        print("Выполняется вход...")
        rp.login(l, p)

    if args.query:
        search(args.query)
    else:
        print("Не указан поисковый запрос")
        exit(1)


def search(query, start=0):
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Поиск...")
    res = rp.search(query)

    if args.minify:
        print(make_row(['#', 'Топик', 'Название', 'Размер', 'Сиды', 'Личи', 'Загружено', 'Создано']))

    for i, result in enumerate(res['results']):
        print(make_row([str(i),
                        result['topic_name'],
                        result['torrent_name'],
                        result['torrent_size'],
                        result['seeds'],
                        result['leeches'],
                        result['download_count'],
                        result['created_at']
                        ]))
    print("Страница {} из {}".format(res['start']//50, res['results_count']//50))

    x = input("'d<ID>' загрузить '<ID>' открыть 'nn' след. 'pp' пред.: ")
    if 'd' in x:
        id_of = x.split('d')[1].strip()
        selected_torrent = res['results'][int(id_of)]
        rp.dl_torrent(selected_torrent, LOAD_DIR)
    elif x == 'nn':
        if res['results_count'] != start:
            search(query, start + 50)
        else:
            print("Конец")
            exit(0)
    elif x == 'pp':
        if start-50 >= 0:
            search(query, start - 50)
        else:
            print("Начало")
            search(query, start)
    elif x == "q":
        exit(0)
    else:
        webbrowser.open('https://rutracker.org/forum/{}'.format(res['results'][int(x)]['torrent_link']))


if __name__ == '__main__':
    print("Rutracker.org CLI")
    print("Инициализация")
    rp = RutrackerParser()
    main()
