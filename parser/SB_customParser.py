import requests
import requests_cache
import json
from bs4 import BeautifulSoup
from SB_replacements import current_id_replacements, verse_replacements, synonyms_replacements, translation_replacements, purport_replacements
from pathlib import Path

requests_cache.install_cache(cache_name='SB-Vanipedia-Custom', backend='sqlite', expire_after=-1)


def parser(soup):
    b_tags = soup.find_all("b")
    print(b_tags)

    note1 = "<b>Translation and purport composed by disciples of Śrīla Prabhupāda</b>"
    note2 = "<b>Please note</b>"
    
    if str(b_tags[len(b_tags)-1])==note1:
        headers = str(b_tags[len(b_tags)-3])
    elif str(b_tags[len(b_tags)-1])==note2:
        headers = str(b_tags[len(b_tags)-2])
    else:
        headers = str(b_tags[len(b_tags)-1])

    headers = headers.replace('<b>', '')
    headers = headers.replace('</b>', '')
    headers = headers.replace(' - ', '---')
    headers = list(headers.split('---'))
    
    
    # Debug objects
    # print(headers)

    pointers = []
    for header in headers:
        head = list(list(header.split('>'))[1].split('<'))[0]
        pointers.append(head)
    
    print(pointers)

    current_id = str(soup.find("h1", {"id": "firstHeading"}))
    current_id = current_id_replacements(current_id)

    print(current_id)

    global _index
    # _index = "summary"
    # _index = "appendix"
    _index = "additional_notes"

    if len(pointers)==1:
        navigation = {"id": current_id, "prevId": None, "nextId": pointers[0]}

    else:
        navigation = {"id": current_id, "prevId": pointers[0], "nextId": pointers[1]}

    
    # Preparing Verse Entry
    verse_entry = None

    # Preparing Synonyms Entry
    synonyms_entry = None


    # Preparing Translation Entry
    translation_entry = None


    # Preparing Purport Entry
    purport = str(soup.find_all("div", {"class": "purport"}))
    purport_entry = None

    if purport and purport!="[]":
        purport = purport_replacements(purport)
        purport = list(filter(None, list(purport.split('---'))))

        purport_entry = []

        for para in purport:
            if para=="\n\n" or para=="\n":
                continue
            else:
                para_dictionary = {}

                if para[1:9]=='verse>>>':
                    para_dictionary["type"]="verse"
                    para_dictionary["content"]=para[9:]
                else:
                    para_dictionary["type"]="normal"
                    para_dictionary["content"]=para
            
                purport_entry.append(para_dictionary)

    
    # Preparing the consolidated JSON file.
    knowledge = {"info": navigation, "verses": verse_entry, "synonyms": synonyms_entry, "translation": translation_entry, "purport": purport_entry}
    
    json_knowledge = json.dumps(knowledge, indent=4, ensure_ascii=False)

    print(json_knowledge)
    print(type(json_knowledge))


    # Handling Directory creation.
    # directory = Path(f'/home/somit/Projects/web-scraping/SB/{canto}/{chapter}/')
    global canto
    # directory = Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{chapter}\\')
    directory = Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\')

    if not directory.exists():
        directory.mkdir(parents=True)
    


    # if Path(f'/home/somit/Projects/web-scraping/SB/{canto}/{chapter}/{_index}.json').is_file():
    if Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{_index}.json').is_file():
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{_index}.json', 'w', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)
    else:
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{_index}.json', 'x', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)


    global chap
    chap += 1



# Driver Code for parser
canto = 11
chap = 1

# custom_indices = ["Summary"]
custom_indices = ["Appendix"]
# custom_indices = ["Additional_Notes"]

# while chap<14:
# for chapter in range(chap,chap+1):
for _index in custom_indices:
    url = f'https://vanisource.org/wiki/SB_{canto}_{_index}'

    # print("Making a GET request")
    _source = requests.get(url)
    # print("Received response from the server")
    soup = BeautifulSoup(_source.content, 'html.parser')
    # print("Doing necessary validation and calling the Parser")

    page_check = str(soup.find("div", {"class":"noarticletext mw-content-ltr"}))

    if page_check and str(page_check)!=str(None):
        total += 1
        continue
    else:
        print(_index)
        # with open("C:\\Users\\somit.sinha\\Desktop\\soup.txt", 'w', encoding="utf-8") as soup_file:
        #     print(soup, file=soup_file)

        parser(soup)