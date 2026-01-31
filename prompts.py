import google.generativeai as genai
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
ここに推奨タイトル、推奨ディスクリプション、画像プロンプトを含めてください。形式は以下の通り:
Recommended Title: [32文字以内のタイトル]
Recommended Description: [クリック率重視のディスクリプション]
Image Prompts:
- [画像プロンプト1]
- [画像プロンプト2]
</metadata>

<html_content>
ここには純粋な商品詳細ページのHTML（`<body>`の中身のみ）を記述してください。
**注意**: 
- ここにレビューや参考リンクは含めないでください。
- `h1`, `h2`, `h3` を論理的に使用。
- 構造化データ（JSON-LD）はここに含めてください（Product, FAQPage schema）。
- styleタグで最低限のCSSを含めてください。
- 構成: 
  1. 商品ヘッダー（h1, キャッチコピー）
  2. 概要・結論
  3. 成分・作用機序（表形式）
  4. 効果・効能
  5. 用法・用量・副作用・注意点
  6. よくある質問 (FAQ)
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

def generate_content(api_key, context_text, product_name):
    """
    Gemini APIを呼び出してHTMLを生成する
    モデル名が見つからないエラー(404)対策として、複数のモデル名を順次試行する
    """
    genai.configure(api_key=api_key)

    user_prompt = f"""
    以下の情報を元に、商品「{product_name}」の詳細ページHTMLを作成してください。
    
    ## 参考情報（競合サイト等）
    {context_text}
    
    ## 追加指示
    - レビューは非常にリアルな日本語で作成してください。
    - HTMLはそのままコピペして使える品質に仕上げてください。
    """


    
    # 利用可能なモデルを動的に検索して使用する
    valid_model_name = None
    errors = [] # エラーログ収集用変数を初期化
    try:
        # 具体的なモデル名の候補（優先度順）
        # APIによっては "models/" プレフィックスが必要な場合があるため両方用意
        candidates = [
            "gemini-1.5-flash", "models/gemini-1.5-flash",
            "gemini-1.5-flash-001", "models/gemini-1.5-flash-001",
            "gemini-1.5-flash-latest", "models/gemini-1.5-flash-latest",
            "gemini-pro", "models/gemini-pro",
            "gemini-1.5-pro", "models/gemini-1.5-pro" 
        ]
        
        # 1. まずは候補リストを順に試す（これが一番速い）
        for cand in candidates:
            try:
                model = genai.GenerativeModel(model_name=cand, system_instruction=SYSTEM_INSTRUCTION)
                # テスト呼び出し（実際に通るか確認）ではなく、まずは生成を試みる
                response = model.generate_content(user_prompt)
                return response.text
            except Exception as e:
                errors.append((cand, str(e)))
                continue

        # 2. 全滅した場合、サーバーからリストを取得して使えるものを探す
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    try:
                        model = genai.GenerativeModel(model_name=m.name, system_instruction=SYSTEM_INSTRUCTION)
                        response = model.generate_content(user_prompt)
                        return response.text
                    except Exception as e:
                        errors.append((m.name, str(e)))
                        continue
        
    except Exception as e:
        return f"Error: 生成準備中に予期せぬエラーが発生しました: {str(e)}"

    # ここまで来てしまった場合（全滅）
    # エラーの詳細を表示してデバッグしやすくする
    error_details = "\\n".join([f"- {m}: {err}" for m, err in errors[:3]])
    return f"""Error: 利用可能なGeminiモデルが見つかりませんでした。
APIキーが「Gemini API」を利用できる権限を持っていない可能性があります（デフォルトキーなど）。
Google AI Studioで「Create API key」ボタンから **新しいキーを作成** して試してください。

[発生したエラー詳細]
{error_details}
...
"""
