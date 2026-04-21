import os, sys
print("当前工作目录:", os.getcwd())
print("main.py 所在目录:", os.path.dirname(__file__))
print("sys.path 包含:")
for p in sys.path:
    print("  ", p)
print("server 目录下的文件列表:")
print(os.listdir(os.path.dirname(__file__)))
from fastapi import FastAPI,Depends,HTTPException
from sql import _data
from object import _users,_cuser,_tokens
from api import api
from contextlib import asynccontextmanager
from usersmanage import user_api
from adminapi import admin_api
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic,HTTPBasicCredentials

def clear_all_tokens():
    x = _cuser()
    x.execute("DELETE FROM tokens")
    x.commit()
    x.close()

@asynccontextmanager
async def lifespan(app:FastAPI):
    _data()
    _users()
    def _init_admin():
        x=_cuser()
        row = x.execute("SELECT id FROM users WHERE name='admin'").fetchone()
        if not row:
            x.execute("INSERT INTO users (name,password,power) VALUES (?,?,?)",("admin","123456",0))
            x.commit()
        x.close()
    _init_admin()
    _tokens()
    yield

app=FastAPI(lifespan=lifespan)
#app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None)

docuser="abab"
docpw="666666"
security=HTTPBasic()
@app.get("/docs",include_in_schema=False)
async def custom_docs(x:HTTPBasicCredentials=Depends(security)):
    if x.username!=docuser or x.password!=docpw:
        raise HTTPException(401,"Incorrect username or passward")
    return get_swagger_ui_html(openapi_url="/openapi.json",title="API Docs",)
@app.get("/openapi.json",include_in_schema=False)
async def openapi():
    return get_openapi(title=app.title,version=app.version,routes=app.routes)

app.include_router(api)
app.include_router(admin_api)
app.include_router(user_api)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=2333, reload=True)