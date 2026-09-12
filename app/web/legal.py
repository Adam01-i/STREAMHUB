from fastapi import APIRouter, Request

from app.core.templates import templates

router = APIRouter(tags=["legal"])


@router.get("/privacy")
async def privacy_page(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request})


@router.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
