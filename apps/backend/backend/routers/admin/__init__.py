from fastapi import APIRouter
from . import auth, dyads

router = APIRouter()

router.include_router(auth.router, prefix='/auth')
router.include_router(dyads.router, prefix="/dyads")