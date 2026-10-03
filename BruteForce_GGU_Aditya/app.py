"""
Streamlit Application for ConvoSense.
Interactive Dashboard for Conversation Intelligence & Communication Gap Analysis.
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from src.parser import parse_conversation_input
from src.semantic_analysis import analyze_conversation
from src.reporting import export_findings_to_json, export_findings_to_csv
from src.schema import Finding



# Page Configuration & Custom Styling

st.set_page_config(
    page_title="ConvoSense — Communication Gap Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }
    .finding-card {
        background: #1E222D;
        border-left: 5px solid #FF4B4B;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .badge-unanswered { background-color: #FF4B4B; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
    .badge-ignored { background-color: #FFA500; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
    .badge-clarification { background-color: #9B59B6; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
    .badge-unresolved { background-color: #F1C40F; color: black; padding: 4px 10px; border-radius: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)



# Preset Datasets

SAMPLE_CONVERSATIONS = {
    "Sample 1: General Team Discussion": """10:00 Rahul: Who will prepare the slides for tomorrow?
10:02 Priya: I can prepare the introduction slides.
10:04 Amit: What is the submission deadline for the report?
10:05 Rahul: We need someone to prepare the demo setup.
10:07 Rahul: I'll book the conference room for 3 PM.
10:08 Priya: Confirmed, thanks!
10:12 Amit: Should we submit PDF or DOCX format?
10:15 Amit: Which file format is required for submission?
""",
    "Sample 2: WhatsApp Chat Export": """[01/10/26, 10:00:15 AM] Rahul: Hey everyone, deadline is tomorrow!
[01/10/26, 10:01:20 AM] Priya: Should we send the final draft today?
[01/10/26, 10:02:00 AM] Rahul: <Media omitted>
[01/10/26, 10:03:10 AM] Amit: I will fix the database bug by 5 PM.
[01/10/26, 10:05:00 AM] Rahul: Who is testing the deployment?
[01/10/26, 10:10:00 AM] Priya: Is the deployment ready?
""",
    "Sample 3: All Resolved (Clean)": """10:00 Rahul: When is the meeting starting?
10:01 Priya: At 4 PM in Room 3B.
10:02 Rahul: Got it, thanks!
10:03 Amit: I'll review the pull request.
10:04 Priya: Approved, looks good.
"""
}



# Header Section

st.title("🧠 ConvoSense")
st.markdown("##### *Conversation Intelligence & Communication Gap Analysis*")
st.caption("Detect unanswered questions, ignored proposals, repeated clarification requests, and unresolved topics with evidence-based explanations.")

st.divider()



# Sidebar Controls

with st.sidebar:
    st.header("⚙️ Configuration")
    
    input_method = st.radio("Input Source", ["Paste Text / Log", "Upload File (CSV / TXT)"])
    
    selected_preset = st.selectbox("Load Sample Dataset", ["Custom Input"] + list(SAMPLE_CONVERSATIONS.keys()))
    
    st.subheader("Engine Parameters")
    window_size = st.slider("Lookahead Window (Messages)", min_value=2, max_value=10, value=5)
    similarity_thresh = st.slider("Similarity Threshold", min_value=0.10, max_value=0.70, value=0.35, step=0.05)



# Input Data Ingestion

df_raw = None

if selected_preset != "Custom Input":
    pasted_text = SAMPLE_CONVERSATIONS[selected_preset]
    df_raw = parse_conversation_input(pasted_text)
elif input_method == "Paste Text / Log":
    user_text = st.text_area("Paste Conversation Log:", height=200, placeholder="10:00 Rahul: Who will prepare the slides?\n10:02 Priya: I can prepare intro.")
    if user_text.strip():
        df_raw = parse_conversation_input(user_text)
else:
    uploaded_file = st.file_uploader("Upload CSV or TXT Conversation File", type=["csv", "txt"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df_csv = pd.read_csv(uploaded_file)
            df_raw = parse_conversation_input(df_csv)
        else:
            text_str = uploaded_file.read().decode("utf-8")
            df_raw = parse_conversation_input(text_str)



# Main Analysis Pipeline

if df_raw is None or df_raw.empty:
    st.info("👈 Please paste a conversation, upload a file, or select a sample dataset from the sidebar to begin analysis.")
else:
    # Run analysis
    analysis_results = analyze_conversation(df_raw, window_size=window_size, similarity_threshold=similarity_thresh)
    
    # Store findings in session state for interactive status modification
    if "findings_list" not in st.session_state or st.sidebar.button("🔄 Re-run Analysis"):
        st.session_state["findings_list"] = analysis_results["findings"]

    findings_list = st.session_state["findings_list"]

    # Navigation Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🔍 Evidence Explorer", 
        "📈 Interactive Timeline", 
        "📌 Unresolved Topics", 
        "📥 Export & Audit"
    ])

    
    # TAB 1: OVERVIEW & KPIS
    
    with tab1:
        st.subheader("Analysis Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("Total Messages", len(df_raw))
        col2.metric("Unanswered Qs", sum(1 for f in findings_list if f.type == "Unanswered Question"))
        col3.metric("Ignored Proposals", sum(1 for f in findings_list if f.type == "Ignored Response"))
        col4.metric("Repeated Requests", sum(1 for f in findings_list if f.type == "Repeated Clarification"))
        col5.metric("Unresolved Topics", sum(1 for f in findings_list if f.type == "Unresolved Topic"))
        
        st.divider()
        
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.markdown("#### Communication Gap Breakdown")
            gap_data = {
                "Gap Type": ["Unanswered Question", "Ignored Response", "Repeated Clarification", "Unresolved Topic"],
                "Count": [
                    sum(1 for f in findings_list if f.type == "Unanswered Question"),
                    sum(1 for f in findings_list if f.type == "Ignored Response"),
                    sum(1 for f in findings_list if f.type == "Repeated Clarification"),
                    sum(1 for f in findings_list if f.type == "Unresolved Topic")
                ]
            }
            fig_pie = px.pie(
                gap_data, 
                values="Count", 
                names="Gap Type", 
                hole=0.4,
                color="Gap Type",
                color_discrete_map={
                    "Unanswered Question": "#FF4B4B",
                    "Ignored Response": "#FFA500",
                    "Repeated Clarification": "#9B59B6",
                    "Unresolved Topic": "#F1C40F"
                }
            )
            fig_pie.update_layout(template="plotly_dark", height=320)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c_right:
            st.markdown("#### Speaker Message Distribution")
            speaker_counts = df_raw["speaker"].value_counts().reset_index()
            speaker_counts.columns = ["Speaker", "Messages"]
            fig_bar = px.bar(speaker_counts, x="Speaker", y="Messages", color="Speaker", template="plotly_dark")
            fig_bar.update_layout(height=320, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

   
    # TAB 2: EVIDENCE EXPLORER
    
    with tab2:
        st.subheader("Evidence-Based Findings Explorer")
        st.caption("Inspect why each message was flagged, review supporting evidence, and update resolution status.")
        
        if not findings_list:
            st.success("🎉 No communication gaps detected in this conversation!")
        else:
            for idx, finding in enumerate(findings_list):
                with st.container():
                    st.markdown(f"""
                    <div class="finding-card">
                        <div style="display: flex; justify-space-between; align-items: center;">
                            <span class="badge-{finding.type.split()[0].lower()}">{finding.type}</span>
                            <span style="float: right; color: #888;">ID: {finding.id} | Timestamp: {finding.timestamp}</span>
                        </div>
                        <h4 style="margin-top: 10, margin-bottom: 5px;">Speaker: {finding.speaker}</h4>
                        <p style="font-size: 1.1em; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px;">
                            💬 "{finding.message}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**Supporting Evidence:**")
                    for ev in finding.evidence:
                        st.markdown(f"- 🔎 {ev}")
                        
                    st.progress(finding.confidence, text=f"Model Confidence Score: {int(finding.confidence*100)}%")
                    
                    # Interactive Status Review Controls
                    st.markdown("**Review Control:**")
                    new_status = st.radio(
                        f"Status for {finding.id}:", 
                        ["Needs review", "Resolved", "False positive"], 
                        index=["Needs review", "Resolved", "False positive"].index(finding.status),
                        key=f"status_radio_{idx}",
                        horizontal=True
                    )
                    finding.status = new_status
                    st.divider()

  
    # TAB 3: INTERACTIVE TIMELINE
   
    with tab3:
        st.subheader("Chronological Conversation & Gap Timeline")
        
        flagged_indices = {f.message_index: f for f in findings_list}
        
        timeline_data = []
        for i, row in df_raw.iterrows():
            finding_info = flagged_indices.get(i)
            status_label = finding_info.type if finding_info else "Normal Message"
            color = "#3498DB"  # Normal blue
            if finding_info:
                if finding_info.type == "Unanswered Question":
                    color = "#FF4B4B"
                elif finding_info.type == "Ignored Response":
                    color = "#FFA500"
                elif finding_info.type == "Repeated Clarification":
                    color = "#9B59B6"
                elif finding_info.type == "Unresolved Topic":
                    color = "#F1C40F"
                    
            timeline_data.append({
                "Index": i,
                "Speaker": row["speaker"],
                "Message": row["message"],
                "Timestamp": row["timestamp"],
                "Status": status_label,
                "Color": color
            })
            
        df_timeline = pd.DataFrame(timeline_data)
        
        fig_timeline = px.scatter(
            df_timeline, 
            x="Index", 
            y="Speaker", 
            color="Status", 
            size=[14]*len(df_timeline),
            hover_data=["Timestamp", "Message"],
            title="Message Chronology & Flagged Communication Gaps",
            template="plotly_dark",
            color_discrete_map={
                "Normal Message": "#3498DB",
                "Unanswered Question": "#FF4B4B",
                "Ignored Response": "#FFA500",
                "Repeated Clarification": "#9B59B6",
                "Unresolved Topic": "#F1C40F"
            }
        )
        fig_timeline.update_traces(marker=dict(line=dict(width=1, color='White')))
        fig_timeline.update_layout(height=420)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        st.subheader("Conversation Log View")
        st.dataframe(df_raw, use_container_width=True)

   
    # TAB 4: UNRESOLVED TOPICS
   
    with tab4:
        st.subheader("Unresolved Topics & Action Items")
        unresolved_items = [f for f in findings_list if f.type in ["Unresolved Topic", "Ignored Response", "Unanswered Question"]]
        
        if not unresolved_items:
            st.success("No open unresolved topics or unassigned action items.")
        else:
            for item in unresolved_items:
                st.warning(f"📌 **[{item.type}]** {item.speaker} (at {item.timestamp}): \"{item.message}\"")
                for e in item.evidence:
                    st.caption(f"  • {e}")

    
    # TAB 5: EXPORT & AUDIT
    
    with tab5:
        st.subheader("Export Analysis & Audit Trail")
        st.caption("Download the findings with user review updates.")
        
        json_str = export_findings_to_json(findings_list)
        csv_str = export_findings_to_csv(findings_list)
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 Download Findings as JSON",
                data=json_str,
                file_name="convosense_findings.json",
                mime="application/json"
            )
        with col_dl2:
            st.download_button(
                label="📥 Download Findings as CSV",
                data=csv_str,
                file_name="convosense_findings.csv",
                mime="text/csv"
            )
            
        st.subheader("Raw JSON Findings Audit Output")
        st.json(json_str)
