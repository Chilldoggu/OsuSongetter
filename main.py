import requests
import zipfile
import shutil
from pathlib import Path

decomp_path = Path().cwd().joinpath("Decompressed")
comp_path = Path().cwd().joinpath("Compressed")
songs_path = Path().cwd().joinpath("Songs")

def check_dir_health():
    if not decomp_path.exists() and not decomp_path.is_dir():
        decomp_path.mkdir()
    if not comp_path.exists() and not comp_path.is_dir():
        comp_path.mkdir()
    if not songs_path.exists() and not songs_path.is_dir():
        songs_path.mkdir()

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
            map_dest = comp_path.joinpath(map_info["Title"] + ".osz")
            with open(map_dest, 'wb') as fp:
                fp.write(map_dl.content)


def decompress_maps():
    for file in comp_path.glob("*.osz"):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            beatmap_dir = decomp_path.joinpath(file.stem)
            if not beatmap_dir.exists():
                beatmap_dir.mkdir()
                zip_ref.extractall(beatmap_dir)


def get_song_files():
    audio_filename = None

    for file in decomp_path.rglob("*.osu"):
        with open(file, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                if line[:13] == "AudioFilename":
                    audio_filename = line.split()[1]
                    break
        shutil.copy(file.parent.joinpath(audio_filename), songs_path.joinpath(file.parent.stem + "." + audio_filename.split('.')[-1]))
    

if __name__ == "__main__":
    # Check if all dirs exists
    check_dir_health()
    
    # Get map ids from URL
    beatmaps = get_beatmaps_id()

    # Downlond maps
    download_maps(beatmaps)

    # Decompress beatmaps into folder "Decompressed"
    decompress_maps()

    # Get songs from decompressed beatmaps and save them to a folder "Songs"
    get_song_files()