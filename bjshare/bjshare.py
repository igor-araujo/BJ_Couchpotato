# coding=utf-8
# Author: Gabriel Bertacco <niteckbj@gmail.com>
#
# This file was developed as a 3rd party provider for CouchPotato.
# It is not part of CouchPotato's oficial repository.

from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
from .bs4_parser import BS4Parser
import requests
import urllib
import re

log = CPLog(__name__)

class BJShare(TorrentProvider, MovieProvider):

    urls = {"base_url" : "https://www.bj-share.me/",
            "login" :    "https://www.bj-share.me/login.php",
            "search" :   "https://bj-share.me/torrents.php"}

    http_time_between_calls = 1 #seconds
    cat_backup_id = None

    def _searchOnTitle(self, title, movie, quality, results):
        params = {"searchstr" : "",
                  "order_way" : "desc",
                  "order_by" :"seeders",
                  "filter_cat[1]" : "1",
                  "searchstr" : urllib.quote_plus(movie['title'])}

        search_url = self.urls["search"]
        search_url += "?"+"&".join(["{0}={1}".format(key,value) for key,value in params.items()])
        log.info(u'Searching BJ-Share for %s' % (title))

        data = self._session.get(search_url)

        with BS4Parser(data.text, "html.parser") as html:
            try:
                torrent_group = html.find("div",class_='group_info').find("a",title="View torrent group").attrs["href"]
            except AttributeError:
                log.debug(u"Data returned from provider does not contain any torrents")
                return

        data = self._session.get("{0}{1}".format(self.urls["base_url"], torrent_group))

        if not data:
            log.debug(u"URL did not return data, maybe try a custom url, or a different one")
            return

        log.debug('Data received from BJ-Share')
        with BS4Parser(data.text, "html.parser") as html:
            if html.find('div',class_='torrent_description').find('a',href=re.compile('.+imdb.*')).text != movie['identifiers']['imdb']:
                return

            torrent_table = html.find_all("tr", class_="group_torrent")
            
            _title = html.find("div", class_="thin").find("div", class_="header").h2.text
            _year = re.search('\[(\d{4})\]',_title).groups()[0]
            _title = re.sub(" \[%s\]"%_year, "", _title)
            if re.search("\[(.+?)\]",_title):
                _title = re.search("\[(.+?)\]",_title).groups()[0]
            _name = "{} {}".format(_title,_year)

            if not torrent_table:
                log.debug(u"Data returned from provider does not contain any torrents")
                return

            for torrent in torrent_table:
                if not self._check_audio_language(torrent):
                    continue

                name = self._get_movie_name(_name,torrent)
                download_file = "{}{}".format(self.urls["base_url"],
                                              torrent.find("a", title="Baixar").attrs["href"])
                detail_url = "{}{}".format(self.urls["base_url"],
                                           torrent.find('a', title="Link Permanente")['href'])
                torrent_id = detail_url.split("=")[-1]

                if not all([name, download_file]):
                    continue

                torrent_size, snatches, seeders, leechers = torrent.find_all("td", class_="number_column")
                torrent_size, snatches, seeders, leechers = torrent_size.text, snatches.text, seeders.text, leechers.text

                if seeders == 0:
                    log.debug(u"Discarding torrent because it doesn't meet the minimum seeders: {0} (S:{1} L:{2})".format(name, seeders, leechers))
                    continue

                results.append({
                    'id' : torrent_id,
                    'name' : name,
                    'url' : download_file,
                    'detail_url' : detail_url,
                    'size': self.parseSize(torrent_size),
                    'seeders': seeders,
                    'leechers': leechers,
                })

    def login(self):
        if not self.conf('passkey'):
            log.warning(u'No Passkey was found.')
            return False

        self._session = requests.session()
        self._session.cookies.set('session', urllib.quote_plus(self.conf('passkey')))

        try:
            response = self._session.get(self.urls['login'])
        except requests.exceptions.TooManyRedirects:
            log.warning(u'Unable to connect to provider. Check your SESSION cookie')
            return False

        if not response.ok:
            log.warning(u'Unable to connect to provider')
            return False

        with BS4Parser(response.text, 'html.parser') as html:
            if html.title.text.split()[0] == u'Login':
                log.warning(u'Invalid SESSION cookie. Check your settings')
                return False
        return True

    def _check_audio_language(self, html):
        lang = re.match('.+:\ (.*)',html.find_next_sibling().find('blockquote',text=re.compile("\xc3\x81udio:.*")).text).groups()[0]

        if 'Dual' in lang:
            return True

        if 'Dublado' in lang and self.conf('dubbed'):
            return True

        if 'Legendado' in lang and self.conf('subtitled'):
            return True

        return False

    def _get_movie_name(self, _name, html):
        if not html:
            return

        # Wanted show infos
        show_info = {
            "3D" : "3D",
            "Resolution" : "Resolu\xc3\xa7\xc3\xa3o",
            "Quality" : "Qualidade",
            "Audio" : "Codec de \xc3\x81udio",
            "Video" : "Codec de V\xc3\xaddeo",
            "Extension" : "Formato",
        }

        for key,value in show_info.items():
            show_info[key] = re.match('.+:\ (.*)',html.find_next('blockquote',text=re.compile("%s.*"%value)).text).groups()[0]

        show_info["Name"] = _name
        show_info["3D"] = "3D" if show_info["3D"][0] == 'S' else ""
        show_info["Video"] = re.sub("H.","x",show_info["Video"])
        show_info["Extension"] = show_info["Extension"].lower()

        resolution = int(show_info["Resolution"].split("x")[0])

        if 1260 <= resolution <= 1300:
            show_info["Resolution"] = "720p"
        elif 1900 <= resolution <= 1940:
            show_info["Resolution"] = "1080p"
        elif 3820 <= resolution <= 3860:
            show_info["Resolution"] = "4K"
        else:
            show_info["Resolution"] = ""

        name = " ".join(_ for _ in [show_info["Name"],show_info["3D"],show_info["Resolution"],show_info["Quality"],
                            show_info["Video"],show_info["Audio"],show_info["Extension"]])
        name = re.sub(" {1,}", ".", name)
        name = re.sub("\.{1,}", ".", name)

        return name
