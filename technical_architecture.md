# 技術詳細ドキュメント: 医薬品LP自動生成ツール

このドキュメントでは、本プロジェクトの技術スタック、システムアーキテクチャ、およびデプロイメントの仕組みについて解説します。

## 1. 技術スタック (Tech Stack)

このアプリケーションは、**Python** エコシステムを中心に構築されており、シンプルかつ強力なライブラリ構成で動作しています。

| カテゴリ | 技術・ライブラリ | 用途・選定理由 |
| :--- | :--- | :--- |
| **言語** | **Python 3.10+** | AIライブラリとの親和性が高く、記述が容易。 |
| **Webフレームワーク** | **Streamlit** | フロントエンドとバックエンドを単一のPythonファイルで完結できるため、開発速度が非常に速い。 |
| **AI モデル** | **Google Gemini API** | `gemini-2.5-flash` / `gemini-1.5-pro` を使用。高速かつ日本語の長文生成に優れる。 |
| **AI SDK** | **google-genai** | Google公式の最新SDK。Google AI Studioの機能をフルに活用。 |
| **スクレイピング** | **BeautifulSoup4** | 競合サイトのHTML解析とテキスト抽出に使用。 |
| **HTTP通信** | **Requests** | 競合サイトへのアクセスに使用。 |
| **デプロイ環境** | **Streamlit Community Cloud** | GitHub連携だけで無料かつ即座にWeb公開できるPaaS。 |

## 2. システムアーキテクチャ (Architecture)

本システムは、ユーザーの入力（URL）を受け取り、外部サイトを解析し、AIがコンテンツを生成する「データパイプライン」として動作します。

### データフロー図
```mermaid
graph TD
    User[ユーザー] -->|URL & API Key入力| App[Streamlit App (app.py)]
    
    subgraph Data Pipeline
        App -->|URL送信| Scraper[Scraper (scraper.py)]
        Scraper -->|HTTP Request| TargetSite[競合サイト]
        TargetSite -->|HTML| Scraper
        Scraper -->|テキスト抽出 & 前処理| CleanText[整形済みテキスト]
        
        App -->|プロンプト構築| SystemPrompt[Prompt Engine (prompts.py)]
        CleanText --> SystemPrompt
        
        SystemPrompt -->|Prompt + Context| Gemini[Google Gemini API]
        Gemini -->|Generated HTML| App
    end
    
    subgraph Post Processing
        App -->|clean_html_tags| Cleaner[HTML Cleaner]
        Cleaner -->|正規表現でStyle属性削除| FinalHTML[最終HTML]
    end
    
    FinalHTML -->|プレビュー表示| User
    FinalHTML -->|ダウンロード| User
```

### 主要コンポーネントの解説

1.  **Streamlit App (`app.py`)**:
    *   **UI層**: ユーザーインターフェース（入力フォーム、ボタン、タブ表示）を提供。
    *   **コントローラー**: 各モジュールの呼び出し制御を行います。
    *   **HTML Cleaner**: AIが生成したHTMLに対し、**強制的にスタイル属性（`style="..."`）を削除する正規表現処理**を実行し、サイト全体のCSSとの競合を防ぎます。

2.  **Scraper (`scraper.py`)**:
    *   指定されたURLにアクセスし、メインコンテンツ（`article`, `div#main` など）からノイズを除去してテキストのみを抽出します。
    *   `lxml` パーサーや `html.parser` を使用し、高速に処理します。

3.  **Prompt Engine (`prompts.py`)**:
    *   **役割**: AIに対する指示書（プロンプト）の管理。
    *   **特徴**: SEOの専門知識、医薬品の薬機法・広告規制を意識した厳格なルールセットが記述されています。「ターゲット層と禁忌情報の分離」などのロジックもここに集約されています。

## 3. デプロイメントの仕組み (Deployment)

このアプリは、伝統的なサーバー（AWS EC2やVPS）ではなく、**サーバーレスに近いPaaS (Platform as a Service)** である **Streamlit Community Cloud** 上で動作させることを想定しています。

### デプロイの流れ
1.  **GitHubリポジトリ**: ソースコード一式（`app.py`, `requirements.txt` 等）をGitHubにアップロードします。
2.  **Streamlit Cloud**: 管理画面でGitHubリポジトリを選択します。
3.  **自動ビルド**:
    *   Streamlit Cloudが `requirements.txt` を読み込み、必要なライブラリ（`google-genai`, `beautifulsoup4` 等）を自動インストールした仮想環境を構築します。
    *   `streamlit run app.py` コマンドが自動実行され、アプリがWeb上に公開されます。

### なぜこの構成なのか？
*   **Vercelとの違い**: VercelはJavaScript(Next.js)向けですが、Streamlit CloudはPython専用の同様のサービスです。
*   **メリット**: インフラ管理（OSアップデート、SSL証明書設定、Nginx設定など）が一切不要。APIキーさえあれば誰でも使えます。

## 4. ディレクトリ構造

```text
product_generator/
├── app.py                # メインアプリケーション
├── prompts.py            # プロンプト定義ファイル（AIへの指示）
├── scraper.py            # Webスクレイピングロジック
├── requirements.txt      # 依存ライブラリ一覧（デプロイ用）
├── check_models_ui.py    # デバッグ用ツール（利用可能モデル確認）
├── .gitignore            # Git除外設定
└── implementation_plan.md # 実装計画書
```
