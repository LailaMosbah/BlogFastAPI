from fastapi import FastAPI , Request , HTTPException , status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as starletteHTTPException

app = FastAPI()
app.mount("/static" , StaticFiles(directory="static") , name="static")

templates = Jinja2Templates(directory="./templates") # name of the directory which has a html files to render

posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]


# Routes
@app.get("/" , name="home" )
@app.get("/posts" , include_in_schema=False , name="posts")
def home(request:Request):
    return templates.TemplateResponse(request,"home.html" , {"posts":posts , "title":"Blog FastAPI"})


@app.get("/posts/{post_id}")
def post_page(request:Request, post_id : int):
    for post in posts :
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request,
                "post.html" ,
                {"post":post , "title":title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Post Not Found")



# Endpoints
@app.get("/api/posts")
def get_posts():
    return posts


@app.get("/api/posts/{post_id}")  # post_id is a Path Parameters 
def get_post(post_id : int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Post not found")



# Exception Erros
@app.exception_handler(starletteHTTPException)
def general_http_exception_handler(request : Request , exception : starletteHTTPException):
    message =(
        exception.detail
        if exception.detail
        else "An error occurred , Please check your request and try again"
    )
    print("message")
    print( message)
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            content={"detail" : message},
            status_code=exception.status_code,
        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "title":exception.status_code,
            "status_code" : exception.status_code,
            "message":message,
        },
        status_code=exception.status_code
    )
    

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )