# 主要フロー（API → ユースケース → ドメイン）

この章では「REST API がどのようにドメインに到達するか」を順に追います。読みながらコードを開くと理解が深まります。

## 1. ジョブ作成（POST /api/jobs）

**入口**: `backend/src/app/adapters/inbound/api/job_router.py` の `create_job`

**流れ**:
1. リクエストを `CreateJobRequest` で受ける
2. `PostgresJobRepository` と `RedisEventPublisher` を生成
3. `CreateJobUseCase` を実行
4. ドメインの `Job.create()` が新規ジョブを作る
5. `JobCreated` イベントを発行
6. `RedisEventPublisher` が Redis に Publish
7. 作成した `Job` をレスポンスに変換

**対応コード**:
- API: `job_router.py` `create_job`
- ユースケース: `usecases/create_job.py`
- ドメイン: `domain/models/job.py` `Job.create()`
- イベント配信: `adapters/outbound/messaging/redis_event_publisher.py`

## 2. ジョブ一覧（GET /api/jobs）

**入口**: `job_router.py` の `list_jobs`

**流れ**:
1. `ListJobsUseCase` を実行
2. `JobRepository.find_all()` を呼ぶ
3. `PostgresJobRepository` が DB から取得
4. 結果を API レスポンスに変換

## 3. ジョブ詳細（GET /api/jobs/{job_id}）

**入口**: `job_router.py` の `get_job`

**流れ**:
1. `GetJobUseCase` を実行
2. `JobRepository.find_by_id()` を呼ぶ
3. 見つからない場合は `JobNotFoundError`

## 4. ジョブキャンセル（POST /api/jobs/{job_id}/cancel）

**入口**: `job_router.py` の `cancel_job`

**流れ**:
1. `CancelJobUseCase` を実行
2. `Job.cancel()` が状態遷移（PENDING/RUNNING → CANCELLED）
3. `JobCancelled` イベントを発行
4. `RedisEventPublisher` が Redis に Publish

**ポイント**:
- キャンセルはドメインのルールに従う
- 不正な遷移は `InvalidStatusTransitionError` で失敗

## 5. どこで “ルール” を守るか

- API ではなく **ドメインでルールを守る**
- API は「入力を受け取り、ユースケースを呼ぶだけ」
- ルールの中心は `Job` と `JobStatus`

この分離が、変更に強い構造を作ります。
