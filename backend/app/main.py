import math

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import seed
from app.routers import api
app = FastAPI(title="Paintcan", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _json_safe(o):
    # Non-finite floats (NaN/Infinity from a lenient JSON parser) would crash
    # the default error response; replace them so a bad request stays a clean 422.
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, BaseException):
        return str(o)
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_safe(v) for v in o]
    return o if isinstance(o, (str, int, bool)) or o is None else str(o)


@app.exception_handler(RequestValidationError)
async def _validation_error(_request, exc):
    return JSONResponse(status_code=422, content={"detail": _json_safe(exc.errors())})


@app.on_event("startup")
def _startup(): seed.init_db()
app.include_router(api)
@app.get("/api/health")
def health(): return {"ok": True, "project": "paintcan"}
