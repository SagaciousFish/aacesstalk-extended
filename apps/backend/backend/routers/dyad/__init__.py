from fastapi import APIRouter, Depends
from . import account, session
from .common import get_signed_in_dyad

router = APIRouter()

router.include_router(account.router, prefix="/account")
router.include_router(session.router, prefix="/session", dependencies=[Depends(get_signed_in_dyad)])
