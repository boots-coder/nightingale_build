from fastapi import FastAPI

from .db import models
from .db.session import engine
from fastapi.staticfiles import StaticFiles # 新增导入
from fastapi.responses import HTMLResponse # 新增导入
import os # 新增导入
# 这行代码会告诉 SQLAlchemy 根据我们定义的模型，在数据库中创建对应的表。
# 它只会在表不存在时进行创建，所以重复运行是安全的。
models.Base.metadata.create_all(bind=engine)
from .api import endpoints



app = FastAPI(
    title="Nightingale AI Patient Experience",
    description="A prototype for the 48-hour build challenge.",
    version="0.1.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_index():
    # 读取并返回 index.html 文件
    with open(os.path.join("static", "index.html")) as f:
        return HTMLResponse(content=f.read(), status_code=200)


# @app.get("/")
# def read_root():
#     """
#     根路径，用于简单的健康检查。
#     """
#     return {"message": "Welcome to the Nightingale AI API!"}
#
# # 将 endpoints.py 中定义的所有路由都包含进来
app.include_router(endpoints.router, prefix="/api/v1")