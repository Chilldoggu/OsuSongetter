from pathlib import Path
import json
from ossapi import Ossapi

def init_client(acc_id, secret):
    ... 

def get_credentials():
    secret = acc_id = 0
    fp_credentials = Path().cwd().joinpath("OAuth_credentials.json")

    if fp_credentials.exists():
        with open(fp_credentials, 'r') as fp:
            data = json.load(fp)
            secret = data["secret"] 
            acc_id = int(data["id"])
    else:
        secret = input("Input your OAuth secret: ")
        acc_id = int(input("Input your OAuth id: "))
    
    return [acc_id, secret]

if __name__ == "__main__":
    acc_id, secret = get_credentials()
    init_client(acc_id, secret) 