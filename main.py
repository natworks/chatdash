import streamlit as st

import data_handling
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
    preprocessed_chat_data = data_handling.preprocess_input_data(chat_file)
    data_analysis.display_general_analysis(preprocessed_chat_data)
