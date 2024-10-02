from utils.variable import VARIABLES_LIST, DATAFRAME_HEIGHT
from utils.imports import *
from tools import *
from session_variables import *

csv_file = upload_dataframe()
if csv_file:
    # Create a Leafmap map
    m = leafmap.Map()
            
    # Create the dataframe from the uploaded file
    st.cache_data.clear()
    complete_df = manage_csv(uploaded_file=csv_file)    

    # Display the complete dataframe
    st.dataframe(complete_df, height=DATAFRAME_HEIGHT)

    # Select the variable to see
    selected_variable = st.selectbox(label="Chose a variable to observe",options=VARIABLES_LIST)
    if selected_variable != st.session_state.selected_variable or csv_file != st.session_state.csv_file:
    
        variable, grid_values, transform, complete_path = create_rasters_needs(complete_df,f'{selected_variable}_remake.tif')
        save_and_add_raster_to_map(variable, grid_values, transform, complete_path, m)


        m.add_layer_control()
        st.session_state.m = m
        # Afficher la carte dans Streamlit
        st_component = st_folium(m, width="100%")
        st.session_state.selected_variable = selected_variable
    else:
        st_component = st_folium(st.session_state.m, width="100%")