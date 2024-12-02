# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:24:42 2013

@author: kmacmanu
"""
import os
from copy import deepcopy
from xlrd import open_workbook
from xlutils.copy import copy as copy
import xlwt
from xlwt import Workbook

rootDir = r"\\Dataserver0\gpw\GPW4\InputData\Country\MOZ\census\census2007\Quadro 2. Populacao por area de residencia e sexo, segundo idade"
# list contents of rootDir
rootContents = os.listdir(rootDir)
# Create workbook
wb = xlwt.Workbook()
# iterate the directories
n = 0
for provDir in rootContents:
    n = n + 1
    disDir = rootDir + os.sep + provDir + os.sep + "distritos"
    disContents = os.listdir(disDir)
    for disSub in disContents:
        district = disDir + os.sep + disSub
        districtContents = os.listdir(district)
        for posDir in districtContents:
            if posDir[-4:] == ".xls":
                pass
            else:
                posContents = os.listdir(district + os.sep + posDir)
                for posFile in posContents:
                    print posFile
                    # open file of interest
                    rb = open_workbook(district + os.sep + posDir + os.sep + posFile, formatting_info=True)
                    # open sheet of interest 
                    sName = rb.sheet_names()[0]
                    rs = rb.sheet_by_name(sName)
                    #  Get number of rows and columns that contain data 
                    numRow = rs.nrows 
                    numCol = rs.ncols  
                    # add new sheet to the wb
                    ws = wb.add_sheet(sName,cell_overwrite_ok=True)
                    for row in xrange(numRow): 
                        #  Get all the rows in the sheet (each rows is a list) 
                        rowList = rs.row_values(row) 
                        for col in xrange(numCol): 
                            #  Get all the values in each list 
                            oneValue = rowList[col] 
                            #  Copy the values to target worksheet 
                            ws.write(row, col, oneValue)
                            ws.write(11,0,"5 - 9")
                            ws.write(17,0,"10 - 14")
                            ws.write(0,0,sName)

# save to output xls
wb.save(rootDir + os.sep + "moz_raw.xls")    
            
            
        





    
