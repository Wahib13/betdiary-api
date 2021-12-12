from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dependencies.data import connect_db, close_db
from routers import users, bet_info

app = FastAPI()

app.include_router(users.router)
app.include_router(bet_info.router)

origins = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'https://betdiary-ui.vercel.app',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", close_db)
