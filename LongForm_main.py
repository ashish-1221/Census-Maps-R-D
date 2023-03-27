import streamlit as st
import pandas as pd
import geopandas as gd
from io import StringIO
from gdrive import *


st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
    layout="wide"
)

st.sidebar.title("About")
st.sidebar.info(
    """
    Integrating All workstreams related to EDM-DB Team
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    email:-maharanaashish72@gmail.com | ashish.maharana@inverv.com
    """
)

def show_file_details(uploaded_file):
    file_details = {
        'FileName':uploaded_file.name,
        'FileType':uploaded_file.type
    }
    st.write(file_details)


def upload_file(uploaded_file):
    st.text_input("Enter the name of the file")
        
def state_name_abbvs(name):
    # Read the csv file containing the name of the states and their respective abbreviations
    state = pd.read_csv(r"data\stateList_abbv.csv")
    for ind in state.index:
        if name.lower() == state['dict'][ind].split("_")[0].lower() or \
            name.upper() == state['dict'][ind].split("_")[1].upper():
            return state['dict'][ind]
        
    
    

    
#"""Enter the state """
def start_point():
    name = st.text_input("Enter the State Full Name/Abbreviation","")
    return name

st_name = start_point()
state_dict = state_name_abbvs(st_name)




# """Enter the CAPI Sheet"""    
# st.subheader("Enter the CAPI Sheet")
# uploaded_file = st.file_uploader("CAPI sheet",type=['xlsx'])
# if uploaded_file is not None:
#     show_file_details(uploaded_file)
#     data = pd.read_excel(uploaded_file,sheet_name="Booth Master Data")
#     data.to_csv(r"data\\capi_file_master.csv")
       
        
# """Adding the Booth Location Files"""
# st.subheader("Enter the Booth Lat/Long Sheet")
# uploaded_file = st.file_uploader("Booth Sheet",type=['csv'])
# if uploaded_file is not None:
#     show_file_details(uploaded_file)
#     with open(os.path.join("data","booth_loc_master.csv"),"wb") as f:
#         f.write(uploaded_file.getbuffer())


# """Adding the Shape Files"""
# st.subheader("Enter the Shape Files (All and Required Files)")
# uploaded_files = st.file_uploader("All Shape Files",accept_multiple_files=True)
# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     with open(os.path.join("data",uploaded_file.name),"wb") as f:
#         f.write(uploaded_file.getbuffer())


