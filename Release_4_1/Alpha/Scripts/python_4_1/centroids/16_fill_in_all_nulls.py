#Jane Mills
#3/23/2017
#Fill in pop counts for units with data context

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

cenFields = ['UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E',
             'UN_2020_E','UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS','B_2010_E',
             'F_2010_E','M_2010_E','A00_04B', 'A00_04F', 'A00_04M', 'A05_09B', 'A05_09F', 'A05_09M',
             'A10_14B', 'A10_14F', 'A10_14M', 'A15_19B', 'A15_19F', 'A15_19M', 'A20_24B', 'A20_24F',
             'A20_24M', 'A25_29B', 'A25_29F', 'A25_29M', 'A30_34B', 'A30_34F', 'A30_34M', 'A35_39B',
             'A35_39F', 'A35_39M', 'A40_44B', 'A40_44F', 'A40_44M', 'A45_49B', 'A45_49F', 'A45_49M',
             'A50_54B', 'A50_54F', 'A50_54M', 'A55_59B', 'A55_59F', 'A55_59M', 'A60_64B', 'A60_64F',
             'A60_64M', 'A65PLUSB', 'A65PLUSF', 'A65PLUSM','A65_69B', 'A65_69F', 'A65_69M', 'A70PLUSB',
             'A70PLUSF', 'A70PLUSM', 'A70_74B', 'A70_74F','A70_74M', 'A75PLUSB', 'A75PLUSF', 'A75PLUSM',
             'A75_79B', 'A75_79F', 'A75_79M', 'A80PLUSB','A80PLUSF', 'A80PLUSM', 'A80_84B', 'A80_84F',
             'A80_84M', 'A85PLUSB', 'A85PLUSF', 'A85PLUSM']

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc[:-10]

    with arcpy.da.UpdateCursor(fc,cenFields) as cursor:
        for row in cursor:
            for i in range(len(cenFields)):
                if row[i] is None:
                    row[i] = 0
            cursor.updateRow(row)

print 'done'
