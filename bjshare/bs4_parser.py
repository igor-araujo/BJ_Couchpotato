# coding=utf-8
# Author: Gabriel Bertacco <niteckbj@gmail.com>
#
# This file was developed as a 3rd party provider for CouchPotato.
# It is not part of CouchPotato's oficial repository.

from bs4 import BeautifulSoup

class BS4Parser(object):
    def __init__(self, *args, **kwargs):
        self.soup = BeautifulSoup(*args, **kwargs)

    def __enter__(self):
        return self.soup

    def __exit__(self, exc_ty, exc_val, tb):
        _ = exc_ty, exc_val, tb  # Throw away unused values
        self.soup.clear(True)
        self.soup = None
