#Jane Mills
#5/31/2017
#Add areas to centroids

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

tableFields = ['UBID','UNE_ATOTPOPBT_2000','UNE_ATOTPOPBT_2005','UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015',
               'UNE_ATOTPOPBT_2020','E_ATOTPOPBT_2010','E_ATOTPOPFT_2010','E_ATOTPOPMT_2010','E_A000_004BT_2010',
               'E_A005_009BT_2010','E_A010_014BT_2010','E_A015_019BT_2010','E_A020_024BT_2010','E_A025_029BT_2010',
               'E_A030_034BT_2010','E_A035_039BT_2010','E_A040_044BT_2010','E_A045_049BT_2010','E_A050_054BT_2010',
               'E_A055_059BT_2010','E_A060_064BT_2010','E_A065PLUSBT_2010','E_A065_069BT_2010','E_A070PLUSBT_2010',
               'E_A070_074BT_2010','E_A075PLUSBT_2010','E_A075_079BT_2010','E_A080PLUSBT_2010','E_A080_084BT_2010',
               'E_A085PLUSBT_2010','E_A000_004FT_2010','E_A005_009FT_2010','E_A010_014FT_2010','E_A015_019FT_2010',
               'E_A020_024FT_2010','E_A025_029FT_2010','E_A030_034FT_2010','E_A035_039FT_2010','E_A040_044FT_2010',
               'E_A045_049FT_2010','E_A050_054FT_2010','E_A055_059FT_2010','E_A060_064FT_2010','E_A065PLUSFT_2010',
               'E_A065_069FT_2010','E_A070PLUSFT_2010','E_A070_074FT_2010','E_A075PLUSFT_2010','E_A075_079FT_2010',
               'E_A080PLUSFT_2010','E_A080_084FT_2010','E_A085PLUSFT_2010','E_A000_004MT_2010','E_A005_009MT_2010',
               'E_A010_014MT_2010','E_A015_019MT_2010','E_A020_024MT_2010','E_A025_029MT_2010','E_A030_034MT_2010',
               'E_A035_039MT_2010','E_A040_044MT_2010','E_A045_049MT_2010','E_A050_054MT_2010','E_A055_059MT_2010',
               'E_A060_064MT_2010','E_A065PLUSMT_2010','E_A065_069MT_2010','E_A070PLUSMT_2010','E_A070_074MT_2010',
               'E_A075PLUSMT_2010','E_A075_079MT_2010','E_A080PLUSMT_2010','E_A080_084MT_2010','E_A085PLUSMT_2010']

cenFields = ['UBID','UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E','UN_2020_E','B_2010_E','F_2010_E','M_2010_E',
             'A00_04B','A05_09B','A10_14B','A15_19B','A20_24B','A25_29B','A30_34B','A35_39B','A40_44B','A45_49B',
             'A50_54B','A55_59B','A60_64B','A65PLUSB','A65_69B','A70PLUSB','A70_74B','A75PLUSB','A75_79B','A80PLUSB',
             'A80_84B','A85PLUSB','A00_04F','A05_09F','A10_14F','A15_19F','A20_24F','A25_29F','A30_34F','A35_39F',
             'A40_44F','A45_49F','A50_54F','A55_59F','A60_64F','A65PLUSF','A65_69F','A70PLUSF','A70_74F','A75PLUSF',
             'A75_79F','A80PLUSF','A80_84F','A85PLUSF','A00_04M','A05_09M','A10_14M','A15_19M','A20_24M','A25_29M',
             'A30_34M','A35_39M','A40_44M','A45_49M','A50_54M','A55_59M','A60_64M','A65PLUSM','A65_69M','A70PLUSM',
             'A70_74M','A75PLUSM','A75_79M','A80PLUSM','A80_84M','A85PLUSM']

for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:5]
    else:
        iso = fc[:3]
    cenPath = os.path.join(centroids,iso+"_centroids")
    print iso
    dataDict = {}

    with arcpy.da.SearchCursor(fc,tableFields) as cursor:
        for row in cursor:
            dataDict[row[0]] = row[1:]

    #Add to centroids
    with arcpy.da.UpdateCursor(cenPath,cenFields) as cursor:
        for row in cursor:
            if row[0] in dataDict:
                row[1:] = dataDict[row[0]]
                cursor.updateRow(row)
            else:
                print row[0],"not in gridding"

    del dataDict

print 'done'
