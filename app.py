from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware
from api.routes import api_router
from api.routes import api_router_v2
from config import ConfigClass
import uvicorn


app = FastAPI(
    title="EntityInfo Service",
    description="EntityInfo",
    docs_url="/v1/api-doc",
    version="0.3.0"
)
app.add_middleware(DBSessionMiddleware, db_url=ConfigClass.SQLALCHEMY_DATABASE_URI)
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

app.include_router(api_router, prefix="/v1")
app.include_router(api_router_v2, prefix="/v2")

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5066, log_level="info", reload=True)
