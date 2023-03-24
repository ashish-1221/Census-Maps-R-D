from winlossmap.backend import CensusMap

# "C:\Users\rahul\Downloads\drive-download-20230316T055405Z-001"
# "C:\Users\rahul\OneDrive\Desktop\RJ\Maps\Shape file village clean\vill.shp"
# Plz!!! Enter base retro data file path: "C:\Users\rahul\OneDrive\Desktop\RJ\Base retro segmentation\Final OP\2018_base_segmentation_RJ.csv"
# Plz!!! Enter election year for which you want to generate map: 2018
# Plz!!! Enter LS/VS: VS
# Plz!!! Enter the folder path in which you want to save maps .png file: "C:\Users\rahul\Downloads\maps 16032023"
mapping_file_folder_path = input("Plz!!! Enter mapping file folder path: ")
mapping_file_folder_path = mapping_file_folder_path.replace('"', '')

village_shp_file = input("Plz!!! Enter village shape file path: ")
village_shp_file = village_shp_file.replace('"', '')

base_retro_path = input("Plz!!! Enter base retro data file path: ")
base_retro_path = base_retro_path.replace('"', '')

election_year = input("Plz!!! Enter election year for which you want to generate map: ")

election_type = input("Plz!!! Enter LS/VS: ")

final_map_folder_path = input("Plz!!! Enter the folder path in which you want to save maps .png file: ")
final_map_folder_path = final_map_folder_path.replace('"', '')

# mandal_boundary_map = input("Do you want to generate Mandal Boundary Map ? Enter : yes/no ")
# village_win_loss = input("Do you want to generate village level win loss Map ? Enter : yes/no ")
# village_vs = input("Do you want to generate village level vote share Map ? Enter : yes/no ")
# village_margin = input("Do you want to generate village level margin Map ? Enter : yes/no ")

# interactive console
census_map = CensusMap(mapping_file_folder_path, village_shp_file, base_retro_path, election_year,
                       election_type, final_map_folder_path)
census_map.data()

