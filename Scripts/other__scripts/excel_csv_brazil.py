import os, csv, codecs, cStringIO
from copy import deepcopy
from xlrd import open_workbook
from xlutils.copy import copy as copy
import xlwt
from xlwt import Workbook

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:24:42 2013

@author: kmacmanu
"""


rootDir = r"\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census\Finished excel files by state"
# list contents of rootDir
rootContents = os.listdir(rootDir)
# define list of sheet suffixes
suffixes = ["women_rural","women_urban","men_total","men_rural","men_urban"]#["women_total"]
for sheetSuffix in suffixes:
    if sheetSuffix == "women_total":
        suffix = "FT"
    elif sheetSuffix == "women_rural":
        suffix = "FR"
    elif sheetSuffix == "women_urban":
        suffix = "FU"
    elif sheetSuffix == "men_total":
        suffix = "MT"
    elif sheetSuffix == "men_rural":
        suffix = "MR"
    elif sheetSuffix == "men_urban":
        suffix = "MU"
        
    outTable = r"\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census" + os.sep + "bra_" + sheetSuffix + ".csv"
    print "Created " + outTable
    csvFile = open(outTable,'wb')
    csvFile = UnicodeWriter(csvFile)
    csvFile.writerow(("UCID0","UCID1","UCID2","UCID3","UCID4","UCID5","USCID",
                      "USCIDa","UCID1a","NAME1","UCID2a","NAME2","UCID3a","NAME3",
                      "UCID4a","NAME4","DELETE","U_R_status","TOTPOP_" + suffix + "_2010",
                      "A000" + suffix + "_2010","A001" + suffix + "_2010","A002" + suffix + "_2010",
                      "A003" + suffix + "_2010","A004" + suffix + "_2010","A005" + suffix + "_2010",
                      "A006" + suffix + "_2010","A007" + suffix + "_2010","A008" + suffix + "_2010",
                      "A009" + suffix + "_2010","A010" + suffix + "_2010","A011" + suffix + "_2010",
                      "A012" + suffix + "_2010","A013" + suffix + "_2010","A014" + suffix + "_2010",
                      "A015" + suffix + "_2010","A016" + suffix + "_2010","A017" + suffix + "_2010",
                      "A018" + suffix + "_2010","A019" + suffix + "_2010","A020" + suffix + "_2010",
                      "A021" + suffix + "_2010","A022" + suffix + "_2010","A023" + suffix + "_2010",
                      "A024" + suffix + "_2010","A025_029" + suffix + "_2010","A030_034" + suffix + "_2010",
                      "A035_039" + suffix + "_2010","A040_044" + suffix + "_2010","A045_049" + suffix + "_2010",
                      "A050_054" + suffix + "_2010","A055_059" + suffix + "_2010","A060_064" + suffix + "_2010",
                      "A065_069" + suffix + "_2010","A070_074" + suffix + "_2010","A075_079" + suffix + "_2010",
                      "A080_084" + suffix + "_2010","A085_089" + suffix + "_2010","A090_094" + suffix + "_2010",
                      "A095_099" + suffix + "_2010","A100plus" + suffix + "_2010"))  
    
    
    for xls in rootContents:
        print xls
        rowIndex = 1
        columnIndex = 0
        xlsRoot = os.path.basename(xls)[:-10]
        # open file of interest
        rb = open_workbook(rootDir + os.sep + xls, formatting_info=True)
        # define worksheet
        worksheet = rb.sheet_by_name(xlsRoot + sheetSuffix)
        
        # count rows and columns
        nRows = worksheet.nrows - 1
        totalRows = worksheet.nrows
        nCols = worksheet.ncols
       
        # iterate
        while nRows:
            row = []
            while nCols:
                value = worksheet.cell_value(rowIndex,columnIndex)
                if isinstance(value,float) == True or isinstance(value,int)==True:
                    value = str(value)
##                elif isinstance(value,str):
##                    value = value.encode('utf-8')
                else:
                    value = value
                row.append(value)                
                columnIndex = columnIndex + 1
                nCols = nCols - 1
            # Write row to CSV
            csvFile.writerow(row)
            # move to the next row
            rowIndex = rowIndex + 1
            # reset column index
            nCols = worksheet.ncols
            columnIndex = 0
            # count the number of rows left to iterate
            nRows = nRows - 1
    

           
            
        





    
