from dotenv import load_dotenv

import csv
import geocoder
import json
import mercantile
import os
import pickle

"""
TODO

- OOP
- Connect to cli.py
- Add city_key to output
- Dynamic filepaths from CLI

"""

def main():
    load_dotenv()
    DATA_PATH = 'data/cities/'
    API_KEY = os.environ.get("GOOGLE_MAPS_KEY")
    us_queries = read_data(f'{DATA_PATH}uscities.csv', 10, region='us')
    can_queries = read_data(f'{DATA_PATH}canadacities.csv', 10, region='can')
    tile_rng = range(5,15)
    us_tiles = geocode(us_queries, tile_rng, API_KEY)
    can_tiles =  geocode(can_queries, tile_rng, API_KEY)
    us_tile_tree = iter_tiles(us_tiles)
    can_tile_tree = iter_tiles(can_tiles)
    json.dump(us_tile_tree, open(f'{DATA_PATH}us_tile_tree.json', 'w'))
    json.dump(can_tile_tree, open(f'{DATA_PATH}can_tile_tree.json', 'w'))

def read_data(file:str, top_n:int, region:str) -> list:
    queries = []
    with open(f'{file}', newline='') as f:
        reader = csv.DictReader(f, delimiter=',')
        for i,row in enumerate(reader):
            if region == 'us':
                city = row['city']
                state = row['state_name']
                county = row['county_name']
                queries.append(f'{city}, {county} County, {state}, United States')
            elif region == 'can':
                city = row['city']
                province = row['province_name']
                queries.append(f'{city}, {province}, Canada')
            if(i >= top_n):
                break
    return queries

def geocode(queries:list, tile_rng:list, api_key:str) -> dict:
    city_tile_pairs = {}
    for q in queries:
        print(q)
        g = geocoder.google(f'metropolitan, {q}', key = api_key)
        city_tile_pairs[q] = tiles_from_bbox(g)
    return city_tile_pairs

def tiles_from_bbox(g:dict) -> list:
    wsen = [g.json['bbox']['southwest'][1],
            g.json['bbox']['southwest'][0],
            g.json['bbox']['northeast'][1],
            g.json['bbox']['northeast'][0]]
    tiles = mercantile.tiles(wsen[0],
                             wsen[1],
                             wsen[2],
                             wsen[3],
                             tile_rng)
    return tiles

def iter_tiles(city_tile_pairs:dict) -> dict:
    tile_tree = {}
    for k in city_tile_pairs.keys():
        tiles = city_tile_pairs[k]
        tile_tree[k] = {}
        for tile in tiles:
            if tile.z not in tile_tree[k]:
                tile_tree[k][tile.z] = list()
                tile_tree[k][tile.z].append((tile.x, tile.y))
            else:
                tile_tree[k][tile.z].append((tile.x, tile.y))
    return tile_tree

if __name__ == "__main__":
    main()
