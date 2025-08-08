import os 
import arcpy
import pandas as pd
import numpy as np



# Mexico Admin 3 and Admin 5 Census 2020 matching

### Part 1 matches the census tables to each other
### Part 2 creates a ingest shapefile out of the matches in part 1


#inputs needed:
shp_folders = r"Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s"
ingest5_folder = r"Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Census\mex_admin5_census_2020_AGEB_urban\mex_admin5_census_2020_ageb_edit1"
ingest3_folder = r"Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Census\mex_admin3_census_2020_ITER_rural\mex_admin3_census_2020_iter_edit1"



ingest5_list = [ filename for filename in os.listdir(ingest5_folder) if filename.endswith( "_ingest.csv" ) ]

shp_folder_list = next(os.walk(shp_folders))[1]

#fields from the boundary shapefiles required
m00m_cols =['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_LOC', 'CVE_AGEB', 'CVE_MZA','AMBITO', 'TIPOMZA']
m00pem_cols =['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_LOC', 'CVE_AGEB', 'CVE_MZA']
m00peml_cols = ['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_LOC']
m00l_cols = ['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_LOC', 'NOMGEO', 'AMBITO']
m00ar_cols =['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_AGEB']
m00lpr_cols =['CVEGEO', 'CVE_ENT', 'CVE_MUN', 'CVE_LOC', 'CVE_AGEB', 'CVE_MZA','NOMGEO', 'PLANO']

#columns for final use
main_cols =['USCID', 'CVEGEO', 'ISO', 'UCADMIN0', 'NAME0', 'CENSUS_YEAR',
            'UCADMIN1', 'NAME1', 'UCADMIN2', 'NAME2', 'UCADMIN3', 'NAME3',
            'UCADMIN4', 'UCADMIN5', 'ATOTPOPBT', 'ATOTPOPFT', 'ATOTPOPMT']

main3_cols =['USCID', 'CVEGEO', 'ISO', 'UCADMIN0', 'NAME0', 'CENSUS_YEAR',
            'UCADMIN1', 'NAME1', 'UCADMIN2', 'NAME2', 'UCADMIN3', 'NAME3', 'ATOTPOPBT', 'ATOTPOPFT', 'ATOTPOPMT']



#function extract data from shapefiles to data frame
def feature_class_to_pandas_data_frame(feature_class, field_list):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param feature_class: Input ArcGIS Feature Class.
    :param field_list: Fields for input.
    :return: Pandas DataFrame object.
    """
    return pd.DataFrame(
        arcpy.da.FeatureClassToNumPyArray(
            in_table=feature_class,
            field_names=field_list,
            skip_nulls=False,
            null_value=-9999
        )
    )

def get_result(m00shp_ingest, m00shps):
    result = int(arcpy.management.GetCount(m00shp_ingest)[0])
    
    #shp_len = [len(x) for x in m00shps]
    if result == sum(m00shps):
        return(print("- SUCCESS: Layer row count matches census table, ", result, sum(m00shps)))
    else:
        print("- ERROR: shape rows not matched to number of rows.", result, sum(m00shps))
        return False
        #exit()
        


def append_shapes(m00url, shp_name, fieldMappings):
    field_names = df35concat.loc[df35concat['SHP_NAME']==shp_name, ['SHP_ID']]
    field_names = list(field_names['SHP_ID'])
    fldStr = "', '".join (field_names)
    sql = "CVEGEO IN ('{}')".format (fldStr)
    try:
        arcpy.management.Append(
            inputs=m00url,
            target=m00_ingest,
            schema_type="NO_TEST",
            field_mapping= fieldMappings,
            subtype="",
            expression= sql,
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY")
        return(len(field_names))
    except arcpy.ExecuteError:
        print(arcpy.GetMessages()) 

def append_shapes_ID(m00url, shp_name, fieldMappings):
    field_names = df35concat.loc[df35concat['SHP_NAME']==shp_name, ['SHP_ID']]
    field_names = list(field_names['SHP_ID'])
    fldStr = "', '".join (field_names)
    sql = "SHP_ID IN ('{}')".format (fldStr)
    try:
        arcpy.management.Append(
            inputs=m00url,
            target=m00_ingest,
            schema_type="NO_TEST",
            field_mapping= fieldMappings,
            subtype="",
            expression= sql,
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY")
        return(len(field_names))
    except arcpy.ExecuteError:
        print(arcpy.GetMessages()) 


    

arcpy.env.workspace = r"in_memory"
arcpy.env.overwriteOutput = True    
# ingest5_list = [x for x in ingest5_list if "08_ingest" in x]
print("ingest list: ", ingest5_list)
for ingest_csv in ingest5_list[:]:
    ucadmin1 = ingest_csv[16:18] 
    ca5 = os.path.join(ingest5_folder, ingest_csv)
    ca3 = os.path.join(ingest3_folder, "mex_adm3_2020_"+ucadmin1+"_ingest.csv")
    
    shp_folder = next(shp_folder for shp_folder in shp_folder_list if ucadmin1 in shp_folder) # [nm for ps in str_list for nm in full_list if ps in nm]
    print("working on " , shp_folder)

    #boundaries 
    m00m = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}m.shp' #adm 5 manzana
    m00pem = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}pem.shp' #adm5 external manzana points
    m00a = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}a.shp' #adm 5 manzana
    m00l = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}l.shp' #adm3 localities
    m00pe = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}pe.shp' #adm3 extrenal polygons
    m00lpr = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}lpr.shp' #adm3 points rural
    m00ar =fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}ar.shp' #adm3 polygons rural RURAL AGEB
    m00ent = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}ent.shp' #adm3 points rural
    m00mun = fr'Z:\GPW\GPW5\Input_Data\Country\MEX\Boundaries\INEGI\2020\889463807469_s\{shp_folder}\conjunto_de_datos\{ucadmin1}mun.shp' #adm2 municipal polygons


    ##deletable files
    m00peml = r'F:\gpwv5\country\MEX\MEX_scratch.gdb\m00peml'
    m00armi = r'F:\gpwv5\country\MEX\MEX_scratch.gdb\m00armi'
    m00ami = r"F:\gpwv5\country\MEX\MEX_scratch.gdb\m00ami"
    m00amims = r"F:\gpwv5\country\MEX\MEX_scratch.gdb\m00amims"

    excel_match =fr'Z:\GPW\GPW5\Preprocessing\Country\MEX\Match\mex_admin3_5_census_2020\mex_{ucadmin1}_admin3_5_census_2020_match.xlsx'
    # m00_ingest = fr'F:\gpwv5\country\MEX\MEX.gdb\m{ucadmin1}_ingest'
    # excel_match =fr'F:\gpwv5\country\MEX\mex_{ucadmin1}_admin3_5_census_2020_match.xlsx'
    m00_ingest = fr'Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Boundaries\mex_admin3_5\new\mex_admin3_5.gdb\m{ucadmin1}_ingest'

    #read shapefiles to dataframe using function
    df_ca5 = pd.read_csv(ca5, dtype = {'CVEGEO': str, 'UCADMIN0': str,'UCADMIN1': str,'UCADMIN2': str,'UCADMIN3': str,'UCADMIN4': str,'UCADMIN5': str, }) #census admin 5
    df_ca3 = pd.read_csv(ca3, dtype = {'CVEGEO': str, 'UCADMIN0': str,'UCADMIN1': str,'UCADMIN2': str,'UCADMIN3': str})#reach admin 3 census
    df_m00m = feature_class_to_pandas_data_frame(m00m, m00m_cols) #manzana shapefiles
    df_m00pem = feature_class_to_pandas_data_frame(m00pem, m00pem_cols) #manzana external polygon files
    df_m00pe = feature_class_to_pandas_data_frame(m00pe, m00peml_cols) #extrenal locality polygon
    df_m00lpr = feature_class_to_pandas_data_frame(m00lpr, m00lpr_cols) #extrenal locality polygon

    df_m00ar = feature_class_to_pandas_data_frame(m00ar, m00ar_cols) #rural agebs polygon
    # df_m00mun = feature_class_to_pandas_data_frame(m00mun, m00mun) #rural agebs polygon



    #left join admin 5 census with manzanas
    df = pd.merge(df_ca5, df_m00m, on='CVEGEO', how='left')
    # df_prisons = df.copy()
    df_prisons = df[df['NAME3'].str.contains(' \[CERESO\]', case=False)]
    df_prisons = df_prisons[main_cols]
    df_prisons['SHP_NAME'] = 'm00armi'
    df_prisons['SHP_ID'] = df_prisons['CVEGEO'].str[:5]+ df_prisons['UCADMIN4'] + "a" 
    df_prisons['POP_CONTEXT'] = '102'

    df = df[~df['NAME3'].str.contains(' \[CERESO\]', case=False)]
    dfn = df[df['CVE_MZA'].isnull()] [main_cols]
    dfn = pd.merge(dfn, df_m00pem, on='CVEGEO', how='left')

    #select admin 5 census entries not matched my two attemps above and attempt to match with polygon extranal localities
    dfnn = dfn[dfn['CVE_MZA'].isnull()][main_cols]
    dfnn['peml']= dfnn['CVEGEO'].str[:-7]
    dfnn = pd.merge(dfnn, df_m00pe, left_on='peml', right_on='CVEGEO', how='left')
    dfnn = dfnn.rename(columns={"CVEGEO_x": "CVEGEO"})

    #check that all admin 5 census entries have been matched
    dfn3 = dfnn[dfnn['CVE_LOC'].isnull()][main_cols]
    dfn3
    if len(dfn3) !=0:
        print(len(dfn3), " admin5 manzana entries not matched.")
        exit()
        
    else:
        print('- matched all census 3 entries')
        print('- ', len(df_prisons), ' prisons removed from admin5 match as is it found at the admin3 level.')
    
    #make list of unique urban localities CVEGEO
    urbLOC = df_ca5.copy()
    urbLOC.drop(urbLOC[urbLOC['NAME3'] == 'Ninguno [CERESO]'].index, inplace = True)
    urbLOC = list(urbLOC['CVEGEO'].str[:-7].unique())
    

    #select only the rural localities
    df_l_rural = df_ca3[~df_ca3.CVEGEO.isin(urbLOC)]

    #admin 3 localities boundaries to dataframe
    df_m00l = feature_class_to_pandas_data_frame(m00l, m00l_cols )
    df_m00pe = feature_class_to_pandas_data_frame(m00pe, m00peml_cols )
    
    # Select only the 'SHP_ID' and 'EML' columns for merging
    # df_m00lpr_subset = df_m00lpr[['EML', 'CVE_AGEB', 'SHP_ID']]
    
    #left merge adm3 rural census and  localities 
    dfl = pd.merge(df_l_rural, df_m00l, on='CVEGEO', how='left')

    #select unmatched entries and left join locality external polygons
    dfln = dfl[dfl['CVE_LOC'].isnull()][main3_cols]

    dfln = pd.merge(dfln, df_m00pe, on='CVEGEO', how='left')

    # df_m00lpr = feature_class_to_pandas_data_frame(m00lpr, m00lpr_cols )
    # df_m00lpr['EML']= df_m00lpr['CVEGEO'].str[:5]+ df_m00lpr['CVE_LOC']
    # df_m00lpr['EMA']= df_m00lpr['CVEGEO'].str[:5]+ df_m00lpr['CVE_AGEB']
    df_m00lpr['EML']= df_m00lpr['CVEGEO'].str[:5]+ df_m00lpr['CVE_LOC']
    df_m00lpr['SHP_ID']= df_m00lpr['CVEGEO'].str[:5]+ df_m00lpr['CVE_AGEB'] + "a"
    # Select only the 'SHP_ID' and 'EML' columns for merging
    df_m00lpr_subset = df_m00lpr[['EML', 'CVE_AGEB', 'SHP_ID']]

    dflnn = dfln[dfln['CVE_LOC'].isnull()][main3_cols]

    ## PRISONS ADDED BACK AS POINTS AND SUMMED TO THE m00amri shape

    # Merge and transfer only 'SHP_ID'
    dflnn = pd.merge(dflnn, df_m00lpr_subset, left_on='CVEGEO', right_on='EML', how='left')

    # Drop 'EML' column (if not needed after merging)
    dflnn = dflnn.drop(columns=['EML'])

    #select unmatched from two attempts above and left merge locality rural points
    # dflnn = dfln[dfln['CVE_LOC'].isnull()][main3_cols]
    # dflnn = pd.merge(dflnn, df_m00lpr, left_on='CVEGEO', right_on='EML', how='left')
    # dflnn = dflnn.rename(columns={"CVEGEO_x": "CVEGEO"})
    
    dflnn['SHP_NAME'] = 'm00armi'
    dflnn['POP_CONTEXT'] = '121'
    

    #check that all admin3 census entries have been matched
    dfln3 = dflnn[dflnn['SHP_ID'].isnull()][main3_cols]

    if len(dfln3) !=0:
        print(len(dfln3), " entries not matched.")
        exit()
        
    else:
        print('- ', shp_folder, ' census 3 matched all entries')

    #select admin5 entries that are matched to manzanas only main columns
    dfconcat = df[~df['CVE_MZA'].isnull()][main_cols]
    #Add name of matched shapefile and shape ID (CVEGEO)
    dfconcat['SHP_NAME'] = 'm00m'
    
    dfconcat['SHP_ID'] = dfconcat['CVEGEO']

    #select admin5 entries that are matched to external manzanas only main columns
    dfnconcat = dfn[~dfn['CVE_MZA'].isnull()][main_cols]
    #Add name of matched shapefile and shape ID (CVEGEO)
    dfnconcat['SHP_NAME'] = 'm00pem'
    dfnconcat['SHP_ID'] = dfnconcat['CVEGEO']

    #select admin5 entries that are matched to external manzanas only main columns plus the matching shape CVEGEO
    dfnnconcat = dfnn[~dfnn['CVE_LOC'].isnull()][main_cols+['peml']]
    #Add name of matched shapefile and shape ID (CVEGEO)
    dfnnconcat['SHP_NAME'] = 'm00peml'
    dfnnconcat = dfnnconcat.rename(columns={'peml': 'SHP_ID'})

    #concatenate all dataframes
    dfconcat = pd.concat([dfconcat, dfnconcat, dfnnconcat, df_prisons], axis=0)

    #select admin3 entries that are matched to localities
    dflconcat = dfl[~dfl['CVE_LOC'].isnull()][main3_cols]
    #Add name of matched shapefile and shape ID (CVEGEO)
    dflconcat['SHP_NAME'] = 'm00l'
    dflconcat['SHP_ID'] = dflconcat['CVEGEO']
    

    #select admin3 entries that are matched to external localities only main columns
    dflnconcat = dfln[~dfln['CVE_LOC'].isnull()][main3_cols]
    #Add name of matched shapefile and shape ID (CVEGEO)
    dflnconcat['SHP_NAME'] = 'm00pe'
    dflnconcat['SHP_ID'] = dflnconcat['CVEGEO']

    #concat points to the rural AGEBs
    dflnnconcat = dflnn[~dflnn['SHP_ID'].isnull()][main3_cols+[ 'SHP_NAME','SHP_ID', 'POP_CONTEXT']]

    ##ADD PRISONS HERE TO CONCATENATE

    if len(dflnnconcat[dflnnconcat['ATOTPOPBT']=="-8888"]) > 0 :
        print('- ', shp_folder, " TOTAL POP BOTH HAS BLANK ROWS")
        exit()
    else:
        print('- ', shp_folder, ' TOTAL POP TEST PASSED for {0}'.format(ucadmin1))
    #rename to SHP_ID
        
    # dflnnconcat = dflnnconcat.rename(columns={'CVEGEO_y': 'SHP_ID'})

    #concatenate the three dataframes
    dfl3concat = pd.concat([dflconcat, dflnconcat, dflnnconcat ], axis=0, ignore_index=True)
    dfl3concat[['ATOTPOPFT','ATOTPOPMT']] = dfl3concat[['ATOTPOPFT','ATOTPOPMT']].astype(int)
    dfl3concat['POP_CONTEXT'] = dfl3concat['POP_CONTEXT'].replace({np.nan: None})


    ### merge the points to the rural AGEBS
    dflmconcat = dflnnconcat.copy()

    exclusions = ["08_ingest", "09_ingest"]

    if all(x not in ingest_csv for x in exclusions):
        print(ingest_csv, " adding prisons.")
        dflmconcat = pd.concat([dflmconcat, df_prisons], axis=0, ignore_index=True)
    else:
        print(ingest_csv, " skipping prisons to aggregate.")
    dflmconcat = dflmconcat.replace([-8888.0], np.nan)
    dflmconcatS = dflmconcat[["SHP_ID", "ATOTPOPBT", "ATOTPOPFT", "ATOTPOPMT"]].groupby("SHP_ID").sum()
    dflmconcatS = dflmconcatS.reset_index()
    dflmconcatS = dflmconcatS.replace(np.nan, -8888.0)
    dflmconcatS = dflmconcatS.replace(0, -8888.0)
    dflmconcatS["CVEGEO"]= dflmconcatS["SHP_ID"]
    # dflmconcatS = dflmconcatS.rename(columns={"SHP_ID": "CVEGEO"})
    #add shape name and ID
    dflmconcatS["SHP_NAME"] = "m00armi"
    dflmconcatS.insert(1, 'UCADMIN3', dflmconcatS['SHP_ID'].str[-4:], True)
    

    #selecting admin information
    dflmconcat = dflnnconcat[["ISO",  "UCADMIN0", "NAME0", "CENSUS_YEAR", "UCADMIN1", "NAME1","UCADMIN2", "NAME2","NAME3", "SHP_ID"]].groupby("SHP_ID").max()
    dflmconcat = dflmconcat.reset_index()
    # dflmconcat = dflmconcat.rename(columns={"SHP_ID": "CVEGEO"})

    # #mergin admin info and summed up data
    dflmconcat = pd.merge(dflmconcat, dflmconcatS, on='SHP_ID', how='right')
    # dflmconcat.insert(0, 'USCID', '' , False)
    dflmconcat['USCID'] = dflmconcat['ISO'].astype(str) + \
        "_"+dflmconcat['UCADMIN1'].astype(str) + \
            "_"+dflmconcat['UCADMIN2'].astype(str)+ \
                "_"+dflmconcat['UCADMIN3'].astype(str) 
    dflmconcat.insert(0, 'USCID', dflmconcat.pop('USCID'))  
    # dflmconcat[['ATOTPOPFT','ATOTPOPMT']] = dflmconcat[['ATOTPOPFT','ATOTPOPMT']].astype(int)
    dflmconcat['POP_CONTEXT'] = '121'

    #concatenate the three admin3 dataframes including merged data
    dflconcat_merge = pd.concat([dflconcat, dflnconcat, dflmconcat ], axis=0)
    # dflconcat_merge['UCADMIN4'] = dflconcat_merge['UCADMIN4'].fillna('0000')
    # col_e = dflconcat_merge.pop("UCADMIN4")
    # dflconcat_merge.insert(12, "UCADMIN4", col_e)
    dflconcat_merge[['ATOTPOPFT','ATOTPOPMT']] = dflconcat_merge[['ATOTPOPFT','ATOTPOPMT']].astype(int)
    print('- ', shp_folder, 'Admin3 rural: {0} + {1} + {3} = {4}. \n- {2} rows summed to {3}'.format(len(dflconcat),len(dflnconcat), len(dflnnconcat), len(dflmconcat),len(dflconcat_merge)))
    dflconcat_merge = dflconcat_merge.where(dflconcat_merge.notnull(), None)
    dflconcat_merge['UCADMIN4'] = np.nan
    dflconcat_merge['UCADMIN5'] = np.nan 

    #combine admin 5 and admin3 dataframes
    # df35concat = pd.concat([dfconcat[dfconcat['NAME3'] != '[CERESO]'], dflconcat_merge], axis=0) #.fillna(0)
    # df35concat = pd.concat([dfconcat[~dfconcat['NAME3'].str.contains(r'\[Cereso\]', na=False)], dflconcat_merge], axis=0)
    df35concat = pd.concat([dfconcat[~dfconcat['NAME3'].str.contains(r'\[cereso\]', na=False, case=False)], dflconcat_merge], axis=0)


    # df35concat['UCADMIN4'] = df35concat['UCADMIN4'].astype(str)  
    # df35concat['UCADMIN5'] = df35concat['UCADMIN5'].astype(str)

    #duplicate ID check
    print('- SHAPE ID duplucates found {0}'.format(df35concat.SHP_ID.duplicated().sum()))
    print('- Census 5 ({0}) and 3 ({1}) merged to {2} rows.'.format(len(dfconcat),len(dflconcat_merge),len(df35concat)))
    if df35concat.SHP_ID.duplicated().sum() > 0:
        
        df35dup = df35concat.loc[df35concat.SHP_ID.duplicated(keep=False), :]
        print(df35dup)
        #exit()

    # #create a excel writer object
    print("- writing excel sheet for ", shp_folder)
    with pd.ExcelWriter(excel_match) as writer:

        # use to_excel function and specify the sheet_name and index
        # to store the dataframe in specified sheet
        dfconcat.to_excel(writer, sheet_name="mex_adm5_match_edit1", index=False, na_rep="")
        dfl3concat.to_excel(writer, sheet_name="mex_adm3_match_edit1", index=False, na_rep="")
        dflconcat_merge.to_excel(writer, sheet_name="mex_adm3_match_edit2", index=False, na_rep="")
        df35concat.to_excel(writer, sheet_name="mex_adm3_5_match", index=False, na_rep="")

    #select SHAPES

    arcpy.Delete_management("in_memory\\m00mi")
    arcpy.Delete_management("in_memory\\m00mni")
    arcpy.Delete_management('in_memory\\m00_ma')
    arcpy.Delete_management('in_memory\\m00_armi')
    arcpy.Delete_management('in_memory\\m00_ami')



    print("- creating shapefile for ", shp_folder)
    #make list of manzanas to select
    field_names = df35concat.loc[df35concat['SHP_NAME']=='m00m', ['SHP_ID']]
    field_names = list(field_names['SHP_ID'])
    fldStr = "', '".join (field_names)
    sql = "CVEGEO IN ('{}')".format (fldStr)
    m00m_len = len(field_names)



    arcpy.Select_analysis(m00m, 'in_memory\\m00_ma', where_clause=sql)



    field_mapping = r'FID FID HIDDEN NONE;Shape Shape HIDDEN NONE;' \
        r'CVEGEO CVEGEO VISIBLE NONE;CVE_ENT CVE_ENT VISIBLE NONE;'\
        r'CVE_MUN CVE_MUN VISIBLE NONE;CVE_LOC CVE_LOC VISIBLE NONE;' \
        r'CVE_AGEB CVE_AGEB VISIBLE NONE;CVE_MZA CVE_MZA VISIBLE NONE;' \
        r'AMBITO AMBITO VISIBLE NONE;TIPOMZA TIPOMZA VISIBLE NONE'




    arcpy.management.MakeFeatureLayer(
        in_features="in_memory\\m00_ma",
        out_layer="in_memory\\m01mi",
        where_clause="TIPOMZA = 'Contenedora'",
        workspace=None,
        field_info=field_mapping
    )

    arcpy.management.MakeFeatureLayer(
        in_features="in_memory\\m00_ma",
        out_layer="in_memory\\m01mni",
        where_clause="TIPOMZA <> 'Contenedora'",
        workspace=None,
        field_info= field_mapping 
    )
    arcpy.analysis.Update(
        in_features="in_memory\\m01mi",
        update_features="in_memory\\m01mni",
        out_feature_class=m00_ingest,
        keep_borders="BORDERS",
        cluster_tolerance=None
    )

    print('- m00m:',)
    get_result(m00_ingest, [m00m_len])

    #add external polygons moanzanas
    fieldMappings = r'CVEGEO "CVEGEO" true true false 16 Text 0 0,First,#,{0}' \
        r',CVEGEO,0,16; CVE_ENT "CVE_ENT" true true false 2 Text 0 0,First,#,{0}' \
        r',CVE_ENT,0,2; CVE_MUN "CVE_MUN" true true false 3 Text 0 0,First,#,{0}' \
        r',CVE_MUN,0,3; CVE_LOC "CVE_LOC" true true false 4 Text 0 0,First,#,{0}' \
        r',CVE_LOC,0,4; CVE_AGEB "CVE_AGEB" true true false 4 Text 0 0,First,#,{0}'  \
        r',CVE_AGEB,0,4; CVE_MZA "CVE_MZA" true true false 3 Text 0 0,First,#,{0}' \
        r',CVE_MZA,0,3; AMBITO "AMBITO" true true false 6 Text 0 0,First,#; TIPOMZA "TIPOMZA" true true false 16 Text 0 0,First,#'.format(m00pem)

    m00pem_len = append_shapes(m00pem, 'm00pem', fieldMappings)
   

    print('- m00pem:')
    get_result(m00_ingest, [m00m_len, m00pem_len])

    #make shapefile admin3 m00peml from 00pe minus 00l 
    arcpy.analysis.Erase(
        in_features=m00pe,
        erase_features=m00l,
        out_feature_class=m00peml,
        cluster_tolerance=None
    )


    fieldMappings = r'CVEGEO "CVEGEO" true true false 16 Text 0 0,First,#,{0},CVEGEO,0,12;' \
        r'CVE_ENT "CVE_ENT" true true false 2 Text 0 0,First,#,{0},CVE_ENT,0,2;' \
        r'CVE_MUN "CVE_MUN" true true false 3 Text 0 0,First,#,{0},CVE_MUN,0,3; ' \
        r' CVE_LOC "CVE_LOC" true true false 4 Text 0 0,First,#,{0},CVE_LOC,0,4;' \
        r'CVE_AGEB "CVE_AGEB" true true false 4 Text 0 0,First,#;'  \
        r'CVE_MZA "CVE_MZA" true true false 3 Text 0 0,First,#;' \
        r'AMBITO "AMBITO" true true false 6 Text 0 0,First,#;' \
        r'TIPOMZA "TIPOMZA" true true false 16 Text 0 0,First,#'.format(m00peml)

    m00peml_len = append_shapes(m00peml, 'm00peml', fieldMappings)
 

    print('- m00peml:')
    get_result(m00_ingest, [m00m_len, m00pem_len, m00peml_len ])

    ##Add admin3 shapes 

    fieldMappings = r'CVEGEO "CVEGEO" true true false 16 Text 0 0,First,#,{0},CVEGEO,0,9;' \
        r'CVE_ENT "CVE_ENT" true true false 2 Text 0 0,First,#,{0},CVE_ENT,0,2;' \
        r'CVE_MUN "CVE_MUN" true true false 3 Text 0 0,First,#,{0},CVE_MUN,0,3; ' \
        r'CVE_LOC "CVE_LOC" true true false 4 Text 0 0,First,#,{0},CVE_LOC,0,4;' \
        r'CVE_AGEB "CVE_AGEB" true true false 4 Text 0 0,First,#;'  \
        r'CVE_MZA "CVE_MZA" true true false 3 Text 0 0,First,#;' \
        r'AMBITO "AMBITO" true true false 6 Text 0 0,First,#,{0},AMBITO,0,6;' \
        r'TIPOMZA "TIPOMZA" true true false 16 Text 0 0,First,#'.format(m00l)

    m00l_len = append_shapes(m00l, 'm00l', fieldMappings)
   
    print('- m00l')
    get_result(m00_ingest, [m00m_len, m00pem_len, m00peml_len, m00l_len ])

    fields = ['CVEGEO','CVEGEO', 'CVE_AGEB', 'CVE_MZA']
    with arcpy.da.UpdateCursor(m00_ingest, fields) as cursor:
        # For each row, evaluate the WELL_YIELD value (index position 
        # of 0), and update WELL_CLASS (index position of 1)
        for row in cursor:
            if row[0] in field_names:
                #print("its in!", row[0])
                #print(row[1])
                row[1] = df35concat.loc[df35concat.SHP_ID == row[0], 'CVEGEO'].values[0]
                row[2] = df35concat.loc[df35concat.SHP_ID == row[0], 'UCADMIN4'].values[0] 
                row[3] = df35concat.loc[df35concat.SHP_ID == row[0], 'UCADMIN5'].values[0] 
                #print(row[1], row[2], row[3])

            else:
                pass
                #print("it's not")
            
            # Update the cursor with the updated list
            cursor.updateRow(row)

    fieldMappings = r'CVEGEO "CVEGEO" true true false 16 Text 0 0,First,#,{0},CVEGEO,0,9;' \
        r'CVE_ENT "CVE_ENT" true true false 2 Text 0 0,First,#,{0},CVE_ENT,0,2;' \
        r'CVE_MUN "CVE_MUN" true true false 3 Text 0 0,First,#,{0},CVE_MUN,0,3; ' \
        r'CVE_LOC "CVE_LOC" true true false 4 Text 0 0,First,#,{0},CVE_LOC,0,4;' \
        r'CVE_AGEB "CVE_AGEB" true true false 4 Text 0 0,First,#;'  \
        r'CVE_MZA "CVE_MZA" true true false 3 Text 0 0,First,#;' \
        r'AMBITO "AMBITO" true true false 6 Text 0 0,First,#;' \
        r'TIPOMZA "TIPOMZA" true true false 16 Text 0 0,First,#'.format(m00pe)

    m00pe_len = append_shapes(m00pe, 'm00pe', fieldMappings)
  
    print('- m00pe')
    get_result(m00_ingest, [m00m_len, m00pem_len, m00peml_len, m00l_len, m00pe_len ])

    #make shapefile admin3 m00armi from 00ar minus m00_ingest 


    arcpy.analysis.Erase(
        in_features=m00ar,
        erase_features=m00_ingest,
        out_feature_class=m00armi,
        cluster_tolerance=None
    )

    # Add a new text field with a length of 13
    arcpy.management.AddField(m00armi, "SHP_ID", "TEXT", field_length=16)
    arcpy.management.CalculateField(m00armi, "SHP_ID", '!CVEGEO! + "a"', "PYTHON3")
    arcpy.management.CalculateField(m00armi, "CVE_AGEB", '!CVE_AGEB! + "a"', "PYTHON3")

    arcpy.management.AddField(m00_ingest, "SHP_ID", "TEXT", field_length=16)
    arcpy.management.CalculateField(m00_ingest, "SHP_ID", f"!CVEGEO!")


    # Copy values from the old field to the new field
    # arcpy.CalculateField_management(m00armi, new_field, f"!CVEGEO!", "PYTHON3")

    # # Delete the old field (optional)
    # arcpy.DeleteField_management(m00armi, "CVEGEO")

    # # Rename the new field to the original name (optional)
    # arcpy.AlterField_management(m00armi, new_field, "CVEGEO")

    # arcpy.management.AlterField(
    #     in_table=m00armi,
    #     field="CVEGEO",
    #     new_field_name="",
    #     new_field_alias="",
    #     field_type="TEXT",  
    #     field_length=13,
    #     field_is_nullable="NULLABLE",
    #     clear_field_alias="DO_NOT_CLEAR"
    # )
    # arcpy.management.CalculateField(m00armi, "CVEGEO", '!CVE_ENT! + !CVE_MUN! + "0000" + !CVE_AGEB! ', "PYTHON3")

    # add selected rural agebs to ingest

    fieldMappings = r'CVEGEO "CVEGEO" true true false 16 Text 0 0,First,#,{0},CVEGEO,0,9;' \
        r'CVE_ENT "CVE_ENT" true true false 2 Text 0 0,First,#,{0},CVE_ENT,0,2;' \
        r'CVE_MUN "CVE_MUN" true true false 3 Text 0 0,First,#,{0},CVE_MUN,0,3; ' \
        r'CVE_LOC "CVE_LOC" true true false 4 Text 0 0,First,#;' \
        r'CVE_AGEB "CVE_AGEB" true true false 4 Text 0 0,First,#, {0}, CVE_AGEB,0,5;'  \
        r'CVE_MZA "CVE_MZA" true true false 3 Text 0 0,First,#;' \
        r'AMBITO "AMBITO" true true false 6 Text 0 0,First,#;' \
        r'TIPOMZA "TIPOMZA" true true false 16 Text 0 0,First,#;' \
        r'SHP_ID "SHP_ID" true true false 16 Text 0 0,First,#, {0}, SHP_ID,0,16'.format(m00armi)


    
    m00armi_len = append_shapes_ID(m00armi, 'm00armi', fieldMappings)
   
    

    print('- m00armi')
    get_result(m00_ingest, [m00m_len, m00pem_len, m00peml_len, m00l_len, m00pe_len, m00armi_len])


        # Specify the field to keep
    field_to_keep = "SHP_ID"

    # Get a list of all fields in the feature class
    fields = [f.name for f in arcpy.ListFields(m00_ingest) if f.name not in ("OBJECTID", "Shape", "Shape_Length", "Shape_Area")]
    # Identify fields to delete (all except the one to keep)
    fields_to_delete = [f for f in fields if f != field_to_keep]

    # Delete unwanted fields
    if fields_to_delete:
        arcpy.DeleteField_management(m00_ingest, fields_to_delete)


        
    # Step 1: Get existing fields in the feature class
    existing_fields = [f.name for f in arcpy.ListFields(m00_ingest)]

    # Step 2: Identify and add missing fields
    missing_fields = [col for col in df35concat.columns if col not in existing_fields]

    for field in missing_fields:
        if df35concat[field].dtype in [np.int64, np.float64]:
            field_type = "DOUBLE"
        else:
            field_type = "TEXT"
        arcpy.AddField_management(m00_ingest, field, field_type)
        # print(f"Added field {field} of type {field_type}")

    # Step 3: Convert DataFrame to dictionary for fast lookup
    df_dict = df35concat.set_index('SHP_ID').to_dict(orient='index')

    # Step 4: Update feature class using UpdateCursor
    fields = ['SHP_ID'] + [col for col in df35concat.columns if col != 'SHP_ID']

    with arcpy.da.UpdateCursor(m00_ingest, fields) as cursor:
        for row in cursor:
            shp_id = row[0]  # SHP_ID is the first field
            if shp_id in df_dict:
                for i, col in enumerate(fields[1:], start=1):
                    row[i] = df_dict[shp_id].get(col, None)  # Assign values from df_dict
                cursor.updateRow(row)




    # x = np.array(np.rec.fromrecords(df35concat.values))
    # names = df35concat.dtypes.index.tolist()
    # x.dtype.names = tuple(names)
    

    # if arcpy.Exists("in_memory\\mytable"):
    #     arcpy.Delete_management("in_memory\\mytable")
        
    # arcpy.da.NumPyArrayToTable(x, "in_memory\\mytable")
    # try:
    #     print('- joining census table to shapefile... ')
    #     arcpy.management.JoinField(m00_ingest, 'SHP_ID', "in_memory\\mytable", 'SHP_ID')
    # except:
    #     print(arcpy.GetMessages())

    # arcpy.DeleteField_management(m00_ingest, "SHP_ID_1")
        
    


    # len_result = m00m_len+m00pem_len+m00peml_len+m00l_len+m00pe_len+m00armi_len
    # result = arcpy.management.GetCount(m00_ingest)
    # result = int(result[0])
    # m00armi_len_xtr = result-len_result
    # print("- ", m00armi_len_xtr, " rural ageb polygons added that are not matched to number of rows.")
    



    ##ADD ENTITY TO FILL REMAINDER OF GAPS 
    #ADD AGEB TO FILL REMAINDER OF GAPS
    print("- creating areas with zero population...")


    arcpy.analysis.Erase(
        in_features= m00mun,  #  m00ent,
        erase_features=m00_ingest,
        out_feature_class=m00ami, #m00entmi,
        cluster_tolerance=None
    )

    # Rename the field
    
    arcpy.management.AddField(m00ami, 'USCID', "TEXT")
    arcpy.management.AddField(m00ami, 'ISO', "TEXT")
    arcpy.management.AddField(m00ami, 'UCADMIN0', "SHORT")
    arcpy.management.AddField(m00ami, 'NAME0', "TEXT")
    arcpy.management.AddField(m00ami, 'NAME1', "TEXT")
    arcpy.management.AddField(m00ami, 'CENSUS_YEAR', "SHORT")
    arcpy.management.AddField(m00ami, 'ATOTPOPBT', "SHORT")
    arcpy.management.AddField(m00ami, 'ATOTPOPFT', "SHORT")
    arcpy.management.AddField(m00ami, 'ATOTPOPMT', "SHORT")
    arcpy.management.AddField(m00ami, 'SHP_NAME', "TEXT")
    arcpy.management.AddField(m00ami, 'SHP_ID', "TEXT", 255)

    # arcpy.management.AddField(m00ami, 'POP_CONTEXT', "SHORT")
    arcpy.management.AddField(m00ami, 'BOUNDARY_CONTEXT', "SHORT")
    # arcpy.management.AddField(m00_ingest, 'POP_CONTEXT', "SHORT")
    arcpy.management.AddField(m00_ingest, 'BOUNDARY_CONTEXT', "SHORT")

    arcpy.management.AlterField(m00ami, 'CVE_ENT', 'UCADMIN1', 'UCADMIN1')
    arcpy.management.AlterField(m00ami, 'CVE_MUN', 'UCADMIN2', 'UCADMIN2')
    arcpy.management.AlterField(m00ami, 'NOMGEO', 'NAME2', 'NAME2')

    arcpy.management.CalculateField(m00ami, "SHP_ID", "!CVEGEO!")
    
    arcpy.management.CalculateField(m00ami, "ISO", "'MEX'", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "NAME0", "'Mexico'", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "CENSUS_YEAR", "2020", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "UCADMIN0", "484", "PYTHON3")
    # arcpy.management.CalculateField(m00ami, "POP_CONTEXT", "115", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "ATOTPOPBT", "0", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "ATOTPOPFT",  "0", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "ATOTPOPMT",  "0", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "BOUNDARY_CONTEXT", "10", "PYTHON3")
    arcpy.management.CalculateField(m00ami, "USCID", "!ISO! + '_' + !UCADMIN1! + '_'  +str(!UCADMIN2!)", "PYTHON3")
    arcpy.management.CalculateField(m00ami,"SHP_NAME", "'m00mun'", "PYTHON3")

    arcpy.management.MultipartToSinglepart(m00ami, m00amims)


    fieldMappings=f'SHP_ID "SHP_ID" true true false 16 Text 0 0,First,#,'\
    f'{m00amims},SHP_ID,0,254;USCID "USCID" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},USCID,0,254;CVEGEO "CVEGEO" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},CVEGEO,0,4;ISO "ISO" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},ISO,0,254;UCADMIN0 "UCADMIN0" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},UCADMIN0,-1,-1;NAME0 "NAME0" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},NAME0,0,254;CENSUS_YEAR "CENSUS_YEAR" true true false 8 Double 0 0,First,#,'\
    f'{m00amims},CENSUS_YEAR,-1,-1;UCADMIN1 "UCADMIN1" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},UCADMIN1,0,1;NAME1 "NAME1" true true false 255 Text 0 0,First,#;'\
    f'UCADMIN2 "UCADMIN2" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},UCADMIN2,0,2;NAME2 "NAME2" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},NAME2,0,79;UCADMIN3 "UCADMIN3" true true false 255 Text 0 0,First,#;'\
    f'NAME3 "NAME3" true true false 255 Text 0 0,First,#;'\
    f'UCADMIN4 "UCADMIN4" true true false 255 Text 0 0,First,#;'\
    f'UCADMIN5 "UCADMIN5" true true false 255 Text 0 0,First,#;'\
    f'ATOTPOPBT "ATOTPOPBT" true true false 8 Double 0 0,First,#;'\
    f'ATOTPOPFT "ATOTPOPFT" true true false 8 Double 0 0,First,#;'\
    f'ATOTPOPMT "ATOTPOPMT" true true false 8 Double 0 0,First,#;'\
    f'SHP_NAME "SHP_NAME" true true false 255 Text 0 0,First,#,'\
    f'{m00amims},SHP_NAME,0,254;POP_CONTEXT "POP_CONTEXT" true true false 255 Text 0 0,First,#;'\
    f'BOUNDARY_CONTEXT "BOUNDARY_CONTEXT" true true false 2 Short 0 0,First,#,'\
    f'{m00amims},BOUNDARY_CONTEXT,-1,-1'
    


    try:
        print("- appending zero population areas.")
        arcpy.management.Append(
            inputs=m00amims,
            target=m00_ingest,
            schema_type="NO_TEST",
            field_mapping= fieldMappings,
            subtype="",
            expression= "",
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages()) 
    m00amims_len= int(arcpy.GetCount_management(m00amims)[0])
  
    print('- m00amims')
    get_result(m00_ingest, [m00m_len, m00pem_len, m00peml_len, m00l_len, m00pe_len, m00armi_len, m00amims_len ])
    
    
    print("- length of each subset: ", m00m_len, m00pem_len, m00peml_len, m00l_len, m00pe_len,  m00armi_len, m00amims_len )
    print("- Sum of above: ", sum( [m00m_len, m00pem_len, m00peml_len, m00l_len, m00pe_len,  m00armi_len, m00amims_len]))
    # print("- length of concatenated dataframe: ", len(df35concat), " + ", m00armi_len_xtr, " rural agebs not matched + 1 filling gaps = ", len(df35concat)+ m00armi_len_xtr + 1)
    result = arcpy.management.GetCount(m00_ingest)
    result = int(result[0])
    print("- length of concatenated shapefile: ", result)

