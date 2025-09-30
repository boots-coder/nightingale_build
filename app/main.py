from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Nightingale AI Patient Experience",
    description="A prototype for the 48-hour build challenge.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    """
    根路径，用于简单的健康检查。
    """
    return {"message": "Welcome to the Nightingale AI API!"}