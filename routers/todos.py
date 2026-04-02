from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from database import get_session
from models import Todo, TodoCreate

router = APIRouter()

# 各種エンドポイント作成

#タスクを作成
@router.post("/todos", status_code=201)
def create_todo(todo: TodoCreate, session: Session = Depends(get_session)):
    db_todo = Todo(title=todo.title, todo=todo.todo, status=todo.status)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

#タスクの一覧を表示
@router.get("/todos")
def get_todos(session: Session = Depends(get_session)):
    todos = session.exec(select(Todo).order_by(Todo.id.desc())).all()
    return todos

#タスクの詳細を表示
@router.get("/todos/{todo_id}")
def get_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    return todo

#タスクを更新
@router.put("/todos/{todo_id}")
def update_todo(
    todo_id: int, todo_data: TodoCreate, session: Session = Depends(get_session)
):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    todo.title = todo_data.title
    todo.todo = todo_data.todo
    todo.status = todo_data.status
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo

@router.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")
    session.delete(todo)
    session.commit()
    return Response(status_code=204)