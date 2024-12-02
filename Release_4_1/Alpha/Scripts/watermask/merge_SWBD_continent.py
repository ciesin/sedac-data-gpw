import arcpy, os
from arcpy import env

eFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\InputData\GlobalBoundaries\WATER MASK\SWBD_2_1\unzipped\east'
wFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\InputData\GlobalBoundaries\WATER MASK\SWBD_2_1\unzipped\west'
outgdb = r'F:\GPW\watermask\SWBD_by_continent.gdb'
outfca = os.path.join(outgdb,'SWBD_Australia')
outfce = os.path.join(outgdb,'SWBD_Eurasia')
outfcf = os.path.join(outgdb,'SWBD_Africa')
outfci = os.path.join(outgdb,'SWBD_Islands')
outfcn = os.path.join(outgdb,'SWBD_NAmerica')
outfcs = os.path.join(outgdb,'SWBD_SAmerica')

env.workspace = eFolder

fcList = arcpy.ListFeatureClasses()

for fc in fcList:
    print fc
    if fc[-5] == "a":
        arcpy.Append_management(fc,outfca,"NO_TEST")
    elif fc[-5] == "e":
        arcpy.Append_management(fc,outfce,"NO_TEST")
    elif fc[-5] == "f":
        arcpy.Append_management(fc,outfcf,"NO_TEST")
    elif fc[-5] == "i":
        arcpy.Append_management(fc,outfci,"NO_TEST")
    elif fc[-5] == "n":
        arcpy.Append_management(fc,outfcn,"NO_TEST")
    elif fc[-5] == "s":
        arcpy.Append_management(fc,outfcs,"NO_TEST")
    else:
        print " not in a continent?"

