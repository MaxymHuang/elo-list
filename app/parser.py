import xml.etree.ElementTree as ET

def elo_modifier(score):
    elo = 500
    elo = elo + score ** 2
    return elo

def parse_xml_to_json(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    anime_list = []
    anime_id = 0

    for anime in root.findall('anime'):
        if anime.find('my_status').text == 'Completed':
            title = anime.find('series_title').text
            score = float(anime.find('my_score').text)
            if score >= 7:
                anime_list.append({
                    'id': anime_id,
                    'title': title,
                    'elo': elo_modifier(score)  # Starting ELO rating
                })
        anime_id += 1

    return anime_list

