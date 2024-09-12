from datetime import datetime

import uvicorn
from db.database import BaseModel, engine
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import users

BaseModel.metadata.create_all(bind=engine)

app = FastAPI()

origins = [

]
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,  
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有標頭
)


app.include_router(users.router)

@app.get("/")

def index(request: Request):

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_host = request.client.host
    message = "You successfully linked to the OMS backend API."

    return {"status":"Success",
            "message": message, 
            "time": current_time, 
            "ip": client_host}


if __name__ == "__main__":

    uvicorn.run("main:app", port=5000, reload=True, host="0.0.0.0")   