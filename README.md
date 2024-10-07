<div style="text-align: center;">
    <h1>Interactive App to change soil properties</h1>
</div>


This application allows you to make changes on the soil to simulate a new landcover, in case you want to see the impact of an urban extension or an NBS on the location you want

## Features

- Visualize variables of your dataframe
- Draw a polygon on the surface you want to change landcover
- Chose certain variable to change within a defined interval
- Transform the dataframe which will automatically be saved

## Install
You should install miniconda to not have any problem with the installation as it will contain everything you need and well separate from anything else that could interfer. Interence between packages is the most annoying problem when making installation.

## Environment

If you don't have miniconda install it, and set it up correctly.

1. Create your conda environment
```
conda create --name env_name python=3.12
```
2. Acitvate it
```
conda activate env_name
```

3. Install the needed packages
```
conda install --file .\requirements.txt     
```

## Launch the app
```
streamlit run '.\Urban Extension.py'
```