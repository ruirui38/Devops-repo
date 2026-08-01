import os
import pytest
from datetime import datetime
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app
from database import get_session

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = "127.0.0.1"
DB_PORT = os.getenv("DB_PORT", "3307")
DB_TEST_NAME = os.getenv("DB_TEST_NAME", "tododb_test")

TEST_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TEST_NAME}"
)


# テスト用のDBを使う（DockerのMySQLに接続）
@pytest.fixture
def client():
    engine = create_engine(TEST_DATABASE_URL)
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
    response = client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "テストタスク"
    assert response.json()["todo"] == "テスト内容"
    assert response.json()["status"] == "InProgress"
    assert "created_at" in response.json()
    assert response.json()["created_at"] is not None


def test_get_todos(client):
    # タスクを作成してから一覧取得
    client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    response = client.get("/todos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if len(response.json()) > 0:
        assert "created_at" in response.json()[0]
        assert response.json()[0]["created_at"] is not None


def test_get_todo(client):
    # まず作成
    create = client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    todo_id = create.json()["id"]

    # 取得
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id
    assert "created_at" in response.json()
    assert response.json()["created_at"] is not None


def test_update_todo(client):
    # まず作成
    create = client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    todo_id = create.json()["id"]

    # 更新
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "更新タスク", "todo": "更新内容", "status": "Complete"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "更新タスク"
    assert response.json()["todo"] == "更新内容"
    assert response.json()["status"] == "Complete"


def test_delete_todo(client):
    # まず作成
    create = client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    todo_id = create.json()["id"]

    # 削除
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204


def test_created_at_format(client):
    # タスク作成
    response = client.post(
        "/todos",
        json={"title": "テストタスク", "todo": "テスト内容", "status": "InProgress"},
    )
    assert response.status_code == 201

    # created_atが存在し、ISO形式でパース可能であることを確認
    created_at_str = response.json()["created_at"]
    assert created_at_str is not None

    # ISO形式の日時文字列をパース
    created_at = datetime.fromisoformat(created_at_str)

    # YYYY/MM/DD形式にフォーマット可能であることを確認
    formatted_date = created_at.strftime("%Y/%m/%d")
    assert len(formatted_date) == 10  # "YYYY/MM/DD"は10文字
    assert formatted_date.count("/") == 2  # スラッシュが2つ


# ===== 異常系 =====


def test_create_todo_empty_title(client):
    response = client.post(
        "/todos", json={"title": "", "todo": "テスト内容", "status": "InProgress"}
    )
    assert response.status_code == 422


def test_create_todo_invalid_status(client):
    response = client.post(
        "/todos",
        json={
            "title": "テストタスク",
            "todo": "テスト内容",
            "status": "無効なステータス",
        },
    )
    assert response.status_code == 422


def test_get_todo_not_found(client):
    response = client.get("/todos/9999")
    assert response.status_code == 404


def test_update_todo_not_found(client):
    response = client.put(
        "/todos/9999",
        json={"title": "更新タスク", "todo": "更新内容", "status": "Complete"},
    )
    assert response.status_code == 404


def test_delete_todo_not_found(client):
    response = client.delete("/todos/9999")
    assert response.status_code == 404
