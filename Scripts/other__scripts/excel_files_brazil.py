
##############
#SCRIPT FAILED BECAUSE MORE THAN 65536 ROWS, BUT XLWT HAS LIMITATION
##############

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

rootDir = r"\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA\Ingest\Census\Finished excel files by state"
# list contents of rootDir
rootContents = os.listdir(rootDir)
# define list of sheet suffixes
suffixes = ["women_total"]#,"women_rural","women_urban","men_total","men_rural","men_urban"]
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
    #Create workbook
    wb = xlwt.Workbook()
    # add new sheet to the wb
    ws = wb.add_sheet("data",cell_overwrite_ok=True)
    # write the schema rows
    ws.write(0,0,"UCID0")
    ws.write(0,1,"UCID1")
    ws.write(0,2,"UCID2")
    ws.write(0,3,"UCID3")
    ws.write(0,4,"UCID4")
    ws.write(0,5,"UCID5")
    ws.write(0,6,"USCID")
    ws.write(0,7,"USCIDa")
    ws.write(0,8,"UCID1a")
    ws.write(0,9,"NAME1")
    ws.write(0,10,"UCID2a")
    ws.write(0,11,"NAME2")
    ws.write(0,12,"UCID3a")
    ws.write(0,13,"NAME3")
    ws.write(0,14,"UCID4a")
    ws.write(0,15,"NAME4")
    ws.write(0,16,"DELETE")
    ws.write(0,17,"U_R_status")
    ws.write(0,18,"TOTPOP_" + suffix + "_2010")
    ws.write(0,19,"A000" + suffix + "_2010")
    ws.write(0,20,"A001" + suffix + "_2010")
    ws.write(0,21,"A002" + suffix + "_2010")
    ws.write(0,22,"A003" + suffix + "_2010")
    ws.write(0,23,"A004" + suffix + "_2010")
    ws.write(0,24,"A005" + suffix + "_2010")
    ws.write(0,25,"A006" + suffix + "_2010")
    ws.write(0,26,"A007" + suffix + "_2010")
    ws.write(0,27,"A008" + suffix + "_2010")
    ws.write(0,28,"A009" + suffix + "_2010")
    ws.write(0,29,"A010" + suffix + "_2010")
    ws.write(0,30,"A011" + suffix + "_2010")
    ws.write(0,31,"A012" + suffix + "_2010")
    ws.write(0,32,"A013" + suffix + "_2010")
    ws.write(0,33,"A014" + suffix + "_2010")
    ws.write(0,34,"A015" + suffix + "_2010")
    ws.write(0,35,"A016" + suffix + "_2010")
    ws.write(0,36,"A017" + suffix + "_2010")
    ws.write(0,37,"A018" + suffix + "_2010")
    ws.write(0,38,"A019" + suffix + "_2010")
    ws.write(0,39,"A020" + suffix + "_2010")
    ws.write(0,40,"A021" + suffix + "_2010")
    ws.write(0,41,"A022" + suffix + "_2010")
    ws.write(0,42,"A023" + suffix + "_2010")
    ws.write(0,43,"A024" + suffix + "_2010")
    ws.write(0,44,"A025_029" + suffix + "_2010")
    ws.write(0,45,"A030_034" + suffix + "_2010")
    ws.write(0,46,"A035_039" + suffix + "_2010")
    ws.write(0,47,"A040_044" + suffix + "_2010")
    ws.write(0,48,"A045_049" + suffix + "_2010")
    ws.write(0,49,"A050_054" + suffix + "_2010")
    ws.write(0,50,"A055_059" + suffix + "_2010")
    ws.write(0,51,"A060_064" + suffix + "_2010")
    ws.write(0,52,"A065_069" + suffix + "_2010")
    ws.write(0,53,"A070_074" + suffix + "_2010")
    ws.write(0,54,"A075_079" + suffix + "_2010")
    ws.write(0,55,"A080_084" + suffix + "_2010")
    ws.write(0,56,"A085_089" + suffix + "_2010")
    ws.write(0,57,"A090_094" + suffix + "_2010")
    ws.write(0,58,"A095_099" + suffix + "_2010")
    ws.write(0,59,"A100plus" + suffix + "_2010")

    rowAggregate = 0
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
        rowAggregate = rowAggregate + totalRows
        # iterate
        while nRows:
            while nCols:
                if rowAggregate == totalRows:
                    ws.write(rowIndex,columnIndex,worksheet.cell_value(rowIndex,columnIndex))
                else:
                    ws.write(rowIndex + rowAggregate - 1,columnIndex,worksheet.cell_value(rowIndex,columnIndex))
                columnIndex = columnIndex + 1
                nCols = nCols - 1
            rowIndex = rowIndex + 1
            nCols = worksheet.ncols
            columnIndex = 0
            nRows = nRows - 1
    

    # save to output xls
    wb.save(r"\\Dataserver0\gpw\GPW4\Preprocessing\Country\BRA" + os.sep + "Test" + suffix + ".xls")  






### Create workbook
##wb = xlwt.Workbook()
### iterate the directories
##n = 0
##for provDir in rootContents:
##    n = n + 1
##    disDir = rootDir + os.sep + provDir + os.sep + "distritos"
##    disContents = os.listdir(disDir)
##    for disSub in disContents:
##        district = disDir + os.sep + disSub
##        districtContents = os.listdir(district)
##        for posDir in districtContents:
##            if posDir[-4:] == ".xls":
##                pass
##            else:
##                posContents = os.listdir(district + os.sep + posDir)
##                for posFile in posContents:
##                    print posFile
##                    # open file of interest
##                    rb = open_workbook(district + os.sep + posDir + os.sep + posFile, formatting_info=True)
##                    # open sheet of interest 
##                    sName = rb.sheet_names()[0]
##                    rs = rb.sheet_by_name(sName)
##                    #  Get number of rows and columns that contain data 
##                    numRow = rs.nrows 
##                    numCol = rs.ncols  
##                    # add new sheet to the wb
##                    ws = wb.add_sheet(sName,cell_overwrite_ok=True)
##                    for row in xrange(numRow): 
##                        #  Get all the rows in the sheet (each rows is a list) 
##                        rowList = rs.row_values(row) 
##                        for col in xrange(numCol): 
##                            #  Get all the values in each list 
##                            oneValue = rowList[col] 
##                            #  Copy the values to target worksheet 
##                            ws.write(row, col, oneValue)
##                            ws.write(11,0,"5 - 9")
##                            ws.write(17,0,"10 - 14")
##                            ws.write(0,0,sName)
##
### save to output xls
##wb.save(rootDir + os.sep + "moz_raw.xls")    
            
            
        





    
