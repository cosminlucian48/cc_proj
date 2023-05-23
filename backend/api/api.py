from fastapi import FastAPI

from api.routes.query import query_route
from api.routes.security import security_route

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_route, prefix='/api')
app.include_router(security_route, prefix='/api')

@app.get("/")
async def read_root():
    return {"Hello": "World!"}
