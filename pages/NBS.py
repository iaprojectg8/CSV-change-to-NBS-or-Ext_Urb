from utils.variable import VARIABLES_LIST, DATAFRAME_HEIGHT, CSV_PATH
from utils.imports import *
from tools import *
from session_variables import *

csv_file = upload_dataframe()

if csv_file:
    # Create the dataframe from the uploaded file
    complete_df = manage_csv(uploaded_file=csv_file)
    if "change" not in complete_df.columns:
            complete_df["change"] = False
    
    # Display the complete dataframe
    st.dataframe(complete_df, height=DATAFRAME_HEIGHT)
    map = leafmap.Map()
    selected_variable = st.selectbox(label="Chose a variable to observe",options=VARIABLES_LIST)

    if selected_variable != st.session_state.selected_variable:
        # In case the selected variable is changed, we rebuild a raster
        map = build_the_raster(map, complete_df, selected_variable)
        
    map = st.session_state.map
    map.add_layer_control()

    st_component = st_folium(map, width="100%") 
    drawn_polygons = map.st_draw_features(st_component=st_component)
    print(drawn_polygons)

    if drawn_polygons: 
    
        new_polygons = []
        df = complete_df[["LON", "LAT", f"{selected_variable}", "change"]]

        gdf = gpd.GeoDataFrame(
            df,  
            geometry=gpd.points_from_xy(df["LON"], df["LAT"]),  
            crs="EPSG:4326" 
        )

        st.button("Variable that will change", on_click=callback_change_variable)
        if st.session_state.change_variable:
            occsol, zone_cli, min_hauta, max_hauta = tuning_variables_value_nbs()

            st.button("Transform dataframe", on_click=callback_transform)
            if st.session_state.transform_dataframe:
                for drawn_polygon in drawn_polygons:

                    if "geometry" in drawn_polygon:
                        print("iam in geometry")
                        geometry = drawn_polygon['geometry']
                        if 'Polygon' in  geometry['type']:
                            polygons = geometry['coordinates']
                            for polygon_coordinates in polygons:
                                new_polygons.append(Polygon(polygon_coordinates))

                        # Create a GeoDataframe from the drawn polygon
                        gdf_new = gpd.GeoDataFrame(geometry=new_polygons)
                        
                        for _, polygon in gdf_new.iterrows():
                            # Finds the point of the area that are in the polygon
                            points_within = gdf[gdf.geometry.within(polygon.geometry)]
                            # Change all the indices in the dataframe
                            for index in points_within.index:
                                df.at[index, 'change'] = True
                    
                st.write("Dataframe with change column")
                st.dataframe(df,height=DATAFRAME_HEIGHT)
                
                # Transferring the change column to the restricted dataframe, to the complete one
                complete_df['change'] = df['change']
                df_final = complete_df.reset_index(drop=True)
                
                # Trying to make something consistent for the tree height
                normalized_proba, possible_value = make_probs_for_tree_distrib(min_hauta, max_hauta)
                df_final = value_attribution(df_final, occsol, zone_cli, possible_value, normalized_proba)
                
                # Display information about new dataframe
                st.write("Changed dataframe still with the change column")
                st.dataframe(df_final, height=DATAFRAME_HEIGHT)
                df_final = df_final.drop("change", axis=1)
                st.write("Final dataframe that will be pushed in a CSV")
                st.dataframe(df_final, height=DATAFRAME_HEIGHT)
                df_final.to_csv(CSV_PATH,index=False)
                st.success(f"Finale CSV saved to {CSV_PATH}")
               
    if st.button("Reset everything"):
        print(st.session_state)
        st.session_state.clear()
        st.rerun()