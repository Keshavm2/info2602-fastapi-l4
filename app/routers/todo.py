from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import status

todo_router = APIRouter(tags=["Todo Management"])


@todo_router.get('/todos', response_model=list[TodoResponse])
def get_todos(db:SessionDep, user:AuthDep):
    return user.todos

@todo_router.get('/todo/{id}', response_model=TodoResponse)
def get_todo_by_id(id:int, db:SessionDep, user:AuthDep):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return todo

@todo_router.post('/todos', response_model=TodoResponse)
def create_todo(db:SessionDep, user:AuthDep, todo_data:TodoCreate):
    todo = Todo(text=todo_data.text, user_id=user.id)
    try:
        db.add(todo)
        db.commit()
        db.refresh(todo)
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while creating an item",
        )

@todo_router.put('/todo/{id}', response_model=TodoResponse)
def update_todo(id:int, db:SessionDep, user:AuthDep, todo_data:TodoUpdate):
    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    if todo_data.text:
        todo.text = todo_data.text
    if todo_data.done:
        todo.done = todo_data.done
    try:
        db.add(todo)
        db.commit()
        return todo
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while updating an item",
        )

@todo_router.delete('/todo/{id}', status_code=status.HTTP_200_OK)
def update_todo(id:int, db:SessionDep, user:AuthDep):

    todo = db.exec(select(Todo).where(Todo.id==id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
@todo_router.post('/category', response_model=Category)
def create_category(db:SessionDep, user:AuthDep, category_data:Category):
    new_category = Category(text=category_data.text, user_id=user.id)

    try:
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Did not create category",
        )
    
@todo_router.post('/todo/{todo_id}/category/{cat_id}')
def add_category_to_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):

    todo = db.exec(select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    
    category = db.exec(select(Category).where(Category.id==cat_id, Category.user_id==user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Category not found",
        )
    
    todo.categories.append(category)
    db.add(todo)
    db.commit()

@todo_router.delete('/todo/{todo_id}/category/{cat_id}')
def reomove_category_from_todo(todo_id:int, cat_id:int, db:SessionDep, user:AuthDep):

    todo = db.exec(select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)).one_or_none()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    try:
        db.delete(todo)
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="An error occurred while deleting an item",
        )
    
    category = db.exec(select(Category).where(Category.id==cat_id, Category.user_id==user.id)).one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Category not found",
        )   
    
    if category not in todo.categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not associated with todo",
        )
    
    todo.categories.remove(category)

    db.add(todo)
    db.commit()

@todo_router.get('/category/{cat_id}/todos', response_model=list[TodoResponse])
def get_todos_by_category(cat_id: int, db: SessionDep, user: AuthDep):      

        category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
        ).one_or_none()

        if not category:
            raise HTTPException(status_code=401, detail="Unauthorized")

        return category.todos   


