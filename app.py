import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os

# ----------------- 配置 -----------------
ETF_CODES = [
    "510050", "510180", "510300", "510500", "510880",
    "510980", "510310", "510060", "510170", "510030"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.sse.com.cn/"
}

st.set_page_config(page_title="ETF份额爬取工具", layout="wide")
st.title("📊 上交所ETF基金份额历史数据爬取")
st.markdown("支持：510050/510180/510300/510500/510880/510980/510310/510060/510170/510030")

# 日期选择
start_date = st.date_input("开始日期", value=datetime(2024, 1, 1))
end_date = st.date_input("结束日期", value=datetime.today())

START = str(start_date)
END = str(end_date)

# 爬取函数
def fetch_etf(code):
    try:
        url = f"https://query.sse.com.cn/security/etf/etfBasicInfo.do?jsonCallBack=&fundId={code}"
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()
        df = pd.DataFrame(data["result"])
        df.columns = ["日期", "基金代码", "基金简称", "基金份额(万份)"]
        df["日期"] = pd.to_datetime(df["日期"])
        df["基金份额(万份)"] = pd.to_numeric(df["基金份额(万份)"])
        df = df[(df["日期"] >= START) & (df["日期"] <= END)]
        return df.sort_values("日期").reset_index(drop=True)
    except:
        return None

# 运行按钮
if st.button("🚀 开始爬取数据"):
    st.info("正在从 上海证券交易所 爬取数据...")
    
    all_data = []
    progress = st.progress(0)
    
    for i, code in enumerate(ETF_CODES):
        df = fetch_etf(code)
        if df is not None and not df.empty:
            all_data.append(df)
        progress.progress((i+1)/len(ETF_CODES))
        time.sleep(0.7)
    
    if all_data:
        final = pd.concat(all_data, ignore_index=True)
        st.success(f"✅ 爬取完成！共 {len(final)} 条数据")
        st.dataframe(final, use_container_width=True)
        
        # 保存Excel
        os.makedirs("./data", exist_ok=True)
        fn = f"ETF份额_{START}_{END}.xlsx"
        with pd.ExcelWriter(f"./data/{fn}", engine="openpyxl") as w:
            final.to_excel(w, sheet_name="全部数据", index=False)
            for c in ETF_CODES:
                sub = final[final["基金代码"] == c]
                if not sub.empty:
                    sub.to_excel(w, sheet_name=c, index=False)
        
        # 下载按钮
        with open(f"./data/{fn}", "rb") as f:
                    st.download_button("📥 下载Excel文件", f, file_name=fn)
    else:
        st.error("❌ 未获取到数据")

st.markdown("---")
st.caption("数据来源：上海证券交易所官网 | 仅供学习使用")
