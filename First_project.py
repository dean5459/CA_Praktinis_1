import requests
from bs4 import BeautifulSoup
import csv
import configparser
import logging

config = configparser.configParser()
config.read('configPath.ini')

logging.basicConfig(filename='main.log', level=logging.ERROR)


def request_and_parse(url_end: str='index.html'):
    try:
        req = requests.get(config['website']['url'] + url_end)
        req.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logging.exception("HTTP error occured: %s", error)
        
    soup = BeautifulSoup(req.content, 'html.parser')
    return soup
 

def get_p_lengths(soup_object: BeautifulSoup):
    text: list = []
    lengths: list = []
    for l in soup_object.find_all('li', class_ = "toctree-l1"):
        a = l.find('a')
        soup = request_and_parse(a['href'])
        p_tags = soup.find_all('p')
        p_tags_no_class = [tag for tag in p_tags if not tag.has_attr('class')]
        for tag in p_tags_no_class:
            text.append(tag.text)
        result = ''.join(text)
        lengths.append({"module_name": a.text, "module_length": len(result)})
        text = []
    return lengths
    

def write_to_csv(lengths_list: list):
    fields = ["module_name", "module_length"]

    with open("subject_lengths.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames = fields)
        writer.writeheader()

        for subject in lengths_list:
            writer.writerow(subject)


if __name__ == "__main__":
    soup = request_and_parse()
    lengths = get_p_lengths(soup)
    lengths.sort(key=lambda row: row['module_length'], reverse=True)
    write_to_csv(lengths)