from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi import Query
import os
from sql import (add_object,remove_object,edit_imformation,list_object,find_object,FILES_DIR,search_object,download_object)
from adminoruser import check_permission
api = APIRouter()

@api.post("/objects")
async def add_obj(obj_id:int=Form(...),t:str=Form(...),zz:str=Form(""),itd:str=Form(""),file:UploadFile=File(...),_:str=Depends(check_permission(0)),):
    if(not add_object(obj_id,t,zz,itd)):
        raise HTTPException(409,"This id exists")
    fp=os.path.join(FILES_DIR,f"{obj_id}.zip")
    with open(fp,"wb") as f:
        f.write(await file.read())
    return {"id":obj_id,"message":"Success"}

@api.put("/objects/{obj_id}")
async def edit_imf(obj_id:int,t:str=Form(None),zz:str=Form(None),itd:str=Form(None),file:UploadFile=File(None),_:str=Depends(check_permission(0)),):
    obj=find_object(obj_id)
    if(not obj):
        raise HTTPException(404,"Not Found!")
    edit_imformation(obj_id,t,zz,itd)
    if(file):
        fp=os.path.join(FILES_DIR,f"{obj_id}.zip")
        with open(fp,"wb") as f:
            f.write(await file.read())
    return {"message":"Success"}

@api.delete("/objects")
async def remove_obj(obj_id:int,_:str=Depends(check_permission(0))):
    obj=find_object(obj_id)
    if(obj):
        remove_object(obj_id)
        fp=os.path.join(FILES_DIR,f"{obj_id}.zip")
        if(os.path.exists(fp)):
            try:
                os.remove(fp)
            except Exception as x:
                print(f"\033[33m[Warning]:Failed to delete file {fp}: {x}\033[0m")
        return {"message":"Success"}
    else:
        return {"message":"Not Found!"}

@api.get("/objects/{obj_id}/download")
async def dl_obj(obj_id:int,_:str=Depends(check_permission(1)),):
    obj=find_object(obj_id)
    if(not obj):
        raise HTTPException(404,"Not Found!")
    fp=os.path.join(FILES_DIR,f"{obj_id}.zip")
    if(not os.path.exists(fp)):
        raise HTTPException(404,"Not Found!")
    download_object(obj_id)
    return FileResponse(path=fp,filename=f"{obj['title']}.zip",media_type="application/zip")

@api.get("/objects")
async def list_obj(kw:str=Query(None,description="Keywords: Title/Author/Introduction"),_:str=Depends(check_permission(1)),):
    if(kw):
        return search_object(kw)
    return list_object()

@api.get("/objects/{obj_id}")
async def fd_obj(obj_id:int,_:str=Depends(check_permission(1)),):
    obj=find_object(obj_id)
    if(not obj):
        raise HTTPException(404,"Not Found!")
    return obj
