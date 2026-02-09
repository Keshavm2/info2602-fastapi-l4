from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr   #insert at top of the file

class User(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str
    role:str = ""

class Admin(User, table=True):
    role:str = "admin"

class RegularUser(User, table=True):
    role:str = "regular_user"
    
    todos: list['Todo'] = Relationship(back_populates="user")

class TodoCategory(SQLModel, table=True):
    category_id: int = Field(foreign_key="category.id", primary_key=True)
    todo_id: int = Field(foreign_key="todo.id", primary_key=True)

class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="regularuser.id")
    text:str
    done: bool = False

    user: RegularUser = Relationship(back_populates="todos")
    def toggle(self):
        self.done = not self.done
    