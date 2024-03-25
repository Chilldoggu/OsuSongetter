import requests
import zipfile
import shutil
import json
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
    fp_beatmapsets = Path().cwd().joinpath("beatmapset_id.json")

    if fp_beatmapsets.exists():
        with open(fp_beatmapsets, 'r') as fp:
            json_obj = json.load(fp)
            beatmaps_id = [str(set_id) for set_id in json_obj["id"]]

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
    audio_filename = []

    for file in decomp_path.rglob("*.osu"):
        with open(file, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                if line[:13] == "AudioFilename" and audio_filename.count(line[15:].strip('\n')) == 0:
                    audio_filename.append(line[15:].strip('\n'))
                    # Avoid having multiple audio.mp3 files as it is the most common way of saving it in the beatmapset
                    if audio_filename[-1].split('.')[0] == "audio":
                        shutil.copy(file.parent.joinpath(audio_filename[-1]), songs_path.joinpath(file.parent.stem + "." + audio_filename[-1].split('.')[-1]))
                    else:
                        shutil.copy(file.parent.joinpath(audio_filename[-1]), songs_path.joinpath(audio_filename[-1]))
                    break
    

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