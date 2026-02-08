## Context

ヘキサゴナルアーキテクチャ + DDD でジョブ管理Webアプリケーションを新規構築する。プロセス間通信の学習が目的であり、APIサーバー・ワーカー・フロントエンドが独立したプロセスとして動作し、Redis Pub/Sub を介してドメインイベントをやり取りする構成とする。

現在コードベースは空の状態であり、すべてをゼロから構築する。

## Goals / Non-Goals

**Goals:**
- ヘキサゴナルアーキテクチャの層構造（ドメイン → ポート → アダプター）を明確に分離する
- DDD の集約・ドメインイベント・値オブジェクトパターンを実践する
- Redis Pub/Sub を通じたプロセス間のドメインイベント配信を実現する
- Docker Compose で全サービスをワンコマンドで起動できるようにする
- 学習目的として、各レイヤーの責務が読み取れるコード構成にする

**Non-Goals:**
- 本番環境向けの堅牢性（認証・認可・レートリミット・ログ基盤など）
- ジョブの複雑なスケジューリング（cron、優先度キューなど）
- 複数集約間のサガパターンやプロセスマネージャー
- フロントエンドのデザイン品質（最低限の機能的UIで十分）
- テストカバレッジの網羅（学習に必要な範囲のみ）

## Decisions

### 1. プロジェクト構成: モノレポ構成

**決定**: バックエンド・フロントエンド・Docker構成を1つのリポジトリで管理する。

```
/
├── backend/              # FastAPI + uv
├── frontend/             # React + bun
├── docker-compose.yml
└── openspec/
```

**理由**: 学習プロジェクトであり、サービス間の関係を一箇所で把握できるほうが学びやすい。

### 2. バックエンドのディレクトリ構成: ヘキサゴナルアーキテクチャ

**決定**: ドメイン・ポート・アダプターを明確にディレクトリで分離する。

```
backend/
├── pyproject.toml
├── Dockerfile
└── src/
    └── app/
        ├── domain/              # ドメイン層（外部依存なし）
        │   ├── models/          # 集約・エンティティ・値オブジェクト
        │   │   └── job.py       # Job 集約ルート
        │   ├── events/          # ドメインイベント定義
        │   │   └── job_events.py
        │   └── exceptions.py    # ドメイン例外
        │
        ├── ports/               # ポート層（インターフェース定義）
        │   ├── repository.py    # JobRepository（抽象基底クラス）
        │   └── event_publisher.py  # EventPublisher（抽象基底クラス）
        │
        ├── usecases/            # ユースケース層（アプリケーションロジック）
        │   ├── create_job.py
        │   ├── cancel_job.py
        │   ├── get_job.py
        │   └── list_jobs.py
        │
        └── adapters/            # アダプター層（外部接続の実装）
            ├── inbound/         # プライマリアダプター（外→中）
            │   ├── api/         # FastAPI ルーター
            │   │   └── job_router.py
            │   └── sse/         # SSE エンドポイント
            │       └── job_sse.py
            │
            └── outbound/        # セカンダリアダプター（中→外）
                ├── persistence/ # PostgreSQL 実装
                │   ├── postgres_job_repository.py
                │   └── models.py  # SQLAlchemy モデル
                └── messaging/   # Redis Pub/Sub 実装
                    └── redis_event_publisher.py
```

**理由**: ディレクトリ構成自体がヘキサゴナルアーキテクチャを表現し、依存の方向（外→中）を物理的に示す。学習者がファイルを見るだけで「どの層に何があるか」を理解できる。

**代替案**: レイヤードアーキテクチャ（controller/service/repository）も検討したが、ポートとアダプターの分離が不明確になるため不採用。

### 3. ドメインイベントの配信方式: Redis Pub/Sub

**決定**: ドメインイベントは Redis Pub/Sub チャンネルで配信する。

```
チャンネル: job_events
メッセージ形式: JSON
{
  "event_type": "JobCreated",
  "job_id": "uuid",
  "timestamp": "ISO8601",
  "payload": { ... }
}
```

**フロー**:

```
[APIサーバー]                         [ワーカー]
     │                                    │
     │ 1. Job作成                          │
     │ 2. JobCreated を Publish ─────────► │
     │                                    │ 3. Subscribe で受信
     │                                    │ 4. ジョブ実行（sleep）
     │                          ◄──────── │ 5. JobStarted を Publish
     │                          ◄──────── │ 6. JobCompleted を Publish
     │                                    │
[SSEエンドポイント]                        │
     │ Subscribe で受信                    │
     │ → SSE でフロントに通知               │
```

**理由**: Redis Pub/Sub はシンプルで学習コストが低い。プロセス間通信のパターンを学ぶには十分。

**代替案**: Redis Streams（永続化・再読み込み可能）も検討したが、学習目的では Pub/Sub のシンプルさを優先。

### 4. ワーカープロセス: 独立した Python プロセス

**決定**: ワーカーは API サーバーとは別プロセスとして Docker コンテナで起動する。同じ Python コードベースを共有し、エントリーポイントのみ異なる。

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    command: uvicorn app.main:app
  worker:
    build: ./backend
    command: python -m app.worker
```

**理由**: プロセス間通信を学ぶ目的のため、同一プロセス内ではなく意図的にプロセスを分離する。コードベースを共有することでドメインモデルの再利用性を示す。

### 5. 永続化: SQLAlchemy + asyncpg

**決定**: SQLAlchemy（async）を ORM として使用し、asyncpg ドライバーで PostgreSQL に接続する。

**理由**: FastAPI の async エコシステムと相性が良い。Repository パターンの実装が自然にできる。

**代替案**: 生SQL（asyncpg直接）も検討したが、マッピングの手間が増え学習の焦点がぶれるため不採用。

### 6. ワーカーのキャンセル機構: フラグポーリング

**決定**: RUNNING 中のジョブキャンセルは、ワーカーが定期的にキャンセルフラグ（DBのステータス）を確認する方式とする。

```python
# ワーカーのジョブ実行ループ（概念）
async def execute_job(job_id, duration):
    elapsed = 0
    while elapsed < duration:
        await asyncio.sleep(1)  # 1秒ごとにチェック
        elapsed += 1
        job = await repository.find_by_id(job_id)
        if job.status == JobStatus.CANCELLED:
            return  # キャンセル済みなら中断
    # 完了処理
```

**理由**: ダミージョブ（sleep）の特性を活かし、シンプルなポーリングで実現する。学習目的では十分な方式。

### 7. フロントエンド: React + Vite + bun

**決定**: Vite で React プロジェクトを構成し、bun でパッケージ管理する。TypeScript を使用。

```
frontend/
├── package.json
├── bun.lockb
├── Dockerfile
├── vite.config.ts
└── src/
    ├── App.tsx
    ├── components/
    │   ├── JobCreateForm.tsx
    │   ├── JobList.tsx
    │   └── JobStatusBadge.tsx
    ├── hooks/
    │   └── useJobSSE.ts       # SSE 接続カスタムフック
    └── api/
        └── jobApi.ts          # API クライアント
```

**理由**: bun はユーザーの指定。Vite は高速な開発体験を提供し、学習のイテレーションを速くする。

### 8. Docker Compose サービス構成

**決定**: 5つのサービスで構成する。

```yaml
services:
  api:         # FastAPI サーバー (port 8000)
  worker:      # ジョブワーカープロセス
  frontend:    # React 開発サーバー (port 5173)
  postgres:    # PostgreSQL (port 5432)
  redis:       # Redis (port 6379)
```

**理由**: 各サービスが独立したコンテナとして動作することで、プロセス間通信の境界が物理的に明確になる。

## Risks / Trade-offs

**[Redis Pub/Sub のメッセージ喪失]** → 学習用のため許容する。本番では Redis Streams や専用 MQ を検討すべき点として文書化する。

**[ワーカーのキャンセルポーリングによる DB 負荷]** → ダミージョブの sleep 秒数は短く（最大30秒程度）、同時実行ジョブ数も少ないため問題にならない。

**[SSE の接続管理]** → ブラウザの SSE は自動再接続するため、学習用途では特別な対策は不要。

**[Docker での開発体験]** → ホットリロードを有効にするためバックエンド・フロントエンドともにソースコードをボリュームマウントする。
