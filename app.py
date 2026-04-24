import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
import matplotlib

# Rendering fix for deployment
matplotlib.use('Agg') 

st.set_page_config(page_title="SafeClass AI Moderator", layout="wide")
st.title("🛡️ Context-Aware Content Moderation")
st.write("Developed by: **Asad Ullah & Ahmad Raza**")

# --- 1. FUZZY LOGIC SETUP ---
@st.cache_resource
def setup_system():
    severity = ctrl.Antecedent(np.arange(0, 11, 1), 'severity')
    reputation = ctrl.Antecedent(np.arange(0, 11, 1), 'reputation')
    sentiment = ctrl.Antecedent(np.arange(-1, 2, 0.1), 'sentiment')
    action = ctrl.Consequent(np.arange(0, 11, 1), 'action')

    severity.automf(3, names=['low', 'average', 'high'])
    reputation.automf(3, names=['poor', 'average', 'good'])
    sentiment.automf(3, names=['negative', 'neutral', 'positive'])

    # Output Membership Definitions
    action['none'] = fuzz.trimf(action.universe, [0, 0, 5])
    action['flag'] = fuzz.trimf(action.universe, [3, 5, 7])
    action['remove'] = fuzz.trimf(action.universe, [5, 10, 10])

    # Rule Descriptions (For UI display)
    descriptions = [
        "IF Severity: High AND Reputation: Poor AND Sentiment: Negative THEN Action: Remove",
        "IF Severity: High AND Reputation: Average AND Sentiment: Negative THEN Action: Remove",
        "IF Severity: High AND Reputation: Good AND Sentiment: Negative THEN Action: Flag",
        "IF Severity: High AND Reputation: Good AND Sentiment: Positive THEN Action: Flag",
        "IF Severity: Average AND Reputation: Poor AND Sentiment: Negative THEN Action: Remove",
        "IF Severity: Average AND Reputation: Average AND Sentiment: Negative THEN Action: Flag",
        "IF Severity: Average AND Reputation: Good AND Sentiment: Negative THEN Action: None",
        "IF Severity: Average AND Reputation: Poor AND Sentiment: Neutral THEN Action: Flag",
        "IF Severity: Low AND Reputation: Poor AND Sentiment: Negative THEN Action: Flag",
        "IF Severity: Low AND Reputation: Good AND Sentiment: Negative THEN Action: None",
        "IF Severity: Low AND Reputation: Average AND Sentiment: Neutral THEN Action: None",
        "IF Severity: High AND Reputation: Poor AND Sentiment: Positive THEN Action: Flag",
        "IF Severity: Average AND Reputation: Average AND Sentiment: Positive THEN Action: None",
        "IF Severity: Low AND Reputation: Poor AND Sentiment: Positive THEN Action: None",
        "IF Severity: High AND Reputation: Average AND Sentiment: Neutral THEN Action: Flag"
    ]

    # Converting to Fuzzy Objects
    rules = [
        ctrl.Rule(severity['high'] & reputation['poor'] & sentiment['negative'], action['remove']),
        ctrl.Rule(severity['high'] & reputation['average'] & sentiment['negative'], action['remove']),
        ctrl.Rule(severity['high'] & reputation['good'] & sentiment['negative'], action['flag']),
        ctrl.Rule(severity['high'] & reputation['good'] & sentiment['positive'], action['flag']),
        ctrl.Rule(severity['average'] & reputation['poor'] & sentiment['negative'], action['remove']),
        ctrl.Rule(severity['average'] & reputation['average'] & sentiment['negative'], action['flag']),
        ctrl.Rule(severity['average'] & reputation['good'] & sentiment['negative'], action['none']),
        ctrl.Rule(severity['average'] & reputation['poor'] & sentiment['neutral'], action['flag']),
        ctrl.Rule(severity['low'] & reputation['poor'] & sentiment['negative'], action['flag']),
        ctrl.Rule(severity['low'] & reputation['good'] & sentiment['negative'], action['none']),
        ctrl.Rule(severity['low'] & reputation['average'] & sentiment['neutral'], action['none']),
        ctrl.Rule(severity['high'] & reputation['poor'] & sentiment['positive'], action['flag']),
        ctrl.Rule(severity['average'] & reputation['average'] & sentiment['positive'], action['none']),
        ctrl.Rule(severity['low'] & reputation['poor'] & sentiment['positive'], action['none']),
        ctrl.Rule(severity['high'] & reputation['average'] & sentiment['neutral'], action['flag'])
    ]

    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
    return sim, action, descriptions

moderator, action_var, rule_texts = setup_system()

# --- 2. SIDEBAR ---
st.sidebar.header("Control Panel")
s_val = st.sidebar.slider("Severity (Keyword Intensity)", 0, 10, 6)
r_val = st.sidebar.slider("Reputation (User History)", 0, 10, 4)
sent_val = st.sidebar.slider("Sentiment (Tone)", -1.0, 1.0, 0.0)

# --- 3. EXPLAINING THRESHOLDS ---
with st.expander("📊 Understanding Risk Scores (Thresholds)"):
    st.write("""
    Fuzzy Score 0 to 10 ke darmayan hota hai:
    - **0.0 - 4.0 (NONE):** The system classifies the content as Safe. No moderation action is required, and the content is permitted.
    - **4.0 - 7.0 (FLAG):** The system identifies the content as Suspicious or ambiguous. It is flagged for manual review by a human moderator.
    - **7.0 - 10.0 (REMOVE):** SysThe system classifies the content as Harmful or dangerous. It is automatically blocked or deleted to ensure safety.
    """)

# --- 4. COMPUTATION ---
moderator.input['severity'] = s_val
moderator.input['reputation'] = r_val
moderator.input['sentiment'] = sent_val
moderator.compute()
score = moderator.output['action']

# --- 5. RESULTS & GRAPH ---
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("System Decision")
    if score < 4.0:
        st.success(f"### ✅ ACTION: NONE\n**Risk Score:** {score:.2f}")
    elif score < 7.0:
        st.warning(f"### ⚠️ ACTION: FLAG\n**Risk Score:** {score:.2f}")
    else:
        st.error(f"### 🚫 ACTION: REMOVE\n**Risk Score:** {score:.2f}")

with col2:
    fig, ax = plt.subplots(figsize=(6, 3))
    x = action_var.universe
    ax.plot(x, action_var['none'].mf, 'b', label='None')
    ax.plot(x, action_var['flag'].mf, 'orange', label='Flag')
    ax.plot(x, action_var['remove'].mf, 'r', label='Remove')
    ax.axvline(x=score, color='black', linestyle='--', label=f'Score: {score:.2f}')
    ax.legend()
    st.pyplot(fig)

# --- 6. 15 RULES DISPLAY ---
st.markdown("---")
st.subheader("📜 Rule Execution Logic (Logic Table)")

# Simple logic to find current labels for highlighting
s_l = 'high' if s_val > 7 else ('average' if s_val > 3 else 'low')
r_l = 'poor' if r_val < 4 else ('average' if r_val < 8 else 'good')
sent_l = 'negative' if sent_val < -0.3 else ('positive' if sent_val > 0.3 else 'neutral')

st.write(f"Based on **Severity: {s_l}**, **Reputation: {r_l}**, and **Sentiment: {sent_l}**, the following rules were analyzed:")

for i, text in enumerate(rule_texts):
    # Check if current input labels exist in the rule text (Case insensitive)
    if s_l in text.lower() and r_l in text.lower() and sent_l in text.lower():
        st.info(f"🔥 **Rule #{i+1} Triggered:** {text}")
    else:
        with st.expander(f"Rule #{i+1} (Inactive)"):
            st.text(text)