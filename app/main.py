from fastapi import FastAPI


from .database import engine
from . import models
from .routes import user, auth, admin, restaurant

# Create database tables. Only use this for testing purposes
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Import routes
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(restaurant.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}