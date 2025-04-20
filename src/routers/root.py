from fastapi import APIRouter

from .tron import router as tron_router

router = APIRouter(prefix="/api")
router.include_router(tron_router)
