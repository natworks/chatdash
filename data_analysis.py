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
        st.metric("Month of the year", top_month, None)
        st.altair_chart(month_chat, use_container_width=True)
    with col2:
        st.metric("Day of the week", top_day, None)
        st.altair_chart(day_chat, use_container_width=True)
    with col3:
        st.metric("Hour of the day", f"{top_hour}hr", None)
        st.altair_chart(hour_chat, use_container_width=True)
