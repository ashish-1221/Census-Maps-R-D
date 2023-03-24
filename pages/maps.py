import os
import streamlit as st
import pandas as pd
import geopandas as gd
import numpy as np
from scipy.spatial import cKDTree
from maps_class import *
import os.path
import pandas as pd
from gdrive import *


## Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False


#! Input Parameters for Generaating Maps
## Input Consolidation for the Maps.py 
## (User Input(ST_SHP,Base Folder ID,Mapping Folder ID,Map Generation Format,ST_NAME,ELection Type,Election Year,AC))
## Data Returned (State Shape File,Base Retro Data(AC Filtered),Mapping FIle(rer. AC),ST_NAME,Map Type,Election Year,Election Type,AC)

with st.container():
    #! Download the shape files from EDM-DB/Internal team Resources/00_ShapeFiles folder
    # Creating a drive_object instance of class drive_api() in gdrive.py
    drive_object = drive_api()
    drive_object.main()  # Calling main Function in drive_api class
    folders = drive_object.connect_EDM_DB()  # Connecting to EDM Folder
    print(folders)
    itr_info = {}  # getting the information for the Internal team Resources Folder
    for f_id, f_info in folders.items():
        if f_id == 'Internal Team Resources':
            itr_info['name'] = f_id
            for key in f_info:
                if key == 'id':
                    itr_info['id'] = f_info[key]
                else:
                    itr_info['parent'] = f_info[key]
    print(itr_info)
    # Getting the information of all subfolders in Internal Team Resources Folder
    folders = drive_object.search_a_folder(itr_info['id'])
    #Getting all the info of  00_Shapefiles folder in Internal Team Resources Folder
    folder_info = {}
    for item in folders:
        if item['name'] == '00_Shapefiles(Copy)':
            folder_info['name'] = item['name']
            folder_info['id'] = item['id']
            folder_info['parent'] = item['parents']
    print("\n\n")
    print(folder_info)
    # Getting info of all subfolders in the 00_ShapeFiles folder
    folders = drive_object.search_a_folder(folder_info['id'])
    print("\n\n")
    print(folders)
    # Creating a Select box to Select the State to make Shape of

    # Creating a set of all file names of shape files
    shp_names = [None]
    for item in folders:
        shp_names.append(item['name'])
    print("\n\n")
    print(shp_names)

    # Downloading the shape file and storing it in data/shapefiles folder for the selected state
    ## Select the shape file of the state you want maps for (Streamlit Front end Section)
    sel_option = st.sidebar.selectbox(
        "Select the Shape File of the State",
        (shp_names),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
    )
    print(f"\n\n{sel_option}")
    ##Getting the folder info of the required state (useful:name)
    shape_info = [item for item in folders if item['name'] == sel_option][0]
    print("\n\n")
    print(shape_info)
    # create a new folder with state name for the downloads
    exist = False
    try:
        dir = "data/shapefiles/"+shape_info['name']+"/"
        os.mkdir(dir)
        print("Directory is created")
    except FileExistsError:
        print("Directory already exists")
        exist = True
    # Getting all subfolder info inside the state folder
    folders = drive_object.search_a_folder(shape_info['id'])
    print("\n\n")
    print(folders)
    # TODO: To make sure when the drive is updated with new files to include those files in this data
    # TODO : To make sure if all file exists do not download it again and again
    # Download all files present in the subfolder info
    if exist == False:
        drive_object.export_all_files(folders[0]['id'], dir)

    # Get the AC values from the ac_shape_file
    path = "data/shapefiles/"+shape_info['name']+"/"+"AC_POST.shp"
    ac_shp = pd.DataFrame(gd.read_file(path).drop(["geometry"], axis=1))
    ac_list = set(sorted(ac_shp['AC_NO'].to_list()))

    ## Get the Folder id of the Base Retro Path
    base_retro_folder_id = st.sidebar.text_input(
        "Base Retro Folder ID", label_visibility=st.session_state.visibility, disabled=st.session_state.disabled, key="5")
    ## GEt the Folder Id of the Mapping File
    mapping_file_folder_id = st.sidebar.text_input(
        "Mapping Files Folder ID", label_visibility=st.session_state.visibility, disabled=st.session_state.disabled, key="6")

    ## Select the Map format you want
    map_type = st.sidebar.radio("Choose Map Generation Format",
                                ("Mandal Map",
                                 "Win/Loss",
                                 "Vote Share",
                                 "Margin")
                                )
    print(f"\n\n{map_type}")
    ## Get Election Year, Election Type and State Name and AC
    # Store the initial value of widgets in session state
    # Create a container for state_name
    c1, c2, c3, c4 = st.columns(4)
    # Get State Name
    #with c1.container():
    #c1.subheader("State Name")
    st_name = c1.text_input("State Name", label_visibility=st.session_state.visibility,
                            disabled=st.session_state.disabled, key="1")
    # Get Election Type
    #with c2.container():
    #c2.subheader("Election Type")
    election_type = c2.selectbox(
        "Election Type", ('LS', 'VS', 'Bye-polls'), key="2")
    # Get Election year
    #with c3.container():
    #c3.subheader("Election year")
    election_year = c3.text_input(
        "Election year", label_visibility=st.session_state.visibility, disabled=st.session_state.disabled, key="3")
    # AC Select
    #with c4.container():
    ac = c4.selectbox("AC", ac_list, key="4")

    #! Submit button 
    submitted = st.button('Submit')
    if submitted:
    
    
        ## Data Collection for calling the mandal maps class
        # Data Needed -> ST_NAME,Election Year,Election Type, AC, Village Shape File(AC), Base Retro File(AC),Mapping File(AC)
        
        # Mapping Files of the required AC
        print("\n\nFound the AC File")
        print("Mapping File of the Excel Info")
        mapping_files_excel_list = drive_object.search_a_folder_q_param(
            f"mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and '{mapping_file_folder_id}' in parents and name contains '{ac}'")
        for file in mapping_files_excel_list:
            if (file['name'].split("."))[0] == str(ac):
                ac_mapping_file_info = file
        print(ac_mapping_file_info)
    
        # Base Retro Data of the required_file (AC Filtered)
        base_retro_excel_list = drive_object.search_a_folder_q_param(
            f"mimeType='text/csv' and '{base_retro_folder_id}' in parents")
        for file in base_retro_excel_list:
            if str(st_name) in file['name']:
                if str(election_year) in file['name']:
                    if str(election_type) in file['name']:
                        base_retro_file_info = file
        print("\n\n Base Retro File Found")
        print(base_retro_file_info)
        
        ## Download the Base retro file and mapping file of the AC
        base_retro_folder_path = "data/baseretro/"
        mapping_file_folder_path = "data/mappingfile/"
        ac_mapping_file = export_the_file(ac_mapping_file_info,mapping_file_folder_path)
        base_retro_data = export_the_file(base_retro_file_info,base_retro_folder_path)
        base_retro_data = base_retro_data.loc[base_retro_data['AC Number']==int(ac)]

        ## Calling the Mandal Maps Function to plot a map
        
        st.write(shape_info)
        vill_shp = pd.DataFrame(gd.read_file(
            "data/shapefiles/"+shape_info['name']+"/"+"VILLAGE_TOWN.shp").drop(["geometry"], axis=1))
        st.dataframe(vill_shp)
        mandal_map = mapping_files()
        ac_mapping_file = mandal_map.first_one(ac_mapping_file)
        df_vill_ex,df_man = mandal_map.basic_correction_and_explode(ac_mapping_file)
        df1,ac_name = mandal_map.mapped_locality(df_vill_ex,df_man,vill_shp)
        ac_shape_file = mandal_map.implement_nearest_neighbour()
        st.dataframe(ac_shape_file)
        








#Performing Sjoin to find the Booths presents inside
#each village map (geometry) polygon"""

# Performing spatial join
def s_join(t_merged_gdf, v_info):
    pointInPolys_2 = gd.sjoin(t_merged_gdf, v_info,
                              how='right', predicate='within')
    pointInPolys_2 = pointInPolys_2.iloc[:, 1:]

    df = pd.DataFrame(pointInPolys_2)
    ## Separating the df DF based on null value condition in CAPI Sheet present in t_merged
    ## Contains the info all villages with values
    df1 = df[~df['Mandal'].isna()]
    df2 = df[df['Mandal'].isna()]  ## Comtains the info of all NaN villages
    return df1, df2

## Performing nearest neighbour analysis
def nearest(v_shp_unmapped, merged_file):
    ## Finding the nearest PS stations from the t_merged_gdf and v_info_unmapped
    nA = np.array(list(v_shp_unmapped['centroid'].apply(lambda x: (x.x, x.y))))
    nB = np.array(list(merged_file['geometry'].apply(lambda x: (x.x, x.y))))
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdb_nearest_v = merged_file.iloc[idx].\
        drop(columns="geometry").\
        reset_index(drop=True)
    gdf = pd.concat(
        [gdb_nearest_v, v_shp_unmapped.reset_index(drop=True)], axis=1)
    return gdf




# ## Read the Shape files
# v_shp = gd.read_file(r"data\VILLAGE_TOWN.shp")
# ## State Shape file reading
# st_shp = gd.read_file(r"data\STATE.shp")
# ## AC shape file reading
# ac_shp = gd.read_file(r"data\AC_POST.shp")

# ## Getting the required columns from the files
# v_shp = v_shp.iloc[:, [0, 5, 10, -1]]
# st_shp = st_shp.iloc[:, [0, 1, 2, -1]]
# ac_shp = ac_shp.iloc[:, [0, 1, 2, -1]]

# ## Converting the CRS
# ac_shp = ac_shp.to_crs(epsg=4326)
# st_shp = st_shp.to_crs(epsg=4326)
# v_shp = v_shp.to_crs(epsg=4326)


# ## Adding centroid to village_shape file
# v_shp['centroid'] = v_shp['geometry']\
#     .to_crs(epsg=3857)\
#     .centroid.to_crs(epsg=4326)
# v_shp = v_shp.to_crs(epsg=4326)

# capi_file = pd.read_csv(r"data\capi_file_master.csv",skiprows=1)
# columns = st.multiselect("Select Columns:-",capi_file.columns)
# capi_file = capi_file[columns]


# ## Merging the capi_file and the booth_file
# booth_file = pd.read_csv(r"data\booth_loc_master.csv")
# booth_file['key'] = booth_file['key'].str.replace(" ","")
# merged_file= pd.merge(capi_file,booth_file,how='outer',on='key')

# ##Filling the nan values
# merged_file['Latitide']=merged_file['Latitide']\
#         .fillna(merged_file.groupby('Mandal')['Latitide']\
#                 .transform(('mean')))
# merged_file['Longitude']=merged_file['Longitude']\
#         .fillna(merged_file.groupby('Mandal')['Longitude']\
#                 .transform(('mean')) )
        
# ##Converting the merged_file to geodataframe
# merged_file = gd.GeoDataFrame(merged_file,\
#                     geometry=gd.points_from_xy(merged_file.Longitude,\
#                                                merged_file.Latitide))
# merged_file = merged_file.set_crs(epsg=4326)




# ##Performing Sjoin on merged_file and village shape file
# mapped_merged_file_df,unmapped_merged_file_df = s_join(merged_file,v_shp)

# ## Getting the info of all villages shapes which are 
# ## unmapped capi+Booth_info
# unmapped_v_list = unmapped_merged_file_df['TR_ID'].to_list()
# v_shp_unmapped = v_shp[v_shp['TR_ID'].\
#                              isin(unmapped_v_list)]
       
# ## Finding the values of CAPI sheet for the unmapped villages
# unmapped_merged_file_df = nearest(v_shp_unmapped,merged_file)
       
# ## Conacating the unmapped and mapped villages
# v_map = pd.concat([unmapped_merged_file_df,mapped_merged_file_df],axis=0)

# m2 = folium.Map(location=[23.745127,91.746826],tiles='cartodb positron',zoom_start=8)
# acs_list = list(set(v_shp['AC_POST'].to_list()))
# acs_list = sorted(acs_list)
# acs_choice = st.multiselect("Choose AC:-(Single Selection Only)", acs_list)
# df1 = v_shp[v_shp['AC_POST'].isin( (acs_choice))]
# fg1 = folium.FeatureGroup(name='villages')



# ## Search for spreadsheet in the required folder
# ## Open and read the r2.csv
# ## file_list = search_file(folder_id=)

# ## ## See the sheets in folder_id
# ## for file in file_list:
# ##     if file['name'].split(".")[0] in acs_choice:
# ##         link_for_mapping_sheet = file['webViewLink']
        
        
# ## if st.button('Open Booth Mapping Sheet'):
# ##     webbrowser.open_new_tab(link_for_mapping_sheet)
# for _, r in df1.iterrows():
#         ## Without simplifying the representation of each borough,
#         ## the map might not be displayed
#         sim_geo = gd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
#         geo_j = sim_geo.to_json()
#         geo_json = (folium.GeoJson(data=geo_j,
#                                style_function=lambda x: {'fillColor': 'Yellow', 'color': 'black', 'weight': '1.5', 'fillOpacity': '0.1'}))
#         folium.Tooltip(r['TR_ID'],sticky=True).add_to(geo_json)
#         fg1.add_child(geo_json)
# m2.add_child(fg1)
# fg2 = folium.FeatureGroup(name='PS Station')
# ac_choice = [float(i) for i in acs_choice]
# merged_file = merged_file[merged_file['AC No_x'].isin(ac_choice)]
# for i in merged_file.index:
#     fg2.add_child(folium.Marker(location=[merged_file['Latitide'][i], merged_file['Longitude'][i]],
#                                     popup="PS Name"+":-"+str(merged_file['Point'][i])+"\t" +
#                                         "Locality"+":-"+str(merged_file['locality'][i]) +
#                                     "Mandal:-"+str(merged_file['Mandal'][i]))
#                       )
#     m2.add_child(fg2)
# fg3 = folium.FeatureGroup(name='ACs')
# ac_shp = ac_shp[ac_shp['AC_NO'].isin(ac_choice)]
# for _,r in ac_shp.iterrows():
#         sim_geo = gd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
#         geo_j = sim_geo.to_json()
#         geo_json = (folium.GeoJson(data=geo_j,\
#                            style_function=lambda x: {'fillColor': 'Blue','color':'black','weight':'2','fillOpacity':'0.05'}))
#         folium.Popup("<a href=https://edm-electoral.s3.ap-south-1.amazonaws.com/census_maps/"+str(r['AC_NO'])+".xlsx> Mapping Sheet < /a >").add_to(geo_json)
#         fg3.add_child(geo_json)
# m2.add_child(fg3)    

# folium.LayerControl(collapsed=True).add_to(m2)
# output = folium_static(m2,width=1100,height=500)

# if st.button("Booth Info for the AC"):
#     merged_file_df = merged_file.copy()
#     merged_file_df = merged_file_df.drop(columns='geometry')
#     st.dataframe(merged_file_df)
    
    
# """Base retro, village shape files, AC-Village Locality Mapping-> next steps"""