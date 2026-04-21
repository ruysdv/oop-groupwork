from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from object import _cuser
from adminoruser import check_permission

admin_api=APIRouter()

class SetPermissionInput(BaseModel):
    permission: int

class AdminCreateUserInput(BaseModel):
    username: str
    password: str
    permission: int = 1

@admin_api.post("/admin/users")
def admin_create_user(name:str,pw:str,power:int=1, _:str=Depends(check_permission(0))):
    x=_cuser()
    try:
        x.execute("INSERT INTO users (name,password,power) VALUES (?,?,?)",(name,pw,power))
        x.commit()
    except Exception as e:
        x.close()
        raise HTTPException(400,"Failed")
    x.close()
    return {"message":"Success","username":name}

@admin_api.get("/admin/users/list")
def admin_users_list(_str=Depends(check_permission(0))):
    x=_cuser()
    r=x.execute("SELECT * FROM users").fetchall()
    x.close()
    return [dict(row) for row in r]

@admin_api.delete("/admin/users/{username}")
def admin_delete_user(name:str,_:str=Depends(check_permission(0))):
    x=_cuser()
    r=x.execute("SELECT id FROM users WHERE name=?",(name,)).fetchone()
    if(not r):
        x.close()
        raise HTTPException(400,"Failed")
    x.execute("DELETE FROM users WHERE name=?",(name,))
    x.execute("DELETE FROM tokens WHERE name=?",(name,))
    x.commit()
    x.close()
    return {"message": f"Delete {name} successfully"}

@admin_api.put("/admin/users/{username}/permission")
def admin_set_permission(name:str,power:int,_: str=Depends(check_permission(0))):
    x=_cuser()
    r=x.execute("SELECT id FROM users WHERE name=?",(name,)).fetchone()
    if(not r):
        x.close()
        raise HTTPException(400,"X")
    x.execute("UPDATE users SET power=? WHERE name=?",(power,name))
    x.commit()
    x.close()
    return {"message":"Success"}
