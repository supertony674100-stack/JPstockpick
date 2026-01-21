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
st.set_page_config(page_title="2026 日本コア資産 リアルタイム監視", layout="wide")

# ==========================================
# 1. 毎日更新：専門家レビュー (13銘柄分)
# ==========================================
DAILY_DATE = "2026/01/21" 
BEST_5_TICKERS = ["6857.T", "3778.T", "9984.T", "6861.T", "6501.T"]

DAILY_REVIEWS = {
    "6857.T": {"レビュー": "AIテスター需要は盤石。1万円が強力な支持線。", "判断": "強気"},
    "3778.T": {"レビュー": "国産クラウド。GPU増設ニュースに敏感に反応中。", "判断": "押し目買い"},
    "9984.T": {"レビュー": "ARM株絶好調。AI投資のハブとして価値増大。", "判断": "継続保有"},
    "4180.T": {"レビュー": "SaaS収益化が進展。底値圏からの反発狙い。", "判断": "打診買い"},
    "3993.T": {"レビュー": "アルゴリズムライセンス拡大。長期成長継続。", "判断": "監視継続"},
    "8035.T": {"レビュー": "HBM装置で優位性。サイクル中間期として良好。", "判断": "強気"},
    "6723.T": {"レビュー": "エッジAI採用増。バリュエーション的に割安。", "判断": "押し目買い"},
    "2638.T": {"レビュー": "リスクを抑えつつAI成長を取る最良のETF。", "判断": "積立推奨"},
    "6861.T": {"レビュー": "自動化の王。高利益率は驚異。長期保有鉄板。", "判断": "優良"},
    "6954.T": {"レビュー": "フィジカルAI大手。景気回復待ちの段階。", "判断": "回復期待"},
    "4063.T": {"レビュー": "ウエハ世界首位。圧倒的財務基盤と供給力。", "判断": "鉄板銘柄"},
    "8058.T": {"レビュー": "データセンター向け電力供給で重要役割。", "判断": "高配当維持"},
    "6501.T": {"レビュー": "インフラDXの覇者。2026年も盤石。", "判断": "DX成長"}
}

# ==========================================
# 2. データベース
# ==========================================
CORE_DATABASE = {
    "6857.T": {"股名": "アドバンテスト", "目標": 15500},
    "3778.T": {"股名": "さくらインターネット", "目標": 12000},
    "9984.T": {"股名": "ソフトバンクG", "目標": 16000},
    "4180.T": {"股名": "Appier Group", "目標": 2500},
    "3993.T": {"股名": "PKSHA Tech", "目標": 6800},
    "8035.T": {"股名": "東京エレクトロン", "目標": 38000},
    "6723.T": {"股名": "ルネサス", "目標": 4200},
    "2638.T": {"股名": "GX 日本ロボAI", "目標": 3500},
    "6861.T": {"股名": "キーエンス", "目標": 85000},
    "6954.T": {"股名": "ファナック", "目標": 6200},
    "4063.T": {"股名": "信越化学", "目標": 8800},
    "8058.T": {"股名": "三菱商事", "目標": 4500},
    "6501.T": {"股名": "日立製作所", "目標": 6000}
}

@st.cache_data(ttl=60)
def get_market_data():
    rows = []
    for ticker, info in CORE_DATABASE.items():
        try:
            s_obj = yf.Ticker(ticker)
            hist = s_obj.history(period="1d")
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                upside = ((info["目標"] / curr) - 1) * 100
                rows.append({
                    "コード": ticker, "銘柄名": info["股名"], "現在値": curr,
                    "判断": DAILY_REVIEWS[ticker]["判断"],
                    "目標": info["目標"], "期待余地": round(upside, 1)
                })
        except: continue
    return pd.DataFrame(rows)

# ==========================================
# 3. UI 描画
# ==========================================
st.title("🇯🇵 2026 日本コア資産・戦情室")
df_main = get_market_data()

# --- 強調表示：ベスト5 ---
st.subheader("🔥 2026年 厳選ベスト5 (重点監視)")
cols = st.columns(5)
best_5_df = df_main[df_main['コード'].isin(BEST_5_TICKERS)]

for i, ticker in enumerate(BEST_5_TICKERS):
    row = best_5_df[best_5_df['コード'] == ticker]
    if not row.empty:
        with cols[i]:
            st.metric(row['銘柄名'].values[0], f"{int(row['現在値'].values[0]):,}円", f"{row['期待余地'].values[0]}%")
            st.caption(f"判断: {row['判断'].values[0]}")

st.divider()

# --- 全リスト ---
st.subheader("📋 日本コア資産 監視ボード (全13銘柄)")
if not df_main.empty:
    df_display = df_main.copy()
    # ゼロ消し & カンマ区切り
    df_display['現在値'] = df_display['現在値'].apply(lambda x: f"{int(x):,}")
    df_display['目標'] = df_display['目標'].apply(lambda x: f"{int(x):,}")
    df_display['期待余地'] = df_display['期待余地'].map("{:.1f}%".format)
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# サイドバー
with st.sidebar:
    st.write(f"📅 更新日: {DAILY_DATE}")
    if st.button("🔄 今すぐ更新"):
        st.cache_data.clear()
        st.rerun()
