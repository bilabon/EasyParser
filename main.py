#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import sqlite3
from lxml.html import fromstring, tostring


class EasyParser(object):
    """Parser which can save a source page to a file and some blocks of
    a source page to a database by specified URL's search parameter
    """
    def __init__(self, search_text='text', file_name='file.html'):
        self.search_text = search_text
        self.file_name = file_name

    def save_to_file(self, file_name, source):
        """Saving a string to a file"""
        with open(file_name, "w") as file_:
            file_.write(str(source))

    def save_to_bd(self, block_list):
        """Saving some list of blocks to the database
        Args:
            block_list, example:
            [<table><tr><td>text</td></tr></table>,
             <table><tr><td>text</td></tr></table>]
        """
        conn = sqlite3.connect("easy_parser.sqlite")
        c = conn.cursor()
        sql = '''CREATE TABLE IF NOT EXISTS block
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        );'''
        c.execute(sql)
        for block in block_list:
            c.execute("insert into block (data) values (?)", (block, ))
        conn.commit()
        conn.close()

    def get_source_page(self, url):
        """Getting a source page by given URL"""
        page = urllib.urlopen(url)
        return page.read()

    def get_block_list(self, source_page):
        """Getting some html blocks from given source page
        Args:
            source_page: string parameter with a source page
        Returns:
            block_list, example:
            [<table><tr><td>text</td></tr></table>,
             <table><tr><td>text</td></tr></table>]
        """
        block_list = []
        tree = fromstring(source_page)
        for elem in tree.xpath(u"//table[@class='pline']"):
            # checking if elem is right block
            if "2" not in elem.values():
                block_list.append(tostring(elem, pretty_print=True))
        return block_list

    def build_search_url(self, search_text):
        """Building a URL with given search parameter
        Args:
            search_text: string search paraperet
        """
        url = u"https://nnm-club.me/?q=%s" % (search_text)
        return url

    def run_parser(self):
        """Here we run the parser.
        Returns:
            count of blocks whick parcer has just saved
        """
        url = self.build_search_url(self.search_text)
        source_page = self.get_source_page(url)
        block_list = self.get_block_list(source_page)
        # import pdb
        # pdb.set_trace()
        self.save_to_file(self.file_name, source_page)
        self.save_to_bd(block_list)
        return len(block_list)

if __name__ == '__main__':
    """Usage example"""
    parser = EasyParser(search_text=u"Machina")
    blocks_count = parser.run_parser()
    print "%s blocks completed" % blocks_count
