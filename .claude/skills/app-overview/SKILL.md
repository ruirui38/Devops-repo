---
name: app-overview
description: このアプリケーションの構成・ディレクトリ・データフローを説明するスキル。PRレビュー・実装・修正のいずれのタスクでも、変更対象のコードに触れる前に必ず読み込む。
---

# アプリケーション構成

このリポジトリは、FastAPI製のTodo管理APIです。

## ディレクトリ構成

- `main.py`: FastAPIのエントリポイント。`lifespan`でDB初期化(`create_db_and_tables`)し、`routers/todos.py`のルーターを登録する
- `routers/todos.py`: `/todos` 配下のルーティングとDB操作（サービス層は分離されておらず、ルーター内でSQLModel Sessionを直接操作する）
- `models.py`: SQLModelスキーマ。`TodoCreate`（入力バリデーション用）と`Todo`（`todos`テーブル）
- `database.py`: `DATABASE_URL`の組み立てとエンジン・セッション（`get_session`）の提供
- `setup_db.py`: DBセットアップ用スクリプト
- `requirements.txt`: 依存パッケージ（fastapi, uvicorn, sqlmodel, pymysql, python-dotenv, pydantic, cryptography, pytest, httpx）
- `tests/test_todos.py`: pytest + `TestClient`によるAPIテスト（テスト用MySQLに接続）

## データフロー

1. クライアントが `/todos` に POST/GET/PUT/DELETE を投げる
2. `routers/todos.py` が `Depends(get_session)` でDBセッションを受け取り、`Todo`/`TodoCreate`（SQLModel）を介してMySQLを直接操作する
3. FastAPIが結果をJSONにシリアライズしてレスポンスを返す

## 制約と方針

- 認証は本アプリケーションの対象外
- 永続化はMySQL（SQLModel + pymysql）で行う。インメモリではない
- `TodoCreate`の`title`・`todo`・`status`はいずれも空文字列（空白のみ含む）を許容しない（`field_validator`）
- `status`は `"InProgress"` / `"Complete"` / `"Cancel"` の3値のみ許可（`Literal`）
- バリデーションエラー時のステータスコードはFastAPI標準の**422**（カスタム例外ハンドラは無い）
- 対象の`todo_id`が存在しない場合は**404**を返す（`HTTPException`）
- 作成成功時は**201**を返す