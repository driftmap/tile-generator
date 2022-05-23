from dotenv import load_dotenv
from src.tile_tree_generator import TileTreeGenerator
from src.tile_iterator import TileIterator

import click
import os

load_dotenv()

"""
TODO:
- Add arguments for filename & outpath, etc
- Add help

"""

city_key_help = """
City key to generate tiles for. Write city in lower case and connect with identifier using underscore.\n
For US cities, identifier is county FIPS number. For example, atlanta_ga.\n
For Canadian cities, identifier is province abbrevation. For example, montreal_QC.\n
"""

@click.group()
def main() -> None:
    pass

@click.command()
@click.option("--region", type=click.Choice(['us', 'can']), required=True, help="Region to geocode.")
@click.option("--top-n", default=10, help="Number of cities to geocode.")
@click.option("--z-low", default=5, help="Lower bound of zoom.")
@click.option("--z-high", default=15, help="Upper bound of zoom.")
@click.option("--data-path", default='data/cities/', help="Folder from which to read and write data.")
def gentiletrees(region:str, top_n:int, z_low:int, z_high:int, data_path:str) -> None:
    click.echo(f'Launching geocoder for region "{region}", with top {top_n} cities and zoom range {z_low}-{z_high}.')
    API_KEY = os.environ.get("GOOGLE_MAPS_KEY")
    filename = f'{data_path}{region}cities.csv'
    outpath = f'{data_path}{region}'
    ti = TileIterator(API_KEY, region, filename, z_low, z_high, top_n, outpath)
    ti.tiles_from_tileserver()

@click.command()
@click.option("--region", type=click.Choice(['us', 'can']), required=True, help="Region to geocode.")
@click.option("--city_key", default="atlanta_ga", help=city_key_help)
@click.option("--check_tiles", default=True, help=city_key_help)
def gentiles(city_key:str, region:str, check_tiles:bool) -> None:
    click.echo(f'Launching tilegenerator for city key "{city_key}."')
    OMT = os.environ.get("OMT_URL")
    filename = str(os.environ.get("DATA_PATH_CITY")) + f"{region}_tile_tree.json"
    outpath = "data/tiles/"
    ttg = TileTreeGenerator(OMT,city_key,filename,outpath,check_tiles)
    ttg.generate_tiletrees()

main.add_command(gentiletrees)
main.add_command(gentiles)

if __name__ == '__main__':
    main()
