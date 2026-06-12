from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def _extract_messages(errors: list) -> str:
    """从 Pydantic 错误列表中提取去重的业务提示信息"""
    messages = []
    seen = set()
    for err in errors:
        msg = err.get("msg", "").replace("Value error, ", "")
        if msg not in seen:
            messages.append(msg)
            seen.add(msg)
    return "; ".join(messages) if messages else "请求参数校验失败"


def register_exception_handlers(app: FastAPI) -> None:
    """注册自定义异常处理器，隐藏 Pydantic 底层错误详情，只返回业务错误信息"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        detail = _extract_messages(exc.errors())
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        detail = _extract_messages(exc.errors())
        return JSONResponse(status_code=422, content={"detail": detail})
