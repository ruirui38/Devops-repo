from sqlalchemy import text
from sqlmodel import Session, select

from database import create_db_and_tables, engine
from models import Todo

# テーブルの作成（すでに存在する場合はスキップ）
with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES LIKE 'todos'")).fetchone()

if result is None:
    create_db_and_tables()
    print("テーブル todos を作成しました")
else:
    print("テーブル todos はすでに存在するためスキップしました")

# テストデータの挿入（すでにデータが存在する場合はスキップ）
with Session(engine) as session:
    existing = session.exec(select(Todo)).all()
    if len(existing) == 0:
        todo1 = Todo(
            title="最初タスク", 
            todo="dbにタスクを登録", 
            status="Complete"
        )
        todo2 = Todo(
            title="2番目のタスク",
            todo="2番目のタスクを登録",
            status="InProgress"
        )
        session.add(todo1)
        session.add(todo2)
        session.commit()
        print("テストデータを2件挿入しました")
    else:
        print(f"テストデータはすでに{len(existing)}件存在するためスキップしました")