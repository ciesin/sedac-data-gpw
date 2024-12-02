import os, csv, arcpy


f = r'D:/gpw/4_0_prod/centroids/csv/abw_centroids.csv'
##masterDict = {}
##badRows = {}
with open(f,'rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        header = row
        break
##        if row['ISOALPHA']=="EGY":
##            badRows[row['OBJECTID']]=row
##        elif row['ISOALPHA']=="PAN":
##            badRows[row['OBJECTID']]=row
##        elif row['ISOALPHA']=="POL":
##            badRows[row['OBJECTID']]=row
##        else:
##            masterDict[row['OBJECTID']]=row
nf = r'D:/gpw/4_0_prod/centroids/global/header.csv'
inFC = r'D:/gpw/4_0_prod/centroids/global/merged.gdb/global'


with open(nf, 'wb') as csvfile2:
    writer = csv.writer(csvfile2)
    writer.writerow(header)
##    with arcpy.da.SearchCursor(inFC,"*") as sc:
##        for r in sc:
##            writer.writerow(r)
    
