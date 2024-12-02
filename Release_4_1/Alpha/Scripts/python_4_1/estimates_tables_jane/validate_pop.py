import arcpy, csv, os, numpy

rootFolder = r'D:\gpw\release_4_1\loading\processed'

isoList = ['bfa','bhr','blr','caf','col','cuw','dji','eri','gab','grd','irq',
           'lbn','mdg','mhl','prt','rus','som','tca','tjk','tkm','ukr','uzb']
gdbList = [os.path.join(rootFolder,iso+'.gdb') for iso in isoList]
#arcpy.env.workspace = root
#gdbList = arcpy.ListWorkspaces("*","FILEGDB")
#gdbList.sort()

headers = ['E_ATOTPOPBT_2010','E_ATOTPOPFT_2010','E_ATOTPOPMT_2010','E_A000_004BT_2010','E_A005_009BT_2010',
           'E_A010_014BT_2010','E_A015_019BT_2010','E_A020_024BT_2010','E_A025_029BT_2010','E_A030_034BT_2010','E_A035_039BT_2010',
           'E_A040_044BT_2010','E_A045_049BT_2010','E_A050_054BT_2010','E_A055_059BT_2010','E_A060_064BT_2010','E_A065PLUSBT_2010',
           'E_A000_004FT_2010','E_A005_009FT_2010','E_A010_014FT_2010','E_A015_019FT_2010','E_A020_024FT_2010','E_A025_029FT_2010',
           'E_A030_034FT_2010','E_A035_039FT_2010','E_A040_044FT_2010','E_A045_049FT_2010','E_A050_054FT_2010','E_A055_059FT_2010',
           'E_A060_064FT_2010','E_A065PLUSFT_2010','E_A000_004MT_2010','E_A005_009MT_2010','E_A010_014MT_2010','E_A015_019MT_2010',
           'E_A020_024MT_2010','E_A025_029MT_2010','E_A030_034MT_2010','E_A035_039MT_2010','E_A040_044MT_2010','E_A045_049MT_2010',
           'E_A050_054MT_2010','E_A055_059MT_2010','E_A060_064MT_2010','E_A065PLUSMT_2010']

csvFile = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\age_validation_5_23.csv'
csvMem = csv.writer(open(csvFile,"wb"))
csvMem.writerow(['ISO'] + headers)

for gdb in gdbList:
    arcpy.env.workspace = gdb
    iso = os.path.basename(gdb)[:-4]
    print iso
    
    table = arcpy.ListTables("*estimates")[0]

    data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    with arcpy.da.SearchCursor(table,headers,"UBID IS NOT NULL") as cursor:
        for row in cursor:
            data = list(numpy.array(data) + numpy.array(row))

    csvMem.writerow([iso]+data)


