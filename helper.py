from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap

def average_response_time(df):
    # Assuming 'date' and 'time' columns exist
    df = df.sort_values(by=['date'])
    df['prev_timestamp'] = df['date'].shift(1)

    df['response_time'] = (df['date'] - df['prev_timestamp']).dt.total_seconds()

    response_times = df.groupby('user')['response_time'].mean().dropna()
    return response_times.apply(lambda x: np.round(x / 60, 2))  # Convert to minutes

def message_length_analysis(df):
    df['message_length'] = df['message'].apply(len)
    avg_length = df.groupby('user')['message_length'].mean()
    max_length = df.groupby('user')['message_length'].max()
    min_length = df.groupby('user')['message_length'].min()

    return avg_length, max_length, min_length


def streak_tracker(df):
    df = df[['user', 'only_date']].drop_duplicates().sort_values(by=['user', 'only_date'])

    # Convert date to datetime
    df['only_date'] = pd.to_datetime(df['only_date'])

    # Shift the date column within each user group to get the previous date
    df['prev_date'] = df.groupby('user')['only_date'].shift(1)

    # Check if the difference is exactly 1 day to continue the streak
    df['streak_continued'] = (df['only_date'] - df['prev_date']).dt.days == 1

    # Create a new streak ID every time the streak breaks
    df['streak_group'] = (~df['streak_continued']).cumsum()

    # Count the length of each streak for each user
    streaks = df.groupby(['user', 'streak_group']).size()

    # Get the longest streak per user
    max_streak = streaks.groupby('user').max()

    return max_streak


def dead_chat_detector(df):
    df['date'] = pd.to_datetime(df['only_date'])
    df['prev_date'] = df['date'].shift(1)

    df['gap'] = (df['date'] - df['prev_date']).dt.days
    max_gap = df['gap'].max()

    return max_gap

