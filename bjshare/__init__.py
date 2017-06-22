# coding=utf-8
# Author: Gabriel Bertacco <niteckbj@gmail.com>
#
# This file was developed as a 3rd party provider for CouchPotato.
# It is not part of CouchPotato's oficial repository.

from .bjshare import BJShare

def autoload():
    return BJShare()

config = [{
    'name': 'bjshare',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'BJ-Share',
            'description': '<a href="https://bj-share.me" target="_blank">BJ-Share</a>',
            'wizard': True,
            'icon': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4AYdFDsWJOqaBQAAAqdJREFUOMudk0tIVGEUx//nu3funacjTooaWg4NZVbgK4WE0FoUgtjCNlGbiBZRGlgQBNamRRDt3dQumNGUMBAGGqSgWphlmqHOWFMZoyONznu8954W4dRQQXTgwOE8fhzOAx/2Hz+3tL3lRrjnsgX/IbIeiTJtJHq1yUk1VN5iR5H1qXs+4P1XgBC1O8eI6C3HkyeQSJ3ir6sX5tt6Sv8VQAAQcjX0I529RhZzFOvrNSgvPV/z+fm9vxWx1yvNAlIesNjS6RFvQsPksKqcSFWSyfQkWb/71L4JX+JPgA+e9n5jUzsMl9MvAGDXy8cLZFJGsZFwkc7MmcwRSzhSz4DYUgBgDIiPTZ1uzm4epHiqmJeja7RFDdYdaxYLS0PIbVazxTzHTrufImsuAGCTrFN56TtsxD3Q2UyKqZgd1rhUWXld3gKktznmrIv4QkA17Nb3QjMaQdQKw5CgKlNIJKsoFm/PzyGb8VJz03IeYAt+PsoGH2BJxFiiRWIRZEUuQybngcv5hq0WiQz+hNhGFctSWtjsI9W+u2kBADMDAwpi8W7a1GykG8UisnYJK6sXKZPzwGpekoucd0Sd5yrrWhAAYFEn0LpnHABkALDd9x9CTuv8uSeoeZMwVD39eCa0cvAMsrk2EHJQlYePOhrSPUpKkpmZljwdR0hVzFCV/NpYQALjhSgrfTBfUl9E06+6kNNk2KzPRGPt2OzsrOHz+QyZiHjxdN+o0HQ/AJBZLcHMwllksnspnpQRi/Uq0aiDda0LRAZkafjWDlt0cHBQ/9HgLxIIBOQdJ6/cRvRbH3FhDADYbpkWbnf3rdaKSDgc1sfHx7MFSUH34TaxvPIQmexvv8AAo7jopjv2+mbBNxZkmZVyOGwhOGyh3+5Xkr5yRdkIpl4XuL8DKo8cbpHgDHEAAAAASUVORK5CYII=',
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'passkey',
                    'default': '',
                },
				{
                    'name': 'ignore_year',
                    'label': 'ignore year',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Will ignore the year in the search results',
                },
                {
                    'name': 'hc_blurred',
                    'label': 'HC/BLURRED',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Will accept HC or BLURRED titles',
                },
                {
                    'name': 'tc',
                    'label': 'TC/HDTC',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Will search TC/HDTC titles',
                },
                {
                    'name': 'dubbed',
                    'label': 'Dubbed',
                    'defaul': 0,
                    'type': 'bool',
                    'description': 'Will search for dubbed and multi audio titles.'
                },
                {
                    'name': 'subtitled',
                    'label': 'Subtitled',
                    'defaul': 1,
                    'type': 'bool',
                    'description': 'Will search for subtitled and multi audio titles.'
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 40,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'type': 'int',
                    'default': 20,
                    'description': 'Starting score for each release found via this provider.',
                },
            ],
        },
    ],
}]
