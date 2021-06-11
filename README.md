# tile-generator

CLI tool for:

1. geocoding cities,
2. determining the tiles necessary to span their bbox at different zoom levels, and
3. querying the tiles from an OpenMapTiles server to generate a folder tree with the tiles organized by zoom level.

Current CLI commands:

1. Geocoding:

Mandatory --region flag, with "us" and "can" as options.

```bash
python cli.py gentiletree --region us
```

2. Generate tiles:

```bash
python cli.py gentiles
```

For more command flags, type:

```bash
python cli.py [COMMAND] --help
```
