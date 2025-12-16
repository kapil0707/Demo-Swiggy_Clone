from fastapi import FastAPI




app = FastAPI()

# Import routes



@app.get("/")
def read_root():
    return {"Hello": "World"}