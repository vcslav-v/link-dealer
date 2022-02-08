from fastapi import APIRouter
from link_dealer.api.local_routes import api

routes = APIRouter()

routes.include_router(api.router, prefix='/api')
