import hashlib
import hmac
import json
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="GitHub Webhook")

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


@app.post("/github/webhook")
async def github_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256", "")

    if WEBHOOK_SECRET:
        computed = "sha256=" + hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, computed):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = json.loads(body)
    event = request.headers.get("x-github-event")

    if event == "issues":
        issue = payload.get("issue", {})
        return {
            "status": "received",
            "event": event,
            "issue": {
                "title": issue.get("title"),
                "state": issue.get("state"),
            },
        }

    if event == "pull_request":
        pr = payload.get("pull_request", {})
        return {
            "status": "received",
            "event": event,
            "pr": {
                "title": pr.get("title"),
                "state": pr.get("state"),
            },
        }

    return {"status": "ignored", "event": event}
