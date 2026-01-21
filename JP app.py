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
# 1. 資産データベース (13銘柄・理想の買値・目標)
# ==========================================
DAILY_DATE = "2026/01/21" 
BEST_5_LIST = ["6857.T", "3778.T", "9984.T", "6861.T", "6501.T"]

CORE_DB = {
    "6857.T": {"名": "アドバンテスト", "買値": [9000, 10000], "目標": 15500, "判断": "強気", "メモ": "AIテスター需要は盤石。"},
    "3778.T": {"名": "さくらインターネット", "買値": [4200, 4800], "目標": 12000, "判断": "押し目待ち", "メモ": "国産クラウド。"},
    "9984.T": {"名": "ソフトバンクG", "買値": [8500, 9500], "目標": 16000, "判断": "継続保有", "メモ": "ARMとAI投資のハブ。"},
    "6861.T": {"名": "キーエンス", "買値": [65000, 68000], "目標": 85000, "判断": "優良", "メモ": "自動化の王。"},
    "6501.T": {"名": "日立製作所", "買値": [3800, 4100], "目標": 6000, "判断": "DX成長", "メモ": "インフラDXの覇者。"},
    "8035.T": {"名": "東京エレクトロン", "買値": [22000, 25000], "目標": 38000, "判断": "強気", "メモ": "製造装置世界大手。"},
    "4180.T": {"名": "Appier Group", "買値": [1300, 1500], "目標": 2500, "判断": "打診買い", "メモ": "AI SaaSの成長。"},
    "3993.T": {"名": "PKSHA Tech", "買値": [3800, 4200], "目標": 6800, "判断": "監視継続", "メモ": "法人向けAI実装。"},
    "6723.T": {"名": "ルネサス", "買値": [2200, 2400], "目標": 4200, "判断": "押し目買い", "メモ": "エッジAIチップ。"},
    "2638.T": {"名": "GX 日本ロボAI", "買値": [2300, 2500], "目標": 3500, "判断": "積立推奨", "メモ": "セクター全体。"},
    "6954.T": {"名": "ファナック", "買値": [4000, 4300], "目標": 6200, "判断": "回復期待", "メモ": "産業用ロボ大手。"},
    "4063.T": {"名": "信越化学", "買値": [5800, 6200], "目標": 8800, "判断": "鉄板銘柄", "メモ": "ウエハ世界一。"},
    "8058.T": {"名": "三菱商事", "買値": [2800, 3100], "目標": 4500, "判断": "高配当維持", "メモ": "資源・AIインフラ。"}
}

# ==========================================
# 2. データ取得ロジック
# ==========================================
@st.cache_data(ttl=60)
def get_all_data():
    # 指数
    idx_map = {"^N225": "日経平均", "^TPX": "TOPIX", "^MOTH": "グロース250"}
    indices = []
    for t, n in idx_map.items():
        try:
            h = yf.Ticker(t).history(period="2d")
            c = h['Close'].iloc[-1]
            p = h['Close'].iloc[-2]
            indices.append({"名": n, "値": c, "変": c-p, "率": ((c-p)/p)*100})
        except: pass

    # 銘柄
    rows = []
    for ticker, info in CORE_DB.items():
        try:
            curr = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            # 判定ロジック
            if curr <= info["買値"][1]: status = "🔥 理想の買値"
            elif curr <= (info["買値"][1] * 1.1): status = "👀 押し目待ち"
            else: status = "⏳ 高値警戒"
            
            rows.append({
                "コード": ticker, "銘柄名": info["名"], "現在値": curr,
                "理想の買値": f"{info['買値'][0]:,}〜{info['買値'][1]:,}",
                "判定": status, "判断": info["判断"], "2026目標": info["目標"]
            })
        except: pass
    return indices, pd.DataFrame(rows)

# ==========================================
# 3. 画面描画
# ==========================================
st.title("🇯🇵 2026 日本コア資産 統合戦情室")
index_data, df_stocks = get_all_data()

# 主要指数表示 (エラー対策済み)
if index_data:
    cols = st.columns(len(index_data))
    for i, idx in enumerate(index_data):
        cols[i].metric(idx['名'], f"{idx['値']:,.2f}", f"{idx['変']:+.2f} ({idx['率']:+.2f}%)")

st.divider()

# ベスト5表示
st.subheader("🚀 2026年 厳選ベスト5")
if not df_stocks.empty:
    b5_cols = st.columns(5)
    df_b5 = df_stocks[df_stocks['コード'].isin(BEST_5_LIST)]
    for i, ticker in enumerate(BEST_5_LIST):
        row = df_b5[df_b5['コード'] == ticker]
        if not row.empty:
            with b5_cols[i]:
                st.info(f"**{row['銘柄名'].values[0]}**")
                st.markdown(f"**{int(row['現在値'].values[0]):,}** 円")
                st.caption(f"判定: {row['判定'].values[0]}")

st.divider()

# 全銘柄リスト
st.subheader(f"📋 全資産監視ボード ({DAILY_DATE} 更新)")
if not df_stocks.empty:
    df_disp = df_stocks.copy()
    # 整数化とカンマ区切り (image_1fbea0の修正)
    df_disp['現在値'] = df_disp['現在値'].apply(lambda x: f"{int(x):,}")
    df_disp['2026目標'] = df_disp['2026目標'].apply(lambda x: f"{int(x):,}")
    
    # 判定色分け
    def style_status(val):
        color = 'red' if '買値' in val else 'orange' if '押し目' in val else 'gray'
        return f'color: {color}; font-weight: bold'

    st.dataframe(df_disp.style.applymap(style_status, subset=['判定']), use_container_width=True, hide_index=True)

with st.sidebar:
    if st.button("🔄 最新データを取得"):
        st.cache_data.clear()
        st.rerun()
