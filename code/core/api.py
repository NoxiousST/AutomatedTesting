from ninja import NinjaAPI, Schema, Router

api = NinjaAPI()
router = Router()

class HelloResponse(Schema):
    msg: str

@router.get("/hello", response=HelloResponse)
def hello(request):
    return {"msg": "Hello World"}

api.add_router("", router)
