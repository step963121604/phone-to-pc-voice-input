"""FastAPI HTTP + WebSocket server."""

from __future__ import annotations

import io
import json
import secrets
from functools import lru_cache
from pathlib import Path

import qrcode
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw

from . import injector

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@lru_cache(maxsize=1)
def _app_icon_png() -> bytes:
    img = Image.new("RGB", (192, 192), color=(37, 99, 235))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((24, 24, 168, 168), radius=28, fill=(255, 255, 255))
    draw.text((72, 58), "PC", fill=(37, 99, 235))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_app(token: str, lan_host: str, port: int) -> FastAPI:
    phone_url = f"http://{lan_host}:{port}/?token={token}"

    app = FastAPI(title="PhoneToPC Voice Input")
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/")
    async def index():
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/app.js")
    async def app_js():
        return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")

    @app.get("/sw.js")
    async def service_worker():
        return FileResponse(
            WEB_DIR / "sw.js",
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/"},
        )

    @app.get("/qr")
    async def qr_page():
        return FileResponse(WEB_DIR / "qr.html")

    @app.get("/qr.png")
    async def qr_png():
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(phone_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")

    @app.get("/manifest.json")
    async def manifest():
        return JSONResponse(
            {
                "name": "发送到电脑",
                "short_name": "发PC",
                "description": "手机听写，一键发到电脑输入框",
                "start_url": f"/?token={token}",
                "scope": "/",
                "display": "standalone",
                "orientation": "portrait",
                "background_color": "#0f172a",
                "theme_color": "#3b82f6",
                "icons": [
                    {
                        "src": "/icon.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "any maskable",
                    }
                ],
            }
        )

    @app.get("/icon.png")
    async def icon_png():
        return Response(content=_app_icon_png(), media_type="image/png")

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        query_token = ws.query_params.get("token", "")
        if not secrets.compare_digest(query_token, token):
            await ws.close(code=1008, reason="invalid token")
            return

        await ws.accept()

        try:
            while True:
                raw = await ws.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    await ws.send_json(
                        {"t": "err", "code": "bad_json", "msg": "无效 JSON"}
                    )
                    continue

                kind = msg.get("t")
                if kind == "clr":
                    continue

                if kind != "send":
                    await ws.send_json(
                        {"t": "err", "code": "unknown", "msg": f"未知类型: {kind}"}
                    )
                    continue

                text = msg.get("text", "")
                if not isinstance(text, str):
                    await ws.send_json(
                        {"t": "err", "code": "bad_text", "msg": "text 必须是字符串"}
                    )
                    continue

                if not text:
                    await ws.send_json({"t": "ok", "ms": 0})
                    continue

                try:
                    ms = injector.inject_text_timed(text)
                    await ws.send_json({"t": "ok", "ms": ms})
                except OSError as e:
                    await ws.send_json(
                        {
                            "t": "err",
                            "code": "inject_failed",
                            "msg": str(e) or "注入失败",
                        }
                    )

        except WebSocketDisconnect:
            pass

    return app
