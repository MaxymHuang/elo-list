import xml.etree.ElementTree as ET

def parse_xml_to_json(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    anime_list = []
    anime_id = 0

    for anime in root.findall('anime'):
        title = anime.find('title').text
        anime_list.append({
            'id': anime_id,
            'title': title,
            'elo': 1000  # Starting ELO rating
        })
        anime_id += 1

    return anime_list
