import requests
import requests_cache
import json
from bs4 import BeautifulSoup
from SB_replacements import current_id_replacements, verse_replacements, synonyms_replacements, translation_replacements, purport_replacements
from pathlib import Path


requests_cache.install_cache(cache_name='SB-Vanipedia', backend='sqlite', expire_after=-1)

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
    global canto
    if canto<10:
        if len(current_id)>9 and current_id[7]=='.':
            _index = current_id[8:]

        elif len(current_id)>9:
            _index = current_id[7:]

        # if current_id[7]==".":
        #     current_chapter = int(current_id[5:7])
        # else:
        #     current_chapter = int(current_id[5:6])
        
        # print(current_chapter)

        if len(pointers)==1:
            navigation = {"id": current_id, "prevId": None, "nextId": pointers[0]}

            # if pointers[0][7]==".":
            #     next_chapter = int(pointers[0][5:7])
            # else:
            #     next_chapter = int(pointers[0][5:6])
            
            # print(next_chapter)
        else:
            navigation = {"id": current_id, "prevId": pointers[0], "nextId": pointers[1]}

            # if pointers[1][7]==".":
            #     next_chapter = int(pointers[1][5:7])
            # else:
            #     next_chapter = int(pointers[1][5:6])
            
            # print(next_chapter)
    else:

        if len(current_id)>9 and current_id[5]=="." and current_id[7]==".":
            _index = current_id[8:]

        elif len(current_id)>9 and current_id[5]=="." and current_id[8]==".":
            _index = current_id[9:]
        
        elif len(current_id)>9 and current_id[7]=='.':
            _index = current_id[8:]

        elif len(current_id)>9:
            _index = current_id[7:]



        # if current_id[7]=="." and current_id[5]==".":
        #     current_chapter = int(current_id[6:7])
        
        # elif current_id[8]==".":
        #     current_chapter = int(current_id[6:8])

        # elif current_id[7]==".":
        #     current_chapter = int(current_id[5:7])
        # else:
        #     current_chapter = int(current_id[5:6])
        
        # print(current_chapter)



        if len(pointers)==1:
            navigation = {"id": current_id, "prevId": None, "nextId": pointers[0]}


            # if pointers[0][7]=="." and pointers[0][5]==".":
            #     next_chapter = int(pointers[0][6:7])

            # elif pointers[0][8]==".":
            #     next_chapter = int(pointers[0][6:8])

            # elif pointers[0][7]==".":
            #     next_chapter = int(pointers[0][5:7])
            # else:
            #     next_chapter = int(pointers[0][5:6])
            
            # print(next_chapter)

        else:
            navigation = {"id": current_id, "prevId": pointers[0], "nextId": pointers[1]}

            # if pointers[1][7]=="." and pointers[1][5]==".":
            #     next_chapter = int(pointers[1][6:7])
            
            # elif pointers[1][8]==".":
            #     next_chapter = int(pointers[1][6:8])

            # elif pointers[1][7]==".":
            #     next_chapter = int(pointers[1][5:7])

            # else:
            #     next_chapter = int(pointers[1][5:6])
            
            # print(next_chapter)

    
    # Preparing Verse Entry
    verse = str(soup.find("div", {"class":"verse"}))
    verse_entry = None
    
    if verse:
        verse = verse_replacements(verse)
        verse_entries = list(filter(None, list(verse.split('---'))))
        verse_entry = [{"roman": verse} for verse in verse_entries]
        verse_entry = verse_entry[1:]

    # Preparing Synonyms Entry
    synonyms = str(soup.find("div", {"class": "synonyms"}))
    synonyms_entry = None
    
    if synonyms:
        synonyms_entry = synonyms_replacements(synonyms)


    # Preparing Translation Entry
    translation = str(soup.find("div", {"class":"translation"}))
    translation_entry = None

    if translation:
        translation_entry = translation_replacements(translation)


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
    directory = Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{chapter}\\')

    if not directory.exists():
        directory.mkdir(parents=True)
    


    # if Path(f'/home/somit/Projects/web-scraping/SB/{canto}/{chapter}/{_index}.json').is_file():
    if Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{chapter}\\{_index}.json').is_file():
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{chapter}\\{_index}.json', 'w', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)
    else:
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\sb\\{canto}\\{chapter}\\{_index}.json', 'x', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)


    # Code to automate the parser run for an entire Canto.
    # global total
    # if current_chapter==next_chapter:
    #     total += 1
    # else:
    #     total = 1
    #     global chap
    #     chap += 1


# Driver Code for parser
canto = 10
chap = 1
total = 69

custom_verses = ["1a-2a", "1b", "2b"]

# while chap<14:
for chapter in range(chap,chap+1):
    for _index in range(total,total+1):
    # custom code
    # for _index in custom_verses:
        url = f'https://vanisource.org/wiki/SB_{canto}.{chapter}.{_index}'

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