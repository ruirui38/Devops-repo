# Todo API

FastAPIとMySQLを使用したTodo管理のCRUD APIです。

---

## APIの概要

- タスクの作成・取得・更新・削除ができるREST APIです
- FastAPI + SQLModel + MySQLで構成されています
- Dockerを使用してローカルで動作します

---

## エンドポイント一覧

### タスク一覧取得

| 項目 | 内容 |
|------|------|
| メソッド | GET |
| パス | /todos |

**レスポンス例**
```json
[
  {
    "id": 1,
    "title": "最初タスク",
    "todo": "dbにタスクを登録",
    "status": "Complete",
    "created_at": "2026-03-28T07:49:31",
    "updated_at": "2026-03-28T07:49:31"
  }
]
```

---

### タスク詳細取得

| 項目 | 内容 |
|------|------|
| メソッド | GET |
| パス | /todos/{id} |

**レスポンス例**
```json
{
  "id": 1,
  "title": "最初タスク",
  "todo": "dbにタスクを登録",
  "status": "Complete",
  "created_at": "2026-03-28T07:49:31",
  "updated_at": "2026-03-28T07:49:31"
}
```

**異常系レスポンス例（404）**
```json
{
  "detail": "タスクが見つかりません"
}
```

---

### タスク作成

| 項目 | 内容 |
|------|------|
| メソッド | POST |
| パス | /todos |

**リクエスト例**
```json
{
  "title": "新しいタスク",
  "todo": "タスクの内容",
  "status": "InProgress"
}
```

**バリデーションルール**
- `title`: 必須・最大100文字
- `todo`: 必須・最大255文字
- `status`: `InProgress` / `Complete` / `Cancel` のいずれか

**レスポンス例（201）**
```json
{
  "id": 3,
  "title": "新しいタスク",
  "todo": "タスクの内容",
  "status": "InProgress",
  "created_at": "2026-03-28T07:49:31",
  "updated_at": "2026-03-28T07:49:31"
}
```

**異常系レスポンス例（422）**
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "title"],
      "msg": "入力は必須です"
    }
  ]
}
```

---

### タスク更新

| 項目 | 内容 |
|------|------|
| メソッド | PUT |
| パス | /todos/{id} |

**リクエスト例**
```json
{
  "title": "更新タスク",
  "todo": "更新内容",
  "status": "Complete"
}
```

**レスポンス例（200）**
```json
{
  "id": 1,
  "title": "更新タスク",
  "todo": "更新内容",
  "status": "Complete",
  "created_at": "2026-03-28T07:49:31",
  "updated_at": "2026-03-28T08:00:00"
}
```

**異常系レスポンス例（404）**
```json
{
  "detail": "タスクが見つかりません"
}
```

---

### タスク削除

| 項目 | 内容 |
|------|------|
| メソッド | DELETE |
| パス | /todos/{id} |

**レスポンス（204 No Content）**

ボディなし

**異常系レスポンス例（404）**
```json
{
  "detail": "タスクが見つかりません"
}
```

---

## ローカルでの起動手順

### 前提条件
- Docker Desktop がインストールされていること

### 手順

**① リポジトリをクローン**
```bash
git clone <リポジトリURL>
cd todo-api
```

**② .env ファイルを作成**
```properties
DB_HOST=db
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=tododb
DB_PORT=3307
DB_TEST_NAME=tododb_test
```

**③ Dockerを起動**
```bash
docker-compose up --build
```

**④ 動作確認**

ブラウザで以下にアクセス：
```
http://localhost:8000/docs
```

Swagger UIが表示されれば起動成功です。

### 停止方法
```bash
docker-compose down
```

### DBをリセットして再起動する場合
```bash
docker-compose down -v
docker-compose up --build
```

---

## テストの実行方法

### 前提条件
- Pythonがインストールされていること
- Dockerが起動していること（`docker-compose up` で起動済みであること）

### テスト用DBの作成
DockerのMySQL内に `tododb_test` を作成します：
```powershell
docker exec -it todo-api-db-1 mysql -u root -p<パスワード> -e "CREATE DATABASE tododb_test;"
```

### 必要なパッケージのインストール
```bash
pip install pytest httpx
```

### テスト実行
```bash
pytest tests/ -v
```

### テスト結果例
```
tests/test_todos.py::test_create_todo PASSED
tests/test_todos.py::test_get_todos PASSED
tests/test_todos.py::test_get_todo PASSED
tests/test_todos.py::test_update_todo PASSED
tests/test_todos.py::test_delete_todo PASSED
tests/test_todos.py::test_create_todo_empty_title PASSED
tests/test_todos.py::test_create_todo_invalid_status PASSED
tests/test_todos.py::test_get_todo_not_found PASSED
tests/test_todos.py::test_update_todo_not_found PASSED
tests/test_todos.py::test_delete_todo_not_found PASSED
10 passed in x.xxs
```