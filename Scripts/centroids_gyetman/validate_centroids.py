#-------------------------------------------------------------------------------
# Name:        validate_centroids.py
# Purpose:     validate the output of centroid_export.py and centroids_concatenate.py
#              to make sure that the row count and row length match the inputs (compare
#              the printed number of rows to the input feature class).
#              Also validate the conversion of unicode strings to integer or float values
#              where appropriate. 
#
# Author:      gyetman
#
# Created:     13/11/2015
# Copyright:   (c) gyetman 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import codecs, csv
# field types in order that they were export, as Python field types, not Esri types. 
types = ['int','unicode','int','unicode','unicode','unicode','unicode','unicode','unicode','unicode',
         'unicode','float','float','float','float','float','float','float','int','int','int','int',
         'int','float','float','float','float','float','int','unicode','unicode']
def main():
    with codecs.open(r'E:\gpw_centroids\centroids_gpwv4.csv', 'rU') as f:
    #with open(r'D:\GPWv4\centroids\centroids_gpwv4.csv', 'rb') as f:
        csvReader = csv.reader(f)
        # line count
        i = 0
        print 'Processing CSV file.'
        for line in csvReader:
            uRow = [x.decode('utf-8') for x in line]
            if len(uRow) <> 31:
                print 'odd line length of {} at line {}'.format(len(uRow),i)
                print line
            i+= 1
            # if type should be float or int, check that it converts OK
            # I'm sure there's a more efficient way to do this validation...
            for j in range(0,len(uRow)):
                if types[j] == 'int' and uRow[j] <> '':
                    try:
                        int(uRow[j])
                    except(ValueError):
                        print 'Error converting row {}, column {}, to integer'.format(i,j)
                elif types[j] == 'float' and uRow[j] <> '':
                    try:
                        float(uRow[j])
                    except(ValueError):
                        print 'Error converting row {}, column {}, to float'.format(i,j)
        print 'File contains:', i, 'lines.'

if __name__ == '__main__':
    main()
