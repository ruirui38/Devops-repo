import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from database import get_session

# テスト用のDBを使う
@pytest.fixture
def client():
    engine = create_engine(
        "mysql+pymysql://root:ikimono0308@localhost/tododb_test"
    )
    # テーブル作成
    SQLModel.metadata.create_all(engine)  

    def get_test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    client = TestClient(app)
    yield client
    # テスト後にテーブル削除
    SQLModel.metadata.drop_all(engine)  
    app.dependency_overrides.clear()

# ===== 正常系 =====

def test_create_todo(client):
    response = client.post("/todos", json={
        "title": "テストタスク",
        "todo": "テスト内容",
        "status": "InProgress"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "テストタスク"
    assert response.json()["todo"] == "テスト内容"
    assert response.json()["status"] == "InProgress"

def test_get_todos(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_todo(client):
    # まず作成
    create = client.post("/todos", json={
        "title": "テストタスク",
        "todo": "テスト内容",
        "status": "InProgress"
    })
    todo_id = create.json()["id"]

    # 取得
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

def test_update_todo(client):
    # まず作成
    create = client.post("/todos", json={
        "title": "テストタスク",
        "todo": "テスト内容",
        "status": "InProgress"
    })
    todo_id = create.json()["id"]

    # 更新
    response = client.put(f"/todos/{todo_id}", json={
        "title": "更新タスク",
        "todo": "更新内容",
        "status": "Complete"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "更新タスク"
    assert response.json()["todo"] == "更新内容"
    assert response.json()["status"] == "Complete"

def test_delete_todo(client):
    # まず作成
    create = client.post("/todos", json={
        "title": "テストタスク",
        "todo": "テスト内容",
        "status": "InProgress"
    })
    todo_id = create.json()["id"]

    # 削除
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200


# ===== 異常系 =====

def test_create_todo_empty_title(client):
    response = client.post("/todos", json={
        "title": "",
        "todo": "テスト内容",
        "status": "InProgress"
    })
    assert response.status_code == 422

def test_create_todo_invalid_status(client):
    response = client.post("/todos", json={
        "title": "テストタスク",
        "todo": "テスト内容",
        "status": "無効なステータス"
    })
    assert response.status_code == 422

def test_get_todo_not_found(client):
    response = client.get("/todos/9999")
    assert response.status_code == 404

def test_update_todo_not_found(client):
    response = client.put("/todos/9999", json={
        "title": "更新タスク",
        "todo": "更新内容",
        "status": "Complete"
    })
    assert response.status_code == 404

def test_delete_todo_not_found(client):
    response = client.delete("/todos/9999")
    assert response.status_code == 404