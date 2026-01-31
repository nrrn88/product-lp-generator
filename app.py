import streamlit as st
import scraper
import importlib
import prompts
importlib.reload(prompts) # モジュールの変更を強制的に反映
import os
import re
import json
from datetime import datetime

# ページ設定
st.set_page_config(
    page_title="商品LP自動生成ツール (SEO/AIO強化版)",
    page_icon="💊",
    layout="wide"
)

# タイトルと説明
st.title("💊 医薬品EC 商品詳細ページ自動生成ツール")
st.markdown("""
競合サイトのURLを入力して、SEO・AIO（AI Overview）に最適化された商品ページHTMLを自動生成します。
""")

# APIキー入力（メインエリアに移動）
st.info("👇 ここに先ほどコピーした「APIキー」を貼り付けてください")
api_key = st.text_input("Gemini API Key", type="password", help="Google AI Studioで取得したAPIキーを入力してください")
if not api_key:
    st.warning("⚠️ APIキーが入力されていません")
else:
    st.success("APIキーが設定されました！")

    st.markdown("---")
    
    st.caption("🤖 モデル設定")
    # テキスト生成モデルの選択
    text_model = st.selectbox(
        "テキスト生成モデル",
        options=[
            "gemini-3-pro-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro-002"
        ],
        index=0,
        help="HTMLとコンテンツ生成に使用するモデル"
    )
    





st.markdown("---")

def parse_generated_content(text):
    """
    生成されたテキストから各セクションを抽出する
    """
    # エラーチェック
    if text.startswith("Error:"):
        return {"error": text}

    sections = {}
    
    # 正規表現でタグの中身を抽出
    patterns = {
        "metadata": r"<metadata>(.*?)</metadata>",
        "html_content": r"<html_content>(.*?)</html_content>",
        "reviews": r"<reviews>(.*?)</reviews>",
        "references": r"<references>(.*?)</references>"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            sections[key] = match.group(1).strip()
        else:
            sections[key] = ""
            
    return sections

# メインエリア
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 情報入力")
    
    product_name = st.text_input("商品名", placeholder="例: アナドリン")
    
    target_urls = st.text_area(
        "参考にする競合URL (複数可)", 
        height=150, 
        placeholder="https://example.com/product/a\nhttps://competitor.com/item/b"
    )
    
    additional_info = st.text_area("特記事項 (任意)", placeholder="例: 成分量は50mgです。配送は1週間程度です。")

    if st.button("🚀 ページを生成する", type="primary", disabled=not api_key):
        if not product_name or not target_urls:
            st.error("商品名とURLは必須です。")
        else:
            with st.status("処理を実行中...", expanded=True) as status:
                # 1. スクレイピング
                st.write("🌐 競合サイトから情報を収集中...")
                scrape_results = scraper.scrape_multiple_urls(target_urls)
                
                # コンテキストの作成
                context_text = ""
                for res in scrape_results:
                    if "error" in res:
                        st.warning(f"取得失敗: {res['url']} ({res['error']})")
                    else:
                        st.success(f"取得成功: {res['title']}")
                        context_text += f"\n--- Source: {res['url']} ---\nTitle: {res['title']}\nContent: {res['content']}\n"
                
                if additional_info:
                    context_text += f"\n--- User Note ---\n{additional_info}\n"

                # 2. AI生成
                st.write(f"🧠 AI ({text_model}) が構成とコンテンツを生成中 (SEO/AIO対策)...")
                raw_response = prompts.generate_content(api_key, context_text, product_name, text_model)
                
                st.session_state['raw_response'] = raw_response
                st.session_state['product_name'] = product_name
                
                status.update(label="完了!", state="complete", expanded=False)

with col2:
    st.subheader("2. プレビュー & 出力")
    
    if 'raw_response' in st.session_state:
        raw_text = st.session_state['raw_response']
        parsed_data = parse_generated_content(raw_text)
        
        # エラー判定
        if "error" in parsed_data:
            st.error(parsed_data["error"])
        else:
            # タブで表示切り替え
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🖼️ プレビュー", "📝 HTML", "⚙️ メタデータ", "⭐ レビュー", "🔗 参考リンク"])
            
            html_content = parsed_data.get("html_content", "")
            
            with tab1:
                st.caption("※スタイルは簡易的なものです。")
                if html_content:
                    # プレビュー用に背景色を白に固定するラッパーを追加
                    preview_html = f"""
                    <div style="background-color: #ffffff; color: #333333; padding: 20px; border-radius: 5px;">
                        {html_content}
                    </div>
                    """
                    st.components.v1.html(preview_html, height=600, scrolling=True)
                else:
                    st.warning("HTMLコンテンツが見つかりませんでした。")
            
            with tab2:
                st.text_area("HTML Source", html_content, height=400)
                
                # ダウンロードボタン
                file_name = f"{product_name}_{datetime.now().strftime('%Y%m%d')}.html"
                st.download_button(
                    label="💾 HTMLファイルをダウンロード",
                    data=html_content,
                    file_name=file_name,
                    mime="text/html"
                )
            
            with tab3:
                metadata_text = parsed_data.get("metadata", "")
                
                # タイトルとディスクリプション、H1を抽出
                title_match = re.search(r"Recommended Title:\s*(.*)", metadata_text)
                h1_match = re.search(r"Recommended H1:\s*(.*)", metadata_text)
                desc_match = re.search(r"Recommended Description:\s*(.*)", metadata_text)
                
                rec_title = title_match.group(1).strip() if title_match else ""
                rec_h1 = h1_match.group(1).strip() if h1_match else ""
                rec_desc = desc_match.group(1).strip() if desc_match else ""

                st.subheader("推奨タイトル")
                st.code(rec_title, language=None)
                
                st.subheader("推奨H1")
                st.code(rec_h1, language=None)
                
                st.subheader("推奨ディスクリプション")
                st.code(rec_desc, language=None)
                
                st.markdown("---")
                st.subheader("推奨画像プロンプト")
                st.caption("以下のプロンプトを他の画像生成ツール（Midjourney、DALL-E3など）で使用してください。")

                st.caption("🎨 抽象イメージ (効果・悩み解決)")
                # プロンプト抽出はしていないので、metadata全体から参照するか、ユーザーにRawデータを見てもらう
                # ここでは簡易的に正規表現で再抽出する
                img_abstract_match = re.search(r"(?:-|\*)\s*(?:\*\*)?\[Abstract\](?:\*\*)?:?\s*(.*)", metadata_text, re.IGNORECASE)
                if img_abstract_match:
                    st.code(img_abstract_match.group(1).strip(), language=None)

                st.caption("😊 人物イメージ (信頼感・笑顔)")
                img_person_match = re.search(r"(?:-|\*)\s*(?:\*\*)?\[Person\](?:\*\*)?:?\s*(.*)", metadata_text, re.IGNORECASE)
                if img_person_match:
                    st.code(img_person_match.group(1).strip(), language=None)
                
                with st.expander("全てのメタデータ & 生データ"):
                    st.text_area("Raw Metadata", metadata_text, height=200)
                
            with tab4:
                reviews_text = parsed_data.get("reviews", "")
                st.caption("生成されたJSONデータ")
                st.code(reviews_text, language="json")
                
                # JSONパースを試みる
                try:
                    reviews_json = json.loads(reviews_text)
                    st.markdown("#### レビュープレビュー")
                    for rev in reviews_json:
                        with st.expander(f"{rev.get('rating', '5')}⭐ {rev.get('title', 'No Title')} ({rev.get('name', 'Anonymous')})"):
                            st.write(rev.get('body', ''))
                            st.caption(f"日付: {rev.get('date', '')}")
                except:
                    st.warning("レビューデータのJSONパースに失敗しました（形式が崩れている可能性があります）。")
            
            with tab5:
                ref_text = parsed_data.get("references", "")
                st.markdown(ref_text)
        

        


    else:
        st.info("左側のフォームに入力して生成ボタンを押してください。")

