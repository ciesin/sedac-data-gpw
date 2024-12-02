#-------------------------------------------------------------------------------
# Name:        centroid_export.py
# Purpose:     export country .csv files from a global feature class of centroids.
#
# Author:      gyetman
#
# Created:     13/11/2015
# Copyright:   (c) gyetman 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os, codecs
from arcpy import env

# testing with codecs to see if Brazil writes records properly!
# shoot, Brazilian records with a ~A combination do not seem to
# be readalbe after export. Modified the six records to have just A.

centroids = r'E:\gpw_centroids\Experiments.gdb\gpw_v4_centroids'
outPath = r'E:\gpw_centroids\csvs'

# countries to process, each will be selected from the global centroids feature class.

isos = [u'ABW', u'AFG', u'AGO', u'AIA', u'ALA', u'ALB', u'AND', u'ARE', u'ARG',
        u'ARM', u'ASM', u'ATG', u'AUS', u'AUT', u'AZE', u'BDI', u'BEL', u'BEN',
        u'BES', u'BFA', u'BGD', u'BGR', u'BHR', u'BHS', u'BIH', u'BLM', u'BLR',
        u'BLZ', u'BMU', u'BOL', u'BRA', u'BRB', u'BRN', u'BTN', u'BWA', u'CAF',
        u'CAN', u'CHE', u'CHL', u'CHN', u'CIV', u'CMR', u'COD', u'COG', u'COK',
        u'COL', u'COM', u'CPV', u'CRI', u'CUB', u'CUW', u'CYM', u'CYP', u'CZE',
        u'DEU', u'DJI', u'DMA', u'DNK', u'DOM', u'DZA', u'ECU', u'EGY', u'ERI',
        u'ESH', u'ESP', u'EST', u'ETH', u'FIN', u'FJI', u'FLK', u'FRA', u'FRO',
        u'FSM', u'GAB', u'GBR', u'GEO', u'GGY', u'GHA', u'GIB', u'GIN', u'GLP',
        u'GMB', u'GNB', u'GNQ', u'GRC', u'GRD', u'GRL', u'GTM', u'GUF', u'GUM',
        u'GUY', u'HKG', u'HND', u'HRV', u'HTI', u'HUN', u'IDN', u'IMN', u'IND',
        u'IRL', u'IRN', u'IRQ', u'ISL', u'ISR', u'ITA', u'JAM', u'JEY', u'JOR',
        u'JPN', u'KAZ', u'KEN', u'KGZ', u'KHM', u'KIR', u'KNA', u'KOR', u'KOS',
        u'KWT', u'LAO', u'LBN', u'LBR', u'LBY', u'LCA', u'LIE', u'LKA', u'LSO',
        u'LTU', u'LUX', u'LVA', u'MAC', u'MAF', u'MAR', u'MCO', u'MDA', u'MDG',
        u'MDV', u'MEX', u'MHL', u'MKD', u'MLI', u'MLT', u'MMR', u'MNE', u'MNG',
        u'MNP', u'MOZ', u'MRT', u'MSR', u'MTQ', u'MUS', u'MWI', u'MYS', u'MYT',
        u'NAM', u'NCL', u'NER', u'NFK', u'NGA', u'NIC', u'NIU', u'NLD', u'NOR',
        u'NPL', u'NRU', u'NZL', u'OMN', u'PAK', u'PAN', u'PCN', u'PER', u'PHL',
        u'PLW', u'PNG', u'POL', u'PRI', u'PRK', u'PRT', u'PRY', u'PSE', u'PYF',
        u'QAT', u'REU', u'ROU', u'RUS', u'RWA', u'SAU', u'SDN', u'SEN', u'SGP',
        u'SHN', u'SJM', u'SLB', u'SLE', u'SLV', u'SMR', u'SOM', u'SPM', u'SRB',
        u'SSD', u'STP', u'SUR', u'SVK', u'SVN', u'SWE', u'SWZ', u'SXM', u'SYC',
        u'SYR', u'TCA', u'TCD', u'TGO', u'THA', u'TJK', u'TKL', u'TKM', u'TLS',
        u'TON', u'TTO', u'TUN', u'TUR', u'TUV', u'TWN', u'TZA', u'UGA', u'UKR',
        u'URY', u'UZB', u'VAT', u'VCT', u'VEN', u'VGB', u'VIR', u'VNM', u'VUT',
        u'WLF', u'WSM', u'YEM', u'ZAF', u'ZMB', u'ZWE', u'USA']

# test cases
##isos = ['GTM','MDV']
# Brazil fix
# isos = ['BRA']

where = "ISOALPHA = '" + isos[0] + "'"
clyr = arcpy.MakeTableView_management(centroids, 'lyr', where)
# get the fields for making the layer
fieldInfos = arcpy.ListFields(clyr)
fields = []
fieldDict = {}
# get field names as a list, removing the shape field.
# get the types in a dictionary. 
for field in fieldInfos:
    if field.name <> 'Shape':
        fields.append(field.name)
        fieldDict[field.name] = field.type
rows = arcpy.da.SearchCursor(clyr,fields)

# now getting fields from ListFields, see above
##cols = rows.fields
##fields = []
##for col in cols: fields.append(col)
### drop the shape field from the list
##fields.remove('Shape')

del clyr

print '...........................'
for iso in isos:
    print 'processing', iso
    where = "ISOALPHA = '" + iso + "'"
    print where
    cTableView = arcpy.MakeTableView_management(centroids, iso + 'cTableView', where)
    outFile = iso + '.csv'
    with codecs.open(os.path.join(outPath,outFile), 'w', 'utf-8') as f:
        rows = arcpy.da.SearchCursor(cTableView,fields)
        for row in rows:
            line = ''
            for i in range(0,len(row)):
                if fieldDict[fields[i]] == 'String':
                    #output no data values (None) as an empty string
                    if row[i] == None:
                        line += '"",'
                    else:
                        line += '"' + unicode(row[i]) + '",'
                else:
                    # handle no data values so they are written as empty rather than 'None'
                    if row[i] == None:
                        line += ','
                    else:
                        line += unicode(row[i]) + ','
##            #This method didn't encapsulate strings in double-quotes, leading to problems with commas in fields
##            #replaced with the lines above
##            line = unicode(row[0])
##            for i in range(1,len(row)):
##                line += ',' + unicode(row[i])
                        
            # remove the trailing comma the lazy way
            line = line[:-1]
            #f.write(line.encode('utf-16') + '\n') # no need to encode with codecs.open of the file object.
            f.write(line + '\n')
    del cTableView
    
print '...done.'
