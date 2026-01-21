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
st.set_page_config(page_title="2026 日本AI株 リアルタイム戦情室", layout="wide")

# ==========================================
# 1. 日本AIコア資産データベース (2026年ターゲット)
# ==========================================
JP_AI_DATABASE = {
    "6857.T": {"股名": "アドバンテスト", "区間": [9000, 10000], "目標": 15500, "動態": "AIテスター需要独占。Nvidia関連の筆頭株。"},
    "3778.T": {"股名": "さくらインターネット", "区間": [4200, 4800], "目標": 12000, "動態": "国産クラウド。経産省支援のGPU基盤が2026年にフル稼働。"},
    "9984.T": {"股名": "ソフトバンクG", "区間": [8500, 9500], "目標": 16000, "動態": "ARM上場益とOpenAI提携。AI投資のハブ。"},
    "4180.T": {"股名": "Appier Group", "区間": [1300, 1500], "目標": 2500, "動態": "アジア展開のAI SaaS。収益化フェーズへ突入。"},
    "3993.T": {"股名": "PKSHA Tech", "区間": [3800, 4200], "目標": 6800, "動態": "日本企業のAI実装。アルゴリズムライセンスが伸長。"},
    "8035.T": {"股名": "東京エレクトロン", "区間": [22000, 25000], "目標": 38000, "動態": "次世代メモリ(HBM)用製造装置で圧倒的シェア。"},
    "6723.T": {"股名": "ルネサス", "区間": [2200, 2400], "目標": 4200, "動態": "エッジAIチップ。車載・産業用AIでの復権に期待。"},
    "2638.T": {"股名": "GX 日本ロボAI", "区間": [2300, 2500], "目標": 3500, "動態": "日本のAI・ロボ銘柄を網羅。低リスクな選択肢。"}
}

# ==========================================
# 2. データの取得ロジック
# ==========================================
def get_japan_market_data():
    idx_val, chg, pct = None, 0.0, 0.0
    try:
        # 日経平均（リアルタイム性の高い指数）
        n225 = yf.Ticker("^N225")
        hist_idx = n225.history(period="2d")
        if not hist_idx.empty:
            idx_val = hist_idx['Close'].iloc[-1]
            prev_idx = hist_idx['Close'].iloc[-2]
            chg = idx_val - prev_idx
            pct = (chg / prev_idx) * 100
    except: pass

    rows = []
    for ticker, info in JP_AI_DATABASE.items():
        try:
            s_obj = yf.Ticker(ticker)
            # 最新の1日のデータを取得
            hist = s_obj.history(period="1d")
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                upside = ((info["目標"] / curr) - 1) * 100
                
                # 判定
                if curr <= info["区間"][1]: status = "🔥 買い場到来"
                elif curr <= (info["区間"][1] * 1.1): status = "👀 押し目待ち"
                else: status = "⏳ 様子見(高値)"
                    
                rows.append({
                    "コード": ticker, "銘柄名": info["股名"], "現在値": round(curr, 0),
                    "目標買値": f"{info['区間'][0]}~{info['区間'][1]}",
                    "ステータス": status, "2026目標": info["目標"],
                    "上昇期待": round(upside, 1), "分析": info["動態"]
                })
        except: continue
    return idx_val, chg, pct, pd.DataFrame(rows)

# ==========================================
# 3. メイン画面の構築
# ==========================================
st.title("🇯🇵 2026 日本AI株 リアルタイム監視戦情室")

# サイドバー設定
with st.sidebar:
    st.header("⚡ ライブ更新設定")
    live_mode = st.checkbox("自動更新モードを有効化", value=False)
    refresh_rate = st.slider("更新間隔 (秒)", 30, 300, 60)
    
    st.divider()
    if st.button("🔄 手動更新"):
        st.cache_data.clear()
        st.rerun()

# データ取得
idx_val, chg, pct, df_main = get_japan_market_data()
now_str = datetime.now(jp_tz).strftime('%Y-%m-%d %H:%M:%S')

# 市場サマリー
col_m1, col_m2 = st.columns([2, 1])
with col_m1:
    if idx_val:
        st.metric(f"日経平均株価 ({now_str})", f"{idx_val:,.2f} JPY", f"{chg:+.2f} ({pct:+.2f}%)")
with col_m2:
    if live_mode:
        st.success(f"🟢 ライブ監視中: {refresh_rate}秒毎に更新")
    else:
        st.info("⚪ 静止モード: 手動で更新してください")

st.divider()

# 注目トップ3
st.subheader("🚀 2026年 ポテンシャルTOP3 (上昇余地順)")
if not df_main.empty:
    top_3 = df_main.sort_values("上昇期待", ascending=False).head(3)
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.metric(row['銘柄名'], f"{row['現在値']:,.0f}円", f"{row['上昇期待']}%")
            st.caption(f"🎯 目標: {row['2026目標']:,}円 | {row['ステータス']}")

st.divider()

# 全リスト
st.subheader("📋 日本AI銘柄 監視ボード")
if not df_main.empty:
    # 色分け用のスタイリング関数
    def highlight_status(val):
        color = 'red' if '買い場' in val else 'orange' if '押し目' in val else 'gray'
        return f'color: {color}; font-weight: bold'

    df_display = df_main.copy()
    df_display['上昇期待'] = df_display['上昇期待'].map("{:.1f}%".format)
    st.dataframe(df_display.style.applymap(highlight_status, subset=['ステータス']), use_container_width=True, hide_index=True)

# 投資アドバイス
with st.expander("💡 2026年に向けた投資戦略アドバイス"):
    st.markdown("""
    1. **時間分散**: 日本のAI株はボラティリティ（価格変動）が激しいため、一度に買わず、推奨区間で3〜4回に分けてエントリーするのが理想です。
    2. **為替の影響**: アドバンテストや東京エレクトロンは円安がプラスに働きますが、2026年に向けて円高が進む場合は、内需系のAppierやPKSHAの方が耐性がある可能性があります。
    3. **出口戦略**: 2026年の目標株価に達した際は、半分を利確し、残りをさらに長期（2030年）で保有する「恩株化」を検討してください。
    """)

# 自動更新の処理
if live_mode:
    time.sleep(refresh_rate)
    st.rerun()
