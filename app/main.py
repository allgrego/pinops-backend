from typing import Union
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import clients, international_agents, carriers, ops_files, geodata, users, auth, partners
from app.database import create_db_and_tables
from contextlib import asynccontextmanager

import logging

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try: 
        log.debug('Initializing...')
        create_db_and_tables()
        log.debug('Initialization finished!')
        pass
        #await defaults.load_default_parameters()
        # example of a service that can perform custom actions. 
        # TODO service that checks DB consistency at startup? 
    
    except Exception as e:
        log.exception(f"Failed to initialized DB {e}")
    
    yield 

    # Shutdown logic
    print("Shutting down...")
    # Clean up resources here (e.g., close database connections, stop tasks)
    
    app.state.some_resource = None


app = FastAPI(title='PinOps - API', 
              lifespan=lifespan,
              redoc_url=None, version="1.0.0", 
              swagger_ui_parameters={"docExpansion": "none"})

# CORS config
CORS_ALLOWED_ORIGIN = os.environ.get("ALLOWED_CORS_ORIGINS", "") # Must be comma-separated. e.g. "http://localhost:3000,https://localhost:3000"
CORS_origins= CORS_ALLOWED_ORIGIN.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.middleware("http")
# async def middleware(request: Request, call_next):
#     log.info(f'[{request.method}] {request.url}')
#     response = await call_next(request)
#     return response

app.include_router(geodata.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(partners.router)
app.include_router(international_agents.router)
app.include_router(carriers.router)
app.include_router(ops_files.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}