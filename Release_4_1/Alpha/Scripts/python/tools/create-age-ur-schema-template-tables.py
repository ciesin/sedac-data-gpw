# create age schema tables
import arcpy, os
# set workspace
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\schema_tables.gdb'
# define age fields
ageFields = ['A000_004BT','A005_009BT','A010_014BT','A015_019BT','A020_024BT','A025_029BT',
            'A030_034BT','A035_039BT','A040_044BT','A045_049BT','A050_054BT','A055_059BT',
            'A060_064BT','A065_069BT','A070_074BT','A075_079BT','A080_084BT','A085plusBT']
# define ur fields
urFields = ['ATOTPOPBU','ATOTPOPBR','ATOTPOPFU','ATOTPOPFR','ATOTPOPMU','ATOTPOPMR']

# list total pop tables
tbls = arcpy.ListTables('total_pop*')
for tbl in tbls:
    print tbl
    ageTable = 'age_structure_5_year_' + tbl.split("_")[2]
    urTable = 'ur_structure_' + tbl.split("_")[2]
    newTables = [ageTable,urTable]
    # make a copy of the total pop table for the age data and the ur data
    for newTable in newTables:
        arcpy.Copy_management(tbl,newTable)
        # add fields
        [arcpy.AddField_management(newTable,ageField,"DOUBLE")
         for ageField in ageFields if newTable == ageTable]
        [arcpy.AddField_management(newTable,urField,"DOUBLE")
         for urField in urFields if newTable == urTable]
    
    # alter RPOPYEAR to variable appropriate name
    [arcpy.AlterField_management(newTable,"RPOPYEAR","APOPYEAR","APOPYEAR")
     for newTable in newTables if newTable == ageTable]
    [arcpy.AlterField_management(newTable,"RPOPYEAR","UPOPYEAR","UPOPYEAR")
     for newTable in newTables if newTable == urTable]

    
    
       
