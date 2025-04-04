import pandas as pd
import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")

# Custom CSS for professional styling
st.markdown("""
    <style>
        .main {background-color: #ffffff;}
        .stSidebar {background-color: #e4e5ed; color: black;}
        .stButton>button {border-radius: 5px; background-color: #1abc9c; color: white; font-size: 16px;}
        .stSelectbox div[data-baseweb="select"] {background-color: white !important;}
        .metric-box {background-color: #ecf0f1; padding: 15px; border-radius: 10px; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# Sidebar UI
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg", width=100)
st.sidebar.title("📊 WhatsApp Chat Analyzer")
st.sidebar.markdown("Upload your WhatsApp chat file to analyze statistics and insights.")

uploaded_file = st.sidebar.file_uploader("📂 Upload Chat File")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Select User", user_list)

    if st.sidebar.button("🔍 Analyze Chat"):
        st.markdown("## 📊 Chat Statistics")

        # Stats Display
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-box'><h4>💬 Messages</h4><h2>{num_messages}</h2></div>",
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'><h4>📝 Words</h4><h2>{words}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'><h4>📷 Media Shared</h4><h2>{num_media_messages}</h2></div>",
                        unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-box'><h4>🔗 Links Shared</h4><h2>{num_links}</h2></div>",
                        unsafe_allow_html=True)

        # Chat Timeline
        st.markdown("## 🕒 Chat Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(timeline['time'], timeline['message'], marker='o', color='#3498db', linewidth=2)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Activity Insights
        st.markdown("## 🔥 User Activity")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Most Active Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='#e74c3c')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### Most Active Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='#f39c12')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Heatmap
        st.markdown("## 📊 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(user_heatmap, cmap='Blues', annot=False)
        st.pyplot(fig)

        # WordCloud
        st.markdown("## ☁ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        st.pyplot(fig)

        # Common Words
        st.markdown("## 🔠 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='#9b59b6')
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Emoji Analysis
        st.markdown("## 😂 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f",
                   colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
            st.pyplot(fig)

        # Average Response Time
        response_times = helper.average_response_time(df)
        st.markdown("## ⏳ Average Response Time (minutes)")
        st.dataframe(response_times)

        # Message Length Analysis
        avg_len, max_len, min_len = helper.message_length_analysis(df)
        st.markdown("## 📝 Message Length Analysis")
        st.dataframe(pd.DataFrame({'Avg Length': avg_len, 'Max Length': max_len, 'Min Length': min_len}))

        # Streak Tracker
        streaks = helper.streak_tracker(df)
        st.markdown("## 🔥 Streak Tracker (Longest Active Streak)")
        st.dataframe(streaks)

        # Dead Chat Detector
        max_gap = helper.dead_chat_detector(df)
        st.markdown(f"## ☠ Dead Chat Detector: Longest Inactivity Period")
        st.write(f"📉 The longest inactivity period was **{max_gap} days**.")