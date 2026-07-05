from fastapi import APIRouter
from services.loginservice import login_service
from models.login_model import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login")
def login_api(request: LoginRequest) -> LoginResponse:
    try:
        return login_service.login(request.email, request.password)
    except Exception as ex:
        return LoginResponse(status_code=500, message=str(ex))
