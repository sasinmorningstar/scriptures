import requests
import requests_cache
import json
from bs4 import BeautifulSoup
from pathlib import Path
from multiprocessing import Pool
from BG_replacements import devanagari_replacements, current_id_replacements, verse_replacements, synonyms_replacements,translation_replacements, purport_replacements


requests_cache.install_cache(cache_name='BG-Vanipedia', backend='sqlite', expire_after=-1)


def parser(soup):
    b_tags = soup.find_all("b")
    # print(b_tags)

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

    # print(headers)

    pointers = []
    for header in headers:
        head = list(list(header.split('>'))[1].split('<'))[0]
        # head = head[:7]
        # head = head.replace(" ", "/").replace("BG", "bg")

        pointers.append(head)

    # print(pointers)

    current_id = str(soup.find("h1", {"id": "firstHeading"}))
    current_id = current_id_replacements(current_id)

    print(current_id)

    global _index
    if len(current_id)==13:
        current_id = current_id[:-7]
        _index = current_id[5:]
        current_chapter = int(current_id[3])
        print(current_chapter)

    elif len(current_id)==14 and current_id[5]=='.':
        current_id = current_id[:-7]
        _index = current_id[6:]
        current_chapter = int(current_id[3:5])
        print(current_chapter)
    
    elif len(current_id)==15 and current_id[5]=='.':
        current_id = current_id[:-7]
        _index = current_id[6:]
        current_chapter = int(current_id[3:5])
        print(current_chapter)

    elif len(current_id)==14 and current_id[4]=='.':
        current_id = current_id[:-7]
        _index = current_id[5:]
        current_chapter = int(current_id[3])
        print(current_chapter)

    else:
        if current_id[4]=='.':
            current_id = current_id[:-7]
            _index = current_id[5:]
            current_chapter = int(current_id[3])
        else:
            current_id = current_id[:-7]
            _index = current_id[6:]
            current_chapter = int(current_id[3:5])


    if len(pointers)==1:
        navigation = {"id": current_id, "prevId": None, "nextId": pointers[0]}

        next_string = pointers[0]
        print(next_string)
        if len(next_string)==13:
            next_chapter = int(next_string[3])
            print(next_chapter)

        elif len(next_string)==14 and next_string[5]=='.':
            next_chapter = int(next_string[3:5])
            print(next_chapter)

        elif len(next_string)==15 and next_string[5]=='.':
            next_chapter = int(next_string[3:5])
            print(next_chapter)

        elif len(next_string)==14 and next_string[4]=='.':
            next_chapter = int(next_string[3])
            print(next_chapter)

        else:
            if current_chapter>10:
                next_chapter = int(next_string[3:5])
            else:
                next_chapter = int(next_string[3])

    else:
        navigation = {"id": current_id, "prevId": pointers[0], "nextId": pointers[1]}

        next_string = pointers[1]
        print(next_string)
        if len(next_string)==13:
            next_chapter = int(next_string[3])
            print(next_chapter)

        elif len(next_string)==14 and next_string[5]=='.':
            next_chapter = int(next_string[3:5])
            print(next_chapter)

        elif len(next_string)==15 and next_string[5]=='.':
            next_chapter = int(next_string[3:5])
            print(next_chapter)

        elif len(next_string)==14 and next_string[4]=='.':
            next_chapter = int(next_string[3])
            print(next_chapter)

        else:
            if current_chapter>10:
                next_chapter = int(next_string[3:5])
            else:
                next_chapter = int(next_string[3])



    # Preparing Devanagari Entry
    devanagari = str(soup.find("div", {"class":"devanagari"}))
    devanagari_entry = None

    if devanagari:
        devanagari = devanagari_replacements(devanagari)
        devanagari_entries = list(filter(None, list(devanagari.split('---'))))
        devanagari_entry = [{"devanagari": devanagari} for devanagari in devanagari_entries]
        devanagari_entry = devanagari_entry[1:]


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
    



    # Preparing the consolidated JSON entry.
    knowledge = {"info": navigation, "verses":verse_entry, "devanagari": devanagari_entry, "synonyms": synonyms_entry, "translation": translation_entry, "purport": purport_entry}

    json_knowledge = json.dumps(knowledge, indent=4, ensure_ascii=False)

    print(json_knowledge)

    # Handling Directory Creation
    directory = Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\bg\\{chapter}\\')

    if not directory.exists():
        directory.mkdir(parents=True)

    
    if Path(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\bg\\{chapter}\\{_index}.json').is_file():
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\bg\\{chapter}\\{_index}.json', 'w', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)

    else:
        with open(f'C:\\Users\\somit.sinha\\Desktop\\Projects\\Srimad-Bhagavatam\\books\\bg\\{chapter}\\{_index}.json', 'x', encoding="utf-8") as json_file:
            print(json_knowledge, file=json_file)

    
    # Code to automate the parser run for the entire Bhagavad Gita
    global total
    if current_chapter==next_chapter:
        total+=1
    else:
        total = 1
        global chap
        chap += 1









# def pipeline(url):
#     _source = requests.get(url)
#     soup = BeautifulSoup(_source.content, 'html.parser')
    
#     parser(soup)



# Driver Code for parser
# urls = ["https://vanisource.org/wiki/BG_1.1_(1972)",
# "https://vanisource.org/wiki/BG_2.1_(1972)",
# "https://vanisource.org/wiki/BG_3.1_(1972)",
# "https://vanisource.org/wiki/BG_4.1_(1972)",
# "https://vanisource.org/wiki/BG_5.1_(1972)",
# "https://vanisource.org/wiki/BG_6.1_(1972)",
# "https://vanisource.org/wiki/BG_7.1_(1972)",
# "https://vanisource.org/wiki/BG_8.1_(1972)",
# "https://vanisource.org/wiki/BG_9.1_(1972)",
# "https://vanisource.org/wiki/BG_10.1_(1972)",
# "https://vanisource.org/wiki/BG_11.1_(1972)",
# "https://vanisource.org/wiki/BG_12.1_(1972)",
# "https://vanisource.org/wiki/BG_13.1_(1972)",
# "https://vanisource.org/wiki/BG_14.1_(1972)",
# "https://vanisource.org/wiki/BG_15.1_(1972)",
# "https://vanisource.org/wiki/BG_16.1_(1972)",
# "https://vanisource.org/wiki/BG_17.1_(1972)",
# "https://vanisource.org/wiki/BG_18.1_(1972)",
# "https://vanisource.org/wiki/BG_18.18_(1972)"]



# if __name__ == '__main__':
#     with Pool(7) as processes:
#         processes.map(pipeline, urls)



# Driver Code for parser
chap = 10
total = 1

while chap<11:
    for chapter in range(chap, chap+1):
        for _index in range(total,total+1):
            url = f'https://vanisource.org/wiki/BG_{chapter}.{_index}_(1972)'

            _source = requests.get(url)
            soup = BeautifulSoup(_source.content, 'html.parser')

            page_check = str(soup.find("div", {"class":"noarticletext mw-content-ltr"}))

            if page_check and str(page_check)!=str(None):
                total += 1
                continue
            else:
                parser(soup)