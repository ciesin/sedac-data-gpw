#-------------------------------------------------------------------------------
# Name:        centroids_concatenate.py
# Purpose:     combine the output of validate_centroids.py (country files) into
#              a global .csv file.
#
# Author:      gyetman
#
# Created:     13/11/2015
# Copyright:   (c) gyetman 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
# headerFile created using generate_header.py, which must exist! 
headerFile = r'D:/gpw/4_0_prod/centroids/global/header.csv'
# list of files to process, folder should only contain country .csv files.
os.chdir(r'D:/gpw/4_0_prod/centroids/csv')
files = os.listdir(os.curdir)
print 'processing', len(files)
with open(r'D:/gpw/4_0_prod/centroids/global/global2.csv','w') as outFile:
    # first, write the header line
    with open(headerFile, 'r') as inFile:
        for line in inFile:
            outFile.write(line)
    # open each file. Note that using for line in InFile will not
    # read the whole file into memory; using readlines() would try
    # and do so, resulting in a memory error
    for f in files:
        if f == 'Thumbs.db':
            continue
        print 'processing', f
        with open(os.path.join(os.curdir,f), 'r') as inFile:
            for line in inFile:
                outFile.write(line)

print '..done.'
