from fastapi import Request,Depends,HTTPException,Header
from object import _cuser
import time

LOCK_TIME=30*60

async def get_user(auth:str=Header(None))->str:
    if(not auth):
        raise HTTPException(401,"\033[31m[ERROR]:Unauthorized\033[0m")
    tk=auth.replace("Bearer ","")
    x=_cuser()
    r=x.execute("SELECT name,create_time FROM tokens WHERE token=?",(tk,)).fetchone()
    
    if(r):
        if(int(time.time())-r['create_time']>LOCK_TIME):
            x.execute("DELETE FROM tokens WHERE token=?",(tk,))
            x.commit()
            x.close()
            raise HTTPException(401,"\033[31m[ERROR]:Unauthorized\033[0m")
        x.close()
        return r["name"]
    x.close()
    raise HTTPException(422,"\033[31m[ERROR]:Unprocessable Entity\033[0m")

async def cklogin(users:str=Depends(get_user))->str:
    return users

def check_permission(request:int=0):
    def _ck(users:str=Depends(get_user))->str:
        x=_cuser()
        r=x.execute("SELECT power FROM users WHERE name=?",(users,)).fetchone()
        x.close()
        if(not r):
            raise HTTPException(401,"\033[31m[ERROR]:Unauthorized\033[0m")
        if(r['power']<=request):
            return users
        else:
            raise HTTPException(403,"\033[31m[ERROR]:Forbidden\033[0m")
    return _ck
    """
    权限检查函数，作为 FastAPI 依赖注入使用
    每个 api 路由都会先经过这里

    后期示例：
        token = request.headers.get("Authorization")
        if not token or not verify_token(token):
            raise HTTPException(401, "未登录")
        # 也可以把用户信息存到 request.state 上供后续使用
        request.state.user = parse_token(token)
    """
    #pass  # 目前直接放行