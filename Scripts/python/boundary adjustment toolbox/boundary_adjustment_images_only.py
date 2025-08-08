import argparse
import arcpy
import os
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
import csv
import datetime


gpwv4_out_gdb_folder = r'Z:\GPW\GPW5\Preprocessing\Global\gpwv4_updated_boundaries'

# preserve global id
arcpy.env.preserveGlobalIds = True
# blow away output! 
arcpy.env.overwriteOutput = True
in_memory = "in_memory"
#field names
GlobalID = 'GlobalID'
clipArea = "CLIPAREAKM"
clipAreaDiff = "CLIPAREAPCTDIFF"
finalArea = "ADJAREAKM"
finalAreaDiff = "ADJAREAPCTDIFF"
areafield = "AREA_SQKM"
absArea = "ADJAREAABSDIFF"
newFields = [clipArea, clipAreaDiff, finalArea, finalAreaDiff, absArea]
inputBoundaries =os.path.join(in_memory, "inputBoundaries")
mem_fishnet =os.path.join(in_memory,"clipFishnet")
clipBoundaries = os.path.join(in_memory,  "clipBoundary")
symBoundaries = os.path.join(in_memory, "symdiff")
symdifFishnet = os.path.join(in_memory,  "symdifFishnet")
mergeBoundaries = os.path.join(in_memory,  "mergeBoundaries")


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
    fdesc = arcpy.Describe(featClass)
    fields = fdesc.fields
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


def delList_ofFields(featclass):
    '''
    delete any field in feature class that is a duplicate (ends with "_1")
    '''
    deleteList = arcpy.ListFields(featclass,"*_1")
    if len(deleteList) == 0:
        arcpy.AddMessage("No fields to delete")
    else:
        for delFld in deleteList:
            try:
                arcpy.DeleteField_management(featclass, delFld.name)
                #arcpy.AddMessage(f"Deleted {delFld.name}")
            except arcpy.ExecuteError:
                arcpy.GetMessages()

def delete_memory_features(del_fc):
    '''
    Deletes any featue class
    '''
    try:
        arcpy.Delete_management(del_fc)
    except arcpy.ExecuteError:
        arcpy.GetMessages()

def check_null_values_in_column(feature_class_path, column_name):
    '''
    Check if any column has a null value
    '''
    null_found = False

    with arcpy.da.SearchCursor(feature_class_path, column_name) as cursor:
        for row in cursor:
            if row[0] is None:
                null_found = True
                break

    if null_found:
        arcpy.AddWarning(f"Error: Null values found in the column {column_name} of the feature class {feature_class_path}.")
    #else:
        #arcpy.AddMessage(f"No null values found in the column {column_name} of the feature class {feature_class_path}.")  

def remove_gr_fc(gdb_path):
        arcpy.env.workspace = gdb_path 
        feature_classes = arcpy.ListFeatureClasses('*')
        filtered_feature_classes = [fc for fc in feature_classes if 'growth_rate' not in fc.lower() and 'admin' in fc.lower()]
        filtered_feature_classes.sort()
        filtered_feature_classes = filtered_feature_classes[-1:]
        filtered_feature_classes = filtered_feature_classes[0]

        return filtered_feature_classes

def ingested_fc_name(in_gdb):
        """
        List feature classes in given geodatabase that end with _ingested
        Return the first (and only) feature class in the list
        """
        arcpy.env.workspace = in_gdb
        try:
            fc_list = arcpy.ListFeatureClasses('*_ingested')
            fc_list = fc_list[0]
            return fc_list
        except Exception as e:
            arcpy.AddWarning(f"Error: {e}")
            return []
        

if __name__ == '__main__':
    arcpy.AddMessage('Start of script...')
    parser = argparse.ArgumentParser(description='Ingest GWv4 or GPWv5 boundaries using ISO codes separated by commas.')
    #arcpy.AddMessage('Parser created...')
    parser.add_argument('ISO_string',
        help='One or more ISO codes separated by a comma. E.g. "ABC, CDE" or "FGH"')
    parser.add_argument('gpw_project',
        help='Select one of the options.')
    parser.add_argument('framework_gdb_loc', 
        help='Location of the Framework GDB.')
    parser.add_argument('fishnet_folder', 
        help='Location of the fishnet folder containing GDBs.')
    parser.add_argument('out_folder',
        help='Location of the output folder')
    #arcpy.AddMessage('parser arguentsdone.' )
    
    
    args = parser.parse_args()
    arcpy.AddMessage(f'parser created: {args}')

    


    ISO_parse_string = args.ISO_string
    framework_gdb = args.framework_gdb_loc
    fishnet_path = args.fishnet_folder
    out_img_folder = args.out_folder


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
    csv_file_name = f"areas_missing_in_{args.gpw_project}_framework_{current_time.year}{current_time.month}{current_time.day}_{current_time.hour}{current_time.minute}{current_time.second}.csv"
    csv_file_path = os.path.join(out_img_folder, "reports","framework_reports", csv_file_name)
    arcpy.AddMessage(f'csv file path {csv_file_path}')
    create_folder_if_not_exists(os.path.join(out_img_folder, "reports","framework_reports"))
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        headers = ['ISO', 'GlobalID', "Area (km)", "Note"]  # Modify based on initial known columns
        csv_writer.writerow(headers)
    for iso in ISO_list:
        framework_list = []
        arcpy.AddMessage(iso)
        #keeps track of CVS length to update appropiate row.
        last_written_index = len(framework_list)
        #arcpy.AddMessage(f"Framework list length: {last_written_index}")
        if iso == "and":
            frameworkBoundaries = os.path.join(framework_gdb, iso.upper()+"_")
        else:
            frameworkBoundaries = os.path.join(framework_gdb, iso.upper())
        
        


        #finding path of ISO's fishnet boundary feature class from the framework GDB
        fishnetBoundaries = os.path.join(fishnet_path, iso.lower()+'_fishnet.gdb',iso.lower()+'_fishnet')

        if not arcpy.Exists(frameworkBoundaries):
            arcpy.AddError(f'{frameworkBoundaries} does not exist.')
            subrow = (iso, None, None, 'Framework boundaries not found')
            framework_list.append(subrow)
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                csv_writer.writerows(framework_list)
            continue
            

        if not arcpy.Exists(fishnetBoundaries):
            arcpy.AddError(f'{fishnetBoundaries} does not exist.')
            subrow = (iso, None, None, 'Fishnet boundaries not found.')
            framework_list.append(subrow)
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                csv_writer.writerows(framework_list)
            continue

        if args.gpw_project == 'gpwv4':
            GUID = "GUBID"
            gdb_directory = r'Z:\GPW\GPW4\Release_411\data\boundaries\original_boundaries_with_census_data'
            ingdb_path = os.path.join(gdb_directory, iso.lower()+'.gdb')
            if not arcpy.Exists(ingdb_path):
                gdb_directory = r'Z:\GPW\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'
                ingdb_path = os.path.join(gdb_directory, iso.lower()+'.gdb')

            arcpy.AddMessage(ingdb_path)
            fc_list = []
            fc_list = remove_gr_fc(ingdb_path)
            arcpy.AddMessage(fc_list)
            if not fc_list:
                arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
                subrow = (iso, None, None, 'No input classes found.')
                framework_list.append(subrow)
                with open(csv_file_path, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                    csv_writer.writerows(framework_list)
            
                continue
            
            outgdb = os.path.join(gpwv4_out_gdb_folder, iso +'.gdb')
            finalBoundaries = os.path.join(outgdb, f"{fc_list}_adj")
            inputBName = os.path.join(ingdb_path, fc_list)

            if not arcpy.Exists(outgdb):
                try:
                    # Create the geodatabase
                    arcpy.CreateFileGDB_management(gpwv4_out_gdb_folder, iso + '.gdb')
                    arcpy.AddMessage(f"Geodatabase '{outgdb}' created successfully.")
                except Exception as e:
                    arcpy.AddWarning(f"Error creating geodatabase: {str(e)}")
            else:
                arcpy.AddMessage(f"Geodatabase '{outgdb}' already exists.")


        elif args.gpw_project == 'gpwv5':
            GUID = "GUID"
            gdb_directory = r'Z:\GPW\GPW5\Preprocessing\Country'
            ingdb_path = os.path.join(gdb_directory, iso.upper(), 'Ingest','Boundaries', iso.lower()+'_ingest.gdb')
            #finding path of ISO's framework boundary feature class from the framework GDB
            
            #finding ingested feature class from the GDB
            fc_list = ingested_fc_name(ingdb_path)
            #if no input feature class is found, get out of this ISO's loop
            if not fc_list:
                arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
                subrow = (iso, None, None, 'No input classes found.')
                framework_list.append(subrow)
                with open(csv_file_path, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                    csv_writer.writerows(framework_list)
                continue
            elif fc_list is None:
                arcpy.AddWarning(f"No feature classes found in {ingdb_path}. Skipping...")
                subrow = (iso, None, None, 'No input classes found.')
                framework_list.append(subrow)
                with open(csv_file_path, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                    csv_writer.writerows(framework_list)
                continue

            gdb_directory = r'Z:\GPW\GPW5\Preprocessing\Country'
            finalBoundaries = os.path.join(ingdb_path, f"{fc_list}_adj")
            inputBName = os.path.join(ingdb_path, fc_list)
            
            #Check the input feature class has required GUID field, if not, create field and populate by GLobalID field.
            if check_for_field(inputBName, GUID) == 0 :
                arcpy.AddWarning(f'GUID missing {arcpy.GetMessages()}')
                subrow = (iso, None, None, 'GIUD from Global ID failed.')
                framework_list.append(subrow)
                with open(csv_file_path, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile) # Modify based on initial known columns
                    csv_writer.writerows(framework_list)
                continue
            else:
                arcpy.AddMessage(f'{GUID} field exists.') 
        
        searchFields = [GUID,  areafield, finalArea, finalAreaDiff, clipAreaDiff, absArea]


        arcpy.AddMessage(f"inputBoundary name {inputBName}")
        arcpy.AddMessage(f'final boundaries {finalBoundaries}')
        
        arcpy.env.workspace = in_memory
        arcpy.env.overwriteOutput = True
        #check that there are no empy ID records    
        try:
            # create a memory copy of input feature class
            arcpy.conversion.FeatureClassToFeatureClass(inputBName, in_memory, 'inputBoundaries')
        #     arcpy.AddMessage(f'input row count:  {arcpy.GetCount_management(inputBName)}')
        #     arcpy.AddMessage(f'after copy features, IB count: {arcpy.GetCount_management(inputBoundaries)}')
        except arcpy.ExecuteError:
            arcpy.GetMessages()
        
        check_null_values_in_column(inputBoundaries, GUID)

        #check that the area field exists, if not add field and calculate area
        if check_for_field(inputBoundaries, areafield)== 0:
            arcpy.AddField_management(inputBoundaries,areafield,'FLOAT')
            try:
                arcpy.CalculateField_management(inputBoundaries, areafield, "!shape.area@squarekilometers!", "PYTHON3")
                #(f"Field {areafield} in '{inputBoundaries}' updated successfully.")
            except arcpy.ExecuteError:
                arcpy.GetMessages()
        else:
            arcpy.AddMessage(f'{areafield} field exists.')
        #Create clipBoundaries in_memory
        # try:
        #     # Set the environment to preserve GlobalIDs
        #     arcpy.env.preserveGlobalIds = True
            
            # Clip the inputBoundaries to create the clipBoundaries feature class
        #     arcpy.analysis.PairwiseClip(inputBoundaries, frameworkBoundaries, clipBoundaries)

        #     # Calculate  clip Area
        #     arcpy.AddField_management(clipBoundaries, clipArea, "FLOAT")
        #     arcpy.CalculateField_management(clipBoundaries,clipArea,'!shape.area@SQUAREKILOMETERS!','PYTHON3')
        #     #arcpy.AddMessage(f"Calculated {clipArea}")
            
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # # Find symmetrical difference of clipBoundaries and frameworkBoundaries 
        # try:
        #     arcpy.env.workspace = in_memory
        #     arcpy.analysis.SymDiff(clipBoundaries, frameworkBoundaries, symBoundaries, "ONLY_FID")
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # #Clip Fishnets to symmetrical difference 
        # try:
        #     # Clip the fisnet boundaries to create the symmetricalDifference boudantirs to create mem_fishnet feature class
        #     arcpy.analysis.PairwiseClip(fishnetBoundaries, symBoundaries, mem_fishnet)
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        # if arcpy.Exists(symdifFishnet):
        #     arcpy.Delete_management(symdifFishnet)

        # #Symmetrical difference spatially joined with input boundaries
        # try:
        #     #join input boundary fields to symdifFishnet
        #     arcpy.env.preserveGlobalIds = True
        #     arcpy.analysis.SpatialJoin(mem_fishnet, inputBoundaries, symdifFishnet, "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "CLOSEST_GEODESIC")
        #     #arcpy.AddMessage("spatial join of inputfeatures to fishnet done.")
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # delList_ofFields(symdifFishnet)
        # check_null_values_in_column(symdifFishnet, GUID)

        # #merge clipped boundaries with the symmetricalDifference fishnets
        # try:
        #     arcpy.Merge_management([clipBoundaries, symdifFishnet] , mergeBoundaries)
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        # if arcpy.Exists(finalBoundaries):
        #     if check_for_field(finalBoundaries, GUID)==0:
        #         arcpy.AddError(f'{GUID} missing in finalBoundaries')
        #         subrow = (iso, None, None, 'GUID missing in final boundaries.')
        #         framework_list.append(subrow)
        #         with open(csv_file_path, 'a', newline='') as csvfile:
        #             csv_writer = csv.writer(csvfile) # Modify based on initial known columns
        #             csv_writer.writerows(framework_list)
        
        #         continue
        #     arcpy.AddWarning(f'Deleting existing Finalboundaries: {finalBoundaries}')
        #     arcpy.env.overwriteOutput = True
        #     arcpy.Delete_management(finalBoundaries)
    
        # try:
        #     arcpy.analysis.PairwiseDissolve(mergeBoundaries, finalBoundaries, GUID, [(clipArea, 'SUM')])
        #     # join inputboundries fields to the final boundaries
        #     arcpy.management.JoinField(finalBoundaries, GUID, inputBoundaries, GUID)
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()
        
        #check that the final number of records match the initial number or records
        finalRow_count = arcpy.GetCount_management(finalBoundaries)
        arcpy.AddMessage(f'after finalBoundary join, IB count: {finalRow_count}')
        
        # #add fields to finalBoundaries if fields don't exist
        # for newField in newFields:
        #     add_newField(finalBoundaries,newField)
        
        # #Calculate FINALAREA and FINALAREADIFF of finalBoundaries 
        # try:
        #     #arcpy.CalculateField_management(finalBoundaries,origArea,f'!{areafield}!','PYTHON3')
        #     arcpy.CalculateField_management(finalBoundaries,finalArea,'!shape.area@SQUAREKILOMETERS!','PYTHON3')
        #     sumcliArea = "!SUM_"+clipArea+"!"
        #     arcpy.CalculateField_management(finalBoundaries,clipArea,sumcliArea,'PYTHON3')
            
        #     expression =f"((!{finalArea}!-!{areafield}!)/!{areafield}!)*100"
        #     arcpy.CalculateField_management(finalBoundaries,finalAreaDiff, expression,'PYTHON3', field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")
            
        #     expression =f"(!{clipArea}!-!{areafield}!)/!{areafield}!*100"
        #     arcpy.CalculateField_management(finalBoundaries,clipAreaDiff, expression,'PYTHON3', field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")

        #     expression =f"!{finalArea}!-!{areafield}!"
        #     arcpy.CalculateField_management(finalBoundaries,absArea, expression,'PYTHON3', field_type="TEXT", enforce_domains="NO_ENFORCE_DOMAINS")
                
        # except arcpy.ExecuteError:
        #     arcpy.GetMessages()

        # # delete duplicate fields in finalBoundaries   
        # delList_ofFields(finalBoundaries)
        # #delete copy of field
        # arcpy.DeleteField_management(finalBoundaries, "SUM_CLIPAREAKM")

        #####
        #turking image development
        #####
        
        #list of all boundaries from inputBoundaries
        inboundaries =[]
        #list of all boundaries from finalBoundaries
        boundaries =[]
        #list of records to generate PNG images
        subBoundaries = []

        #create list of inputBoundaries
        with arcpy.da.SearchCursor(inputBoundaries, [GUID, areafield]) as cursor:
            for row in cursor:
                inboundaries.append(row)

        #create list of finalBoundaries
        with arcpy.da.SearchCursor(finalBoundaries, searchFields) as cursor:
            for row in cursor:
                boundaries.append(row)

        arcpy.AddMessage(f'Input boundries are {len(inboundaries)}, Boundaries list length: {len(boundaries)}')

        #append unusual rows from final boundaries to subBoundaries list
        for row in boundaries:
            if any(elem is None for elem in row):
                # If any element in the row is None, append the row to subBoundaries
                subBoundaries.append(row)
            elif abs(row[5]) > 10.0:
                if abs(row[3])> 5.0 or abs(row[4])>5.0:
                    subBoundaries.append(row)
            elif abs(row[3])> 20.0 or abs(row[4])>20.0:
                subBoundaries.append(row)
        # get length of subBoundaries after finalBoundaries
        sub_len1 = len(subBoundaries)

        #append unusual rows from inputboundaries to subBoundaries list
        for row in inboundaries:
            #if row in inboundary is missing in the finalBoundaries
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
            #add message to missing framework list if there are no missing records
            if sub_len1 == sub_len2:
                subrow = ()
                subrow = (iso, None, None, "No missing boundaries, images produced." )
                framework_list.append(subrow)
            
            

            #update Frameowrk CSV from list
            # Update CSV file after each iteration
            # Get the index of the last successfully written row
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(framework_list)


            img_path = os.path.join(out_img_folder, args.gpw_project, "adj_images")
            create_folder_if_not_exists(img_path)
            #name of folder where turking images will be saved
            img_folder_name = os.path.basename(finalBoundaries) + "_images"
            img_folder = os.path.join(img_path, img_folder_name)
            create_folder_if_not_exists(img_folder)

            
            

            # load dataframes of boundaries to generate image
            over_df = pd.DataFrame.spatial.from_featureclass(finalBoundaries)
            base_df = pd.DataFrame.spatial.from_featureclass(inputBoundaries)

            
            # get spatial reference of finalBoundaries
            desc = arcpy.Describe(finalBoundaries)
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
                ifDiff = row[3]
                cldif = row[4]
                abdif = row[5]

                # create figure name and path for record
                fig_name = iso + "_" + str(gid) + "_overlay.png"
                fig_path = os.path.join(img_folder, fig_name)
                
                #get row dataframe, coords, and geometry
                row_df = base_df[base_df[GUID]==gid] 
                row_df.crs = crsg
                row_df = row_df.set_geometry('SHAPE')
                row_bbox =  row_df.total_bounds

                if not final == 0.0:
                    
                    #get row dataframe, coords, and geometry
                    orow_df = over_df[over_df[GUID]==gid] 
                    orow_df.crs = crsg
                    orow_df = orow_df.set_geometry('SHAPE')
                    orow_bbox =  orow_df.total_bounds

            

                #arcpy.AddMessage('geometry set...')
                
                # image title
                titl = (
                        "Version: "
                        + args.gpw_project
                        +", ISO: "
                        + os.path.basename(frameworkBoundaries)
                        + ", GlobalID: "
                        + str(gid)
                        + "\n Initial Area: "
                        + (str(round(initial, 2)) if initial is not None else "None")
                        + " sq.km, Final Area: "
                        + (str(round(final, 2)) if final is not None else "None")
                        + " sq.km\nPercent Area Diff: "
                        + (str(round(ifDiff, 2)) if ifDiff is not None else "None")
                        + " %, Clip Area Diff: "
                        + (str(round(cldif, 2)) if cldif is not None else "None")
                        + " %, Area Dif: "
                        + (str(round(abdif, 2)) if abdif is not None else "None")
                        + " sq.km"
                        )
                # Calculate the bounding box that encompasses both layers
                if not row[2] == 0.0:
                    min_lon = min(row_bbox[0], orow_bbox[0])
                    max_lon = max(row_bbox[2], orow_bbox[2])
                    min_lat = min(row_bbox[1], orow_bbox[1])
                    max_lat = max(row_bbox[3], orow_bbox[3])
                else:
                    min_lon = row_bbox[0]
                    max_lon = row_bbox[2]
                    min_lat = row_bbox[1]
                    max_lat = row_bbox[3]
                    

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
                #arcpy.AddMessage('lat lon added.')

                # Create a figure with two subplots, one for each basemap
                try:
                    #arcpy.AddMessage('trying figure...')
                    fig, axes = plt.subplots(1,2, figsize=(12, 6))
                    #arcpy.AddMessage('figure added.')
                except arcpy.ExecuteError:
                    arcpy.AddWarning('figure tool failed')
                    arcpy.GetMessages()
                    

                #plot three shapes and Basemap left side
                row_df.plot(ax=axes[0], edgecolor='red', linewidth=0.7, label="Admin Boundary",hatch='..', facecolor="None", legend=False)
                if not row[2] == 0.0:
                    orow_df.plot(ax=axes[0], edgecolor='blue', linewidth=1, label="Final Boundary",  facecolor=(0, 0, 0, 0.15), legend=True)
                #cliprow_df.plot(ax=axes[0], edgecolor='black', linewidth=0.4, label="Difference", facecolor=(0, 0, 0, 0.5), legend=True)
                try:
                    inset_map_street = Basemap(ax=axes[0], projection='merc', 
                                            llcrnrlon=new_min_lon, llcrnrlat=new_min_lat, 
                                            urcrnrlon=new_max_lon, urcrnrlat=new_max_lat, 
                                            epsg=4326, resolution='i')
                except Exception as e:
                    arcpy.AddWarning('Street basemap tool failed')
                    arcpy.AddWarning(f"Error creating Basemap: {e}")

                #plot three shapes and Basemap right side
                row_df.plot(ax=axes[1], edgecolor='red', linewidth=0.7, label="Admin Boundary",  facecolor="None", legend=True)
                if not row[2] == 0.0:
                    orow_df.plot(ax=axes[1], edgecolor='blue', linewidth=1, label="Final Boundary", facecolor="None", legend=False)
                #cliprow_df.plot(ax=axes[1], edgecolor='black', linewidth=0.4, label="Difference", facecolor=(0, 0, 0, 0.5), legend=True)
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
                custom_patches = [Patch(edgecolor='red', hatch='..', facecolor="None"),
                                Patch(edgecolor='blue', facecolor=(0, 0, 0, 0.15))] # Patch(edgecolor='black',  facecolor=(0, 0, 0, 0.5))]
                    
                    
                # add title to figure
                fig.suptitle(titl)

                # add legend to figure
                fig.legend( custom_patches, [ "Ingest","Final" ])

                # Adjust subplot spacing
                plt.tight_layout()
                
                #save figure to path
                fig.savefig(fig_path)
                
                # close plot
                plt.close('all')
            arcpy.AddMessage('Images completed.')
        
        else:
            #else statement in case no area or ISO had PNGs generated
            arcpy.AddMessage('No final boundaries were more than 50 percent different from the original.')
            subrow = ()
            subrow = (iso,  None, None, 'No errors found, no images created')
            framework_list.append(subrow)
            #create a CSV from list
            with open(csv_file_path, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(framework_list)
        

        #delete in_memory feature to rpepare for next ISO loop
        # delete_memory_features(inputBoundaries)
        # delete_memory_features(clipBoundaries)  
        # delete_memory_features(symBoundaries)
        # delete_memory_features(mem_fishnet)  
        # delete_memory_features(symdifFishnet)  
        # delete_memory_features(mergeBoundaries)
        arcpy.AddMessage(f'{iso} loop finished')


    arcpy.AddMessage('end of script.')

        
            


    
    
        

    
    
