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
# 1. 毎日更新：資産データベース (ここを毎日書き換えるだけでOK)
# ==========================================
DAILY_DATE = "2026/01/21" 
BEST_5_LIST = ["6857.T", "3778.T", "9984.T", "6861.T", "6501.T"]

# 全13銘柄のデータ (理想の買値・目標・日々のメモ)
CORE_DB = {
    "6857.T": {"名": "アドバンテスト", "買値": [9000, 10000], "目標": 15500, "状況": "堅調", "判断": "強気", "メモ": "AIテスター需要は2026年も盤石。Nvidia動向に連動。"},
    "3778.T": {"名": "さくらインターネット", "買値": [4200, 4800], "目標": 12000, "状況": "急騰中", "判断": "押し目待ち", "メモ": "政府支援のGPUセンターがフル稼働へ。"},
    "9984.T": {"名": "ソフトバンクG", "買値": [8500, 9500], "目標": 16000, "状況": "上放れ", "判断": "継続保有", "メモ": "ARM株が資産価値を牽引。"},
    "6861.T": {"名": "キーエンス", "買値": [65000, 68000], "目標": 85000, "状況": "安定", "判断": "優良", "メモ": "工場の自動化需要は不変。押し目は好機。"},
    "6501.T": {"名": "日立製作所", "買値": [3800, 4100], "目標": 6000, "状況": "ジリ高", "判断": "DX成長", "メモ": "Lumada事業が収益の柱。"},
    "8035.T": {"名": "東京エレクトロン", "買値": [22000, 25000], "目標": 38000, "状況": "反発", "判断": "強気", "メモ": "次世代半導体製造装置で世界シェア堅持。"},
    "4180.T": {"名": "Appier Group", "買値": [1300, 1500], "目標": 2500, "状況": "底練り", "判断": "打診買い", "メモ": "AI SaaSの収益化フェーズ。1,500円以下は割安。"},
    "3993.T": {"名": "PKSHA Tech", "買値": [3800, 4200], "目標": 6800, "状況": "調整中", "判断": "監視継続", "メモ": "法人向けAI実装。次の決算で成長性を確認。"},
    "6723.T": {"名": "ルネサス", "買値": [2200, 2400], "目標": 4200, "状況": "割安", "判断": "押し目買い", "メモ": "エッジAIチップで存在感。"},
    "2638.T": {"名": "GX 日本ロボAI", "買値": [2300, 2500], "目標": 3500, "状況": "安定", "判断": "積立推奨", "メモ": "日本AI・ロボット全体に分散。"},
    "6954.T": {"名": "ファナック", "買値": [4000, 4300], "目標": 6200, "状況": "底入れ", "判断": "回復期待", "メモ": "産業用ロボットの在庫調整が完了間近。"},
    "4063.T": {"名": "信越化学", "買値": [5800, 6200], "目標": 8800, "状況": "堅実", "判断": "鉄板銘柄", "メモ": "ウエハシェア世界一。AI社会の土台。"},
    "8058.T": {"名": "三菱商事", "買値": [2800, 3100], "目標": 4500, "状況": "高配当", "判断": "継続保有", "メモ": "電力・資源・AIインフラ投資を網羅。"}
}

# ==========================================
# 2. データ取得関数
# ==========================================
def get_data():
    # 指数データ
    indices = {"^N225": "日経平均", "^TPX": "TOPIX", "^MOTH": "グロース250"}
    idx_res = []
    for ticker, name in indices.items():
        try:
            h = yf.Ticker(ticker).history(period="2d")
            curr = h['Close'].iloc[-1]
            chg = curr - h['Close'].iloc[-2]
            idx_res.append({"名": name, "値": curr, "変": chg, "率": (chg/h['Close'].iloc[-2])*100})
        except: pass

    # 個別銘柄データ
    rows = []
    for ticker, info in CORE_DB.items():
        try:
            curr = yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
            upside = ((info["目標"] / curr) - 1) * 100
            
            # エントリー判定
            if curr <= info["買値"][1]: status = "🔥 理想の買値"
            elif curr <= (info["買値"][1] * 1.1): status = "👀 押し目待ち"
            else: status = "⏳ 高値警戒"

            rows.append({
                "コード": ticker, "銘柄名": info["名"], "現在値": curr,
                "判定": status, "判断": info["判断"], "目標": info["目標"],
                "期待余地": f"{upside:.1f}%", "レビュー": info["メモ"]
            })
        except: continue
    return idx_res, pd.DataFrame(rows)

# ==========================================
# 3. UI 描画
# ==========================================
index_data, df_stocks = get_data()

st.title("🇯🇵 2026 日本コア資産 統合戦情室")

# 市場指数
idx_cols = st.columns(len(index_data))
for i, idx in enumerate(index_data):
    idx_cols[i].metric(idx['名'], f"{idx['値']:,.2f}", f"{idx['変']:+.2f} ({idx['率']:+.2f}%)")

st.divider()

# ベスト5
st.subheader("🚀 2026年 厳選ベスト5")
b5_cols = st.columns(5)
df_b5 = df_stocks[df_stocks['コード'].isin(BEST_5_LIST)]
for i, ticker in enumerate(BEST_5_LIST):
    row = df_b5[df_b5['コード'] == ticker]
    if not row.empty:
        with b5_cols[i]:
            st.info(f"**{row['銘柄名'].values[0]}**")
            # 整数化して .000000 を消去
            st.markdown(f"**{int(row['現在値'].values[0]):,}** 円")
            st.caption(f"判定: {row['判定'].values[0]}")

st.divider()

# 全リスト
st.subheader(f"📋 全資産リスト ({DAILY_DATE} 更新)")
if not df_stocks.empty:
    df_disp = df_stocks.copy()
    # 表示用に現在値と目標のゼロを消してカンマ区切りにする
    df_disp['現在値'] = df_disp['現在値'].apply(lambda x: f"{int(x):,}")
    df_disp['目標'] = df_disp['目標'].apply(lambda x: f"{int(x):,}")
    
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

with st.sidebar:
    if st.button("🔄 データを更新"):
        st.cache_data.clear()
        st.rerun()
