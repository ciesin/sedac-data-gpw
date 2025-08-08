import arcpy
import os

in_memory = r"F:\gpwv5\country\MEX\mex_ingest.gdb"
fc_path = r"Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Boundaries\mex_admin3_5\mex_admin3_5.gdb\m00_final_ingest"
out_fc = r"F:\gpwv5\country\MEX\mex_ingest.gdb\m00_final_ingest_updated"

arcpy.env.workspace = in_memory
arcpy.env.overwriteOutput = True




# Create initial feature layer from m00m
arcpy.conversion.ExportFeatures(fc_path, out_fc, where_clause=""" "SHP_NAME" = 'm00m' """)
initial_count = arcpy.GetCount_management(out_fc)
print(f"Rows in initial 'm00m' layer: {initial_count}")

# List of SHP_NAME values to process iteratively
shp_names = ['m00pem', 'm00peml', 'm00l', 'm00pe', 'm00armi', 'm00mun']

for shp_name in shp_names[:3]:
    source_temp = os.path.join(in_memory, "m00source_temp")

    arcpy.management.MakeFeatureLayer(fc_path, source_temp, f""" "SHP_NAME" = '{shp_name}' """)
    source_count = arcpy.GetCount_management(source_temp)
    print(f"Processing '{shp_name}' - initial rows: {source_count}")
    #     # erase_temp = os.path.join(in_memory, "erase_temp")
    
    erase_temp = r"F:\gpwv5\country\MEX\mex_ingest.gdb\m00_final_erasetemp"
    try:
        arcpy.analysis.Erase(source_temp, out_fc, erase_temp)

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        print("Erase or append operation failed.")



    count = arcpy.GetCount_management(erase_temp)
    print(f"Erase successful. Rows remaining: {count}")

    if count > 0:
        try:
            arcpy.management.Append(erase_temp, out_fc, "TEST")
            updated_count = arcpy.GetCount_management(out_fc)
            print(f"Append successful. Rows after append: {updated_count}")
        
        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))
            print("Erase or append operation failed.")
    else:
        print("No rows to append after erase.")

       

    

#     # erase_and_append(source_temp, out_fc)

# print(" All processing complete.")


# # def append_to_feature(temp_df, updated_temp, erase_temp):
# #     try:
# #         arcpy.analysis.Erase(
# #             in_features=temp_df,
# #             erase_features=updated_temp,
# #             out_feature_class=erase_temp,
# #             cluster_tolerance=None
# #         )
# #     except: 
# #         print("erase failed")
# #         # exit()
        
# #     count = arcpy.GetCount_management(erase_temp)

# #     print(f"Number of rows in erase: {count}")
# #     print("trying append")

    
# #     try: 
# #         arcpy.management.Append(
# #                 inputs=erase_temp,
# #                 target=updated_temp,
# #                 schema_type="TEST",
# #                 field_mapping= None,
# #                 subtype="",
# #                 expression= "",
# #                 match_fields=None,
# #                 update_geometry="NOT_UPDATE_GEOMETRY")
# #         count = arcpy.GetCount_management(updated_temp)
# #         print(f"Number of rows after append: {count}")
# #     except: 
# #         print("append failed")
# #         # exit()

# # # m00m_temp = os.path.join(in_memory, "m00m")
# # m00pem_temp = os.path.join(in_memory, "m00pem")
# # m00peml_temp = os.path.join(in_memory, "m00peml")
# # m00l_temp = os.path.join(in_memory, "m00l")
# # m00pe_temp = os.path.join(in_memory, "m00pe")
# # m00armi_temp = os.path.join(in_memory, "m00armi")
# # m00mun_temp = os.path.join(in_memory, "m00mun")
# # updated_temp = os.path.join(in_memory, "m00updated")
# # erase_temp = os.path.join(in_memory, "erase_temp")

# # arcpy.env.workspace = in_memory
# # arcpy.management.MakeFeatureLayer(fc_path, out_fc,  where_clause=""" "SHP_NAME" = 'm00m' """)
# # count = arcpy.GetCount_management(out_fc)

# # print(f"Number of rows in m00m: {count}")



    


# # arcpy.management.MakeFeatureLayer(fc_path, m00pem_temp, """ "SHP_NAME" = 'm00pem' """)
# # count = arcpy.GetCount_management(m00pem_temp)

# # print(f"Number of rows in m00pem_temp: {count}")

# # # append_to_feature(m00pem_temp, updated_temp, erase_temp)

# # try:
# #     arcpy.analysis.Erase(
# #         in_features=m00pem_temp,
# #         erase_features=out_fc,
# #         out_feature_class=erase_temp,
# #         cluster_tolerance=None
# #     )
# # except: 
# #     print("erase failed")
# #     # exit()
    
# # count = arcpy.GetCount_management(erase_temp)

# # print(f"Number of rows in erase: {count}")
# # print("trying append")


# # try: 
# #     arcpy.management.Append(
# #             inputs=erase_temp,
# #             target=out_fc,
# #             schema_type="TEST",
# #             field_mapping= None,
# #             subtype="",
# #             expression= "",
# #             match_fields=None,
# #             update_geometry="NOT_UPDATE_GEOMETRY")
# #     count = arcpy.GetCount_management(updated_temp)
# #     print(f"Number of rows after append: {count}")
# # except: 
# #     print("append failed")
# #     # exit()



# # arcpy.management.CopyFeatures(updated_temp, out_fc)

# # append_to_feature(m00peml_temp,  """ "SHP_NAME" = 'm00peml' """)
# # count = arcpy.GetCount_management(out_fc)
# # print(f"Number of rows after append: {count}")

# # append_to_feature(m00l_temp, """ "SHP_NAME" = 'm00l' """)

# # count = arcpy.GetCount_management(out_fc)
# # print(f"Number of rows after append: {count}")

# # append_to_feature(m00pe_temp, """ "SHP_NAME" = 'm00pe' """)
# # count = arcpy.GetCount_management(out_fc)
# # print(f"Number of rows after append: {count}")

# # append_to_feature(m00armi_temp, """ "SHP_NAME" = 'm00armi' """)
# # count = arcpy.GetCount_management(out_fc)
# # print(f"Number of rows after append: {count}")

# # append_to_feature(m00mun_temp, """ "SHP_NAME" = 'm00mun' """)
# # count = arcpy.GetCount_management(out_fc)
# # print(f"Number of rows after append: {count}")
 
    