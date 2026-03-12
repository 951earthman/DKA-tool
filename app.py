import streamlit as st

# 設定網頁標題與排版
st.set_page_config(page_title="急診 DKA/HHS 導航系統", layout="centered")

st.title("🚨 急診 DKA/HHS 動態導航系統")
st.markdown("**配方標準：Apidra 100U + 0.9% N/S 100mL (1 U/mL = 1 mL/hr = 1 U/hr)**")

# --- 階段一：初始評估 ---
st.header("Phase 1: 初始給藥與點滴評估")
col1, col2 = st.columns(2)

with col1:
    weight = st.number_input("病患體重 (kg)", min_value=30.0, max_value=200.0, value=60.0, step=1.0)
    init_gluc = st.number_input("初始指尖血糖 (mg/dL)", min_value=50, max_value=1500, value=400, step=10)

with col2:
    init_k = st.number_input("初始血鉀 K+ (mEq/L)", min_value=1.0, max_value=10.0, value=4.0, step=0.1)
    init_na = st.number_input("初始測量血鈉 Na+ (mEq/L)", min_value=100, max_value=200, value=135, step=1)

if st.button("計算 Phase 1 初始醫囑", type="primary"):
    st.divider()
    
    # 1. 血鉀 Hard Stop 邏輯
    st.subheader("🛑 1. 血鉀檢核 (Hard Stop)")
    if init_k < 3.3:
        st.error(f"絕對禁忌：血鉀 {init_k} < 3.3！\n\n禁止啟動 Insulin！請先由靜脈補充 KCl 20-30 mEq/hr，直到 K+ >= 3.3。")
    elif 3.3 <= init_k <= 5.3:
        st.success(f"血鉀 {init_k}：安全範圍。\n\n允許啟動 Insulin。點滴中需加入 KCl 20-30 mEq/L (目標維持 4-5)。")
    else:
        st.warning(f"血鉀 {init_k} (> 5.3)：偏高。\n\n允許啟動 Insulin。點滴暫不加鉀，請 Q2H 追蹤。")

    # 2. 校正血鈉與點滴選擇
    st.subheader("💧 2. 維持輸液選擇 (第2小時起)")
    corr_na = init_na + 1.6 * ((init_gluc - 100) / 100)
    st.info(f"計算出「校正血鈉」為：**{corr_na:.1f} mEq/L**")
    
    if corr_na >= 135:
        st.warning("👉 判斷：病患極度缺乏游離水。\n\n處置：請改掛 **0.45% Saline (低張鹽水)** 250-500 mL/hr。")
    else:
        st.success("👉 判斷：病患嚴重缺鈉。\n\n處置：請續掛 **0.9% Normal Saline (等張鹽水)** 250-500 mL/hr。")

    # 3. 初始 Insulin 劑量
    st.subheader("💉 3. Insulin 初始給藥")
    if init_k >= 3.3:
        bolus = weight * 0.1
        rate = weight * 0.1
        st.info(f"1. **IV Bolus**: 給予 **{bolus:.1f} U** (IV stat)\n2. **Pump 起始速率**: 設定為 **{rate:.1f} mL/hr**")

st.divider()

# --- 階段二：動態滴定 ---
st.header("Phase 2: Q1H Pump 動態滴數調整")
col3, col4 = st.columns(2)

with col3:
    old_gluc = st.number_input("前一小時血糖 (mg/dL)", min_value=20, max_value=1500, value=300, step=10)
    new_gluc = st.number_input("最新指尖血糖 (mg/dL)", min_value=20, max_value=1500, value=250, step=10)

with col4:
    current_rate = st.number_input("目前 Pump 速率 (mL/hr)", min_value=0.0, max_value=50.0, value=6.0, step=0.5)

if st.button("計算 Phase 2 最新滴數", type="primary"):
    st.divider()
    
    # 危機處理：低血糖
    if new_gluc < 70:
        st.error("🆘 **嚴重低血糖！**\n\n立刻關閉 Pump！給予 D50W 2 amp (40mL) IV stat，並改為 Q15min 測量血糖。")
    
    # 防護轉換期：血糖 <= 200
    elif new_gluc <= 200:
        half_rate = current_rate / 2
        min_rate = weight * 0.02
        max_rate = weight * 0.05
        
        st.error(f"🚨 **關鍵防護轉換期**：血糖已達 {new_gluc} mg/dL！\n\n為防止飢餓性酮酸中毒，必須**立刻同時**執行以下兩項：")
        st.warning("1. **加糖**：維持點滴立即換成 **D5W + 0.45% Saline** (150-250 mL/hr)。")
        st.warning(f"2. **降速**：Pump 速率直接減半為 **{half_rate:.1f} mL/hr** (或設定在 {min_rate:.1f} - {max_rate:.1f} 之間)。")
        st.info("🎯 後續目標：持續微調點滴與 Pump，將血糖鎖定在 150-200 之間，直到 DKA 緩解。")
        
    # 正常動態調整
    else:
        drop = old_gluc - new_gluc
        adjust = weight * 0.05
        
        st.write(f"過去一小時血糖降幅：**{drop:.0f} mg/dL**")
        
        if drop < 50:
            new_rate = current_rate + adjust
            st.warning(f"📉 **降幅 < 50 (降太慢)**：\n\n👉 處置：Pump 速率調升 **+{adjust:.1f}**\n\n🎯 **新滴數設定：{new_rate:.1f} mL/hr**")
        elif 50 <= drop <= 75:
            st.success(f"✨ **降幅 50-75 (完美達標)**：\n\n👉 處置：維持原速率不變\n\n🎯 **新滴數設定：{current_rate:.1f} mL/hr**")
        else:
            new_rate = max(0, current_rate - adjust)
            st.warning(f"📉 **降幅 > 75 (降太快)**：\n\n👉 處置：Pump 速率調降 **-{adjust:.1f}**\n\n🎯 **新滴數設定：{new_rate:.1f} mL/hr**")
