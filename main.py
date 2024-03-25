from pathlib import Path
import json
from ossapi import Ossapi

def init_client(acc_id, secret):
    print(acc_id, secret)

def get_credentials():
    credentials = {
        "id": 0,
        "secret": ""
    }
    fp_credentials = Path().cwd().joinpath("OAuth_credentials.json")

    if fp_credentials.exists():
        with open(fp_credentials, 'r') as fp:
            data = json.load(fp)
            credentials["id"] = int(data["id"])
            credentials["secret"] = data["secret"] 
    else:
        credentials["id"] = int(input("Input your OAuth id: "))
        credentials["secret"] = input("Input your OAuth secret: ")
        json_obj = json.dumps(credentials, indent=4)
        with open(fp_credentials, 'w') as fp:
            fp.write(json_obj)

    return credentials

if __name__ == "__main__":
    credentials = get_credentials()
    init_client(credentials["id"], credentials["secret"]) 