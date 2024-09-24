from imports import *
from variable import REMAKE_FOLDER
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

def create_rasters_needs(df,filename):
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
    lat_min, lat_max, lon_min, lon_max = get_min_max(df)
    grid_values, pixel_size = create_grid(df,variable=variable)
    transform = from_origin(lon_min, lat_max, pixel_size, pixel_size)

    # Check if the remake folder exists, if not, create it
    if not os.path.exists(REMAKE_FOLDER):
        os.makedirs(REMAKE_FOLDER)
    else:
        print(f"Folder already exists: {REMAKE_FOLDER}")
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



def create_grid(df, variable):
    """
    Create a grid of values using latitude and longitude from the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing LAT and LON columns along with the variable of interest.
        variable (str): Name of the variable (column) from the dataframe to use for grid creation.

    Returns:
        grid_values (np.array): Grid of interpolated values based on LAT, LON, and the variable.
        pixel_size (float): The average pixel size based on latitude differences.
    """ 
    lat_unique, lon_unique = sorted(df['LAT'].unique()), sorted(df['LON'].unique()) 
    pixel_size = np.mean(pd.DataFrame(lat_unique).diff())
    grid_x, grid_y = np.meshgrid(lon_unique, lat_unique)

    points = df[['LAT', 'LON']].values
    values = df[variable].values 

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
    with rasterio.open(path, 'w+', driver='GTiff', height=grid_values.shape[0],
                width=grid_values.shape[1], count=1, dtype=grid_values.dtype,
                crs='EPSG:4326', transform=transform) as destination:
            destination.write(grid_values, 1)
            print(np.nanmin(grid_values))
            min = np.nanmin(grid_values)
            print(np.nanmax(grid_values))
            max = np.nanmax(grid_values)
    st.success("TIF file done")
    return min, max

def save_and_add_raster_to_map(variable, grid_values, transform, complete_path, map):
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