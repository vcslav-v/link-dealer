from fastapi import FastAPI
from link_dealer.api.routes import routes

app = FastAPI(debug=True)

app.include_router(routes)
