from utils.imports import *

if "map" not in st.session_state:
    st.session_state.map = None

if "m" not in st.session_state:
    st.session_state.m = None   

if "selected_variable" not in st.session_state:
    st.session_state.selected_variable = None

if "csv_file" not in st.session_state:
    st.session_state.csv_file = None

if "transform_dataframe" not in st.session_state:
    st.session_state.transform_dataframe = 0


if "change_variable" not in st.session_state:
    st.session_state.change_variable = 0

def callback_transform():
    st.session_state.transform_dataframe = 1

def callback_change_variable():
    st.session_state.change_variable = 1
