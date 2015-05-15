#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import sqlite3
from lxml.html import fromstring, tostring


class EasyParser(object):
    def __init__(self, search_text='text', file_name='file.html'):
        self.search_text = search_text
        self.file_name = file_name

    def save_to_file(self, file_name, source):
        with open(file_name, 'w') as file_:
            file_.write(str(source))

    def save_to_bd(self, block_list):
        conn = sqlite3.connect('example.sqlite')
        c = conn.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS block (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT NOT NULL);'
        c.execute(sql)
        for block in block_list:
            c.execute('insert into block (data) values (?)', (block, ))
        conn.commit()
        conn.close()

    def get_source_page(self, url):
        page = urllib.urlopen(url)
        return page.read()

    def get_block_list(self, source_page):
        block_list = []
        tree = fromstring(source_page)
        for elem in tree.xpath("//table[@class='pline']"):
            # checking if elem is right block
            if '2' not in elem.values():
                block_list.append(tostring(elem, pretty_print=True))
        return block_list

    def build_search_url(self, search_text):
        url = 'https://nnm-club.me/?q=%s' % (search_text)
        return url

    def run_parser(self):
        url = self.build_search_url(self.search_text)
        source_page = self.get_source_page(url)
        block_list = self.get_block_list(source_page)
        # import pdb
        # pdb.set_trace()
        self.save_to_file(self.file_name, source_page)
        self.save_to_bd(block_list)
        return len(block_list)


parser = EasyParser(search_text='Machina')
print parser.run_parser()
