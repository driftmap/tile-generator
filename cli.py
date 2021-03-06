from dotenv import load_dotenv
from src.tile_server_iterator import TileServerIterator
from src.tile_tree_generator import TileTreeGenerator

import upload_tool
import click
import os

load_dotenv()

city_key_help = """
City key to generate tiles for. Write city in lower case and connect with identifier using underscore.\n
For US cities, identifier is county FIPS number. For example, atlanta_ga.\n
For Canadian cities, identifier is province abbrevation. For example, montreal_QC.\n
"""

@click.group()
def main() -> None:
    pass

@click.command()
@click.option("--region", type=click.Choice(['us', 'can', 'beta']), required=True, help="Region to geocode.")
@click.option("--top-n", default=10, help="Number of cities to geocode.")
@click.option("--z-low", default=5, help="Lower bound of zoom.")
@click.option("--z-high", default=15, help="Upper bound of zoom.")
@click.option("--data-path", default='data/cities/', help="Folder from which to read and write data.")
def gentiletrees(region:str, top_n:int, z_low:int, z_high:int, data_path:str) -> None:
    click.echo(f'Launching geocoder for region "{region}", with top {top_n} cities and zoom range {z_low}-{z_high}.')
    outpath = f'{data_path}{region}'
    print([region, z_low, z_high, top_n, outpath])
    ttg = TileTreeGenerator(region, z_low, z_high, top_n, outpath)
    ttg.generate_tile_trees_from_shapefiles()

@click.command()
@click.option("--region", type=click.Choice(['us', 'can','beta']), required=True, help="Region to geocode.")
@click.option("--city_key", default="atlanta_ga", help=city_key_help)
@click.option("--check_tiles", default=True, help=city_key_help)
def itertileserver(city_key:str, region:str, check_tiles:bool) -> None:
    click.echo(f'Launching tilegenerator for city key "{city_key}."')
    OMT = os.environ.get("OMT_URL")
    filename = str(os.environ.get("DATA_PATH_CITY")) + f"{region}_tile_tree.json"
    outpath = "data/tiles/"
    tsi = TileServerIterator(OMT,city_key,filename,outpath,check_tiles)
    tsi.get_tiles_from_server()

@click.command()
def uploadall() -> None:
    click.echo("Uploading all tiles")
    HOSTNAME = os.environ.get("HOSTNAME")
    USERNAME = os.environ.get("USERNAME")
    DRIFT_KEY = os.environ.get("DRIFT_KEY")
    LOCAL_DIR = os.environ.get("LOCAL_DIR")
    upload_tool.upload_all(HOSTNAME, USERNAME, DRIFT_KEY, LOCAL_DIR)

main.add_command(gentiletrees)
main.add_command(itertileserver)
main.add_command(uploadall)

if __name__ == '__main__':
    main()