import json, os
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from db import DB
from manager import Manager

app = FastAPI()

db = DB()
mgr = Manager()

# এখানে সামান্য পরিবর্তন - directory পাথ confirm করুন
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ওপশনাল: cache সমস্যা হলে এই লাইন যোগ করুন
templates.env.cache_size = 0  # development এর জন্য


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


async def send_users():
    users = mgr.users()
    # কপি করে লুপ চালান
    for ws in list(mgr.name_to_ws.values()):
        try:
            await ws.send_text(json.dumps({
                "type": "users",
                "data": users
            }))
        except:
            mgr.disconnect(ws)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            t = data.get("type")

            # REGISTER
            if t == "register":
                ok = db.register(data.get("name"), data.get("password"))
                await websocket.send_text(json.dumps({
                    "type": "register_ok" if ok else "register_fail"
                }))

            # LOGIN
            elif t == "login":
                ok = db.login(data.get("name"), data.get("password"))

                if ok:
                    await mgr.connect(data.get("name"), websocket)
                    await send_users()

                await websocket.send_text(json.dumps({
                    "type": "login_ok" if ok else "login_fail"
                }))

            # DM
            elif t == "dm":
                sender = mgr.get_name(websocket)
                target = mgr.get_ws(data.get("to"))

                if not sender:
                    continue

                time = datetime.now().strftime("%H:%M")

                db.save_msg(sender, data.get("to"), None, data.get("msg"), time)

                if target:
                    await target.send_text(json.dumps({
                        "type": "msg",
                        "from": sender,
                        "msg": data.get("msg"),
                        "time": time
                    }))

            # ROOM
            elif t == "room":
                sender = mgr.get_name(websocket)

                if not sender:
                    continue

                time = datetime.now().strftime("%H:%M")

                db.save_msg(sender, None, data.get("room"), data.get("msg"), time)

                msg = json.dumps({
                    "type": "room",
                    "from": sender,
                    "msg": data.get("msg"),
                    "time": time
                })

                # কপি করে লুপ চালান
                for ws_client in list(mgr.name_to_ws.values()):
                    try:
                        await ws_client.send_text(msg)
                    except:
                        mgr.disconnect(ws_client)

    except WebSocketDisconnect:
        mgr.disconnect(websocket)
        await send_users()
