import requests
from pathlib import Path


def get_beatmaps_id():
    beatmaps_id = None
    fp_beatmapsets = Path().cwd().joinpath("beatmapset_id.txt")

    if fp_beatmapsets.exists():
        with open(fp_beatmapsets, 'r') as fp:
            beatmaps_id = [beatmapset_id.strip('\n') for beatmapset_id in fp.readlines()]

    return beatmaps_id


def download_maps(beatmaps):
    for set_id in beatmaps:
        map_info = requests.get("https://api.chimu.moe/v1/set/" + set_id).json()
        map_dl = requests.get("https://api.chimu.moe/v1/download/" + set_id)

        if map_dl.status_code == 200 and not map_info.get("error_code"):
            map_dest = Path().cwd().joinpath("Compressed", map_info["Title"] + ".osz")
            with open(map_dest, 'wb') as fp:
                fp.write(map_dl.content)


if __name__ == "__main__":
    # Get map ids from URL
    beatmaps = get_beatmaps_id()

    # Downlond maps
    download_maps(beatmaps)

    # Decompress beatmaps into folder "Decompressed"

    # Get songs from decompressed beatmaps and save them to a folder "Songs"