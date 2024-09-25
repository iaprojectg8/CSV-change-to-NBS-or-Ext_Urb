from utils.imports import *

if "map" not in st.session_state:
    st.session_state.map = None

if "selected_variable" not in st.session_state:
    st.session_state.selected_variable = None

if "csv_file" not in st.session_state:
    st.session_state.csv_file = None