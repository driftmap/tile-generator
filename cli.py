from dotenv import load_dotenv
from src.tile_generator import TileGenerator
from src.city_geocoder import Geocoder

import click
import os

load_dotenv()

"""
TODO:
- Add arguments for filename & outpath, z range, top_n etc
- Add command for geocoding
- Add help

"""

@click.group()
def main():
    pass

@click.command()
@click.argument('city_key')
def gentiles(city_key):
    click.echo(f'Launching tilegenerator for city key "{city_key}."')
    OMT = os.environ.get("OMT_URL")
    city_name = "Atlanta, Fulton County, Georgia, United States"
    filename = str(os.environ.get("DATA_PATH_CITY")) + "us_tile_tree.json"
    outpath = "data/tiles/"
    tg = TileGenerator(OMT,city_key,city_name,filename,outpath)
    tg.generate_tiles()

@click.command()
@click.argument('region')
def gentiletree(region):
    click.echo(f'Launching geocoder top cities."')
    API_KEY = os.environ.get("GOOGLE_MAPS_KEY")
    top_n = 10
    DATA_PATH = 'data/cities/'
    z_low = 5
    z_high = 15
    filename = f'{DATA_PATH}uscities.csv'
    outpath = f'{DATA_PATH}us_tile_tree.json'
    gc = Geocoder(API_KEY, region, filename, z_low, z_high, top_n, outpath)
    gc.geocode()

main.add_command(gentiles)
main.add_command(gentiletree)

if __name__ == '__main__':
    main()
