from utils.imports import *

if "map" not in st.session_state:
    st.session_state.map = None 

if "selected_variable" not in st.session_state:
    st.session_state.selected_variable = None

if "transform_dataframe_nbs" not in st.session_state:
    st.session_state.transform_dataframe_nbs = 0

if "transform_dataframe_ext" not in st.session_state:
    st.session_state.transform_dataframe_ext = 0


if "change_variable" not in st.session_state:
    st.session_state.change_variable = 0


def callback_transform_nbs():
    st.session_state.transform_dataframe_nbs = 1

def callback_transform_ext():
    st.session_state.transform_dataframe_ext = 1

def callback_change_variable():
    st.session_state.change_variable = 1
