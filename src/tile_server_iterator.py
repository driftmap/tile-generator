from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps
from typing import overload, Callable, Dict, Tuple

import json
import os
import requests
import time

class TileServerIterator():
    def __init__(self, OMT:str, city_key:str, filename:str, outpath:str, check_if_tile_exists:bool) -> None:
        self.OMT = OMT
        self.city = city_key
        self.filename = filename
        self.outpath = outpath
        self.check_if_tile_exists = check_if_tile_exists
        self.tilesize = 0

    def _timer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"The function {func.__name__} with arguments: {args} took: {(end-start)} sec")
            return result
        return wrapper

    def _init_city_dir(self, tile_tree_dict:Dict[str,Dict]):
        if not os.path.isdir(f"{self.outpath}{self.city}"):
            os.mkdir(f"{self.outpath}{self.city}")

    def _init_zoom_dir(self, zoom:int):
        if not os.path.isdir(f"{self.outpath}{self.city}/{zoom}"):
            os.mkdir(f"{self.outpath}{self.city}/{zoom}")

    def _init_x_dir(self, zoom:int, x:int):
        if not os.path.isdir(f"{self.outpath}{self.city}/{zoom}/{x}"):
            os.mkdir(f"{self.outpath}{self.city}/{zoom}/{x}")

    def _init_tile_req(self, x:int, y:int, zoom:int) -> Tuple[str, str]:
        url = f"{self.OMT}{zoom}/{x}/{y}.pbf"
        file = f"{self.outpath}{self.city}/{zoom}/{x}/{y}.pbf"
        return url, file

    def _update_city_metadata(self, tile_tree_dict):
        tile_tree_dict[self.city]['_total_tile_size'] = self.tilesize
        tile_tree_dict[self.city]['_avg_tile_size'] = self.tilesize / tile_tree_dict[self.city]['_nr_tiles']
        tile_tree_dict[self.city]['_updated'] = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        json.dump(tile_tree_dict[self.city], 
                  open(f'{self.outpath}{self.city}/config.json', 'w'), 
                  indent=4,  
                  sort_keys=True)

    @_timer
    def get_tiles_from_server(self) -> None:
        tile_tree_dict = json.load(open(f'{self.filename}', 'rb'))
        self.tile_list = []
        self._init_city_dir(tile_tree_dict)
        for zoom, v in tile_tree_dict[self.city]['tiles'].items():
            self._init_zoom_dir(zoom)
            for tile_nr in v:
                x = tile_nr[0]
                y = tile_nr[1]
                url, file = self._init_tile_req(x, y, zoom)
                self._init_x_dir(zoom, x)
                self.tile_list.append(tuple((url, file)))
        self._download_tile_list()
        self._update_city_metadata(tile_tree_dict)

    def _download_tile_list(self) -> None:
        futures = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            for tile_req in self.tile_list:
                future = executor.submit(self._download_tile, tile_req)
                futures.append(future)
            for future in futures:
                try:
                    print(future.result())
                except Exception as e:
                    print(e)

    def _download_tile(self, tile_req:Tuple[str,str]) -> str:
        if self.check_if_tile_exists:
            if os.path.isfile(tile_req[1]):
                msg = f"File '{tile_req[1]}' already exists."
            else:
                tile = requests.get(tile_req[0]).content
                open(f'{tile_req[1]}', 'wb').write(tile)
                msg = f"Finished downloading tile: {tile_req[0]}"
                self.tilesize += len(tile)
        else:
            tile = requests.get(tile_req[0]).content
            open(f'{tile_req[1]}', 'wb').write(tile)
            msg = f"Finished downloading tile: {tile_req[0]}"
            self.tilesize += len(tile)
        return msg

if __name__ == "__main__":
    main()
