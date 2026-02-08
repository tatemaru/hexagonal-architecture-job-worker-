## ADDED Requirements

### Requirement: Docker Compose による全サービスの構成

Docker Compose で以下の5サービスを定義しなければならない（SHALL）: api、worker、frontend、postgres、redis。`docker compose up` でサービスが起動する。

#### Scenario: 全サービスの一括起動
- **WHEN** `docker compose up` を実行する
- **THEN** api、worker、frontend、postgres、redis の5サービスが起動し、相互に通信可能になる

#### Scenario: サービスの起動順序
- **WHEN** `docker compose up` を実行する
- **THEN** postgres と redis が先に起動し、api と worker はそれらが ready になってから起動する

### Requirement: バックエンドのコンテナ構成

api と worker は同じ Dockerfile からビルドされなければならない（SHALL）。`uv` でパッケージ管理を行い、エントリーポイント（command）のみが異なる。

#### Scenario: API サーバーの起動
- **WHEN** api サービスが起動する
- **THEN** `uvicorn` で FastAPI アプリケーションがポート 8000 で起動する

#### Scenario: ワーカーの起動
- **WHEN** worker サービスが起動する
- **THEN** `python -m app.worker` でワーカープロセスが起動する

### Requirement: フロントエンドのコンテナ構成

frontend サービスは `bun` でパッケージ管理を行い、Vite 開発サーバーとして起動しなければならない（SHALL）。

#### Scenario: フロントエンドの起動
- **WHEN** frontend サービスが起動する
- **THEN** Vite 開発サーバーがポート 5173 で起動し、ブラウザからアクセス可能になる

### Requirement: 開発時のホットリロード

開発体験のため、バックエンド・フロントエンドともにソースコードをボリュームマウントし、ホットリロードを有効にしなければならない（SHALL）。

#### Scenario: バックエンドのコード変更反映
- **WHEN** backend/ 配下の Python ファイルを変更する
- **THEN** uvicorn の --reload オプションにより API サーバーが自動的に再起動する

#### Scenario: フロントエンドのコード変更反映
- **WHEN** frontend/src/ 配下のファイルを変更する
- **THEN** Vite の HMR（Hot Module Replacement）によりブラウザがリロードなしで更新される

### Requirement: データベースの永続化

PostgreSQL のデータは Docker ボリュームに永続化しなければならない（SHALL）。コンテナを再起動してもデータが失われない。

#### Scenario: コンテナ再起動後のデータ保持
- **WHEN** `docker compose down` して再度 `docker compose up` する
- **THEN** PostgreSQL に保存済みのジョブデータが保持されている
