from pydantic import BaseModel

class User(BaseModel):
    id: int|None = None
    fullname: str|None = None
    age: int|None = None
    number: str|None = None

class AddTask(BaseModel):
    id: int|None = None
    user_id: int|None = None
    task: str|None = None
