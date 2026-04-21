from __future__ import annotations
import sqlite3
import os
from object import _connect
from object import _data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.abab")
FILES_DIR = os.path.join(BASE_DIR, "objects")
#DATA_PATH = "data.abab"
#FILES_DIR = "objects"

def add_object(id:int,t:str,zz:str,itd:str):
    x=_connect()
    try:
        x.execute(
            "INSERT INTO objects(id,title,zuozhe,introduction) VALUES (?,?,?,?)",
            (id,t,zz,itd)
        )
        x.commit()
    except sqlite3.IntegrityError:
        x.close()
        return False#失败
    x.close()
    return True

def remove_object(id:int):
    x=_connect()
    x.execute("DELETE FROM objects WHERE id = ?", (id,))
    x.commit()
    x.close()

def edit_imformation(id:int,t:str=None,zz:str=None,itd:str=None):
    x=_connect()
    if(t):
        x.execute("UPDATE objects SET title=? WHERE id=?",(t,id))
    if(zz):
        x.execute("UPDATE objects SET zuozhe=? WHERE id=?",(zz,id))
    if(itd):
        x.execute("UPDATE objects SET introduction=? WHERE id=?",(itd,id))
    #x.execute("UPDATE objects SET title=?,zuozhe=?,introduction=? WHERE id=?",(t,zz,itd,id))
    x.commit()
    x.close()

def list_object()->dict:
    x=_connect()
    r=x.execute("SELECT * FROM objects").fetchall()
    x.close()
    # 将数据库行转换为字典列表
    return [dict(row) for row in r]

def find_object(id:int)->dict|None:
    x=_connect()
    r=x.execute("SELECT * FROM objects WHERE id=?",(id,)).fetchone()
    x.close()
    return dict(r) if r else None

def search_object(kw:str):
    x=_connect()
    r=x.execute("SELECT * FROM objects WHERE title LIKE ? OR zuozhe LIKE ? OR introduction LIKE ?",(f"%{kw}%",f"%{kw}%",f"%{kw}%")).fetchall()
    x.close()
    if(r):
        return [dict(row) for row in r]
    return []

def download_object(id:int):
    x=_connect()
    x.execute("UPDATE objects SET download_sum=download_sum+1 WHERE id=?",(id,))
    x.commit()
    x.close()