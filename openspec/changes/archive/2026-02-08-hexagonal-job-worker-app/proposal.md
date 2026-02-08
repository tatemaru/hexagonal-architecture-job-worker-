## Why

ヘキサゴナルアーキテクチャとDDD（ドメイン駆動設計）におけるプロセス間通信のパターンを学習するために、ジョブ管理Webアプリケーションを構築する。FastAPI・PostgreSQL・Redis Pub/Sub・Reactを組み合わせ、ドメインモデルを中心に据えたポートとアダプターの境界を明確にした実践的な学習プロジェクトとする。

## Domain Model

### ドメイン: ジョブライフサイクル管理

このアプリケーションの核となるドメインは「ジョブのライフサイクル管理」である。ジョブは明確な状態遷移ルールを持ち、そのルールの実行がドメインロジックの中心となる。

### 集約（Aggregate）

**Job（集約ルート）**
- ジョブのライフサイクル全体を管理する唯一の集約
- 状態遷移のルール（不変条件）を内部に持つ
- ドメインイベントを発行する責務を持つ

### 値オブジェクト（Value Object）

| 値オブジェクト | 説明 |
|---|---|
| `JobId` | ジョブの一意識別子（UUID） |
| `JobStatus` | ジョブの状態（列挙型 + 遷移ルール） |
| `JobType` | ジョブの種別。学習用のため、指定秒数 sleep して完了するダミージョブのみ |
| `JobResult` | 実行結果の詳細（出力メッセージ・エラー情報） |

### ドメインイベント（Domain Event）

| イベント | 発行タイミング |
|---|---|
| `JobCreated` | ジョブが作成され、待機キューに入った |
| `JobStarted` | ワーカーがジョブの実行を開始した |
| `JobCompleted` | ジョブが正常に完了した |
| `JobFailed` | ジョブの実行が失敗した |
| `JobCancelled` | ユーザーがジョブをキャンセルした |

### ステートマシン（Job Status State Machine）

```
            ┌──────────┐    JobStarted     ┌──────────────┐
JobCreated  │          │ ────────────────► │              │
──────────► │ PENDING  │                   │   RUNNING    │
            │          │   ─────────────── │              │
            └──────────┘   │               └──────────────┘
                  │        │   　　　           │           │
            　　　　　　JobCancelled     　         │　　　　　　　　　　　│
                  　　　　│                 JobCompleted  JobFailed
                  　　　　│                      │           │
                  　　　　▼                      ▼           ▼
            ┌──────────────────────┐  ┌──────────┐ ┌──────────┐
            │                      │  │          │ │          │
            │      CANCELLED       │  │COMPLETED │ │  FAILED  │
            │                      │  │          │ │          │
            └──────────────────────┘  └──────────┘ └──────────┘
```

**状態遷移ルール（不変条件）**:
- `PENDING` → `RUNNING`: ワーカーがジョブを取得したとき
- `PENDING` → `CANCELLED`: ユーザーがキャンセルを要求したとき
- `RUNNING` → `COMPLETED`: ジョブが正常終了したとき
- `RUNNING` → `FAILED`: ジョブが異常終了したとき
- `RUNNING` → `CANCELLED`: ユーザーがキャンセルを要求したとき
- 上記以外の遷移は**ドメインルールとして禁止**される（例: COMPLETED → PENDING は不可）

### ドメインの境界（何がドメインで、何がアダプターか）

| 関心事 | レイヤー | 説明 |
|---|---|---|
| Job の状態遷移ルール | **ドメイン** | 不変条件を守る集約ロジック |
| ドメインイベントの定義・発行 | **ドメイン** | 状態遷移時にイベントを生成 |
| ジョブの永続化 | ポート（インフラ実装） | Repository ポートを定義し、PostgreSQL アダプターで実装 |
| イベントの配信 | ポート（インフラ実装） | EventPublisher ポートを定義し、Redis Pub/Sub アダプターで実装 |
| HTTP API | アダプター（プライマリ） | FastAPI がユースケースを呼び出す入口 |
| SSE 通知 | アダプター（プライマリ） | Redis Subscribe → SSE 変換 |
| React UI | 外部（別プロセス） | API/SSE を消費するクライアント |

## What Changes

- FastAPIによるバックエンドAPIサーバーを新規作成（ヘキサゴナルアーキテクチャ + DDD で構成）
- Job 集約を中心としたドメインモデルの実装（状態遷移ルール・ドメインイベント）
- ポート（Repository・EventPublisher）の定義とアダプター（PostgreSQL・Redis）の実装
- PostgreSQLによるジョブ履歴の永続化層を追加
- Redis Pub/Subによるドメインイベントのプロセス間配信を実装
- Reactによるフロントエンドを新規作成（ジョブの作成・一覧・状態監視）
- Docker Composeで全サービス（API・Worker・PostgreSQL・Redis・Frontend）を構成
- バックエンドは`uv`でパッケージ管理、フロントエンドは`bun`でパッケージ管理

## Capabilities

### New Capabilities

- `job-management`: Job集約のドメインモデル（状態遷移・ドメインイベント）、ユースケース、Repositoryポート、およびCRUD APIエンドポイント
- `job-worker`: Redis Pub/Subでドメインイベント（JobCreated）を受信しジョブを非同期実行するワーカープロセス。実行結果に応じてJob集約の状態を遷移させドメインイベントを発行する
- `realtime-status`: Redis Pub/Subのドメインイベントを購読し、SSE（Server-Sent Events）でフロントエンドにリアルタイム通知する
- `frontend-ui`: Reactによるジョブ管理画面（ジョブ作成フォーム・一覧テーブル・リアルタイムステータス表示）
- `docker-infrastructure`: Docker Composeによる開発環境の構成（API・Worker・PostgreSQL・Redis・Frontend）

### Modified Capabilities

(なし — 新規プロジェクトのため既存の変更対象はありません)

## Impact

- **新規コード**: バックエンド（Python/FastAPI）、フロントエンド（TypeScript/React）、Docker構成ファイル一式
- **依存サービス**: PostgreSQL、Redis（いずれもDockerコンテナとして提供）
- **API**: RESTful APIエンドポイント（ジョブCRUD）、SSEエンドポイント（リアルタイム通知）
- **パッケージ管理**: バックエンドは`uv`（pyproject.toml）、フロントエンドは`bun`（package.json）
