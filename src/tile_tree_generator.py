from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from mercantile import tiles, Tile
from typing import Dict, List, Tuple
from unidecode import unidecode

import csv
import geopandas as gpd
import json
import os
import pickle

class TileTreeGenerator():
    def __init__(self, API_KEY:str, region:str, file:str, z_low:int, z_high:int, top_n:int, outpath:str) -> None:
        self.API_KEY = API_KEY
        self.region = region
        self.file = file
        self.rng = range(z_low, z_high)
        self.top_n = top_n
        self.outpath = outpath

    def generate_tile_trees_from_shapefiles(self) -> None:
        queries = self._read_census()
        self._process_queries(queries)
        tile_tree, tile_diagnostics = self._iter_tiles()
        print("Tiles with more than 5k tiles:")
        print(dict(sorted(tile_diagnostics.items(), key=lambda item: item[1])))
        json.dump(tile_tree, open(f'{self.outpath}_tile_tree.json', 'w'), indent=4,  sort_keys=True)

    def _read_us_census(self) -> List[Tuple[str,str,Tuple[float,float,float,float]]]:
        queries = []
        census = gpd.read_file(f"data/census_areas/tl_2021_us_uac10")
        name_col = [col for col in census if col.startswith('NAME')][0]
        geom_col = [col for col in census if col.startswith('geom')][0]
        for idx, row in census.iterrows():
            census_key = self._create_census_key(row[name_col])
            census_geom = row[geom_col].bounds
            queries.append((row[name_col], census_key, census_geom))
        return queries

    def _read_can_census(self) -> List[Tuple[str,str,Tuple[float,float,float,float]]]:
        queries = []
        census = gpd.read_file("data/census_areas/lcma000a16a_e")
        census = census.to_crs("epsg:4269")
        for idx, row in census.iterrows():
            name = unidecode(row['CMANAME'])
            census_key = self._create_census_key(name)
            census_geom = row['geometry'].bounds
            queries.append((name, census_key, census_geom))
        return queries

    def _read_census(self) -> List[Tuple[str,str,Tuple[float,float,float,float]]]:
        if self.region == 'us':
            queries = self._read_us_census()
        else:
            queries = self._read_can_census()
        return queries

    def _process_queries(self, queries:List[Tuple[str,str,Tuple[float,float,float,float]]]) -> None:
        self.city_tile_pairs = {}
        futures = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            for q in queries:
                future = executor.submit(self._gen_query, q)
                futures.append(future)

            for future in futures:
                try:
                    print(future.result())
                except Exception as e:
                    print(e)

    def _gen_query(self, q:Tuple[str,str,Tuple[float,float,float,float]]) -> str:
        self._tilegen_from_census_bounds(q[2], q[0], q[1])
        msg = f"Loaded census data for city: {q[0]}"
        return msg

    def _tilegen_from_census_bounds(self, bounds:List[float], name:str, key:str):
        tile_generator = tiles(bounds[0],
                               bounds[1],
                               bounds[2],
                               bounds[3],
                               self.rng)
        self.city_tile_pairs[key] = {} 
        self.city_tile_pairs[key]['_key'] = key
        self.city_tile_pairs[key]['_name'] = name
        self.city_tile_pairs[key]['tile_gen'] = tile_generator
        self.city_tile_pairs[key]['_centroid'] = ((bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2)
        self.city_tile_pairs[key]['_bbox'] = bounds

    def _expand_tile_tree(self, tile_tree:Dict, k:str) -> Dict[str,Dict]:
        tile_tree[k] = {}
        tile_tree[k]['_name'] = self.city_tile_pairs[k]['_name']
        tile_tree[k]['_centroid'] = self.city_tile_pairs[k]['_centroid']
        tile_tree[k]['_bbox'] = self.city_tile_pairs[k]['_bbox']
        tile_tree[k]['_key'] = self.city_tile_pairs[k]['_bbox']
        tile_tree[k]['tiles'] = {}
        return tile_tree

    def _add_tiles(self, tile:Tile, city_tile_tree:Dict[str,Dict]) -> Dict[str,Dict]:
        if tile.z not in city_tile_tree['tiles']:
            city_tile_tree['tiles'][tile.z] = list()
            city_tile_tree['tiles'][tile.z].append((tile.x, tile.y))
        else:
            city_tile_tree['tiles'][tile.z].append((tile.x, tile.y))
        return city_tile_tree

    def _iter_tiles(self) -> Dict[str,Dict]:
        tile_diagnostics = {}
        tile_tree = {}
        for k in self.city_tile_pairs.keys():
            tiles = self.city_tile_pairs[k]['tile_gen']
            tile_tree = self._expand_tile_tree(tile_tree, k)
            tile_counter = 0
            for tile in tiles:
                tile_tree[k] = self._add_tiles(tile, tile_tree[k])
                tile_counter += 1
            if tile_counter > 1000:
                print(f"Finished generating tiles for {tile_tree[k]['_name']} with {tile_counter} tiles.")
            tile_tree[k]['_nr_tiles'] = tile_counter
            tile_diagnostics[k] = tile_counter
        return tile_tree, tile_diagnostics

    def _create_census_key(self, name:str) -> str:
        census_key = name.replace(", ", "_").lower()
        census_key = census_key.replace("--", "_")
        census_key = census_key.replace(" - ", "_")
        census_key = census_key.replace(" ", "")
        return census_key

    def _create_city_key(self, city:str, id:str) -> str:
        city_key = f'{city.replace(" ", "_")}_{id}'.lower()
        return city_key
