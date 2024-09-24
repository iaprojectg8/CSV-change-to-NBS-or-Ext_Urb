from utils.imports import *

if "map" not in st.session_state:
    st.session_state.map = None

if "selected_variable" not in st.session_state:
    st.session_state.selected_variable = None