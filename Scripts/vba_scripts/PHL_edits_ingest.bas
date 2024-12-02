Attribute VB_Name = "Module5"
Sub PHL_ingest()
Attribute PHL_ingest.VB_ProcData.VB_Invoke_Func = "r\n14"
'
' PHL_ingest Macro
'
'the first value of i is equal to the row number of the first cell you are copying
Dim i As Integer
i = 7

'the first value of j is equal to the row number of the first row you are pasting into
Dim j As Integer
j = 2

' Set the max value of j equal to the number of rows you will be producing plus one

Do While j < 5 '(max j+1)
    Sheets(1).Select
    Cells(i - 1, 1).Select
    Selection.Copy
    Sheets(2).Select
    Cells(j, 1).Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=False
    
    Sheets(1).Select
    Range(Cells(i, 2), Cells(i + 17, 2)).Select
    Selection.Copy
    Sheets(2).Select
    Cells(j, 2).Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=True
    
    Sheets(1).Select
    Range(Cells(i, 3), Cells(i + 17, 3)).Select
    Application.CutCopyMode = False
    Selection.Copy
    Sheets(2).Select
    Cells(j, 20).Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=True
    
    Sheets(1).Select
    Range(Cells(i, 4), Cells(i + 17, 4)).Select
    Application.CutCopyMode = False
    Selection.Copy
    Sheets(2).Select
    Cells(j, 38).Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=True

    i = i + 19
    j = j + 1
    
Loop

End Sub
