#Jane Mills
#11/27/2017
#rename asciis

import os, csv

root = r'F:\gpw\gpw4_rev10_fixed_extents\gdal_tifs'
#root = r'F:\gpw\gpw4_rev10_fixed_extents\scratch\gdal_tifs_totpop'
print "processing"

fileList = os.listdir(root)
fileList.sort()

rename = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\fix_extents\rename_tif.csv'
#rename = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\fix_extents\rename_tif_totpop.csv'
csvMem = csv.reader(open(rename,'r'))
nameDict = {}

for row in csvMem:
    nameDict[row[0]] = row[1]

print "filled in name dictionary"

for f in fileList:
    extLoc = f.find(".")
    ext = f[extLoc:]
    name = f[:extLoc]
    if name in nameDict:
        print f
        newName = nameDict[name]
        new = os.path.join(root,newName+ext)
        os.rename(os.path.join(root,f),new)
    else:
        print "Did not find: " + name

