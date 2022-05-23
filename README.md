# tile-generator

CLI tool for:

1. extracting city geometries from shapefiles,
2. determining the bbox for each geometry,
3. determining the tiles necessary to span their bbox at different zoom levels, and
4. querying the tiles from an OpenMapTiles server to generate a folder tree with the tiles organized by zoom level.

Current CLI commands:

1. Geocoding:

Mandatory --region flag, with "us" and "can" as options.

```bash
python cli.py gentiletree --region us
```

2. Generate tiles:

```bash
python cli.py gentiles --region us
```

For more command flags, type:

```bash
python cli.py [COMMAND] --help
```
