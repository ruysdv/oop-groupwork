from __future__ import annotations
from pydantic import BaseModel
from fastapi import Form
from fastapi import APIRouter,Depends,HTTPException
import sqlite3
import os
import time
import uuid
from object import _cuser
from object import _users
from adminoruser import cklogin
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_PATH = os.path.join(BASE_DIR,"user.data")
FILES_DIR = os.path.join(BASE_DIR,"objects")

user_api=APIRouter()

LOCK_TIME=30*60

class info(BaseModel):
    name:str
    password:str

@user_api.post("/register")
async def register(data:info):
    name=data.name
    password=data.password
#async def register(name:str,password:str):
    x=_cuser()
    try:
        x.execute("INSERT INTO users (name,password,power) VALUES (?,?,?)",(name,password,1))
        x.commit()
    except sqlite3.IntegrityError:
        x.close
        raise HTTPException(400,"\033[31m[ERROR]:Users existed\033[0m")
    x.close()
    return {"message":"Register successfully!","name":name}

@user_api.post("/login")
async def login(data:info):
    name=data.name
    password=data.password
#async def login(name:str=Form(...),password:str=Form(...)):
    x=_cuser()
    r=x.execute("SELECT password FROM users WHERE name=?",(name,)).fetchone()
    p=x.execute("SELECT power FROM users WHERE name=?",(name,)).fetchone()
    x.close()
    if(not r)or(r["password"]!=password):
        raise HTTPException(400,"\033[31m[ERROR]:Username or password is wrong!\033[0m")
    tk=str(uuid.uuid4())
    now=int(time.time())
    x=_cuser()
    x.execute("DELETE FROM tokens WHERE name=? AND create_time<?",(name,now-LOCK_TIME))
    x.execute("INSERT INTO tokens (token,name,create_time) VALUES (?,?,?)",(tk,name,now))
    x.commit()
    x.close()
    return {"message":"Login successfully","token":tk,"power":p["power"]}

@user_api.post("/changepassword")
async def change_pw(oldpw:str,newpw:str,users:str=Depends(cklogin)):
    x=_cuser()
    r=x.execute("SELECT password FROM users WHERE name=?",(users,)).fetchone()
    if(not r)or(r['password']!=oldpw):
        x.close()
        raise HTTPException(400,"\033[31m[ERROR]:Password is wrong!\033[0m")
    x.execute("UPDATE users SET password=? WHERE name=?",(newpw,users))
    x.commit()
    x.close()
    return {"message":"Success!"}

@user_api.delete("/account")
async def remove_user(users:str=Depends(cklogin)):
    x=_cuser()
    x.execute("DELETE FROM users WHERE name=?",(users,))
    x.execute("DELETE FROM token WHERE name=?",(users,))
    x.commit()
    x.close()
    return {"message":"Success"}
