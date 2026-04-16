from fastapi import FastAPI

# 'app' is the instance of the FastAPI class, also called the application instance or FastAPI application
app = FastAPI()

# a decorator, also called a path operation decorator. Runs once at startup to register the route
@app.get("/")
async def root():
    # the path operation function (the function that actually runs per request)
    return {"message": "Hello World"}

"""
The naming convention from the docs:
-Path = the URL (/, /items/{id})
-Operation = the HTTP method (GET, POST, PUT, DELETE)
-Path operation = path + operation combined (GET /)
-Path operation function = the function handling that path operation
-Path operation decorator = the @app.get(...) that registers it
"""