import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
from bg_replacements import purport_replacements

def parser(soup):
    b_tags = soup.find_all("b")
    # print(b_tags)

    # Preparing Purport Entry
    purport = str(soup.find_all("div", {"class": "purport"}))

    if purport:
        purport = purport_replacements(purport)
        purport = list(filter(None, list(purport.split('---'))))
        popped = purport.pop()
    
        purport_entry = []

        for para in purport:
            para_dictionary = {}

            if para[1:9]=='verse>>>':
                para_dictionary["verse"]=para[9:]
            else:
                para_dictionary["text"]=para
            
            purport_entry.append(para_dictionary)
    


















# Driver Code for parser
chapters = 4
total = 1

for chapter in range(chapters, chapters+1):
    for _index in range(total,total+1):
        url = f'https://vanisource.org/wiki/BG_{chapter}.{_index}_(1972)'

        _source = requests.get(url)
        soup = BeautifulSoup(_source.content, 'html.parser')

        parser(soup)