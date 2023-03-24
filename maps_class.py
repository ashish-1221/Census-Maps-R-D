import streamlit as st
from gdrive import *
import geopandas as gd
import os
import pandas as pd
from scipy.spatial import cKDTree
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D


@st.cache_data
def return_v_gdf():
    vill_shp = gd.read_file("data/shapefiles/"+"SHP_MadhyaPradesh"+"/"+"VILLAGE_TOWN.shp")
    return vill_shp

@st.cache_data
def return_ac_gdf(ac):
    ac_shp = gd.read_file("data\shapefiles\SHP_MadhyaPradesh\AC_POST.shp")
    return ac_shp

def rename(vill_shp,ac_mapping_file):
            vill_shp = vill_shp[['OID_','AC_POST','AC_NAME_PO','NAME11','geometry']]
            vill_shp = vill_shp.rename(columns={'OID_':'V_ID','AC_POST':'AC','AC_NAME_PO':'AC NAME','NAME11':'V_NAME'})
            ac_mapping_file = ac_mapping_file[['AC','Village Id','Village Name','Mapped Locality','AC.1','booth 2022','Locality','Mandal 01-Dec-22']]  
            ac_mapping_file = ac_mapping_file.rename(
        columns={
            'Village Id':'V_ID',
            'Village Name':'V_NAME',
            'booth 2022':'BOOTH_NO',
            'Locality':'LOCALITY',
            'Mapped Locality':'MAPPED LOCALITY',
            'Mandal 01-Dec-22':'MANDAL'})
            return ac_mapping_file,vill_shp

# Mandal Boundary map


def mandal_maps(ac, ac_shape_file, ac_name, final_map_folder_path):
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    cmap = plt.cm.Set1

    # Plotting mandal and color each category via cmap
    ac_shape_file_shp = ac_shape_file.dissolve('MANDAL', as_index=False)
    ac_shape_file_shp.plot(ax=ax, cmap=cmap, linewidth=1.2, edgecolor='black')
    (ac_shape_file.plot(ax=ax, color='None', linewidth=0.1, edgecolor='grey'))

    # Adding legend
    legend_labels = ac_shape_file_shp['MANDAL'].to_list()
    legend_colors = cmap(np.linspace(0, 1, len(legend_labels)))
    lines = [Line2D([0], [0], marker="s", markersize=10, markeredgecolor='black', linewidth=0, color=c) for c in
             legend_colors]

    plt.legend(lines, legend_labels, prop={'size': 8}, framealpha=0, handletextpad=0.1,
               bbox_to_anchor=(1.05, 0), loc="lower left", labelspacing=1.2)

    # Adding level
    ac_shape_file['rep'] = ac_shape_file['geometry'].representative_point()
    ac_shape_file['centroid'] = ac_shape_file['geometry'].centroid
    za_points_1 = ac_shape_file.copy()
    za_points_1.set_geometry('rep', inplace=True)
    za_points_2 = ac_shape_file.copy()
    za_points_2.set_geometry('centroid', inplace=True)

    texts = []
    for x, y, label in zip(za_points_1.geometry.x,
                           za_points_1.geometry.y,
                           za_points_1["V_ID"]):  # +za_points_2.geometry.x)/2,+za_points_2.geometry.y)/2

        fp = matplotlib.font_manager.FontProperties(
            fname=r"fonts\FiraSans-ExtraBold.ttf")

        texts.append(plt.text(x, y, label, fontproperties=fp, horizontalalignment='center',
                              fontsize=2.3,  # ))
                              path_effects=[pe.withStroke(linewidth=0.6,
                                                          foreground="white")]))

    # Adding title
    plt.title(f'AC -{ac} ({ac_name}) || Mandal Boundary')
    ax.axis('off')
    st.pyplot(fig)
    # Save the map into mandal boundary folder
    if not os.path.exists(final_map_folder_path + "\\" + "mandal boundary map"):
        os.makedirs(final_map_folder_path + "\\" + "mandal boundary map")
        plt.savefig(final_map_folder_path + "\\" + "mandal boundary map" + "\\" + str(ac) + ".png",
                    bbox_inches='tight', dpi=600)
    else:
        plt.savefig(final_map_folder_path + "\\" + "mandal boundary map" + "\\" + str(ac) + ".png",
                    bbox_inches='tight', dpi=600)


class mapping_files():
    def __init__(self,base_retro,ac_mapping_file,vill_shp):
        self.base_retro = base_retro
        self.ac_mapping_file = ac_mapping_file
        self.vill_shp = vill_shp
        
    
    def rename(self):
            vill_shp = vill_shp[['OID_','AC_POST','AC_NAME_PO','NAME11','geometry']]
            vill_shp = vill_shp.rename(columns={'OID_':'V_ID','AC_POST':'AC','AC_NAME_PO':'AC NAME','NAME11':'V_NAME'})
            ac_mapping_file = ac_mapping_file[['AC','Village Id','Village Name','Mapped Locality','AC.1','booth 2022','Locality','Mandal 01-Dec-22']]  
            ac_mapping_file = ac_mapping_file.rename(
        columns={
            'Village Id':'V_ID',
            'Village Name':'V_NAME',
            'booth 2022':'BOOTH_NO',
            'Locality':'LOCALITY',
            'Mapped Locality':'MAPPED LOCALITY',
            'Mandal 01-Dec-22':'MANDAL'})
            return ac_mapping_file,vill_shp
    ##  Creation of two df from mapping file with required columns and dropping NaN values from df_man and df_vill
    ## (Mapping File DataFrame)->(df_man,df_vill)(done)
    def basic_correction_and_explode(self):
        
        def mapped_locality(df_vill_ex, df_man, vill_shp):
            df_loc_man = df_vill_ex.merge(
                df_man, how='left', left_on='MAPPED LOCALITY', right_on='LOCALITY')
            df_loc_man = df_loc_man.drop_duplicates()
            df_loc_man['V_ID'] = df_loc_man['V_ID'].astype(
                'int')
            
            for i in df_loc_man[df_loc_man['MANDAL'].isnull()].index:
                df_loc_man.loc[i, 'MANDAL'] = 'unmapped' + \
                    "_" + str(df_loc_man.loc[i, 'V_ID'])
            df_final = vill_shp.merge(df_loc_man, how='left', on='V_ID')
            df1 = df_final.drop(
                columns=['AC_y', 'V_NAME_y', 'MAPPED LOCALITY'])
            ac_name = df1['AC NAME'].unique()[0]
            return df1, ac_name
        
        def add_centroid(v_shp):
            v_shp['centroid'] = v_shp['geometry'].to_crs(epsg=3857).centroid.to_crs(epsg=4326)
            v_shp = v_shp.to_crs(epsg=4326)
            return v_shp
    
        def nearest(v_shp_unmapped, merged_file):
            # Finding the nearest PS stations from the t_merged_gdf and v_info_unmapped
            na = np.array(
                list(v_shp_unmapped['centroid'].apply(lambda x: (x.x, x.y))))
            nb = np.array(
                list(merged_file['centroid'].apply(lambda x: (x.x, x.y))))
            
            btree = cKDTree(nb)
            dist, idx = btree.query(na, k=1)
            gdb_nearest_v = merged_file.iloc[idx].drop(
                columns="geometry").reset_index(drop=True)
            gdf = pd.concat(
                [gdb_nearest_v, v_shp_unmapped.reset_index(drop=True)], axis=1)
            return gdf
    

        def implement_nearest_neighbour(df1):
                unmapped_vill_ps_shp = df1[df1['LOCALITY'].isnull() == True]
                ps_cord_gdf = df1.dropna()
                unmapped_vill_shp = add_centroid(
                    unmapped_vill_ps_shp)
                ps_cord_gdf_shp = add_centroid(ps_cord_gdf)
                mapped_vill_ps_cord = nearest(unmapped_vill_shp, ps_cord_gdf_shp)
                mapped_vill_ps_cord.columns = ['VILL_ID_', 'AC_POST_x_', 'AC_NAME_PO', 'NAME11_x_', 'booth_no', 'Locality', 'MANDAL', 'centroid_', 'Village Id', 'AC_POST_x', 'AC_NAME_PO_', 'NAME11_x', 'geometry', 'booth_no_', 'Locality_', 'Mandal_', 'centroid']
                mapped_vill_ps_cord = mapped_vill_ps_cord[[
                        'Village Id', 'AC_POST_x', 'AC_NAME_PO', 'NAME11_x', 'geometry', 'booth_no', 'Locality', 'MANDAL']]
                ps_cord_gdf = ps_cord_gdf.rename(columns={'AC_x':'AC','V_NAME_x':'V_NAME' })
                mapped_vill_ps_cord = mapped_vill_ps_cord.rename(columns={
        'Village Id':'V_ID',
        'AC_POST_x':'AC',
        'AC_NAME_PO':'AC NAME',
        'NAME11_x':'V_NAME',
        'booth_no':'BOOTH_NO',
        'Locality':'LOCALITY',
        
    }
)
                ac_shape_file = pd.concat([mapped_vill_ps_cord, ps_cord_gdf]).reset_index(
                        drop=True).drop(columns=['centroid'])
                return ac_shape_file

        

        #! Make sure to standardize the column names of ac mapping file
        df_vill = self.ac_mapping_file[['V_ID', 'AC','V_NAME', 'MAPPED LOCALITY']]
        df_man = self.ac_mapping_file[['BOOTH_NO', 'LOCALITY', 'MANDAL']]
        # dropping all rows with na valu
        df_vill = df_vill.dropna(how='all', axis=0)
        df_man = df_man.dropna(how='all', axis=0)
         ##   Exploding and Separated "Mapped Locality" Column on 'special_character':(done)
         ##   (df_vill)->(df_vill)
        df_vill['MAPPED LOCALITY'] = df_vill['MAPPED LOCALITY'].astype('str')  # Converting Mapped Locality Column to type 'str'
        df_vill['MAPPED LOCALITY'] = df_vill['MAPPED LOCALITY'].apply(lambda x: list(map(str, x.split('&&'))))  # Splitting the Mapped Locality which has '&&' value in df_vill
        # Exploding the df_vill on Mapped Locality
        df_vill_ex = df_vill.explode('MAPPED LOCALITY', ignore_index=True)
        # Dropping the duplicates from df_vill
        df_vill_ex = df_vill_ex.drop_duplicates()
        vill_shp = self.vill_shp

        df1,ac_name = mapped_locality(df_vill_ex,df_man,vill_shp)
        ac_shape_file = implement_nearest_neighbour(df1)
        
        return ac_shape_file,ac_name
