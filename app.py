from fastapi import FastAPI, Depends

from flash.config.config import initiate_database

app = FastAPI()


@app.on_event("startup")
async def start_database():
    # await initiate_database()
    pass


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


from flash.ping.controller import router as ping_router
from flash.service.controller import router as service_router

app.include_router(ping_router, tags=["Ping"])
app.include_router(service_router, tags=["Service"])
