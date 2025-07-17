import json
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

app = FastAPI()


class EventModel(BaseModel):
    name: str
    description: str
    start_date: str
    end_date: str


events_store: List[EventModel] = []


def serialized_stored_events():
    events_converted = []
    for event in events_store:
        events_converted.append(event.model_dump())
    return events_converted


@app.get("/")
def root(request: Request):
    accept_headers = request.headers.get("Accept")
    authorization = request.headers.get("x-api-key")
    if accept_headers != "text/html" and accept_headers != "text/plain":
        return JSONResponse(content={"message": f"Media Type not supported : {accept_headers}"}, status_code=400)
    if authorization != "12345678":
        return JSONResponse(content={"message": f"Provided key unknown : {authorization}"}, status_code=403)
    with open("welcome.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return Response(content=html_content, status_code=200, media_type="text/html")


@app.get("/events")
def list_events():
    return {"events": serialized_stored_events()}


@app.post("/events")
def new_events(event_payload: List[EventModel]):
    events_store.extend(event_payload)
    return {"events": serialized_stored_events()}


@app.put("/events")
def update_or_create_events(event_payload: List[EventModel]):
    global events_store  # `global` to indicate here that we want to use global variable not creating local events_store var

    for new_event in event_payload:
        # Used to check if event already exists later
        found = False
        for i, existing_event in enumerate(events_store):
            if new_event.name == existing_event.name:
                events_store[i] = new_event
                found = True
                break
        if not found:
            events_store.append(new_event)
    return {"events": serialized_stored_events()}


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    with open("not_found.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return Response(content=html_content, status_code=200, media_type="text/html")
