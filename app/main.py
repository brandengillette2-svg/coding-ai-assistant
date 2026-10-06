from fastapi import FastAPI
from app.github_webhook import app as github_app

app = FastAPI(title="Master Code Wizard API")
app.mount("/github", github_app)
