import requests
import os
import sys
base_url="http://localhost:2333"
headers={"Content-Type":"application/json"}

def get_save_path():
    if getattr(sys, 'frozen', False):
        base_dir=os.path.dirname(sys.executable)
    else:
        base_dir=os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "Download")

save_path=get_save_path()

def login_api(name:str,password:str)->dict:
    print(name)
    print(password)
    try:
        r=requests.post(f"{base_url}/login",json={"name":name,"password":password},timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as er:
        return {"message":f"\033[31m[ERROR]:{str(er)}\033[0m"}
def register_api(name:str,password)->dict:
    try:
        r=requests.post(f"{base_url}/register",json={"name":name,"password":password},timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as er:
        return {"message":f"\033[31m[ERROR]:{str(er)}\033[0m"}
def changepw_api(oldpw:str,newpw:str,tokens:str)->dict:
    try:
        r=requests.post(f"{base_url}/changepassword",data={"oldpw":oldpw,"newpw":newpw},headers={"auth":tokens},timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as er:
        return {"message":f"\033[31m[ERROR]:{str(er)}\033[0m"}
def search_api(kw:str,tokens:str):
    r=requests.get(f"{base_url}/objects",params={"kw":kw},headers={"auth":tokens},timeout=10)
    r.raise_for_status()
    return r.json()
def find_api(objid:int,tokens:str):
    r=requests.get(f"{base_url}/objects/{objid}",data={"obj_id":objid},headers={"auth":tokens},timeout=10)
    r.raise_for_status()
    return r.json()
def download_api(id:int,tokens:str):
    os.makedirs(save_path, exist_ok=True)
    try:
        with requests.get(f"{base_url}/objects/{id}/download",headers={"auth":tokens},stream=True,timeout=10) as r:
            r.raise_for_status()
            filename=f"{id}.zip"
            if save_path:
                filepath=os.path.join(save_path,filename)
            else:
                filepath=filename
            with open(filepath,'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return {"message":"Download success","path":filepath}
    except requests.exceptions.RequestException as e:
        return {"message":f"FAILED:{str(e)}"}
