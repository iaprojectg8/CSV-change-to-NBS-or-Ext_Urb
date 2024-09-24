from variable import VARIABLES_LIST
from imports import *
from tools import *

csv_file = upload_dataframe()
if csv_file:
    
    # Create a Leafmap map
    map = leafmap.Map()
            
    # Create the dataframe from the uploaded file
    df = manage_csv(uploaded_file=csv_file)

    selected_variable = st.selectbox(label="Chose a variable to observe",options=VARIABLES_LIST)
    
    if selected_variable:
        variable, grid_values, transform, complete_path = create_rasters_needs(df,f'{selected_variable}_remake.tif')
        save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map)

    map.to_streamlit()  