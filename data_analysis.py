import pandas as pd
import altair as alt
import streamlit as st

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
        title=f'Total messages in 2021: {total_msgs:,}').configure_title(
        fontSize=20,
        font='Courier',
        anchor='middle',
    )

    st.altair_chart(c, use_container_width=True)

"""
Semantic analysis
"""