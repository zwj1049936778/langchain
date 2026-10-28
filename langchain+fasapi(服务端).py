from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from langchain.chat_models import init_chat_model
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI()

model = init_chat_model(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    max_tokens=1000,
    api_key="sk-639cd77989734fd7a4a62437dbf41467",
    model_provider="openai"
)

async def stream_gen(message):
    async for chunk in model.astream(message):
        yield chunk.content + "\n"

# ---------------------- 状态码处理 ----------------------
# 404 找不到接口
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"code":404, "msg":"404 接口地址不存在"})
    if exc.status_code == 405:
        return JSONResponse(status_code=405, content={"code":405, "msg":"405 请求方式不对，只支持POST"})
    if exc.status_code == 500:
        return JSONResponse(status_code=500, content={"code":500, "msg":"500 服务内部错误"})
    return JSONResponse(status_code=exc.status_code, content={"code":exc.status_code, "msg":exc.detail})

# 400 请求参数错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"code":400, "msg":"400 请求参数格式错误"})

# 502 一般是网关，这里单独写一个测试接口演示，上游异常时返回502
@app.get("/test502")
async def test_502():
    return JSONResponse(status_code=502, content={"code":502, "msg":"502 网关错误，上游服务无响应"})
# --------------------------------------------------------

@app.post("/users")
async def chat(request: Request):
    try:
        info = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"code":400, "msg":"400 json解析失败"})
    name = info["id"]
    psd = info["password"]
    data = info["data"]
    if name.strip() != "zwj" or psd.strip() != "123456":
        return JSONResponse(status_code=400, content={"code":400, "msg":"账号密码错误"})
    logging.info("请求成功 200 OK")
    return StreamingResponse(stream_gen(data), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=9256)
