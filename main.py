import streamlit as st

import data_cleaning
import data_analysis


st.set_page_config(page_title='Chat Analysis',
page_icon=":alien:",
layout='centered', 
initial_sidebar_state='auto',
menu_items=None)


chat_file = st.file_uploader(
    label="Please upload your group chat as a text file",
    type=['.txt', '.csv'],
    accept_multiple_files=False, 
)

if chat_file is not None:
    
    preprocessed_chat_data, input_source = data_cleaning.preprocess_input_data(chat_file) 
    author_names, phone_numbers = data_cleaning.get_users(preprocessed_chat_data)
    num_name_pairs = {}
    if phone_numbers:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Hi there! Could you please let us know to whom these numbers belong. The Plots will update accordingly : )")
        with col2:
            for pn in phone_numbers:
                num_name_pairs[pn] = st.selectbox(pn,(author_names))
       
        data_cleaning.fix_phone_numbers(preprocessed_chat_data, num_name_pairs)

    st.markdown("***")
    st.text("")
    st.text("")
    data_analysis.display_num_of_messages(preprocessed_chat_data)
    # data_analysis.display_msg_gap(preprocessed_chat_data)
    data_analysis.display_time_info(preprocessed_chat_data)
    data_analysis.display_favourite_emojis(preprocessed_chat_data)
    data_analysis.display_biggest_spammer(preprocessed_chat_data)
    data_analysis.display_media_person(preprocessed_chat_data, input_source)
    data_analysis.display_quote(preprocessed_chat_data)

    
