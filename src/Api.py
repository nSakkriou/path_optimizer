from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse, RedirectResponse
from Model import Address, Session, getPointWithLabel
import uuid

app = FastAPI()

# -- UTILS --

SESSION = {}

ERRORS = {
    "session_not_exists" : {"errors" : "session doesn't exist"},
    "address_not_reconize" : {"errors" : "address doesn't exist or not reconize"},
    "address_not_exists" : {"errors" : "address doesn't exist"},
    "not_enough_address" : {"errors" : "not enough address in this session"}
}

def sessionExist(token):
    try:
        session = SESSION[token]
        return True, session
    except:
        return False, None

@app.get("/", status_code=200)
def home(response: Response):
    return {
        "info" : "for more information on this api, check url <url_api>/docs.",
        "usage" : "to use it, you have to, create a session, add some address into this session and when it's done, you can generate your graphic. <1> createSession <2> addAddress <3> genGraph."
    }

# -- SESSION --

@app.post("/session", status_code=200)
def createSession(response: Response):
    token = str(uuid.uuid4())
    SESSION[token] = Session(token)

    return {"session_token" : token}

@app.get("/session", status_code=200)
def getSession(token, response: Response):    
    if(sessionExist(token)[0]):
        return SESSION[token].to_json()
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["session_not_exists"]

@app.delete("/session", status_code=200)
def deleteSession(token, response: Response):
    try:
        del SESSION[token]
        return {"nb_session_deleted" : 1}
    except:
        return {"nb_session_deleted" : 0}

# -- ADDRESS --

@app.post("/address", status_code=200)
def addAddress(label, token, response: Response):
    flag, session = sessionExist(token)

    if flag:
        point = getPointWithLabel(label)
        if point != None:
            session.addPoint(point)
            return {"info" : "point correctly added", "point_id" : point.id}

        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["address_not_reconize"]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["session_not_exists"]

@app.delete("/address", status_code=200)
def deleteAddress(point_id, token, response: Response):
    flag, session = sessionExist(token)

    if flag:
        if point := session.getAddressWithId(point_id) != None:
            session.points.remove(point)

            return {"info" : "point correctly remove", "point_id" : point_id}

        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["address_not_exists"]
        
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["session_not_exists"]

@app.get("/address", status_code=200)
def getAddress(point_id, token, response: Response):
    flag, session = sessionExist(token)

    if flag:
        if point := session.getAddressWithId(point_id) != None:
            return point.to_json()

        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["address_not_exists"]
        
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["session_not_exists"]

# -- METHODS --

@app.get("/build", status_code=200)
def build(token, response: Response):
    flag, session = sessionExist(token)

    if flag:
        if session.build():
            return {"info" : "graph correctly generated", "image" : FileResponse(token + ".png")}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return ERRORS["not_enough_address"]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ERRORS["session_not_exists"]


import json, uvicorn, os

with open("conf.json", "r") as f:
    conf = json.loads(f.read())

if __name__ == "__main__":
    uvicorn.run(conf["file_name"]+":app",host=conf["host"], port=conf["port"], reload=conf["reload"], workers=conf["workers"])
