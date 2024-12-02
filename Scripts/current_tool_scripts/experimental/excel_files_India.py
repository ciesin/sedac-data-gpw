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

rootDir = r"\\Dataserver0\gpw\GPW4\Preprocessing\Country\IND\Ingest\Census\PCA-2011"
# list contents of rootDir
rootContents = os.listdir(rootDir)
# Create workbook
wb = xlwt.Workbook()
ws = wb.add_sheet("India_Ingest",cell_overwrite_ok=True)
# iterate the directories
n = 0
i = 0
rowCount = 0
for stateDir in rootContents:
    stateContents = os.listdir(rootDir + os.sep + stateDir)
    for disXLS in stateContents:
        if rowCount > 60000:
            i = i + 1
            n = 0
            ws = wb.add_sheet("India_Ingest" + str(i),cell_overwrite_ok=True)  
        print "File = " + disXLS        
        # open file of interest
        rb = open_workbook(rootDir + os.sep + stateDir + os.sep + disXLS)#, formatting_info=True)
        # open sheet of interest 
        sName = rb.sheet_names()[0]
        rs = rb.sheet_by_name(sName)
        #  Get number of rows and columns that contain data
        numRow = rs.nrows 
        numCol = rs.ncols
        # Create condition in order to only add field names 1 time
        if n == 0:
            n = n + 1
            for row in range(numRow): 
                #  Get all the values in the row
                rowList = rs.row_values(row) 
                for col in range(numCol): 
                    #  Get all the values in each list 
                    oneValue = rowList[col] 
                    #  Copy the values to target worksheet 
                    ws.write(row, col, oneValue)
            rowCount = numRow
            print "Row Count = " + str(rowCount)
        else:
            for row in range(1,numRow): 
                #  Get all the values in the row 
                rowList = rs.row_values(row) 
                for col in range(numCol): 
                    #  Get all the values in each list 
                    oneValue = rowList[col] 
                    #  Copy the values to target worksheet 
                    ws.write(rowCount, col, oneValue)
                rowCount = rowCount + 1                    
                
            print "Row Count now = " + str(rowCount)
            
                

# save to output xls
wb.save(rootDir + os.sep + "ind_ingest.xls")    
            
            
        





    
