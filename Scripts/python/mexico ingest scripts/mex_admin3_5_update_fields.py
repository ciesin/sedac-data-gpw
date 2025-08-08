import arcpy
import os

# Paths to the source and target geodatabases
source_gdb = r"Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Boundaries\mex_admin3_5\new\mex_admin3_5.gdb"
target_gdb = r"Z:\GPW\GPW5\Preprocessing\Country\MEX\Ingest\Boundaries\ingest\mex_ingest.gdb" 
master_fc_name = "mex_admin3_5_ingested"  # feature class inside the target_gdb
master_fc_path = os.path.join(target_gdb, master_fc_name)

# Fields to extract and update
match_field = "CVEGEO"
update_fields = ["ATOTPOPMT", "ATOTPOPBT", "ATOTPOPFT"]

# Dictionary to hold merged data from all feature classes
data_dict = {}

# Loop through all feature classes in the source geodatabase
arcpy.env.workspace = source_gdb
feature_classes = arcpy.ListFeatureClasses()

for fc in feature_classes:
    print(f"Processing: {fc}")
    with arcpy.da.SearchCursor(fc, [match_field] + update_fields) as cursor:
        for row in cursor:
            key = row[0]
            values = row[1:]
            data_dict[key] = values  # This will overwrite if keys repeat; adjust logic if needed

# Update the master feature class using UpdateCursor
with arcpy.da.UpdateCursor(master_fc_path, [match_field] + update_fields) as cursor:
    for row in cursor:
        key = row[0]
        if key in data_dict:
            row[1:] = data_dict[key]
            cursor.updateRow(row)

print("Update completed.")
