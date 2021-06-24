from dotenv import load_dotenv

import json
import os
from functools import wraps
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

"""
TODO:
Create function which takes a CSV of city_strings and maps generate_tiles to each city for mass dling
"""

"""
Timing Improvement Notes:
Original Fetch Time:
Fetching tiles for atlanta took 335.68190026283264  sec to run
Fetching tiles for atlanta took 352.68857431411743  sec to run
Cleaned up Fetch time after threaded:
54.5 seconds
69 seconds
61 seconds
54 seconds
52 seconds
"""

class TileGenerator():
    def __init__(self, OMT:str, city_key:str, filename:str, outpath:str) -> None:
        self.OMT = OMT
        self.city = city_key
        #self.city_abrev = city_string
        self.filename = filename
        self.outpath = outpath

    def _timer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"The function {func.__name__} with arguments: {args} took: {(end-start)} sec")
            return result
        return wrapper

    @_timer
    def generate_tiles(self) -> None:
        tile_tree_dict = json.load(open(f'{self.filename}', 'rb'))
        self.tile_list = []
        if not os.path.isdir(f"{self.outpath}{self.city}"):
            os.mkdir(f"{self.outpath}{self.city}")
        for zoom, v in tile_tree_dict[self.city].items():
            if not os.path.isdir(f"{self.outpath}{self.city}/{zoom}"):
                os.mkdir(f"{self.outpath}{self.city}/{zoom}")
            for tile_nr in v:
                x = tile_nr[0]
                y = tile_nr[1]
                url = f"{self.OMT}{zoom}/{x}/{y}.pbf"
                file = f"{self.outpath}{self.city}/{zoom}/{x}/{y}.pbf"
                if not os.path.isdir(f"{self.outpath}{self.city}/{zoom}/{x}"):
                    os.mkdir(f"{self.outpath}{self.city}/{zoom}/{x}")
                self.tile_list.append(tuple((url, file)))
        self._download_tile_list()

    def _download_tile_list(self) -> None:
        futures = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            for tile_url in self.tile_list:
                future = executor.submit(self._download_tile, tile_url)
                futures.append(future)

            for future in futures:
                try:
                    print(future.result())
                except Exception as e:
                    print(e)

    def _download_tile(self, url:tuple) -> str:
        urllib.request.urlretrieve(url[0], url[1])
        msg = f"Finished downloading tile: {url[0]}"
        return msg

if __name__ == "__main__":
    main()
