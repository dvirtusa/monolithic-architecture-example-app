from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse, summary="Home page")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
