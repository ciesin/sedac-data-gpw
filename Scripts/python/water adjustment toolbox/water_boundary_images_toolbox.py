
import argparse
import arcpy
import os
import pandas as pd
from pathlib import Path

from arcgis.features import GeoAccessor, GeoSeriesAccessor
import pandas as pd
import geopandas as gp
import math 
from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib_scalebar.scalebar import ScaleBar
from collections import OrderedDict
import csv
import datetime


# preserve global id
arcpy.env.preserveGlobalIds = True
# blow away output! 
arcpy.env.overwriteOutput = True

#gpwv4 output folder
gpwv4_in_gdb_folder = r'Z:\GPW\GPW5\Preprocessing\Global\gpwv4_updated_boundaries'
in_memory = "in_memory"
#field names
GlobalID = 'GlobalID'
landArea = "LANDAREAKM"
landAreaDiff = "LANDAREAPCTDIFF"
adjArea = "ADJAREAKM"
IDENTITYAREAKM = "WTRIDENTYAREAKM"
WATERAREAKM = "WTRAREAKM"
WATER_TYPE = "WATER_TYPE"
WATER_CODE = "WATER_CODE"

inputBoundaries =os.path.join(in_memory, "inputBoundaries")



def create_folder_if_not_exists(folder_path):
    """
    Checks if a folder exists at the given path and creates it if it doesn't.

    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        arcpy.AddMessage(f"Folder '{folder_path}' created.")
    else:
        arcpy.AddMessage(f"Folder '{folder_path}' already exists.")

def check_for_field(featClass,fieldName):
    """
    Checks feature class for field name given 
    returns a 1 if field is present or 0  if not
    """
    hasField = 0
    desc = arcpy.Describe(featClass)
    fields = desc.fields
    for field in fields:
        # check without case as ArcGIS is not case sensitive
        if field.name.upper() == fieldName.upper():
            hasField = 1
    return hasField     


def add_newField(featClass, newField):
    """
    Adds a new field to feature class
    """
    # If the field doesn't exist, then add it
    try:
        if check_for_field(featClass,newField)==0:
            arcpy.AddField_management(featClass,newField,'DOUBLE')
            #arcpy.AddMessage(f"Added {newField}")
        
        else:
            arcpy.AddMessage(f"{newField} already exists")
            
    except arcpy.ExecuteError:
        arcpy.GetMessages()



def check_null_values_in_column(feature_class_path, column_name):
    """
    Check if any column has a null value
    """
    null_found = False

    with arcpy.da.SearchCursor(feature_class_path, column_name) as cursor:
        for row in cursor:
            if row[0] is None:
                null_found = True
                break

    if null_found:
        arcpy.AddMessage(f"Error: Null values found in the column {column_name} of the feature class {feature_class_path}.")
    


def ingested_fc_name(in_gdb):
        """
        List feature classes in given geodatabase that end with _adj
        Return the first (and only) feature class in the list
        """
        arcpy.env.workspace = in_gdb
        try:
            fc_list = arcpy.ListFeatureClasses('*_adj')
            fc_list = fc_list[0]
            return fc_list
        except Exception as e:
            arcpy.AddWarning(f"Error: {e}")
            return []

if __name__ == '__main__':
    #arcpy.AddMessage('Start of script...')

    #parsing toolbox inputs
    parser = argparse.ArgumentParser(description='Ingest GWv4 or GPWv5 boundaries using ISO codes separated by commas.')
    #arcpy.AddMessage('Parser created...')
    #ISO Parser
    parser.add_argument('ISO_string',
        help='One or more ISO codes separated by a comma. E.g. "ABC, CDE" or "FGH"')
    #Project parser
    parser.add_argument('gpw_project',
        help='Select one of the options.')
    #water layer parser
    parser.add_argument('water_fc', 
        help='Path of water feature class.')
    #output folder parser
    parser.add_argument('out_folder',
        help='Location of the output folder')
    #arcpy.AddMessage('parser arguentsdone.' )
    
    
    args = parser.parse_args()
    arcpy.AddMessage(f'parser created: {args}')

    # passing parsed info to variables
    ISO_parse_string = args.ISO_string
    water_fc = args.water_fc
    out_folder = args.out_folder
    


    #split the ISO parse string to a list by commas
    ISO_parse_list = ISO_parse_string.split(",")
    ISO_list = []
    for iso in ISO_parse_list:
       nname = iso.lower().strip()
       ISO_list.append(nname)

    arcpy.AddMessage(f'ISO Code(s):  {ISO_list}')
    arcpy.env.workspace = in_memory


    #create a CSV from list
    # Get the current time
    current_time = datetime.datetime.now()
    # Format the time to include minutes in the file name
    #formatted_time = current_time.strftime("%Y-%m.%d_%H-%M")
    # Create the CSV file name using the formatted time
    # csv_file_name = f"areas_missing_in_{args.gpw_project}_water_adjustment_{current_time.year}{current_time.month}{current_time.day}_{current_time.hour}{current_time.minute}{current_time.second}.csv"
    # csv_file_path = os.path.join(out_folder, "reports","framework_reports", csv_file_name)
    
    # arcpy.AddMessage(f'csv file path {csv_file_path}')
    # create_folder_if_not_exists(os.path.join(out_folder, "reports","framework_reports"))
    
    # with open(csv_file_path, 'w', newline='') as csvfile:
    #     csv_writer = csv.writer(csvfile)
    #     headers = ['ISO', 'GlobalID', "Area (km)", "Note"]  # Modify based on initial known columns
    #     csv_writer.writerow(headers)

    


    for iso in ISO_list:
        #blank list that will be filled with the error messages    
        framework_list = []
        arcpy.AddMessage(iso)
        
        if args.gpw_project == 'gpwv4':
            GUID = "GUBID"
            gdb_directory = r'Z:\GPW\GPW5\Preprocessing\Global\gpwv4_updated_boundaries'
            ingdb_path = os.path.join(gdb_directory, iso.lower()+'.gdb')
            
            
            stat_fields = f"{WATER_CODE} MAX"

            arcpy.AddMessage(ingdb_path)
            fc_list = []
            arcpy.env.workspace = ingdb_path
            fc_list = arcpy.ListFeatureClasses("*_adj")
            arcpy.env.workspace = in_memory
            fc_list = fc_list[0]
            inputBName = os.path.join(ingdb_path, fc_list)
            arcpy.AddMessage(fc_list)
            # if not fc_list:
            #     arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
            #     subrow = (iso, None, None, 'No input feature classes found.')
            #     framework_list.append(subrow)
            #     with open(csv_file_path, 'a', newline='') as csvfile:
            #         csv_writer = csv.writer(csvfile) # Modify based on initial known columns
            #         csv_writer.writerows(framework_list)
            #     continue
            
            outgdb = os.path.join(gpwv4_in_gdb_folder, iso +'.gdb')
            finalBoundaries = os.path.join(outgdb, f"{fc_list}_wtrA")
            

            # if not arcpy.Exists(outgdb):
            #     try:
            #         # Create the geodatabase
            #         arcpy.CreateFileGDB_management(out_folder, iso +'.gdb')
            #         arcpy.AddMessage(f"Geodatabase '{outgdb}' created successfully.")
            #     except Exception as e:
            #         arcpy.AddWarning(f"Error creating geodatabase: {str(e)}")
            # else:
            #     arcpy.AddMessage(f"Geodatabase '{outgdb}' already exists.")


        elif args.gpw_project == 'gpwv5':
            GUID = "GUID"
            stat_fields = ""
            gdb_directory = r'Z:\GPW\GPW5\Preprocessing\Country'
            ingdb_path = os.path.join(gdb_directory, iso.upper(), 'Ingest','Boundaries', iso.lower()+'_ingest.gdb')
            
            #finding ingested feature class from the GDB
            fc_list = ingested_fc_name(ingdb_path)
            #if no input feature class is found, get out of this ISO's loop
            # if not fc_list:
            #     arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
            #     subrow = (iso, None, None, 'No input feature classes found.')
            #     framework_list.append(subrow)
            #     with open(csv_file_path, 'a', newline='') as csvfile:
            #         csv_writer = csv.writer(csvfile) # Modify based on initial known columns
            #         csv_writer.writerows(framework_list)
                
            #     continue
            # elif fc_list is None:
            #     arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
            #     subrow = (iso, None, None, f"No feature classes found in {ingdb_path}.")
            #     framework_list.append(subrow)
            #     with open(csv_file_path, 'a', newline='') as csvfile:
            #         csv_writer = csv.writer(csvfile) # Modify based on initial known columns
            #         csv_writer.writerows(framework_list)
            #     continue

            finalBoundaries = os.path.join(ingdb_path, f"{fc_list}_wtrA")
            inputBName = os.path.join(ingdb_path, fc_list)
            
            #Check the input feature class has required GUID field, if not, create field and populate by GLobalID field.
            # if check_for_field(inputBName, GUID) == 0 :
            #     arcpy.AddField_management(inputBName, GUID,'GUID')
            #     try:
            #         arcpy.CalculateField_management(inputBName, GUID, f"!{GlobalID}!", "PYTHON3")
            #     except arcpy.ExecuteError:
            #         arcpy.AddWarning(f'calculating GUID from GLobalID failed {arcpy.GetMessages()}')
            #         subrow = (iso, None, None, "calculating GUID from GLobalID failed")
            #         framework_list.append(subrow)
            #         with open(csv_file_path, 'a', newline='') as csvfile:
            #             csv_writer = csv.writer(csvfile) # Modify based on initial known columns
            #             csv_writer.writerows(framework_list)
            #         continue
            # else:
            #     arcpy.AddMessage(f'{GUID} field exists.') 
        
        identityBoundaries = os.path.join(in_memory, f"{fc_list}_wateridenA")
        dissolveFields= [GUID, WATER_TYPE]
        pivot_fields = [GUID]
        cursor_fields = [GUID, adjArea, landArea, WATERAREAKM, landAreaDiff]
        
        searchFields = [GUID,  WATER_TYPE, IDENTITYAREAKM]
        water_count = finalBoundaries + 'ID'


        arcpy.AddMessage(f"inputBoundary name {inputBName}")
        arcpy.AddMessage(f'final boundaries {finalBoundaries}')
        
        arcpy.env.workspace = in_memory
        arcpy.env.overwriteOutput = True

        ##############
        ##############
        ### Primary code starts here 
        ##############
        ##############

        #delete any previous in_memory feature
        if arcpy.Exists(inputBoundaries):
            arcpy.Delete_management(inputBoundaries)

        # try:
            
        #     # create a memory copy of input feature class
        #     arcpy.conversion.FeatureClassToFeatureClass(inputBName, in_memory, 'inputBoundaries')
        #     # arcpy.AddMessage(f'input row count:  {arcpy.GetCount_management(inputBName)}')
        #     # arcpy.AddMessage(f'after copy features, IB count: {arcpy.GetCount_management(inputBoundaries)}')
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        # check_null_values_in_column(inputBoundaries, GUID)

        #arcpy.AddMessage("Performing Identity tool...")

        # try:
        #     # Set the environment to preserve GlobalIDs
        #     arcpy.env.preserveGlobalIds = True
            
        #     # Clip the inputBoundaries to create the clipBoundaries feature class
        #     arcpy.analysis.Identity(inputBoundaries, water_fc, identityBoundaries)
        #     #arcpy.AddMessage(f"Created {finalBoundaries}")
            
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        #arcpy.AddMessage("Performing Dissolve tool...")
        #update WATER_TYPE field where rows that are blank are changed to "L"
        # with arcpy.da.UpdateCursor(identityBoundaries, dissolveFields, where_clause="WATER_TYPE = ''") as cursor:
        #     for row in cursor:
        #         # Set the 'WATER_TYPE' field to "L"
        #         row[1] = "L"
        #         cursor.updateRow(row)

        # # Clean up cursor
        # del cursor
        
        

        # try:
        #     arcpy.analysis.PairwiseDissolve(in_features= identityBoundaries, 
        #                                     out_feature_class=finalBoundaries,
        #                                     dissolve_field=dissolveFields,
        #                                     statistics_fields=stat_fields,
        #                                     multi_part="MULTI_PART",
        #                                     concatenation_separator="")
            
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        # add_newField(finalBoundaries, IDENTITYAREAKM )
        

        # try:
            
        #     arcpy.CalculateField_management(finalBoundaries,IDENTITYAREAKM,'!shape.area@SQUAREKILOMETERS!','PYTHON3')
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        # if args.gpw_project == 'gpwv4':
        #     arcpy.management.AlterField(finalBoundaries, "MAX_WATER_CODE", WATER_CODE, WATER_CODE)
        #     pivot_fields = [GUID, WATER_CODE]
        
        
        
        # pivot_table = f"{finalBoundaries}PivtTbl"
        # if arcpy.Exists(pivot_table):
        #     arcpy.Delete_management(pivot_table)
        
        # arcpy.management.PivotTable(
        #             in_table= finalBoundaries,
        #             fields= pivot_fields,
        #             pivot_field=WATER_TYPE,
        #             value_field=IDENTITYAREAKM,
        #             out_table=pivot_table) 
        # try:
        #     if check_for_field(pivot_table,'ICE')==0:
        #         arcpy.AddField_management(pivot_table,'ICE','DOUBLE')
        #         #arcpy.AddMessage(f"Added ICE column")
            
        #     else:
        #         arcpy.AddMessage(f"ICE column already exists")

        #     if check_for_field(pivot_table,'IW')==0:
        #         arcpy.AddField_management(pivot_table,'IW','DOUBLE')
        #         #arcpy.AddMessage(f"Added IW column")
            
        #     else:
        #         arcpy.AddMessage(f"IW column already exists")
                    
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        # if check_for_field(pivot_table,'L')==1:
        #     arcpy.management.AlterField(
        #         in_table=pivot_table,
        #         field="L",
        #         new_field_name= landArea,
        #         new_field_alias=landArea,
        #         field_type="DOUBLE",
        #         field_length=255,
        #         field_is_nullable="NULLABLE",
        #         clear_field_alias="DO_NOT_CLEAR"
        #     )

        
        
        # try:
        #     if check_for_field(pivot_table, WATERAREAKM)==0:
        #         arcpy.AddField_management(pivot_table,WATERAREAKM,'DOUBLE')
        #         #arcpy.AddMessage(f"Added {WATERAREAKM} column")
            
        #     else:
        #         arcpy.AddMessage(f"{WATERAREAKM} already exists")
                    
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # arcpy.management.CalculateField(
        #     in_table=pivot_table,
        #     field=WATERAREAKM,
        #     expression="calculate_value(!ICE! , !IW!)",
        #     expression_type="PYTHON3",
        #     code_block="""def calculate_value(field1, field2):
        #     if field1 is None:
        #         field1 = 0
        #     if field2 is None:
        #         field2 = 0
        #     return field1 + field2""",
        #     field_type="TEXT",
        #     enforce_domains="NO_ENFORCE_DOMAINS"
        # )
        water_fields = [WATER_TYPE, landArea, WATERAREAKM]
        
        # if arcpy.Exists(water_count):
        #     arcpy.Delete_management(water_count)

        # arcpy.management.CopyFeatures(inputBName, water_count)

        # arcpy.JoinField_management(water_count,  # Input feature class
        #                            GUID, # Field in the input feature class to join on
        #                            pivot_table,           # Table to join
        #                            GUID,           # Field in the join table to join on
        #                            water_fields     # List of fields to include from the join table
        #                            )
        
        

        # try:
        #     if check_for_field(water_count, landAreaDiff)==0:
        #         arcpy.AddField_management(water_count,landAreaDiff,'DOUBLE')
        #         #arcpy.AddMessage(f"Added {landAreaDiff} column")
            
        #     else:
        #         arcpy.AddMessage(f"{landAreaDiff} column already exists")
                
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # arcpy.management.CalculateField(
        #     in_table=water_count,
        #     field= landAreaDiff,
        #     expression=f'((!{landArea}!-!{adjArea}!)/!{adjArea}!)*100',
        #     expression_type='PYTHON3',
        #     code_block='',
        #     field_type='DOUBLE',
        #     enforce_domains="NO_ENFORCE_DOMAINS"
        # )
        
        # if arcpy.Exists(pivot_table):
        #     arcpy.Delete_management(pivot_table)
        
        ##############
        ##############


        #####
        #turking image development
        #####
        
        #list of all boundaries from inputBoundaries
        inboundaries =[]
        # #list of all boundaries from finalBoundaries
        boundaries =[]
        #list of records to generate PNG images
        subBoundaries = []


        #create list of GUBID to print based on water_count
        with arcpy.da.SearchCursor(water_count, cursor_fields) as cursor:
            for row in cursor:
                inboundaries.append(row)
        del cursor


        #create list of land gubid 
        with arcpy.da.SearchCursor(finalBoundaries, searchFields) as cursor:
            for row in cursor:
                if row[1]== "L":
                    boundaries.append(row)

        arcpy.AddMessage(f'Input boundries are {len(inboundaries)}, Boundaries list length: {len(boundaries)}')
        #arcpy.AddMessage(f'first row of inboundaries: {inboundaries[0]}')
        #arcpy.AddMessage(f'first row of boundaries: {boundaries[0]}')

        #append unusual rows from final boundaries to subBoundaries list
        for row in inboundaries:
            if any(elem is None for elem in row):
                # If any element in the row is None, append the row to subBoundaries
                subBoundaries.append(row)
            elif abs(row[4]) > 40.0:
                subBoundaries.append(row)

            
                
        # get length of subBoundaries
        sub_len1 = len(subBoundaries)

        #append unusual rows from inputboundaries to subBoundaries list
        for row in inboundaries:
            #if row in inboundary is missing in the water_count
            if row[0] not in [item[0] for item in boundaries]:
                subrow = ()
                subrow = (row[0], row[1], None, None, None, None)
                #append to image list
                subBoundaries.append(subrow)
                subrow = (iso, row[0], row[1], "Item not found in framework.")
                # append to missing boundaries list
                framework_list.append(subrow)

        # get length of subBoundaries after inputBoundaries
        sub_len2 = len(subBoundaries)
        #if there are records to create an image
        if len(subBoundaries)>0:
            img_path = os.path.join(out_folder, args.gpw_project, "adj_images")
            create_folder_if_not_exists(img_path)
            #name of folder where turking images will be saved
            img_folder_name = os.path.basename(finalBoundaries) + "_images"
            img_folder = os.path.join(img_path, img_folder_name)
            create_folder_if_not_exists(img_folder)

            #add message to missing framework list if there are no missing records
            if sub_len1 == sub_len2:
                subrow = ()
                subrow = (iso, None, None, "No missing land boundaries, images produced." )
                framework_list.append(subrow)

            # with open(csv_file_path, 'a', newline='') as csvfile:
            #     csv_writer = csv.writer(csvfile)
            #     csv_writer.writerows(framework_list)

            # load dataframes of boundaries to generate image
            over_df = pd.DataFrame.spatial.from_featureclass(finalBoundaries)
            base_df = pd.DataFrame.spatial.from_featureclass(water_count)
            #clip_df = pd.DataFrame.spatial.from_featureclass(symdiffDisso)

            
            # get spatial reference of finalBoundaries
            desc = arcpy.Describe(water_count)
            crsg = desc.spatialReference

            arcpy.AddMessage(f'count of images for {iso}: {len(subBoundaries)}')

            # iterate through subboundaries list
            for row in subBoundaries:
                #get GUID
                gid = row[0]
                arcpy.AddMessage(f'GUID: {gid}')

                #get areas
                initial = row[1]
                final = row[2]
                wtrark = row[3]
                wtrdif = row[4]
                # abdif = row[5]

                # create figure name and path for record
                fig_name = iso + "_" + str(gid) + "_overlay.png"
                fig_path = os.path.join(img_folder, fig_name)
                
                #get row dataframe, coords, and geometry
                row_df = base_df[base_df[GUID]==gid] 
                row_df.crs = crsg
                row_df = row_df.set_geometry('SHAPE')
                row_bbox =  row_df.total_bounds

                

                #get row dataframe, coords, and geometry
                orow_df = over_df[over_df[GUID]==gid] 
                orow_df.crs = crsg
                orow_df = orow_df.set_geometry('SHAPE')
                orow_bbox =  orow_df.total_bounds
                water_type_L = orow_df[orow_df['WATER_TYPE'] == 'L']
                water_type_IW = orow_df[orow_df['WATER_TYPE'] =='IW']
                water_type_ICE = orow_df[orow_df['WATER_TYPE'] == 'ICE']

                titl = (
                        "Version: "
                        + args.gpw_project
                        +", ISO: "
                        + iso
                        + ", GlobalID: "
                        + str(gid)
                        + "\n Initial Area: "
                        + (str(round(initial, 2)) if initial is not None else "None")
                        + " sq.km, Land Area: "
                        + (str(round(final, 2)) if final is not None else "None")
                        + " sq.km\nWater Area: "
                        + (str(round(wtrark, 2)) if wtrark is not None else "None")
                        + " sq.km, Land Area Diff: "
                        + (str(round(wtrdif, 2)) if wtrdif is not None else "None")
                        + " %"
                        # + (str(round(abdif, 2)) if abdif is not None else "None")
                        # + " sq.km"
                        )
                # Calculate the bounding box that encompasses both layers
                min_lon = min(row_bbox[0], orow_bbox[0])
                max_lon = max(row_bbox[2], orow_bbox[2])
                min_lat = min(row_bbox[1], orow_bbox[1])
                max_lat = max(row_bbox[3], orow_bbox[3])

                # Calculate padding as a fraction of the total extent (adjust as needed)
                padding_factor = 0.05  # 3% padding

                # Calculate the padded bounding box
                width = max_lon - min_lon
                height = max_lat - min_lat
                padding_lon = width * padding_factor
                padding_lat = height * padding_factor

                new_min_lon = min_lon - padding_lon
                new_max_lon = max_lon + padding_lon
                new_min_lat = min_lat - padding_lat
                new_max_lat = max_lat + padding_lat

                # Create a figure with two subplots, one for each basemap
                try:
                    fig, axes = plt.subplots(1,2, figsize=(12, 6))
                    #arcpy.AddMessage('figure added.')
                except arcpy.ExecuteError:
                    arcpy.AddWarning('figure tool failed')
                    arcpy.GetMessages()
                    
                

                # Define dash tuple for the map plots
                linestyles = OrderedDict(
                    [ 

                    ('loosely dashed',      (0, (4, 4)))

                    ])
                
                land_color=(0.9, 0.2, 0.2, 0.45)
                water_color=(0.3, 0.3, 0.9, 0.45)
                ice_color=(0.1, 0.9, 0.9, 0.45)
                land_line=(1.0, 0.4, 0.4, 1)
                water_line=(0.8, 0.8, 1.0, 1)
                ice_line=(0.1, 0.9, 0.9, 1)
                land_linestyle = "solid"
                water_linestyle = (1, (4, 2))
                ice_linestyle = (2, (4, 2))


                #plot four shapes and Basemap left side
                row_df.plot(ax=axes[0], edgecolor='black', linewidth=1.5, label="Admin Boundary", facecolor="None", legend=True)
                water_type_L.plot(ax=axes[0], edgecolor="None", linewidth=1.5,  label="Land",  facecolor=land_color, legend=True) #linestyle=linestyles['loosely dashed'],
                water_type_IW.plot(ax=axes[0], edgecolor="None", linewidth=1.5,  label="Inland Water",  facecolor=water_color, legend=True)
                water_type_ICE.plot(ax=axes[0], edgecolor="None", linewidth=1.5, label="Ice",  facecolor=ice_color, legend=True)
                
                try:
                    inset_map_street = Basemap(ax=axes[0], projection='merc', 
                                            llcrnrlon=new_min_lon, llcrnrlat=new_min_lat, 
                                            urcrnrlon=new_max_lon, urcrnrlat=new_max_lat, 
                                            epsg=4326, resolution='i')
                except Exception as e:
                    arcpy.AddWarning('Street basemap tool failed')
                    arcpy.AddWarning(f"Error creating Basemap: {e}")
                

                #plot four shapes and Basemap right side
                #row_df.plot(ax=axes[1], edgecolor='black', linewidth=1.5, label="Admin Boundary",  facecolor="None", legend=True)
                water_type_L.plot(ax=axes[1], edgecolor=land_line, linewidth=1.5, linestyle=land_linestyle, label="Land",  facecolor="None", legend=True)
                water_type_IW.plot(ax=axes[1], edgecolor=water_line, linewidth=1.5, linestyle=water_linestyle,   label="Inland Water",  facecolor="None", legend=True)
                water_type_ICE.plot(ax=axes[1], edgecolor=ice_line, linewidth=1.5, linestyle=ice_linestyle,  label="Ice", facecolor="None", legend=True)
                
                # add imagery
                try:
                    inset_map_imagery = Basemap(ax=axes[1], projection='merc', llcrnrlon=new_min_lon,
                                                llcrnrlat=new_min_lat,
                                                urcrnrlon=new_max_lon,
                                                urcrnrlat=new_max_lat, epsg=4326, resolution='i')
                except Exception as e:
                    arcpy.AddWarning('Imagery basemap tool failed')
                    arcpy.AddWarning(f"Error creating Basemap: {e}")
                #arcpy.AddMessage('Basemap added.')
                max_retries = 3  # Adjust the maximum number of retries as needed
                retry_delay = 5 
                for retry_count in range(max_retries):
                    try:
                        inset_map_street.arcgisimage(service='World_Street_Map', verbose=True, ax= axes[0])
                    except Exception as e:
                        arcpy.AddWarning(f'An error occurred while fetching World Imagery: {str(e)}')
                        arcpy.GetMessages()
                        if retry_count < max_retries - 1:
                            retry_time = datetime.datetime.now() + datetime.timedelta(seconds=retry_delay)
                            arcpy.AddMessage(f"Retrying at {retry_time}...")
                            while datetime.datetime.now() < retry_time:
                                pass  # Wait until the retry time is reached
                        else:
                            arcpy.AddWarning("Unable to fetch Esri World Imagery.")
                            # Handle the error or raise an exception as needed
                            break

                for retry_count in range(max_retries):
                    try:
                        inset_map_imagery.arcgisimage(service='World_Imagery', verbose=True, ax=axes[1])
                        # If the imagery is successfully fetched, break out of the loop
                        break
                    except Exception as e:
                        arcpy.AddWarning(f'An error occurred while fetching World Imagery: {str(e)}')
                        arcpy.GetMessages()
                        if retry_count < max_retries - 1:
                            retry_time = datetime.datetime.now() + datetime.timedelta(seconds=retry_delay)
                            arcpy.AddMessage(f"Retrying at {retry_time}...")
                            while datetime.datetime.now() < retry_time:
                                pass  # Wait until the retry time is reached
                        else:
                            arcpy.AddWarning("Unable to fetch Esri World Imagery.")
                            # Handle the error or raise an exception as needed
                            break
                

                #scalebar creation
                bbox_width_km = 111.320 * math.cos(new_max_lon - new_min_lon)
                for ax in axes:
                    ax.add_artist(ScaleBar(
                        dx=bbox_width_km,
                        units="km",
                        dimension="si-length",
                        length_fraction=0.15,
                        location='lower left'
                    ))
            
                # Legend patches
                custom_patches = [Patch(edgecolor='black',   facecolor="None"),
                                Patch(edgecolor=land_color, linestyle=land_linestyle, facecolor=land_color),
                                Patch(edgecolor=water_color, linestyle=water_linestyle, facecolor=water_color),
                                Patch(edgecolor=ice_color, linestyle=ice_linestyle, facecolor=ice_color)] # Patch(edgecolor='black',  facecolor=(0, 0, 0, 0.5))]
                
                    
                    
                # add title to figure
                fig.suptitle(titl)

                # add legend to figure
                fig.legend( custom_patches, [ "Admin","Land", "Inland Water", "Ice" ])

                # Adjust subplot spacing
                plt.tight_layout()
                
                #save figure to path
                fig.savefig(fig_path)
                
                # close plot
                plt.close('all')
            arcpy.AddMessage('Images completed.')
        
        else:
            #else statement in case no area or ISO had PNGs generated
            arcpy.AddMessage('No final boundaries were flagged.')
            # subrow = ()
            # subrow = (iso, None, None, 'No errors found. No images created.')
            # framework_list.append(subrow)
            
            # with open(csv_file_path, 'a', newline='') as csvfile:
            #     csv_writer = csv.writer(csvfile)
            #     csv_writer.writerows(framework_list)
        
        arcpy.AddMessage(f'{iso} loop finished')
        
    arcpy.AddMessage('end of script.')

        
            


    
    
        

    
    
