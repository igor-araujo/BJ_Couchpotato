# coding=utf-8
# Author: Gabriel Bertacco <niteckbj@gmail.com>
#
# This file was developed as a 3rd party provider for CouchPotato.
# It is not part of CouchPotato's oficial repository.

from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
from .bs4_parser import BS4Parser
from requests.compat import urljoin
try:
    from urllib import urlencode    # Python3 Import
except ImportError:
    from urllib.parse import urlencode    # Python2 Import
import re

log = CPLog(__name__)

class BJShare(TorrentProvider, MovieProvider):

    urls = {'base_url' : "https://bj-share.me/",
            'login' :    "https://bj-share.me/login.php",
            'search' :   "https://bj-share.me/torrents.php"}

    http_time_between_calls = 1 #seconds
    cat_backup_id = None

    def _searchOnTitle(self, title, movie, quality, results):
        params = {'searchstr' : '',
                  'order_way' : 'desc',
                  'order_by' :'seeders',
                  'filter_cat[1]' : '1',
                  'searchstr' : movie['title']}

        search_url = self.urls['search'] + '?' + urlencode(params)
        log.info(u'Searching BJ-Share for %s' % (title))

        data = self.getHTMLData(search_url)
        
        with BS4Parser(data, 'html.parser') as html:
            try:
                torrent_group = html.find('div',class_='group_info').find('a',
                                                                          class_='tooltip',
                                                                          title=re.compile("View torrent(| group)")).attrs['href']
                torrent_group = re.sub('#.*','',torrent_group)
            except AttributeError:
                log.debug(u"Data returned from provider does not contain any torrents")
                return

        data = self.getHTMLData(urljoin(self.urls['base_url'], torrent_group))

        if not data:
            log.debug(u"URL did not return data, maybe try a custom url, or a different one")
            return

        log.debug('Data received from BJ-Share')
        with BS4Parser(data, 'html.parser') as html:
            if html.find('div',class_='torrent_description').find('a',href=re.compile('.+imdb.*')).text != movie['identifiers']['imdb']:
                return

            torrent_table = html.find_all('tr', class_='group_torrent')

            _title = html.find('div', class_='thin').find('div', class_='header').h2.text
            _year = re.search('\[(\d{4})\]',_title).groups()[0]
            _title = re.sub(' \[%s\]'%_year, '', _title)
            if re.search('\[(.+?)\]',_title):
                _title = re.search('\[(.+?)\]',_title).groups()[0]
            if self.conf('ignore_year'):
                _name = _title
            else:
                _name = '{} {}'.format(_title,_year)

            if not torrent_table:
                log.debug(u"Data returned from provider does not contain any torrents")
                return

            for torrent in torrent_table:
                if not self._check_audio_language(torrent):
                    continue
                
                if self._ignore_hc_blurred(torrent):
                    continue

                name = self._get_movie_name(_name,torrent)
                download_file = '{}{}'.format(self.urls['base_url'],
                                              torrent.find('a', title='Baixar').attrs['href'])
                detail_url = '{}{}'.format(self.urls['base_url'],
                                           torrent.find('a', title='Link Permanente')['href'])
                torrent_id = detail_url.split('=')[-1]

                if not all([name, download_file]):
                    continue

                torrent_size, snatches, seeders, leechers = torrent.find_all('td', class_='number_column')
                torrent_size, snatches, seeders, leechers = torrent_size.text, snatches.text, seeders.text, leechers.text

                if seeders == 0:
                    log.debug(u"Discarding torrent because it doesn't meet the minimum seeders: {0} (S:{1} L:{2})".format(name, seeders, leechers))
                    continue
                
                name = '{} {} seeders'.format(name,seeders)

                results.append({
                    'id' : torrent_id,
                    'name' : name,
                    'url' : download_file,
                    'detail_url' : detail_url,
                    'size': self.parseSize(torrent_size),
                    'seeders': seeders,
                    'leechers': leechers,
                })

    def getLoginParams(self):
        log.debug('Getting logging params for BJ-Share')
        return {
                'submit': 'Login',
                'username': self.conf('username'),
                'password': self.conf('password'),
                'keeplogged': 0
            }
        
    def loginSuccess(self, output):
        success = False if re.search('<title>Login :: BJ-Share</title>', output) else True
        log.debug('Checking login success for Quorks: %s' % ('Success' if not success else 'Failed'))
        return success
    
    loginCheckSuccess = loginSuccess

    def _check_audio_language(self, html):
        lang = re.match('.+:\ (.*)',html.find_next_sibling().find('blockquote',text=re.compile(u"Áudio:.*")).text).groups()[0]

        if 'Dual' in lang:
            return True

        if 'Dublado' in lang and self.conf('dubbed'):
            return True

        if 'Legendado' in lang and self.conf('subtitled'):
            return True

        return False
    
    def _ignore_hc_blurred(self, html):
        s = re.search('(?i)(hc|blurred|korsub)', html.find_next('div',class_='filelist_path').text.lower())
        if s and not self.conf('hc_blurred'):
            return True
        return False

    def _get_movie_name(self, _name, html):
        if not html:
            return

        # Wanted show infos
        show_info = {
            '3D' : u"3D",
            'Resolution' : u"Resolução",
            'Quality' : u"Qualidade",
            'Audio' : u"Codec de Áudio",
            'Video' : u"Codec de Vídeo",
            'Extension' : u"Formato",
        }

        for key,value in show_info.items():
            show_info[key] = re.match('.+:\ (.*)',html.find_next('blockquote',text=re.compile(u"%s.*"%value)).text).groups()[0]

        show_info['Name'] = _name
        show_info['3D'] = '3D' if show_info['3D'][0] == 'S' else ''
        show_info['Video'] = re.sub('H.','x',show_info['Video']).lower()
        show_info['Extension'] = show_info['Extension'].lower()

        resolution = int(show_info['Resolution'].split('x')[0])
        
        show_info['Resolution'] = 'SD'
        if 1260 <= resolution <= 1300:
            show_info['Resolution'] = '720p'
        elif 1900 <= resolution <= 1940:
            show_info['Resolution'] = '1080p'
        elif 3820 <= resolution <= 3860:
            show_info['Resolution'] = '2160p'
            
        source = 'HD-Rip'
        if re.search('(TC|HDTC|DVDScr)', show_info['Quality']) and not self.conf('tc'):
            source = 'TeleCine'
        
        if re.search('WEB-DL', show_info['Quality']):
            source = 'WEB-DL'

        if re.search('WebRip', show_info['Quality']):
            source = 'WEBRIP'

        if re.search('(DVD5|DVD9|DVDRip)', show_info['Quality']):
            source = 'DVD-R'

        if re.search('(BRRip|BDRip)', show_info['Quality']):
            source = 'BR-Rip'
            
        if re.search('Blu-ray', show_info['Quality']):
            source = 'BluRay'

        if re.search('Remux', show_info['Quality']):
            source = 'Remux'
        
        show_info['Quality'] = source
        
        release_year = re.match('.+(\d{4}).*',html.find_next('span',class_='time')['title']).groups()[0]
        res = '{} ({}) {} {} {} {}'.format(show_info['Name'],release_year,show_info['3D'],show_info['Resolution'],
                                           show_info['Quality'],show_info['Video'],show_info['Audio'])
        res = re.sub('\ +', ' ', res)
        
        return res
