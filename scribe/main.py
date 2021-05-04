from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import describe, ascribe, prescribe
from .database import get_db
from pydantic import BaseModel

scribe = FastAPI(response_mode=BaseModel,  blamjnefjn=BaseModel)

scribe.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scribe.include_router(
  describe.router,
  prefix="/describe",
  tags=["describe"]
)

scribe.include_router(
  ascribe.router,
  prefix="/ascribe",
  tags=["ascribe"]
)

scribe.include_router(
  prescribe.router,
  prefix="/prescribe",
  tags=["prescribe"]
)
# app.include_router(items.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


@scribe.get("/")
def read_root():
    print(Elo)
    return {"Hello": "World"}


@scribe.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@scribe.on_event("startup")
async def startup_event():
    database_instance = get_db()
    scribe.state.conn = database_instance
    scribe.state.db = database_instance.scribe
    print(scribe.state.db)
    print("Server Startup")

@scribe.on_event("shutdown")
async def shutdown_event():
    if not scribe.state.conn:
        await scribe.state.conn.close()
    print("Server Shutdown")
