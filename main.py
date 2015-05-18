# -*- coding: utf-8 -*-
import urllib
import sqlite3
from lxml.html import fromstring, tostring
from grab import Grab


class EasyParser(object):
    """Parser which can save a source page to a file and some blocks of
    the source page to a database by specified URL's search parameter
    """
    def __init__(self,
                 search_text="text",
                 file_name="file.html",
                 db_name="easy_parser.sqlite"):
        """
        Args:
            search_text: string parameter for searching at a web page
            file_name: a filename for saving a source page
            db_name: a filename for a database
        """
        self.search_text = search_text
        self.file_name = file_name
        self.db_name = db_name

    def save_to_file(self, file_name, source):
        """Saving a string to a file"""
        with open(file_name, "w") as file_:
            file_.write(str(source))

    def save_to_bd(self, block_list, db_name):
        """Saving some list of blocks to a database
        Args:
            block_list, example:
            [<div class='serp-item_plain_yes'>text</div>,
             <div class='serp-item_plain_yes'>text</div>]
            db_name: database name
        """
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql = '''CREATE TABLE IF NOT EXISTS block
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        );'''
        c.execute(sql)
        for block in block_list:
            c.execute("INSERT INTO block (data) VALUES (?)", (block, ))
        conn.commit()
        conn.close()

    def get_source_page(self, url):
        """Getting a source page by given URL"""
        grab = Grab()
        grab.go(url)
        grab.go(url)
        return grab.response.body

    def get_block_list(self, source_page):
        """Getting some html blocks from given source page
        Args:
            source_page: string parameter with a source page
        Returns:
            block_list, example:
            [<div class='serp-item_plain_yes'>text</div>,
             <div class='serp-item_plain_yes'>text</div>]
        """
        block_list = []
        tree = fromstring(source_page)
        for elem in tree.xpath(u"//div[contains(@class,'serp-item_plain_yes')]"):
            block_list.append(tostring(elem, pretty_print=True))
        return block_list

    def build_search_url(self, search_text):
        """Building a URL with given search parameter
        Args:
            search_text: string search paraperet
        """
        url = u'http://yandex.ua/search/?text=%s' % search_text
        return url

    def run_parser(self):
        """Here we run the parser.
        Returns:
            count of blocks which the parcer has just saved
        """
        url = self.build_search_url(self.search_text)
        source_page = self.get_source_page(url)
        block_list = self.get_block_list(source_page)
        self.save_to_file(self.file_name, source_page)
        self.save_to_bd(block_list, self.db_name)
        return len(block_list)


if __name__ == "__main__":
    """Usage example"""
    parser = EasyParser(search_text=u"test")
    blocks_count = parser.run_parser()
    print "%s blocks completed" % blocks_count
