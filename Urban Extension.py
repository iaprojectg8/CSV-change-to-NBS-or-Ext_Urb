from utils.variable import VARIABLES_LIST, DATAFRAME_HEIGHT
from utils.imports import *
from tools import *
from session_variables import *

csv_file = upload_dataframe()
if csv_file:
    # Create a Leafmap map
    map = leafmap.Map()
            
    # Create the dataframe from the uploaded file
    df = manage_csv(uploaded_file=csv_file)
    df = df[["LAT", "LON", "LST"]]
    # Create the geometry column from latitude and longitude
    df['geometry'] = df.apply(lambda row: Point(row['LON'], row['LAT']), axis=1)
    if 'change' not in df.columns:
        df['change'] = False  # Initialize the column

    # Convert the DataFrame to a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry='geometry')
    print(gdf)
        
    st.dataframe(df, height=DATAFRAME_HEIGHT)
    selected_variable = st.selectbox(label="Chose a variable to observe",options=VARIABLES_LIST)
    if selected_variable != st.session_state.selected_variable:
    
        variable, grid_values, transform, complete_path = create_rasters_needs(df,f'{selected_variable}_remake.tif')
        save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map)


        map.add_layer_control()
        st.session_state.map = map
        # Afficher la carte dans Streamlit
        st_component = st_folium(map, width="100%")
        st.session_state.selected_variable = selected_variable
    else:
        st_component = st_folium(st.session_state.map, width="100%")

    # Gestion des polygones dessinés
    drawn_polygons = map.st_draw_features(st_component=st_component)
    print(drawn_polygons)

    if drawn_polygons:  # Si des polygones sont dessinés
        # Initialiser une liste pour stocker les polygones
        new_polygons = []
        
        # Parcourir les polygones dessinés


        ### Voir ça dans le train mais on entre jamais dans la condition.
        for drawn_polygon in drawn_polygons:
            print(drawn_polygon)

            if "geometry" in drawn_polygon:
                print("iam in geometry")
                geometry = drawn_polygon['geometry']
                if 'Polygon' in  geometry['type']:
                    polygons = geometry['coordinates']
                    for polygon_coordinates in polygons:
                        new_polygons.append(Polygon(polygon_coordinates))

                print("coucou")
                print(new_polygons)
            
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
        st.write("i am changing something")
        st.dataframe(df,height=DATAFRAME_HEIGHT)
        df = df.drop("geometry", axis=1)
        st.dataframe(df, height=DATAFRAME_HEIGHT)