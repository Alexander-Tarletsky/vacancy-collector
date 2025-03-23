from uuid import UUID

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

template_router = APIRouter(default_response_class=HTMLResponse)
templates = Jinja2Templates(directory="app/templates")


# @template_router.get("/", include_in_schema=False)
# async def dashboard(request: Request, db_session: Annotated[AsyncSession, Depends(get_db)]):
#     # Example data fetching - implement your actual queries here
#     channels_count = await ChannelService().get_count(db)
#     active_channels_count = await ChannelService().get_active_count(db)
#     recent_vacancies = await VacancyService().get_recent_vacancies(db)
#
#     return templates.TemplateResponse("dashboard.html", {
#         "request": request,
#         "channels_count": channels_count,
#         "active_channels_count": active_channels_count,
#         "recent_vacancies": recent_vacancies
#     })


@template_router.get("/login", include_in_schema=False)
async def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("auth/login.html", {"request": request})


@template_router.get("/register", include_in_schema=False)
async def register_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("auth/register.html", {"request": request})


@template_router.get("/channels")
async def channels_list(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("main/channels/list.html", {"request": request})


@template_router.get("/channels/{id}")
async def channel_detail(id: UUID, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "main/channels/detail.html",
        {
            "request": request,
            "channel_id": id,
        },
    )


@template_router.get("/vacancies")
async def vacancies_list(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("main/vacancies/list.html", {"request": request})


@template_router.get("/vacancies/{id}")
async def vacancy_detail(id: UUID, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "main/vacancies/detail.html",
        {
            "request": request,
            "vacancy_id": id,
        },
    )
