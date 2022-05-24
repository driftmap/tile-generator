import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from mercantile import tiles, Tile

plot = False

# New York City
ny_shp = gpd.read_file("data/census_areas/Borough Boundaries")
ny_shp = ny_shp.to_crs("epsg:4269")
ny_shp = ny_shp.dissolve()
ny_shp = ny_shp.rename(columns={"boro_name":"NAME"}).filter(['NAME', 'geometry'])
ny_shp.NAME = "New York City, NY"
ny_shp = ny_shp.to_crs("epsg:4269")

# Montreal CMA
mtl_shp = gpd.read_file("data/census_areas/lcma000a16a_e")
mtl_shp = mtl_shp[mtl_shp.CMANAME == "Montréal"]
mtl_shp = mtl_shp.dissolve()
mtl_shp = mtl_shp.rename(columns={"CMANAME":"NAME"}).filter(['NAME', 'geometry'])
mtl_shp.NAME = "Montreal, QC"
mtl_shp = mtl_shp.to_crs("epsg:4269")
#census.iloc[:1].to_file("data/census_areas/ny/ny.shp")

# Atlanta
ua_shp = gpd.read_file("data/census_areas/tl_2021_us_uac10")
atl_shp = ua_shp[ua_shp.NAME10 == "Atlanta, GA"]
atl_shp = atl_shp.to_crs("epsg:4269")
atl_shp = atl_shp.dissolve()
atl_shp = atl_shp.rename(columns={"NAME10":"NAME"}).filter(['NAME', 'geometry'])
atl_shp.NAME = "Atlanta, GA"

# Los Angeles
la_shp = ua_shp[ua_shp.NAME10 == "Los Angeles--Long Beach--Anaheim, CA"]
la_shp = la_shp.to_crs("epsg:4269")
la_shp = la_shp.dissolve()
la_shp = la_shp.rename(columns={"NAME10":"NAME"}).filter(['NAME', 'geometry'])
la_shp.NAME = "Los Angeles, CA"

shp = pd.concat([ny_shp, mtl_shp, atl_shp, la_shp]).pipe(gpd.GeoDataFrame)
shp.to_file("data/census_areas/beta/beta.shp")

if plot:
    print(shp)
    shp.plot()
    plt.show()