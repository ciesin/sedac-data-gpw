# this scripts combines the estimates_summary tables and
# produces and ancillary table of UN Estimates

# import libraries
import arcpy,os,sys
arcpy.env.overwriteOutput = True
# define estimates table and create it if it doesn't exists
estimatesSummaryTable = r'D:\gpw\release_4_1\loading\loading_table.gdb\estimates_summary_2_21_2017'

#UPDATE THESE PATHS
# define input wpp table
wppTableIn = r'D:\gpw\ancillary.gdb\un_wpp2015'
# copy of this
wppTable = r'D:\gpw\ancillary.gdb\un_wpp2015_adjustment_factors_2_21_17'
# define groupLookup
groupLookupTable = r'D:\gpw\ancillary.gdb\un_wpp2015_group_lookup'

try:
    # first make a copy of the wppTableIn
    arcpy.CopyRows_management(wppTableIn, wppTable)
    # add the estimates fields
    estimatesFields = ["E_ATOTPOPBT_1975","E_ATOTPOPBT_1990","E_ATOTPOPBT_2000",
                       "E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015",
                       "E_ATOTPOPBT_2020"]
    for estimatesField in estimatesFields:
        adjustmentField = estimatesField.replace("E_ATOTPOPBT_","UNADJFAC_")
        arcpy.AddField_management(wppTable, estimatesField, "FLOAT")
        arcpy.AddField_management(wppTable, adjustmentField, "FLOAT")
    # create groupLookupRows
    with arcpy.da.SearchCursor(groupLookupTable,"GPW4_ISOGRP") as groupLookupRows:
        for groupLookupRow in groupLookupRows:
            # grab the groupISO
            groupISO = str(groupLookupRow[0])
            # make a selection on the wppTable to determine if there is more than 1
            # iso in the group
            wppGroupView = groupISO + "_group_check"
            arcpy.MakeTableView_management(wppTable,wppGroupView, """ "GPW4_ISOGRP" = '""" + groupISO + "'")
            print "Created " + wppGroupView
            # if this view has 1 row the formulate the estimates view and grab values
            
            if int(arcpy.GetCount_management(wppGroupView)[0])==1:
                # define estimatesView
                estimatesView = groupISO + "_estimates_view"
                # if the estimatesView has more than 1 row then process as a group
                arcpy.MakeTableView_management(estimatesSummaryTable,estimatesView, """ "FIRST_ISO" = '""" + groupISO + "'")
                print "Created " + estimatesView
                # if there is only one row just grab the values
                with arcpy.da.SearchCursor(estimatesView,["SUM_SUM_E_ATOTPOPBT_1975","SUM_SUM_E_ATOTPOPBT_1990","SUM_SUM_E_ATOTPOPBT_2000",
                       "SUM_SUM_E_ATOTPOPBT_2005","SUM_SUM_E_ATOTPOPBT_2010","SUM_SUM_E_ATOTPOPBT_2015","SUM_SUM_E_ATOTPOPBT_2020"]) as estimatesRows:
                    for estimatesRow in estimatesRows:
                        print estimatesRow
                        estimate1975 = estimatesRow[0]
                        estimate1990 = estimatesRow[1]
                        estimate2000 = estimatesRow[2]
                        estimate2005 = estimatesRow[3]
                        estimate2010 = estimatesRow[4]
                        estimate2015 = estimatesRow[5]
                        estimate2020 = estimatesRow[6]
            # if there is more than one row read and look through table    
            elif int(arcpy.GetCount_management(wppGroupView)[0])>1:
                with arcpy.da.SearchCursor(wppGroupView,"GPW4_ISO") as groupRows:
                    i=0
                    for groupRow in groupRows:
                        lookupISO = groupRow[0]
                        print "This was a grouped ISO " + groupISO + " that included " + lookupISO
                        # define estimatesView
                        estimatesView = lookupISO + "_estimates_view"
                        # make table view of estimates table and grab the relevant values
                        arcpy.MakeTableView_management(estimatesSummaryTable,estimatesView, """ "FIRST_ISO" = '""" + lookupISO + "'")
                        print "Created " + estimatesView
                        # if it is the first pass then just grab values
                        if i==0:
                            i=1
                            print "It is the first pass"
                            with arcpy.da.SearchCursor(estimatesView,["SUM_SUM_E_ATOTPOPBT_1975","SUM_SUM_E_ATOTPOPBT_1990","SUM_SUM_E_ATOTPOPBT_2000",
                                   "SUM_SUM_E_ATOTPOPBT_2005","SUM_SUM_E_ATOTPOPBT_2010","SUM_SUM_E_ATOTPOPBT_2015","SUM_SUM_E_ATOTPOPBT_2020"]) as estimatesRows:
                                for estimatesRow in estimatesRows:
                                    estimate1975 = estimatesRow[0]
                                    estimate1990 = estimatesRow[1]
                                    estimate2000 = estimatesRow[2]
                                    estimate2005 = estimatesRow[3]
                                    estimate2010 = estimatesRow[4]
                                    estimate2015 = estimatesRow[5]
                                    estimate2020 = estimatesRow[6]
                        # otherwise add to the existing stored values
                        else:
                            print "It is the second pass"
                            with arcpy.da.SearchCursor(estimatesView,["SUM_SUM_E_ATOTPOPBT_1975","SUM_SUM_E_ATOTPOPBT_1990","SUM_SUM_E_ATOTPOPBT_2000",
                                   "SUM_SUM_E_ATOTPOPBT_2005","SUM_SUM_E_ATOTPOPBT_2010","SUM_SUM_E_ATOTPOPBT_2015","SUM_SUM_E_ATOTPOPBT_2020"]) as estimatesRows:
                                for estimatesRow in estimatesRows:
                                    estimate1975 = estimate1975 + estimatesRow[0]
                                    estimate1990 = estimate1990 + estimatesRow[1]
                                    estimate2000 = estimate2000 + estimatesRow[2]
                                    estimate2005 = estimate2005 + estimatesRow[3]
                                    estimate2010 = estimate2010 + estimatesRow[4]
                                    estimate2015 = estimate2015 + estimatesRow[5]
                                    estimate2020 = estimate2020 + estimatesRow[6]


            # create the calculation view
            calcView = groupISO + "calc_view"
            arcpy.MakeTableView_management(wppTable,calcView,""" "GPW4_ISO" = '""" + groupISO + "'")
            print "Created " + calcView
            # update the values in the row
            with arcpy.da.UpdateCursor(calcView,["E_ATOTPOPBT_1975","E_ATOTPOPBT_1990","E_ATOTPOPBT_2000","E_ATOTPOPBT_2005",
                                                 "E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]) as calcRows:
                for calcRow in calcRows:
                    calcRow[0] = estimate1975
                    calcRow[1] = estimate1990 
                    calcRow[2] = estimate2000
                    calcRow[3] = estimate2005
                    calcRow[4] = estimate2010
                    calcRow[5] = estimate2015
                    calcRow[6] = estimate2020
                    calcRows.updateRow(calcRow)
    
    # perform final calculations
    print "Calculating Adjustment Factors"
    arcpy.CalculateField_management(wppTable, "UNADJFAC_1975", """(float(!UNPOP1975!)/float(!E_ATOTPOPBT_1975!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_1990", """(float(!UNPOP1990!)/float(!E_ATOTPOPBT_1990!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_2000", """(float(!UNPOP2000!)/float(!E_ATOTPOPBT_2000!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_2005", """(float(!UNPOP2005!)/float(!E_ATOTPOPBT_2005!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_2010", """(float(!UNPOP2010!)/float(!E_ATOTPOPBT_2010!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_2015", """(float(!UNPOP2015!)/float(!E_ATOTPOPBT_2015!))-1""", "PYTHON")
    arcpy.CalculateField_management(wppTable, "UNADJFAC_2020", """(float(!UNPOP2020!)/float(!E_ATOTPOPBT_2020!))-1""", "PYTHON")
    print "Script Complete"
                  
except:
    print 'failed'#arcpy.GetMessages()
        
