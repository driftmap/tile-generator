import geopandas as gpd

census = gpd.read_file("data/census_areas/500Cities_City_11082016")
census = census.to_crs("epsg:4269")
print(census)
print(census.crs)