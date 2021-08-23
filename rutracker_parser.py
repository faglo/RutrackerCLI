import requests
import webbrowser
import pickle
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, TypedDict
from os import path


class TorrentInfo(TypedDict):
    topic_name:     str
    torrent_name:   str
    torrent_link:   str
    creator_name:   str
    torrent_size:   str
    seeds:          str
    leeches:        str
    download_count: str
    created_at:     str


class OverallInfo(TypedDict):
    results_count: int
    start:         int
    results:       List[TorrentInfo]


class RutrackerParser:
    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'close',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate, lzma, sdch',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        self.cookie_fp = './cookies'
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.base_url = "https://rutracker.org/forum/tracker.php"
        if Path(self.cookie_fp).is_file():
            self.session.cookies.update(pickle.load(open(self.cookie_fp, 'rb')))

    def is_logged_in(self) -> bool:
        r = self.session.get(self.base_url)
        if BeautifulSoup(r.text, 'html.parser').find("a", {'id': 'logged-in-username'}) is None:
            return False
        else:
            return True

    def login(self, username, password) -> str:
        form_data = {
            'login_username': username.encode('cp1251'),
            'login_password': password.encode('cp1251'),
            'login': u'Вход',
        }
        r = self.session.post("https://rutracker.org/forum/login.php", data=form_data)

        try:
            soup = BeautifulSoup(r.text, 'html.parser')

            captcha_pic_link = soup.find('img', {'alt': 'pic'})['src']
            captcha_sid = soup.find('input', {'name': 'cap_sid'})['value']
            captcha_code = soup.find('input', {'class': 'reg-input'})['name']

            webbrowser.open(captcha_pic_link)
            captcha_decode = input("Введите капчу: ")

            form_data.update({
                'cap_sid': captcha_sid,
                captcha_code: captcha_decode,
            })

            r = self.session.post('https://rutracker.org/forum/login.php', data=form_data)
            new_page = BeautifulSoup(r.text, 'html.parser')
            if new_page.find('input', {'name': 'cap_sid'}) is not None:
                return new_page.find('h4', {'class': 'warnColor1'}).text
        except TypeError:
            if self.is_logged_in():
                print("Вход выполнен без капчи")
            else:
                print("Неизвестная ошибка")
                exit(0)

        with open(self.cookie_fp, 'wb') as cookie_f:
            pickle.dump(self.session.cookies, cookie_f)
            cookie_f.close()
            return 'OK'

    def search(self, query, start=0) -> OverallInfo:
        r = self.session.get(self.base_url, params={'nm': query, 'start': start})
        r.encoding = 'windows-1251'
        soup = BeautifulSoup(r.text, 'html.parser')
        body = soup.find('table', {'id': 'tor-tbl'}).find('tbody')
        results: List[BeautifulSoup] = body.find_all('tr')

        results_count = int(soup.find('p',
                                      {'class': 'med bold'}).text.split('Результатов поиска: ')[1].split('(max: 500)\n')[0].strip())

        search_results = []
        if results_count == 0:
            return OverallInfo(
                results_count=0,
                start=0,
                results=[]
            )
        else:
            for result in results:
                data: List[BeautifulSoup] = result.find_all('td')
                topic_name = data[2].text
                torrent_soup: BeautifulSoup = data[3]
                torrent_link = torrent_soup.find('a')['href']
                torrent_name = torrent_soup.text
                creator_name = data[4].text
                torrent_size = data[5].text
                seeds = data[6].text
                leeches = data[7].text
                download_count = data[8].text
                created_at = data[9].text

                serialized = TorrentInfo(
                    topic_name=topic_name.strip(),
                    torrent_link=torrent_link.strip(),
                    torrent_name=torrent_name.strip(),
                    creator_name=creator_name.strip(),
                    torrent_size=torrent_size.strip(),
                    seeds=seeds.strip(),
                    leeches=leeches.strip(),
                    download_count=download_count.strip(),
                    created_at=created_at.strip().replace('\n', ' ')
                )

                search_results.append(serialized)

        return OverallInfo(
            results_count=round(results_count),
            start=start,
            results=search_results
        )

    def get_torrent_link(self, topic_link: str) -> str:
        r = self.session.get('https://rutracker.org/forum/{}'.format(topic_link))
        soup = BeautifulSoup(r.text, 'html.parser')
        part_link = soup.find('a', {'class': 'dl-link'})['href']
        return 'https://rutracker.org/forum/{}'.format(part_link)

    def dl_torrent(self, torrent: TorrentInfo, pth: str):
        r = self.session.get(self.get_torrent_link(torrent['torrent_link']))
        with open(path.join(pth, '{}.torrent'.format(torrent['torrent_name'])), 'wb') as torrent_file:
            torrent_file.write(r.content)
