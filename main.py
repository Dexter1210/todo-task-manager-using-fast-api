from fastapi import FastAPI
from database import engine, Base
from routers import users, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager")

@app.get("/")
def read_root():
    return "Welcome to Task Manager"

app.include_router(users.router)
app.include_router(tasks.router)
