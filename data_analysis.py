import re
import numpy as np
import pandas as pd

import emoji
import altair as alt
import streamlit as st

import data_cleaning

def display_signal_analysis(chat_data: pd.DataFrame):
    """

    Most reacted to msg
    Most beloved msg
    Funniest Message

    Funniest person (the one with most laug reactions)
    Most beloved person (the one with the most heart reactions)

    Favourite Reactions per user

    Total group name changes
    Number of group name changes per person
    Title that stayed on the longest
    """
    pass

def display_num_of_messages(chat_data: pd.DataFrame):
    """
    Total number of msgs and msgs sent per user
    Longest period without conversation
    Biggest Message block



    Who spams the most links

    Most controversial opinion

    
    """
    msg_count = chat_data["author"].value_counts().to_frame()
    msg_count.reset_index(inplace=True)
    msg_count.columns = ['Author', 'Count']
    total_msgs = msg_count['Count'].sum()

    chart = alt.Chart(msg_count).mark_bar().encode(
        x=alt.X('Author:N', sort=alt.EncodingSortField(field="Author", op="count", order='ascending')),
        y='Count',
        color=alt.Color('Author', scale=alt.Scale(scheme='tableau10'), legend=None, sort ="descending")
    )
    text = chart.mark_text(
        align='center',
        dy=-5
    ).encode(
        text='Count:N',
        color=alt.value('black')
    )

    c = (chart + text).properties(
        title=f'2021 Messages: {total_msgs:,}').configure_title(
        fontSize=20,
        anchor='middle'
    )

    st.altair_chart(c, use_container_width=True)

def get_freq_plot(data, column, column_renamed, sorting_order):
    msg_count = data[column].value_counts().to_frame()
    msg_count.reset_index(inplace=True)
    msg_count.columns = [column_renamed, 'Messages']

    chart = alt.Chart(msg_count).mark_bar().encode(
        x=alt.X(f'{column_renamed}', sort=sorting_order),
        y='Messages',
        color=alt.condition(
            alt.datum.Messages > int(msg_count.iloc[1,1]),  # If the message count is the max returns True,
            alt.value('#9d0208'),     # which sets the bar orange.
            alt.value('#457b9d')   # And if it's not true it sets the bar steelblue.
        )
    )
    return chart, msg_count.iloc[0,0]

def display_time_info(chat_data: pd.DataFrame):
    month_chat, top_month  = get_freq_plot(chat_data, 'month', 'Month', ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    day_chat, top_day = get_freq_plot(chat_data, 'weekday', 'Weekday',["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    hour_chat, top_hour = get_freq_plot(chat_data, 'hour_of_day', 'Hour of Day', ['{:02d}'.format(t) for t in range(24)])

    st.subheader("The Busiest...")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Month of the year is:", top_month, None)
        st.altair_chart(month_chat, use_container_width=True)
    with col2:
        st.metric("Day of the week is:", top_day, None)
        st.altair_chart(day_chat, use_container_width=True)
    with col3:
        st.metric("Hour of the day is:", f"{top_hour}:00hr", None)
        st.altair_chart(hour_chat, use_container_width=True)

def display_favourite_emojis(chat_data: pd.DataFrame):
    text = " ".join(str(msg) for msg in chat_data.body)
    all_emojis = "".join(word for word in text if emoji.is_emoji(word))

    unique_emojis = list(set(all_emojis))
    emoji_count = []

    for emoj in unique_emojis:
        count = all_emojis.count(emoj)
        emoji_count.append(count)

    arg_sorted = np.argsort(emoji_count, )[::-1]

    st.subheader("Your group's favourite emojis:")

    [col1, col2, col3, col4, col5] = st.columns(5)

    for i, col in enumerate([col1, col2, col3, col4, col5]):
        col.markdown(f'<span style="font-size: 72px;">{unique_emojis[arg_sorted[i]]}</span>', unsafe_allow_html=True)

def display_biggest_spammer(chat_data: pd.DataFrame):
    author_names, _ = data_cleaning.get_users(chat_data)
    links_per_user = []
    favourite_site = []
    
    for author in author_names:
        author_msgs = chat_data[chat_data["author"]==author]
        author_msgs_list = " ".join(str(msg) for msg in author_msgs.body)
        websites = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', author_msgs_list)
        unique_websites = list(set(websites))
        links_per_user.append(len(websites))
        if len(websites) > 0:
            counts = [
                websites.count(site) for site in unique_websites
            ]
            sorted_idx = np.argsort(counts, )[::-1]
            favourite_site.append([unique_websites[sorted_idx[0]], counts[sorted_idx[0]]])
        else:
            favourite_site.append([0, 0])

    idx_spammer = links_per_user.index(max(links_per_user))
    spammer = author_names[idx_spammer]
    
    st.markdown(f'<span style="font-size: 56px;">{spammer}</span> is the biggest spammer in your group.\
        Their favourite source is {favourite_site[idx_spammer][0]}. In fact, they have shared this website alone {favourite_site[idx_spammer][1]} times in 2021.', unsafe_allow_html=True)