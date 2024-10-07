from utils.imports import *
from utils.variables import REMAKE_FOLDER

def manage_csv(uploaded_file):
    """
    Manage the opening of the CSV file from the temporary file
    Args:
        uploaded_file (UploadedFile) : Dict containing diverse informations about the file
    Returns:
        df (pd.Dataframe) : dataframe containing all the variables
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    df = pd.read_csv(temp_file_path)
    
    return df


def upload_dataframe():
    """
    Handle file uploads from the user, to load the corresponding training file.
    Returns:
        CSV training file.
    """
    st.subheader("Upload your dataframe")
    uploaded_file = st.file_uploader("Choose CSV file you want to change", type=["csv"], accept_multiple_files=False)
    return uploaded_file

def create_rasters_needs(dataframe,filename):
    """
    Create the necessary components to generate a raster from the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing LAT, LON, and the variable to be used for raster creation.
        filename (str): The filename to be used for the output raster file.

    Returns:
        variable (str): The name of the variable to be used for the raster.
        grid_values (np.array): Interpolated grid values based on LAT, LON, and the variable.
        transform (Affine): Affine transformation object for georeferencing the raster.
        complete_path (str): Complete file path for the raster to be saved.
    """
    variable = filename.split("_")[0]
    lat_min, lat_max, lon_min, lon_max = get_min_max(dataframe)
    grid_values, pixel_size = create_grid(dataframe,variable=variable)
    transform = from_origin(lon_min, lat_max, pixel_size, pixel_size)

    # Check if the remake folder exists, if not, create it
    if not os.path.exists(REMAKE_FOLDER):
        os.makedirs(REMAKE_FOLDER)
    else:
        print(f"Folder already exists: {REMAKE_FOLDER}")
        shutil.rmtree(REMAKE_FOLDER)
        os.makedirs(REMAKE_FOLDER)
       
    complete_path = os.path.join(REMAKE_FOLDER,filename)

    return variable, grid_values, transform, complete_path


def get_min_max(df):
    """
    Get the minimum and maximum values for latitude and longitude from the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing all the variables.

    Returns:
        lat_min (float): Minimum latitude value.
        lat_max (float): Maximum latitude value.
        lon_min (float): Minimum longitude value.
        lon_max (float): Maximum longitude value.
    """
    lat_min= df['LAT'].min() 
    lat_max= df['LAT'].max()
    lon_min= df['LON'].min()
    lon_max= df['LON'].max()

    return lat_min, lat_max, lon_min, lon_max



def create_grid(dataframe, variable):
    """
    Create a grid of values using latitude and longitude from the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing LAT and LON columns along with the variable of interest.
        variable (str): Name of the variable (column) from the dataframe to use for grid creation.

    Returns:
        grid_values (np.array): Grid of interpolated values based on LAT, LON, and the variable.
        pixel_size (float): The average pixel size based on latitude differences.
    """ 
    lat_unique, lon_unique = sorted(dataframe['LAT'].unique()), sorted(dataframe['LON'].unique()) 
    pixel_size = np.mean(pd.DataFrame(lat_unique).diff())
    grid_x, grid_y = np.meshgrid(lon_unique, lat_unique)

    points = dataframe[['LAT', 'LON']].values
    values = dataframe[variable].values 

    # Make the grid knowing the pixel size
    grid_values = griddata(points, values, (grid_y, grid_x), method='linear')
    # This is to invert the direction of the raster which is not good
    grid_values = grid_values[::-1, :]      


    return grid_values, pixel_size

def write_raster(path, grid_values, transform):
    """
    Function to create a raster from a dataframe

    Args:
        path  (string) : The path to take to save the raster
        grid_values (ndarray) : containing the LST values to write the raster properly
        transform (Affine) : Object that defines how to convert from geographic coordinates to pixel indices in a raster image.
    Returns:
        min (float) : Minimum of temperature observed in the dataframe
        max (float) : Maximum of temperature observed in the dataframe
    """
    min = 0
    max = 0
    try:
        with rasterio.open(path, 'w', driver='GTiff', height=grid_values.shape[0],
                           width=grid_values.shape[1], count=1, dtype=grid_values.dtype,
                           crs='EPSG:4326', transform=transform) as destination:
            destination.write(grid_values, 1)
            min = np.nanmin(grid_values)
            max = np.nanmax(grid_values)
            print(type(destination))
            print(f"Raster written successfully: {path}")
    except Exception as e:
        print(f"Error while writing raster: {e}")
    finally:
        print(f"File closed: {path}")

    st.success("TIF file creation complete")
    return min, max

def save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map:leafmap.Map):
    """
    Save the grid values to a raster file and add the raster to the map.
    
    Args:
        variable (str): The variable name, used to determine raster properties (e.g., LST, ALB).
        grid_values (np.array): The grid values to be saved in the raster file.
        transform (Affine): The affine transformation for georeferencing.
        complete_path (str): The file path where the raster will be saved.
        map (leafmap.Map): Map object where the raster will be displayed.

    Returns:
        map (leafmap.Map): The updated map with the new raster layer.
    """
    min, max = write_raster(path=complete_path, grid_values=grid_values, transform=transform)
    if variable=="ZONECL":
        map.add_raster(complete_path, indexes=1, colormap='jet_r', layer_name=variable, opacity=1, vmin=min, vmax=max)  
    else:
        map.add_raster(complete_path, indexes=1, colormap='jet', layer_name=variable, opacity=1, vmin=min, vmax=max)  
    return map


def build_the_raster(map, complete_df, selected_variable):
    """
    Builds and adds a raster to a given map based on the selected variable from a DataFrame.

    Args:
        map (leafmap): The map object where the raster will be added .
        complete_df (pd.DataFrame): The DataFrame containing the data used to create the raster.
        selected_variable (str): The name of the variable in the DataFrame to use for raster creation.

    Returns:
        map: The updated map with the newly created raster layer.
    """
    with st.status("Creating the corresponding raster...", expanded=True):
        st.write("Gathering raster needs...")
        variable, grid_values, transform, complete_path = create_rasters_needs(complete_df,f'{selected_variable}_remake.tif')
        st.write("Writing and saving raster...")
        map = save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map)
        st.session_state.selected_variable = selected_variable
        st.session_state.map = map

    return map


def tuning_variables_value_urb():
    """
    This function displays a user interface using Streamlit widgets to allow the user to set and tune
    certain variables like OCCSOL and ZONECL to the right value for an urban extension.
    The user has the option to disable inputs, depending on the toggle state.
    Returns:
        occsol (int): The value selected for OCCSOL (Occupancy solution).
        zone_cli (int): The value selected for ZONECL (Climate zone).
        min_hauta (int): The minimum value for the HAUTA interval.
        max_hauta (int): The maximum value for the HAUTA interval.
    """
    activated = not st.toggle("Authorize user to change values",value=False)
    occsol =  st.number_input("OCCSOL", min_value=0, max_value=6, value=6, disabled=activated)
    zone_cli = st.number_input("ZONECL", min_value=0, max_value=16, value = 6, disabled=activated)
    st.write("Random interval for HAUTA")

    col1, col2 = st.columns(2)
    with col1:
        min_hauta = st.number_input("HAUTA min", min_value=0, max_value=20, value = 0, disabled=activated)
    with col2:
        max_hauta = st.number_input("HAUTA max",min_value=min_hauta, max_value=20, value = min_hauta + 5, disabled=activated)

    return occsol, zone_cli, min_hauta, max_hauta

def tuning_variables_value_nbs():
    """
    This function displays a user interface using Streamlit widgets to allow the user to set and tune
    certain variables like OCCSOL and ZONECL to the right value for NBS.
    The user has the option to disable inputs, depending on the toggle state.
    Returns:
        occsol (int): The value selected for OCCSOL (Occupancy solution).
        zone_cli (int): The value selected for ZONECL (Climate zone).
        min_hauta (int): The minimum value for the HAUTA interval.
        max_hauta (int): The maximum value for the HAUTA interval.
    """

    activated = not st.toggle("Authorize user to change values",value=False)
    occsol =  st.number_input("OCCSOL", min_value=0, max_value=6, value=1, disabled=activated)
    zone_cli = st.number_input("ZONECL", min_value=11, max_value=17, value = 11, disabled=activated)
    st.write("Random interval for HAUTA")

    col1, col2 = st.columns(2)
    with col1:
        min_hauta = st.number_input("HAUTA min", min_value=5, max_value=45, value = 20, disabled=activated)
    with col2:
        max_hauta = st.number_input("HAUTA max",min_value=min_hauta, max_value=50, value = min_hauta + 10, disabled=activated)

    return occsol, zone_cli, min_hauta, max_hauta


def make_probs_for_tree_distrib(min_hauta, max_hauta):
    """
    Generates a probability distribution over a range of values based on a decaying exponential pattern.
    
    The function creates a list of possible values between `min_hauta` and `max_hauta` (exclusive of `max_hauta`),
    and assigns probabilities to each value that decrease exponentially as the values increase.
    The probabilities are then normalized to sum to 1.
    
    Args:
        min_hauta (int): The minimum value for the distribution.
        max_hauta (int): The maximum value (exclusive) for the distribution.
    
    Returns:
        normalized_proba (list of float): A list of normalized probabilities for each value.
        possible_value (numpy.ndarray): An array of possible values in the range [min_hauta, max_hauta).
    """

    possible_value = np.arange(min_hauta, max_hauta)
    associated_proba = [1/2**(i+1) for i, value in enumerate(possible_value)]
    total = sum(associated_proba)
    normalized_proba = [p / total for p in associated_proba]

    return normalized_proba, possible_value 


def value_attribution(df_final, occsol, zone_cli, possible_value, normalized_proba):
    """
    Assigns specific values to the columns "OCCSOL", "ZONECL", and "HAUTA" in a given DataFrame
    where a condition is met (where the 'change' column is True).

    - "OCCSOL" and "ZONECL" columns are assigned fixed values (`occsol` and `zone_cli`).
    - "HAUTA" is assigned a value randomly chosen from the `possible_value` list based on the 
      given probability distribution `normalized_proba`.

    Args:
        df_final (pd.DataFrame): The DataFrame where values will be updated.
        occsol (int): The value to assign to the "OCCSOL" column for rows where 'change' is True.
        zone_cli (int): The value to assign to the "ZONECL" column for rows where 'change' is True.
        possible_value (array-like): List or array of possible values for the "HAUTA" column.
        normalized_proba (list of float): List of probabilities corresponding to each value in `possible_value`.
    
    Returns:
        pd.DataFrame: The updated DataFrame with the assigned values.
    """
    df_final.loc[df_final["change"], "OCCSOL"] = occsol
    df_final.loc[df_final["change"], "ZONECL"] = zone_cli
    df_final.loc[df_final["change"], "HAUTA"] = df_final.loc[df_final["change"]].apply(lambda x: np.random.choice(a=possible_value, p=normalized_proba), axis=1)

    return df_final