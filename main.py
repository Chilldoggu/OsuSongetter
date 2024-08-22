import requests
import zipfile
import shutil
import json
import re
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
    if requests.get("https://api.nerinyan.moe/health").status_code != 200:
        raise Exception("[ERROR] Server https://api.nerinyan.moe is down!")

    for set_id in beatmaps:
        map_dl = requests.get(f"https://api.nerinyan.moe/d/{set_id}")
        if map_dl.status_code != 200:
            raise Exception(f"[ERROR] Couldn't download mapset from server https://api.nerinyan.moe. Status code: {map_dl.status_code} {str(map_dl.content)}!")

        filename_pattern = re.compile(r'filename=\"\d+ (.+\.osz)\"')
        match = filename_pattern.search(map_dl.headers["Content-Disposition"])
        if (not match):
            print("Failed regex match.")
            continue

        title = match.group(1)
        print(f"{title} : {map_dl.status_code}")
        if map_dl.status_code == 200 and match:
            map_dest = comp_path.joinpath(title)
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
    audio_filename = {}

    for file in decomp_path.rglob("*.osu"):
        parent_dir = file.parent.name
        if audio_filename.get(parent_dir) == None:
            audio_filename[parent_dir] = []
        with open(file, 'r', encoding='utf-8') as fp:
            for line in fp.readlines():
                if line[:13] == "AudioFilename" and audio_filename[parent_dir].count(line[15:].strip('\n')) == 0:
                    audio_filename[parent_dir].append(line[15:].strip('\n'))
                    # Avoid having multiple audio.mp3 files as it is the most common way of saving it in the beatmapset
                    if "audio" in audio_filename[parent_dir][-1]:
                        shutil.copy(file.parent.joinpath(audio_filename[parent_dir][-1]), songs_path.joinpath(parent_dir+ "." + audio_filename[parent_dir][-1].split('.')[-1]))
                    else:
                        shutil.copy(file.parent.joinpath(audio_filename[parent_dir][-1]), songs_path.joinpath(audio_filename[parent_dir][-1]))
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