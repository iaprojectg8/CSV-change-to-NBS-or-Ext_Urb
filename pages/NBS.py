from utils.variable import VARIABLES_LIST, DATAFRAME_HEIGHT
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
    # Select the variable to see
    selected_variable = st.selectbox(label="Chose a variable to observe",options=VARIABLES_LIST)
    if selected_variable != st.session_state.selected_variable:
        with st.status("Creating the corresponding raster..."):
            st.write("Gathering raster needs")
            variable, grid_values, transform, complete_path = create_rasters_needs(complete_df,f'{selected_variable}_remake.tif')
            st.write("Writing and saving raster")
            map = save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map)
            st.session_state.selected_variable = selected_variable
            st.session_state.map = map
            # Afficher la carte dans Streamlit
    map = st.session_state.map
    map.add_layer_control()

    st_component = st_folium(map, width="100%") 
    drawn_polygons = map.st_draw_features(st_component=st_component)
    print(drawn_polygons)

    if drawn_polygons:  # Si des polygones sont dessinés
        # Initialiser une liste pour stocker les polygones
        new_polygons = []

        ### Voir ça dans le train mais on entre jamais dans la condition.
        df = complete_df[["LON", "LAT", f"{selected_variable}", "change"]]
        # Create the geometry column from latitude and longitude

        gdf = gpd.GeoDataFrame(
            df,  # Use the existing DataFrame
            geometry=gpd.points_from_xy(df["LON"], df["LAT"]),  # Create the geometry from lon/lat
            crs="EPSG:4326"  # Define the CRS (Coordinate Reference System) as WGS84
        )

        st.button("Variable that will change", on_click=callback_change_variable)
        if st.session_state.change_variable:
            activated = not st.toggle("Authorize user to change values",value=False)
         
            occsol =  st.number_input("OCCSOL", min_value=0, max_value=6, value=6, disabled=activated)
            zone_cli = st.number_input("ZONECL", min_value=0, max_value=16, value = 6, disabled=activated)
            st.write("Random interval for HAUTA",)
            col1, col2 = st.columns(2)
    
            with col1:
                min_hauta = st.number_input("HAUTA min", min_value=0, max_value=20, value = 0, disabled=activated)
            with col2:
                max_hauta = st.number_input("HAUTA max",min_value=min_hauta, max_value=20, value = min_hauta + 5, disabled=activated)

            natsol = st.number_input("NATSOL", min_value=0, max_value=11, value=6, disabled=activated)
            natsol2 = st.number_input("NATSOL2", min_value=0, max_value=11, value=6, disabled=activated)
            



            st.button("Transform dataframe", on_click=callback_transform)
            if st.session_state.transform_dataframe:
                for drawn_polygon in drawn_polygons:
                    print("in drawn polygon")
                    print(drawn_polygon)

                    if "geometry" in drawn_polygon:
                        print("iam in geometry")
                        geometry = drawn_polygon['geometry']
                        if 'Polygon' in  geometry['type']:
                            polygons = geometry['coordinates']
                            for polygon_coordinates in polygons:
                                new_polygons.append(Polygon(polygon_coordinates))

                    
                        # Créer un GeoDataFrame à partir des polygones dessinés
                        gdf_new = gpd.GeoDataFrame(geometry=new_polygons)
                        print(gdf_new)
                        
                
                        for _, polygon in gdf_new.iterrows():
                            # Trouver les points dans le polygone
                            points_within = gdf[gdf.geometry.within(polygon.geometry)]

                            # Ajouter un champ pour indiquer un changement dans ces points
                            for index in points_within.index:
                                df.at[index, 'change'] = True
                        # Vérifier les points marqués pour changement
                print(df)
                st.write("i am putting the changes in the first dataframe")
                st.dataframe(df,height=DATAFRAME_HEIGHT)
                

                # df_final = complete_df.merge(df["LON","LAT","change"], how="left")
                complete_df['change'] = df['change']
                df_final = complete_df.reset_index(drop=True)
                
                # Changes applied on the dataframe
                df_final.loc[df_final["change"], "OCCSOL"] = occsol
                df_final.loc[df_final["change"], "ZONECL"] = zone_cli
                df_final.loc[df_final["change"], "NATSOL"] = natsol
                df_final.loc[df_final["change"], "NATSOL2"] = natsol2

                possible_value = np.arange(min_hauta, max_hauta)
                associated_proba = [1/4**(i+1) for i, value in enumerate(possible_value)]
                total = sum(associated_proba)
                normalized_proba = [p / total for p in associated_proba]
                
                
                print(possible_value)
                print(associated_proba)

                df_final.loc[df_final["change"], "HAUTA"] = df_final.loc[df_final["change"]].apply(lambda x: np.random.choice(a=possible_value, p=normalized_proba), axis=1)
                st.write("All changes still with the change column")
                st.dataframe(df_final, height=DATAFRAME_HEIGHT)
                df_final = df_final.drop("change", axis=1)
                st.dataframe(df_final, height=DATAFRAME_HEIGHT)
                df_final.to_csv("CSV/Changed_df.csv",index=False)
                st.success("Finale CSV saved to CSV/Changed_df.csv")
         
 