# asyncio による並列実行（技術書レベル）

この章では、本アプリの「同時実行」がどのような技術で実現されているかを丁寧に解説します。対象は **Python / asyncio に不慣れなエンジニア** です。

## 結論（このアプリの並列実行の正体）

- **技術**: Python の `asyncio`（協調的マルチタスク）
- **実装箇所**: `backend/src/app/worker.py`
- **仕組み**: イベントを受信するたびに `asyncio.create_task(...)` で新しい非同期タスクを起動する

つまり、1件のジョブが実行中でも、別のジョブ処理が **同じスレッド内で並行して進む** 仕組みです。

## まず押さえるべき前提

### 1. 「並列」と「並行」

- **並列（parallel）**: CPU コアを複数使って本当に同時に実行
- **並行（concurrent）**: 1 つのスレッドで複数の処理を切り替えて進める

このアプリの `asyncio` は **並行** です。I/O 待ち中に別のタスクへ切り替えることで“同時に進んでいるように見える”状態を作ります。

### 2. `asyncio` の基本

- `async def` で非同期関数を作る
- `await` は I/O 待ち中に他の処理へ制御を譲る
- `asyncio.create_task()` で「バックグラウンドで実行するタスク」を作る

この仕組みで **1 スレッド上に複数タスク** が載り、同時進行が実現されます。

## 本アプリの並列実行ポイント

### 1. ワーカーのイベント受信ループ

`worker.py` では Redis Pub/Sub を Subscribe し、イベントを受信するたびに非同期タスクを起動しています。

```python
if message and message["type"] == "message":
    data = json.loads(message["data"])
    asyncio.create_task(handle_event(data, redis_client))
```

ここで `handle_event()` が **1 ジョブの処理単位** です。イベントが連続して届くと、タスクがどんどん積まれ、並行して進みます。

### 2. ジョブ実行自体も await を含む

`execute_job()` 内では `await asyncio.sleep(1)` が呼ばれます。

- sleep 中は **他のタスクに制御が渡る**
- その結果、複数ジョブが“同時に進んでいるように見える”

このように **I/O 待ちや sleep を挟む処理は、asyncio で非常に相性が良い** です。

## マルチスレッドパターンとの対応

以下は、あなたが挙げたパターンのうち **本アプリの並列処理に強く対応するもの** です。

### ✅ Thread-Per-Message（この仕事、やっといてね）

- **理由**: イベント 1 件ごとに `asyncio.create_task()` で処理を起動するため。
- **対応箇所**: `worker.py` の `asyncio.create_task(handle_event(...))`

※ 名前に「Thread」とありますが、実際は **スレッドではなく asyncio タスク** です。

### ✅ Worker Thread（仕事が来るまで待ち、仕事が来たら働く）

- **理由**: ワーカーは Redis Pub/Sub を購読し、仕事（イベント）が来るまで待機している。
- **対応箇所**: `worker.py` のメインループ

### ✅ Producer-Consumer（わたしが作り、あなたが使う）

- **理由**: API 側がイベントを「生産」し、ワーカーが「消費」する。
- **対応箇所**:
  - Producer: `RedisEventPublisher`（API が JobCreated を Publish）
  - Consumer: `worker.py`（Subscribe して処理）

### 条件付き・弱い対応

- **Future（引換券を、お先にどうぞ）**
  - `asyncio.Task` は Future 互換だが、このアプリでは結果を待つ用途はほぼないため **弱い対応**。

### 対応しない（このアプリでは使っていない）

- Single Threaded Execution
- Immutable
- Guarded Suspension
- Balking
- Read-Write Lock
- Two-Phase Termination
- Thread-Specific Storage
- Active Object

## 注意点（実務目線）

- **同時実行数の制限はない**
  - 大量イベントが来るとタスクが増えすぎる可能性がある
- **順序保証はない**
  - 並行に実行されるため、完了順は保証されない

## 1コア = 1プロセス = 1ワーカー？ という理解について

結論: **「1プロセス = 1ワーカー」は正しいが、「1コア固定」ではない** です。

- **1ワーカー = 1プロセス**  
  このアプリの `worker.py` は 1 プロセスとして動くため、1ワーカー = 1プロセスです。
- **1プロセス = 1コア固定ではない**  
  OS のスケジューラが実行中のプロセスをコアに割り当てます。負荷や状況に応じてコアを移動します。
- **1ワーカー内で複数ジョブを“並行”実行**  
  `asyncio` タスクによる協調的マルチタスクなので、1プロセス内で複数ジョブが進みます。

もし「本当の並列（複数コアを同時に使う）」をしたい場合は、**ワーカーを複数プロセスで起動**する設計になります。

## まとめ

- 本アプリの並列実行は `asyncio` による **協調的マルチタスク**
- パターン対応は **Thread-Per-Message / Worker Thread / Producer-Consumer** が中心
- スレッドではなくタスクで並行性を作っている点が重要
