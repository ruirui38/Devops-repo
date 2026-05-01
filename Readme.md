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

## CI/CD パイプライン

### 概要

このリポジトリでは GitHub Actions を使って CI/CD を自動化しています。

```
Pull Request → main         Push → main
      │                          │
   [CI ワークフロー]          [CD ワークフロー]
      │                          │
  ┌───┴────┐              ┌──────┴──────┐
  │ lint   │              │   deploy    │
  │ test   │              │ (AWS ECS)   │
  └────────┘              └─────────────┘
```

| ワークフロー | ファイル | トリガー | 内容 |
|------------|---------|---------|------|
| CI | `.github/workflows/ci.yml` | `main` へのPull Request | 静的解析・テスト |
| CD | `.github/workflows/cd.yml` | `main` へのpush | ECRへのビルド＆プッシュ・ECSデプロイ |

---

### CI ワークフロー詳細

`main` ブランチへのPull Requestが作成または更新されると自動実行されます。

#### lint ジョブ

| ステップ | ツール | 内容 |
|---------|-------|------|
| 静的解析 | flake8 | PEP8準拠チェック（最大行長120文字） |
| フォーマットチェック | Black | コードスタイル統一の確認 |
| 型チェック | mypy | 型アノテーションの検証 |

#### test ジョブ

MySQL 8.0 のサービスコンテナを起動してから `pytest tests/ -v` を実行します。テスト用DBは `tododb_test` が自動作成されます。

---

### CD ワークフロー詳細

`main` ブランチへのpushで自動実行されます。AWS認証にはOIDCを使用しており、長期的なアクセスキーは不要です。

| ステップ | 内容 |
|---------|------|
| AWS認証（OIDC） | IAMロールをAssumeしてAWS操作権限を取得 |
| ECRログイン | Amazon ECRへのDocker認証 |
| イメージビルド＆プッシュ | `linux/arm64` 向けにビルドし、コミットSHAタグと `latest` タグでプッシュ |
| タスク定義取得 | 現在のECSタスク定義をAWS APIから取得 |
| タスク定義更新 | 新しいイメージでタスク定義を再レンダリング |
| ECSデプロイ | サービスを更新し、安定稼働まで待機 |

---

### 必要な Secrets と Variables

AWS認証にOIDCを使用しているため、**AWSアクセスキーのSecretは不要**です。  
以下の Variables をリポジトリの `Settings > Secrets and variables > Actions` で設定してください。

#### Variables（`vars.*`）

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `AWS_IAM_ROLE_ARN` | OIDCでAssumeするIAMロールのARN | `arn:aws:iam::123456789012:role/github-actions-role` |
| `AWS_REGION` | デプロイ先のAWSリージョン | `ap-northeast-1` |
| `ECR_REPOSITORY` | ECRリポジトリ名 | `todo-api` |
| `TASK_DEFINITION` | ECSタスク定義名 | `todo-api-task` |
| `CONTAINER_NAME` | タスク定義内のコンテナ名 | `todo-api` |
| `ECS_SERVICE` | ECSサービス名 | `todo-api-service` |
| `ECS_CLUSTER` | ECSクラスター名 | `todo-api-cluster` |

#### Secrets（`secrets.*`）

| シークレット名 | 説明 |
|-------------|------|
| なし | OIDCを使用するため、AWS認証情報のシークレットは不要 |

> **OIDC設定について**  
> IAMロールの信頼ポリシーに GitHub Actions の OIDC プロバイダー（`token.actions.githubusercontent.com`）を追加し、このリポジトリからのみAssumeできるよう制限してください。

---

### 動作確認手順

#### CI の確認

1. `main` ブランチから作業ブランチを作成してPull Requestを作成する
2. GitHub リポジトリの **Actions** タブを開く
3. `CI` ワークフローが自動起動することを確認する
4. `lint` と `test` の両ジョブが緑（成功）になれば正常動作

```bash
# ローカルでCIと同等のチェックを事前に実行する場合
pip install flake8 black mypy pytest httpx
flake8 . --max-line-length=120 --exclude=.git,__pycache__
black --check .
mypy . --ignore-missing-imports
pytest tests/ -v
```

#### CD の確認

1. Pull RequestをレビューしてマージするとCDが自動起動する
2. GitHub リポジトリの **Actions** タブで `CD` ワークフローを開く
3. 各ステップが順番に成功していることを確認する
4. **ECSサービスをデプロイ** ステップで `wait-for-service-stability: true` により、タスクが正常起動するまでワークフローが待機する
5. デプロイ完了後、ECSサービスのURLで動作確認を行う

#### よくある失敗ケースと対処

| エラー | 原因 | 対処 |
|-------|------|------|
| `lint` ジョブ失敗 | コードスタイル違反 | `black .` でフォーマット修正後、再プッシュ |
| `test` ジョブ失敗 | テストコードのエラー | ローカルで `pytest tests/ -v` を実行して確認 |
| OIDC認証エラー | IAMロールの信頼ポリシー設定ミス | IAMロールのConditionとリポジトリ名を確認 |
| ECRプッシュ失敗 | IAMロールにECR権限がない | IAMロールのポリシーに `ecr:*` 権限を付与 |
| ECSデプロイタイムアウト | タスクが起動失敗している | ECSタスクのログをCloudWatch Logsで確認 |

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