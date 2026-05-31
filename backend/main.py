from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.routers import user as user_router
from backend.routers import attraction as attraction_router
from backend.routers import behavior as behavior_router
from backend.routers import recommend as recommend_router
from backend.routers import model as model_router
from backend.services.recommend_service import recommend_service
from backend.database import SessionLocal

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        recommend_service.load_models(db)
    except Exception as e:
        print(f"Warning: Failed to load models: {e}")
    finally:
        db.close()
    yield


app = FastAPI(title="智能旅游推荐系统", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(attraction_router.router)
app.include_router(behavior_router.router)
app.include_router(recommend_router.router)
app.include_router(model_router.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
