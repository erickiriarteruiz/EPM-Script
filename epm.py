from ctypes import alignment
import streamlit as st
from itertools import groupby
import pandas as pd
import numpy as np
from io import BytesIO
from time import time
start_time = time()
from pandas import notna, read_csv, read_excel, DataFrame, ExcelWriter, concat, merge
from numpy import nan


# Description: This script adds the district code into the EPM file from the stop catalogue 
# Dictionary: 
    # stop_cat: Stop Catalogue File
    # epm_file: EPM file
    # df_: DF of the files


########################################################################################################################################################################################################################################################
############################################################################################## VERSION HISTORY ######################################################################################################################################################################################################
# MVP: Upload both documents and create a df which maps the district code
# Version 1: Convert it into a .txt file
# Version 2: Ensure columns start at the right place (district code - col. 127)
# Version 3: Nan to blank / empty values

########################################################################################################################################################################################################################################################
############################################################################################## PAGE CONFIGURATION ######################################################################################################################################################################################################


st.set_page_config(page_title='EPM Script1',layout='wide')

# Hiding streamlit's footer and menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# # Logos
# from PIL import Image
# cola,colb,colc=st.columns(3)
# image_arriva = Image.open('Arriva logo.png')
# image_optibus = Image.open('Optibus logo.jpg')
# cola.image(image_arriva,width=200)
# colc.image(image_optibus,width=200)


script_title = 'EPM Conversion Script'
st.markdown(f"<h1 style='text-align: center; font-family: Helvetica Neue; color: #004d73;'>{script_title}</h1>", unsafe_allow_html=True)
st.markdown('')
with st.expander(label='Information about this script'):
    st.write('''This script combines the information from the EPM and the Stop Catalogue files. It retrieves the EPM file, but with a new column for the district code. **Note that the mapping is based on the exact stop name.**
    The steps that this script follows are:''')
    st.markdown('')
    st.write('''    
    1. Retrieve from the stop catalogue only the stop names and the district code, while removing any duplicates (unique values)
    2. Create a new column with the stop name reference from the 2nd column on the EPM file (after time information)
    3. Map this new column with the information retrieved in step 1. and once it is mapped, drop the column created in 2.
    4. Button to download the output as an .E03 file, with the correct alignment and position of the content 
    ''')
    st.warning('Note: The outcome will display the columns in the following positions: 11, 46, 58, 66, 76, 88, 95, 11, 12')
    st.markdown('')


col1,col2=st.columns(2)

########################################################################################################################################################################################################################################################
####################################################################################################### Stop Catalogue ###################################################################################################################################################################################


# 1. Upload stops catalogue
stop_cat_file = col1.file_uploader(label='Upload your Stop Catalogue File',type='xlsx')
if stop_cat_file:
    df_stop_cat = pd.read_excel(stop_cat_file,engine='openpyxl')

# 1.1 Create a df with district codes and names
    df_stop_cat_codes = df_stop_cat[['STOP NAME','District Code']]
    df_stop_cat_codes = df_stop_cat_codes.astype(str)


# 1.2 Remove duplicates? - I assume all bus stands will have the same one
    df_stop_cat_codes = df_stop_cat_codes.drop_duplicates()
    df_stop_cat_codes = df_stop_cat_codes.reset_index(drop=True)


########################################################################################################################################################################################################################################################
####################################################################################################### EPM File #########################################################################################################################################################################################


# 2. Upload txt. file
epm_file = col2.file_uploader(label='Upload your EPM File',type=None)

# 2.1 convert it into a df
if epm_file:

# MAKING SURE COLUMN WIDTHS ARE CORRECT IN THE NEXT STATEMENT:
    column_position_0 = [10,35,12,8,10,12,7,21,5]
    df_epm_file = pd.read_fwf(epm_file, header=None, widths=column_position_0)
    epm_file_name=epm_file.name

    df_epm_file[3]=df_epm_file[3].astype(str)
    df_epm_file[3]=df_epm_file[3].str.split('.').str[0]


########################################################################################################################################################################################################################################################
###################################################################################################### Comparison ########################################################################################################################################################################################
disability_var = True
if epm_file and stop_cat_file:
    disability_var = False
button_compare = col1.button(label='RUN CONVERSION',disabled=disability_var)

# 3. Mapping district code with stop name
# 3.1 Extracting the first part of the string to the Stop Names in the EPM File 
if button_compare:
    df_epm_file['First part of str']=df_epm_file[1].str[5:]

# 3.2 Merging based on the stop name and the first part of the string
    df_epm_file = df_epm_file.merge(df_stop_cat_codes,how='left',left_on='First part of str',right_on='STOP NAME')
    df_epm_file = df_epm_file.drop(['First part of str','STOP NAME'],axis=1)
    
    
    
    # for all values within the column District Code
        # if a value is blank and the value in the same row for column 7 is 0000.000Y
            # replace the blank value with the value above
        # After the condition above, if a value is blank 
            # replace the blank value with the value below
    df_epm_file['District Code'] = np.where((df_epm_file['District Code'] == 'nan') & (df_epm_file[7] == '0000.000Y'), df_epm_file['District Code'].shift(1), df_epm_file['District Code'])
    df_epm_file.loc[df_epm_file['District Code']=='nan','District Code'] = df_epm_file['District Code'].shift(-1)

# 3.2.1 Replacing nan values for blanks
    df_epm_file = df_epm_file.astype(str)
    df_epm_file = df_epm_file.replace('nan', '', regex=True)
  
    #position of the longest value in the columns
    pos_0 = df_epm_file[0].str.len().idxmax()
    pos_1 = df_epm_file[1].str.len().idxmax()
    pos_2 = df_epm_file[2].str.len().idxmax()
    pos_3 = df_epm_file[3].str.len().idxmax()
    pos_4 = df_epm_file[4].str.len().idxmax()
    pos_5 = df_epm_file[5].str.len().idxmax()
    pos_6 = df_epm_file[6].str.len().idxmax()
    pos_7 = df_epm_file[7].str.len().idxmax()
    pos_8 = df_epm_file[8].str.len().idxmax()
    pos_9 = 3

    #length of the values defined above
    l_0 = len(df_epm_file.loc[pos_0,0])
    l_1 = len(df_epm_file.loc[pos_1,1])
    l_2 = len(df_epm_file.loc[pos_2,2])
    l_3 = len(df_epm_file.loc[pos_3,3])
    l_4 = len(df_epm_file.loc[pos_4,4])
    l_5 = len(df_epm_file.loc[pos_5,5])
    l_6 = len(df_epm_file.loc[pos_6,6])
    l_7 = len(df_epm_file.loc[pos_7,7])
    l_8 = len(df_epm_file.loc[pos_8,8])
    l_9 = 3

    #position value for new columns
    c_1 = 11 - l_0 - 1 + l_1 - 1
    c_2 = 46 - l_1 - 11 + l_2 - 1
    c_3 = 58 - l_2 - 46 + l_3 - 1
    c_4 = 66 - l_3 - 58 + l_4 - 1
    c_5 = 76 - l_4 - 66 + l_5 - 1
    c_6 = 88 - l_5 - 76 + l_6 - 1
    c_7 = 95 - l_6 - 88 + l_7 - 1
    c_8 = 116 - l_7 - 95 + l_8 - 1
    c_9 = 127 - l_8 - 116 + l_9 - 1

    column_position_1 = [0,c_1, c_2,c_3,c_4,c_5,c_6,c_7,c_8,c_9]

# 3.3 Preview of the document
    with col2.expander('Preview result'):
        st.dataframe(df_epm_file)

# 3.4 Downloading the document
    def left_alignment(df_epm_file, cols=None):
        if cols is None:
            cols = df_epm_file.columns[df_epm_file.dtypes=='object']
        return {col:f'{{:<{df_epm_file[col].str.len().max()}s}}'.format for col in cols}
    a = df_epm_file.to_string(header=False,col_space=column_position_1, formatters=left_alignment(df_epm_file,cols=[0,1,2,3,4,5,6,7,8]), index=False)
    button_download  = col1.download_button(label='Download file', data=a, file_name=epm_file_name)
    
########################################################################################################################################################################################################################################################

