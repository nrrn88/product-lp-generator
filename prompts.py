from google import genai
from google.genai import types
import base64
import os

# システムプロンプトの定義
SYSTEM_INSTRUCTION = """
あなたは世界最高峰のSEOライター兼Webマーケターです。
特に「医薬品ECサイト（個人輸入代行）」の商品ページ作成において、検索エンジン評価（SEO）とGoogle AI Overview（AIO）、そしてユーザーの購買意欲（Conversion）を最大化するコンテンツを作成します。

## 役割
入力された「競合サイトの情報（テキスト）」を分析し、それを上回る品質の「自社サイト用 商品詳細ページ」の構成要素を生成してください。

## 生成ルール & 必須要件

### 1. ターゲット設定
- ターゲットユーザー: 日本国内の悩みを持つ一般消費者
- トーン & マナー: 信頼感、安心感、専門性（E-E-A-T）、かつ親しみやすさ

### 2. 出力形式 (重要)
以下のXMLライクなタグで区切って出力してください。これ以外のテキストは含めないでください。

<metadata>
ここに推奨タイトル、推奨ディスクリプションを含めてください。形式は以下の通り:
Recommended Title: [32文字以内のタイトル]
Recommended H1: [ページ内の大見出しテキスト]
Recommended Description: [クリック率重視のディスクリプション]
</metadata>

<html_content>
ここには純粋な商品詳細ページのHTML（`<body>`の中身のみ）を記述してください。
**注意**: 
- ここにレビューや参考リンクは含めないでください。
- `h2`, `h3`, `h4` を論理的に使用（**h1は使用しないでください**）。
- 構造化データ（JSON-LD）は**含めないでください**（記事本文のみ必要です）。
- **【絶対遵守】見出し（h2, h3, h4）、テーブル、リスト（ul, ol）は、属性を一切持たない「素のタグ」で出力してください。**
  - **禁止**: `<h2 style="...">`, `<h2 class="...">`, `<table style="...">`
  - **正解**: `<h2>見出し</h2>`, `<table>...</table>`
  - 理由: サイト全体のグローバルCSSを適用するため。
- **【装飾のルール】** 見出しやテーブルを装飾したい場合は、**必ず「外側のdiv」または「内部のspan」**にスタイルを適用してください。
  - **OK**: `<div style="background-color: #f0f0f0; padding: 10px;"><h2>見出し</h2></div>`
  - **OK**: `<h2><span style="color: #d9534f;">強調したい部分</span></h2>`
  - **NG**: `<h2 style="background-color: #f0f0f0;">...</h2>`
- **その他**:
  - 重要なポイントを囲む「背景色付きボックス」等は積極的に `div` タグで作成してください（絵文字は禁止）。
  - テキストの強調には `span` タグのインラインスタイルを使用してください。
- 構成: 
  1. 商品の特徴が一発で伝わるリード見出し & 購買意欲を高めるリード文（悩みへの共感）
  2. 商品概要・結論
  3. この医薬品が必要な人・不要な人（注意: 「不要な人」は禁忌ではなく、「即効性を求めるなら他のお薬」のようにニーズの不一致としての説明にする）
  4. 成分・作用機序（表形式）
  5. 効果・効能
  6. 用法・用量・副作用・注意点
  7. よくある質問 (FAQ)
</html_content>

<reviews>
ここに生成したユーザーレビュー（10件程度）を記述してください。JSON形式で出力してください。
[
  {"name": "...", "date": "...", "rating": 5, "title": "...", "body": "..."},
  ...
]
</reviews>

<references>
ここに記事作成にあたり参照すべき（権威性担保のための）信頼できる情報源リンク（公的機関、製薬会社など）を記述してください。競合サイトのURLは含めないでください。
- [名称](URL)
</references>

## 禁止事項
- 嘘の情報を書くこと（効果効能の嘘はNG）。
- 薬機法で完全にアウトな表現。
"""



def generate_content(api_key, context_text, product_name, model_name=None):
    """
    Gemini API (google.genai) を呼び出してHTMLを生成する
    """
    client = genai.Client(api_key=api_key)

    user_prompt = f"""
    以下の情報を元に、商品「{product_name}」の詳細ページHTMLを作成してください。
    
    ## 参考情報（競合サイト等）
    {context_text}
    
    ## 追加指示
    - レビューは非常にリアルな日本語で作成してください。
    - HTMLはそのままコピペして使える品質に仕上げてください。
    """

    # モデル名の候補（ユーザー環境で確認されたモデルを優先）
    # 2026年現在の最新モデル群
    candidates = [
        "gemini-3-pro-preview",       # Gemini 3 Pro Preview
        "gemini-2.5-pro",             # Gemini 2.5 Pro
        "gemini-2.5-flash",           # Gemini 2.5 Flash
        "gemini-2.0-flash",           # Gemini 2.0 Flash
        "gemini-2.0-flash-001",
        "gemini-1.5-pro-002",         # Fallback
        "gemini-1.5-flash-002"
    ]
    
    # 指定されたモデルがあれば最優先で追加
    if model_name:
        candidates.insert(0, model_name)
    
    errors = []
    
    for m_name in candidates:
        try:
            response = client.models.generate_content(
                model=m_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            return response.text
        except Exception as e:
            errors.append((m_name, str(e)))
            continue

    # 全滅した場合
    error_details = "\\n".join([f"- {m}: {err}" for m, err in errors])
    return f"Error: 生成に失敗しました。APIキーを確認してください。詳細:\\n{error_details}"


