Attribute VB_Name = "New_naming_convention"
Option Explicit
Function Rename()
    Dim lastColumn As Long
    Dim current As Worksheet
    Dim i As Integer
    
    
    For Each current In Worksheets
        lastColumn = Sheets(current.Name).Cells(1, Columns.Count).End(xlToLeft).Column
        For i = 1 To lastColumn Step 1
        If InStr(Sheets(current.Name).Cells(1, i).Value, "UCID") > 0 Then
            Sheets(current.Name).Cells(1, i).Value = "UCADMIN" & Right(Sheets(current.Name).Cells(1, i).Value, 1)
        End If
    Next i
    Next
        
End Function

