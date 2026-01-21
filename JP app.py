import streamlit as st
import pandas as pd
import yfinance as yf
import pytz
import time
from datetime import datetime

# ==========================================
# 0. システム設定
# ==========================================
jp_tz = pytz.timezone('Asia/Tokyo')
st.set_page_config(page_title="2026 日本コア資産 統合戦情室", layout="wide")

# ==========================================
# 1. 毎日更新：個別銘柄デイリー・レビュー (全13銘柄)
# ==========================================
# ここを毎日書き換えることで、ダッシュボードの内容がすべて更新されます。
DAILY_DATE = "2026/01/21" 
BEST_5_TICKERS = ["6857.T", "3778.T", "9984.T", "6861.T", "6501.T"]

DAILY_REVIEWS = {
    # 【ベスト5】
    "6857.T": {"状況": "堅調", "判断": "強気", "メモ": "AIテスター需要は2026年も盤石。Nvidiaの動向に連動。"},
    "3778.T": {"状況": "急騰中", "判断": "押し目待ち", "メモ": "政府支援のGPUセンターがフル稼働へ。ボラティリティ大。"},
    "9984.T": {"状況": "上放れ", "判断": "継続保有", "メモ": "ARM株が資産価値を牽引。OpenAI連携による日本市場支配。"},
    "6861.T": {"状況": "安定", "判断": "優良", "メモ": "工場の自動化需要は不変。押し目は長期投資の好機。"},
    "6501.T": {"状況": "ジリ高", "判断": "DX成長", "メモ": "Lumada事業が収益の柱。社会インフラDXの覇者。"},
    # 【その他コア資産】
    "8035.T": {"状況": "反発", "判断": "強気", "メモ": "次世代半導体製造装置で世界シェア堅持。期待大。"},
    "4180.T": {"状況": "底練り", "判断": "打診買い", "メモ": "AI SaaSの収益化フェーズ。1,500円以下は割安圏。"},
    "3993.T": {"状況": "調整中", "判断": "監視継続", "メモ": "法人向けAI実装のパイオニア。次の決算で成長性を再確認。"},
    "6723.T": {"状況": "割安", "判断": "押し目買い", "メモ": "エッジAIチップで存在感。PER的にかなり放置されている。"},
    "2638.T": {"状況": "安定", "判断": "積立推奨", "メモ": "日本AI・ロボット全体に分散。初心者から上級者まで。"},
    "6954.T": {"状況": "底入れ", "判断": "回復期待", "メモ": "産業用ロボットの在庫調整が完了間近。2026年に期待。"},
    "4063.T": {"状況": "堅実", "判断": "鉄板銘柄", "メモ": "ウエハシェア世界一。AI社会の土台を支える最強の素材。"},
    "8058.T": {"状況": "高配当", "判断": "継続保有", "メモ": "電力・資源・AIインフラ投資を網羅。ディフェンシブに最適。"}
}

# ==========================================
# 2. データの取得ロジック (指数 + 個別銘柄)
# ==========================================
def get_comprehensive_data():
    # --- 市場指数の取得 ---
    indices = {"^N225": "日経平均", "^TPX": "TOPIX", "^MOTH": "グロース250"}
    index_results = []
    for ticker, name in indices.items():
        try:
            obj = yf.Ticker(ticker)
            h = obj.history(period="2d")
            curr = h['Close'].iloc[-1]
            chg = curr - h['Close'].iloc[-2]
            pct = (chg / h['Close'].iloc[-2]) * 100
            index_results.append({"名": name, "値": curr, "変": chg, "率": pct})
        except: pass

    # --- 個別銘柄の取得 ---
    CORE_DATABASE = {
        "6857.T": {"名": "アドバンテスト", "目標": 15500},
        "3778.T": {"名": "さくらインターネット", "目標": 12000},
        "9984.T": {"名": "ソフトバンクG", "目標": 16000},
        "4180.T": {"名": "Appier Group", "目標": 2500},
        "3993.T": {"名": "PKSHA Tech", "目標": 6800},
        "8035.T": {"名": "東京エレクトロン", "目標": 38000},
        "6723.T": {"名": "ルネサス", "目標": 4200},
        "2638.T": {"名": "GX 日本ロボAI", "目標": 3500},
        "6861.T": {"名": "キーエンス", "目標": 85000},
        "6954.T": {"名": "ファナック", "目標": 6200},
        "4063.T": {"名": "信越化学", "目標": 8800},
        "8058.T": {"名": "三菱商事", "目標": 4500},
        "6501.T": {"名": "日立製作所", "目標": 6000}
    }
    
    stock_rows = []
    for ticker, info in CORE_DATABASE.items():
        try:
            s_obj = yf.Ticker(ticker)
            hist = s_obj.history(period="1d")
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                upside = ((info["目標"] / curr) - 1) * 100
                stock_rows.append({
                    "コード": ticker, "銘柄名": info["名"], "現在値": curr,
                    "判断": DAILY_REVIEWS[ticker]["判断"],
                    "状況": DAILY_REVIEWS[ticker]["状況"],
                    "目標": info["目標"], "期待余地": upside,
                    "レビュー": DAILY_REVIEWS[ticker]["メモ"]
                })
        except: continue
    return index_results, pd.DataFrame(stock_rows)

# ==========================================
# 3. UI 描画
# ==========================================
index_data, df_stocks = get_comprehensive_data()

# --- セクション1: 市場主要指数 ---
st.subheader("🌐 日本市場・主要指数")
idx_cols = st.columns(3)
for i, idx in enumerate(index_data):
    with idx_cols[i]:
        st.metric(idx['名'], f"{idx['値']:,.2f}", f"{idx['変']:+.2f} ({idx['率']:+.2f}%)")

st.divider()

# --- セクション2: 厳選ベスト5 (重点監視) ---
st.subheader("🔥 2026年 厳選ベスト5")
b5_cols = st.columns(5)
df_b5 = df_stocks[df_stocks['コード'].isin(BEST_5_TICKERS)]
for i, ticker in enumerate(BEST_5_TICKERS):
    row = df_b5[df_b5['コード'] == ticker]
    if not row.empty:
        with b5_cols[i]:
            st.info(f"**{row['銘柄名'].values[0]}**")
            # ゼロ消し整数表示
            st.markdown(f"**{int(row['現在値'].values[0]):,}** 円")
            st.caption(f"期待: {row['期待余地'].values[0]:.1f}%")
            st.caption(f"判断: {row['判断'].values[0]}")

st.divider()

# --- セクション3: 全13銘柄・詳細ボード ---
st.subheader(f"📋 全資産監視ボード ({DAILY_DATE} 更新)")
if not df_stocks.empty:
    df_display = df_stocks.copy()
    
    # 整形処理: 現在値と目標のゼロを消してカンマ区切りにする
    df_display['現在値'] = df_display['現在値'].apply(lambda x: f"{int(x):,}")
    df_display['目標'] = df_display['目標'].apply(lambda x: f"{int(x):,}")
    df_display['期待余地'] = df_display['期待余地'].map("{:.1f}%".format)
    
    # 表の表示
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# 専門家コメント（サイドバー）
with st.sidebar:
    st.header("📝 デイリー所感")
    st.write(f"日付: {DAILY_DATE}")
    st.markdown("""
    - **半導体関連**: Nvidiaの動向を受けアドバンテストと東京エレクトロンが牽引。
    - **AIインフラ**: さくらインターネットが国策支援で頭一つ抜ける。
    - **フィジカルAI**: キーエンスと日立が安定した推移。
    """)
    if st.button("🔄 データを更新"):
        st.cache_data.clear()
        st.rerun()
