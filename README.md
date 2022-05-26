# tile-generator

This is a command line tool for querying a tileserver and getting a static dump of tile files within a given geometry. The code here can be used to

1. extract and merge city geometries from shapefiles,
2. determine the bbox for each geometry,
3. determine the tiles necessary to span their bbox at different zoom levels, and
4. query the tiles from an OpenMapTiles server to generate a folder tree with the tiles organized by zoom level.
5. push the tiles to a dev server

The repo is part of a project to build an end-to-end encrypted mapping app. In the beta stage, the app will include four cities. For this app, the above steps are executed with the following steps:

## 1. Extract and merge city geometries:

```bash
python src/beta_data_merger.py
```

## 2. & 3. Determine bbox for city geometries and bbox to span them

```bash
python cli.py gentiletrees --region beta
```

## 4.  Query OMT server for tiles

```bash
python cli.py itertileserver --region beta --city_key atlanta_ga
```

## 5. Push tiles to dev server

```bash
python cli.py uploadall
```