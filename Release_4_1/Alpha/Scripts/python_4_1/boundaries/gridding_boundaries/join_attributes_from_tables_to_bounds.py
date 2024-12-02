#Jane Mills
#3/23/2017
#Add areas to centroids

# Import Libraries
import arcpy, os

tableFolder = r'D:\gpw\release_4_1\input_data\pop_tables'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['E_ATOTPOPBT_1975','E_ATOTPOPBT_1990','E_ATOTPOPBT_2000','E_ATOTPOPBT_2005','E_ATOTPOPBT_2010','E_ATOTPOPBT_2015',
          'E_ATOTPOPBT_2020','E_ATOTPOPFT_2010','E_ATOTPOPMT_2010','E_A000_004BT_2010','E_A000_014BT_2010','E_A005_009BT_2010',
          'E_A010_014BT_2010','E_A015_019BT_2010','E_A015_064BT_2010','E_A020_024BT_2010','E_A025_029BT_2010','E_A030_034BT_2010',
          'E_A035_039BT_2010','E_A040_044BT_2010','E_A045_049BT_2010','E_A050_054BT_2010','E_A055_059BT_2010','E_A060_064BT_2010',
          'E_A065PLUSBT_2010','E_A065_069BT_2010','E_A070PLUSBT_2010','E_A070_074BT_2010','E_A075PLUSBT_2010','E_A075_079BT_2010',
          'E_A080PLUSBT_2010','E_A080_084BT_2010','E_A085PLUSBT_2010','E_A000_004FT_2010','E_A005_009FT_2010','E_A010_014FT_2010',
          'E_A015_019FT_2010','E_A020_024FT_2010','E_A025_029FT_2010','E_A030_034FT_2010','E_A035_039FT_2010','E_A040_044FT_2010',
          'E_A045_049FT_2010','E_A050_054FT_2010','E_A055_059FT_2010','E_A060_064FT_2010','E_A065PLUSFT_2010','E_A065_069FT_2010',
          'E_A070PLUSFT_2010','E_A070_074FT_2010','E_A075PLUSFT_2010','E_A075_079FT_2010','E_A080PLUSFT_2010','E_A080_084FT_2010',
          'E_A085PLUSFT_2010','E_A000_004MT_2010','E_A005_009MT_2010','E_A010_014MT_2010','E_A015_019MT_2010','E_A020_024MT_2010',
          'E_A025_029MT_2010','E_A030_034MT_2010','E_A035_039MT_2010','E_A040_044MT_2010','E_A045_049MT_2010','E_A050_054MT_2010',
          'E_A055_059MT_2010','E_A060_064MT_2010','E_A065PLUSMT_2010','E_A065_069MT_2010','E_A070PLUSMT_2010','E_A070_074MT_2010',
          'E_A075PLUSMT_2010','E_A075_079MT_2010','E_A080PLUSMT_2010','E_A080_084MT_2010','E_A085PLUSMT_2010','UNE_ATOTPOPBT_1975',
          'UNE_ATOTPOPBT_1990','UNE_ATOTPOPBT_2000','UNE_ATOTPOPBT_2005','UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015','UNE_ATOTPOPBT_2020']

for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:5]
    else:
        iso = fc[:3]
    print iso

    fcPath = os.path.join(gridding,fc)

    gdb = os.path.join(tableFolder,iso+'.gdb')
    try:
        arcpy.env.workspace = gdb
        tableList = arcpy.ListTables("*estimates")
        if len(tableList)> 0:
            table = tableList[0]

            tableFields = [field.name for field in arcpy.ListFields(table)]
            fieldList = ['UBID']+ filter(lambda f: f in fields, tableFields)

            if len(fieldList) > 1:
                dataDict = {}
        
                with arcpy.da.SearchCursor(table,fieldList) as cursor:
                    for row in cursor:
                        dataDict[row[0]] = row[1:]

                fieldList.append('CONTEXT')
                fieldList.append('WATER_CODE')
                with arcpy.da.UpdateCursor(fcPath,fieldList) as cursor:
                    for row in cursor:
                        #clear the row
                        row[1:-2] = [None]*len(row[1:-2])
                        #fill the row
                        if row[0] in dataDict:
                            row[1:-2] = dataDict[row[0]]
                        elif row[-2] == 0 and row[-1] == 'L':
                            print "did not find ubid:", row[0]
                        cursor.updateRow(row)

                del dataDict
        print "success"
    except:
        print "failure"

print 'done'
