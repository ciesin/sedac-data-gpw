import arcpy, csv, os

root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\pop_tables'

arcpy.env.workspace = root

gdbList = arcpy.ListWorkspaces("*","FILEGDB")
gdbList.sort()

csvFile = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\age_validation_2.csv'
csvMem = csv.writer(open(csvFile,"wb"))
csvMem.writerow(['ISO','UBID','CONTEXT','ATOTPOPBT','ATOTPOPFT','ATOTPOPMT','Sum_BT_ages','Sum_FT_ages','Sum_MT_ages'])

headers = ['UBID','POP_CONTEXT','E_ATOTPOPBT_2010','E_ATOTPOPFT_2010','E_ATOTPOPMT_2010','E_A000_004BT_2010','E_A005_009BT_2010',
           'E_A010_014BT_2010','E_A015_019BT_2010','E_A020_024BT_2010','E_A025_029BT_2010','E_A030_034BT_2010','E_A035_039BT_2010',
           'E_A040_044BT_2010','E_A045_049BT_2010','E_A050_054BT_2010','E_A055_059BT_2010','E_A060_064BT_2010','E_A065PLUSBT_2010',
           'E_A000_004FT_2010','E_A005_009FT_2010','E_A010_014FT_2010','E_A015_019FT_2010','E_A020_024FT_2010','E_A025_029FT_2010',
           'E_A030_034FT_2010','E_A035_039FT_2010','E_A040_044FT_2010','E_A045_049FT_2010','E_A050_054FT_2010','E_A055_059FT_2010',
           'E_A060_064FT_2010','E_A065PLUSFT_2010','E_A000_004MT_2010','E_A005_009MT_2010','E_A010_014MT_2010','E_A015_019MT_2010',
           'E_A020_024MT_2010','E_A025_029MT_2010','E_A030_034MT_2010','E_A035_039MT_2010','E_A040_044MT_2010','E_A045_049MT_2010',
           'E_A050_054MT_2010','E_A055_059MT_2010','E_A060_064MT_2010','E_A065PLUSMT_2010']

for gdb in gdbList:
    arcpy.env.workspace = gdb
    iso = os.path.basename(gdb)
    print iso
    
    tables = arcpy.ListTables("*estimates")
    if len(tables) == 1 and len(arcpy.ListTables("*estimates*"))> 1:
        table = tables[0]

        with arcpy.da.SearchCursor(table,headers,"UBID IS NOT NULL") as cursor:
            for row in cursor:
                csvrow = [iso,row[0],row[1],row[2],row[3],row[4],sum(row[5:19]),sum(row[19:33]),sum(row[33:])]
                #check sex
                if abs(row[2]-row[3]-row[4]) > 0.5 or abs(row[2]-sum(row[5:19])) > 0.5 or abs(row[3]-sum(row[19:33])) > 0.5 or abs(row[4]-sum(row[33:])) > 0.5:
                    csvMem.writerow(csvrow)


#check sex alone
##csvFile = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\sex_validation.csv'
##csvMem = csv.writer(open(csvFile,"wb"))
##csvMem.writerow(['ISO','GUBID','CONTEXT','ATOTPOPBT','ATOTPOPFT','ATOTPOPMT'])
##
##headers = ['GUBID','CONTEXT','B_2010_E','F_2010_E','M_2010_E']
##
##for fc in fcList:
##    iso = fc[:-10]
##    print iso
##
##    with arcpy.da.SearchCursor(fc,headers) as cursor:
##        for row in cursor:
##            csvrow = [iso,row[0],row[1],row[2],row[3],row[4]]
##            #check sex
##            if abs(row[2]-row[3]-row[4]) > 0.5:
##                csvMem.writerow(csvrow)
