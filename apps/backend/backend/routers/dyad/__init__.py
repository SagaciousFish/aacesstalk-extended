from fastapi import APIRouter
from . import account, session
from .common import depends_auth_dyad

router = APIRouter()

router.include_router(account.router, prefix="/account")
router.include_router(session.router, prefix="/session", dependencies=[depends_auth_dyad()])
