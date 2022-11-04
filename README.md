# EPM-Script
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
# Version 4: Condition for blank values on district code
