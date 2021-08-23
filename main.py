import webbrowser

from rutracker_parser import RutrackerParser
import os
import argparse

LOAD_DIR = "./"

parser = argparse.ArgumentParser(description="Поиск и загрузка торрентов с Rutracker.org")
parser.add_argument('-q', '--query', type=str, help="Поисковый запрос")
parser.add_argument('-m', '--minify', action='store_true', help="Минималистичное отображение")
args = parser.parse_args()


def get_strip():
    strip = ''
    sz = 0
    cols = os.get_terminal_size().columns
    while sz != cols:
        strip += '-'
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
    strip = get_strip()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Поиск...")
    res = rp.search(query)

    if args.minify:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Поиск...")
        res = rp.search(query, start)
        print(
            fill("#", 2),
            fill("Название", os.get_terminal_size().columns - 80),
            fill("Размер", 10),
            fill("Сиды", 5),
            fill("Личи", 5),
            fill("Загружено", 5),
            fill("Создано", 20),
            sep=" || "
        )
        for i, result in enumerate(res['results']):
            print(
                fill(str(i), 2),
                fill(result['torrent_name'], os.get_terminal_size().columns - 80),
                fill(result['torrent_size'], 10),
                fill(result['seeds'], 5),
                fill(result['leeches'], 5),
                fill(result['download_count'], 5),
                fill(result['created_at'], 20),
                sep=" || "
            )
        print("Страница {} из {}".format(res['start']//50, res['results_count']//50))
    else:
        print("Страниц: {} // Текущая страница: {}\n".format(round(res['results_count']/50), round(res['start']/50)))
        for i, result in enumerate(res['results']):
            print("ID: {}\nТопик: {}\nНазвание: {}\nРазмер: {}\nСиды: {}\nЛичи: {}\nСкачано: {} раз(а)\nСоздано: {}".format(
                i,
                result['topic_name'],
                result['torrent_name'],
                result['torrent_size'],
                result['seeds'],
                result['leeches'],
                result['download_count'],
                result['created_at']
            ))
            print(strip)

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
