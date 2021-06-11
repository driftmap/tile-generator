from dotenv import load_dotenv
from src.tile_generator import TileGenerator

import click
import os

load_dotenv()

"""
TODO:
- Add arguments for filename & outpath
- Add command for geocoding
- Add help 

"""

@click.group()
def main():
    pass

@click.command()
@click.argument('city_key')
def tilegen(city_key):
    click.echo(f'Launching tilegenerator for city key "{city_key}."')
    OMT = os.environ.get("OMT_URL")
    city_name = "Atlanta, Fulton County, Georgia, United States"
    filename = str(os.environ.get("DATA_PATH_CITY")) + "us_tile_tree.json"
    outpath = "data/tiles/"
    tg = TileGenerator(OMT,city_key,city_name,filename,outpath)
    tg.generate_tiles()

main.add_command(tilegen)

if __name__ == '__main__':
    main()
