## Why

現行のバックエンド技術書は概要と対応付けはあるが、ヘキサゴナルアーキテクチャと DDD の深掘りが不足している。Alistair Cockburn の Hexagonal Architecture をベースに、より厚い説明と図解を追加し、初心者でも実装の意図を理解できるようにする。

## What Changes

- ヘキサゴナルアーキテクチャ章を大幅に増補し、用語・意図・依存関係・変形パターン・図解を追加する
- DDD 章を増補し、概念の相互関係・境界・イベント/集約の責務を図解込みで整理する
- 追加の図（Mermaid）を挿入し、アーキテクチャと責務の対応を視覚化する

## Capabilities

### New Capabilities
- （なし）

### Modified Capabilities
- `backend-docs`: ヘキサゴナルアーキテクチャと DDD に関する技術書部分を厚くし、図解を追加する

## Impact

- 変更対象: `docs/backend/03_hexagonal.md`, `docs/backend/02_ddd.md` など既存ドキュメント
- 追加ファイル: 図解を含む補助資料（必要に応じて）
- 既存コードや API への影響はない
