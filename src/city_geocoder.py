from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from unidecode import unidecode

import csv
import geocoder
import geopandas as gpd
import json
import mercantile
import os
import pickle

class Geocoder():
    def __init__(self, API_KEY:str, region:str, file:str, z_low:int, z_high:int, top_n:int, outpath:str) -> None:
        self.API_KEY = API_KEY
        self.region = region
        self.file = file
        self.rng = range(z_low, z_high)
        self.top_n = top_n
        self.outpath = outpath

    def geocode(self) -> None:
        queries = self._read_census()
        self._process_queries(queries)
        tile_tree = self._iter_tiles()
        json.dump(tile_tree, open(f'{self.outpath}_tile_tree.json', 'w'), indent=4,  sort_keys=True)

    def _read_census(self):
        queries = []
        if self.region == 'us':
            census = gpd.read_file("data/census_areas/tl_2021_us_uac10")
            for idx, row in census.iterrows():
                census_key = self._create_census_key(row['NAME10'])
                census_geom = row['geometry'].bounds
                queries.append((row['NAME10'], census_key, census_geom))
        else:
            census = gpd.read_file("data/census_areas/lcma000a16a_e")
            census = census.to_crs("epsg:4269")
            for idx, row in census.iterrows():
                name = unidecode(row['CMANAME'])
                census_key = self._create_census_key(name)
                census_geom = row['geometry'].bounds
                queries.append((name, census_key, census_geom))
        return queries

    def _process_queries(self, queries:list) -> None:
        self.city_tile_pairs = {}
        futures = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            for q in queries:
                future = executor.submit(self._geocode, q)
                futures.append(future)

            for future in futures:
                try:
                    print(future.result())
                except Exception as e:
                    print(e)

    def _geocode(self, q:list) -> str:
        self._tilegen_from_census_bounds(q[2], q[0], q[1])
        msg = f"Finished geocoding city: {q[0]}"
        return msg

    def _tilegen_from_census_bounds(self, bounds:list, name:str, key:str):
        tile_generator = mercantile.tiles(bounds[0],
                                          bounds[1],
                                          bounds[2],
                                          bounds[3],
                                          self.rng)
        self.city_tile_pairs[key] = {} 
        self.city_tile_pairs[key]['name'] = name
        self.city_tile_pairs[key]['tile_gen'] = tile_generator
        self.city_tile_pairs[key]['centroid'] = ((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2)
        self.city_tile_pairs[key]['bbox'] = bounds

    def _iter_tiles(self) -> dict:
        tile_tree = {}
        for k in self.city_tile_pairs.keys():
            tiles = self.city_tile_pairs[k]['tile_gen']
            tile_tree[k] = {}
            tile_tree[k]['name'] = self.city_tile_pairs[k]['name']
            tile_tree[k]['centroid'] = self.city_tile_pairs[k]['centroid']
            tile_tree[k]['bbox'] = self.city_tile_pairs[k]['bbox']
            tile_tree[k]['tiles'] = {}
            tile_counter = 0
            for tile in tiles:
                if tile.z not in tile_tree[k]['tiles']:
                    tile_tree[k]['tiles'][tile.z] = list()
                    tile_tree[k]['tiles'][tile.z].append((tile.x, tile.y))
                else:
                    tile_tree[k]['tiles'][tile.z].append((tile.x, tile.y))
                tile_counter += 1
            if tile_counter > 1000:
                print(f"Finished generating tiles for {tile_tree[k]['name']} with {tile_counter} tiles.")
        return tile_tree

    def _create_census_key(self, name:str) -> str:
        census_key = name.replace(", ", "_").lower()
        census_key = census_key.replace("--", "_")
        census_key = census_key.replace(" - ", "_")
        census_key = census_key.replace(" ", "")
        return census_key

    def _create_city_key(self, city:str, id:str) -> str:
        city_key = f'{city.replace(" ", "_")}_{id}'.lower()
        return city_key
