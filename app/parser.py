import xml.etree.ElementTree as ET

def elo_modifier(score):
    elo = 1000
    elo = elo + score ** 3
    return elo

def parse_xml_to_json(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    anime_list = []
    anime_id = 0

    for anime in root.findall('anime'):
        title = anime.find('series_title').text
        score = float(anime.find('my_score').text)
        anime_list.append({
            'id': anime_id,
            'title': title,
            'elo': elo_modifier(score)  # Starting ELO rating
        })
        anime_id += 1

    return anime_list

