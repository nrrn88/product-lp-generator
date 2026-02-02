# Streamlit Community Cloud デプロイ手順書

このアプリケーションをWeb上に公開し、リンクを知っている人が誰でもアクセスできるようにするための手順です。無料で最も簡単な「Streamlit Community Cloud」を利用します。

## 1. 準備 (GitHubへのアップロード)
まず、現在のコードをGitHubのリポジトリにアップロードする必要があります。

1.  GitHubのアカウントがない場合は作成します: [https://github.com/](https://github.com/)
2.  GitHubで「New repository」をクリックし、新しいリポジトリを作成します（例: `product-generator-app`）。"Public"（公開）または"Private"（非公開）を選べますが、Privateでもデプロイ可能です。
3.  手元のこのフォルダの中身を全てGitHubにアップロード（プッシュ）します。
    - `vscode`等のGit機能を使うか、コマンドラインで行います。
    - **重要**: `requirements.txt` が必ず含まれていることを確認してください（先ほど作成済みです）。

## 2. Streamlit Cloud へのデプロイ
1.  [Streamlit Community Cloud](https://streamlit.io/cloud) にアクセスし、サインアップ（GitHubアカウントでログイン）します。
2.  「Create app」ボタンをクリックします。
3.  **Repository**: 先ほど作成したGitHubリポジトリを選択します。
4.  **Branch**: `main` (または `master`) を選択します。
5.  **Main file path**: `app.py` を入力します。
6.  「Deploy!」ボタンをクリックします。

## 3. アプリの公開設定
デプロイが完了すると、`https://your-app-name.streamlit.app` のようなURLが発行されます。

- **URLの共有**: このURLを共有すれば、誰でもアプリにアクセスできます。
- **APIキーについて**:
  - 現在のアプリは、アクセスしたユーザー自身が「自分のGemini APIキー」を入力して使う仕組みになっています。
  - これにより、作者（あなた）のAPI利用枠を消費することなく、安全に多くの人に使ってもらえます。

## (オプション) URLを知っている人だけにパスワード制限をかける
不特定多数に見られたくない場合、Streamlitの設定で簡易的なパスワード認証をつけることも可能です（またはGitHubをPrivateにしてデプロイ時に制限するなど）。

## (オプション) APIキー入力を省略させる場合
もし「信頼できるメンバーだけ」に使い、APIキー入力を省略させたい場合は、Streamlit Cloudの「Advanced settings」→「Secrets」に以下のように設定します（ただしAPI利用料に注意してください）。

```toml
GEMINI_API_KEY = "あなたのAPIキー"
```
※アプリ側(`app.py`)の修正も少し必要になります（`st.secrets`を読むようにする）。今回は「ユーザー入力方式」なので、この設定は不要です。
