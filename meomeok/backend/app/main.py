from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.recommend import router as recommend_router
from app.api.routes.conditions import router as conditions_router
from app.core.config import KAKAO_JS_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend_router)
app.include_router(conditions_router)

# frontend 폴더를 /static 으로 서빙
app.mount(
    "/static",
    StaticFiles(directory="app/frontend"),
    name="static"
)

templates = Jinja2Templates(directory="app/frontend/templates")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "kakao_js_key": KAKAO_JS_KEY}
    )
