Attribute VB_Name = "Module7"
Sub KOR_ingest()
Attribute KOR_ingest.VB_ProcData.VB_Invoke_Func = "K\n14"
'
' KOR_ingest Macro
'
' Keyboard Shortcut: Ctrl+Shift+K
'
Dim i As Integer
i = 0

Do While i < 136
    Sheets("Data").Select
    Range(Cells(i * 20 + 2, 3), Cells((i + 1) * 20 + 1, 3)).Select
'    Range("C2:C25").Select
    Selection.Copy
    Sheets("Sheet1").Select
    Cells(i + 3, 2).Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=True
    Sheets("Data").Select
    Range(Cells(i * 20 + 2, 4), Cells((i + 1) * 20 + 1, 4)).Select
'    Range("D2:D25").Select
    Selection.Copy
    Sheets("Sheet1").Select
    Cells(i + 3, 22).Select
'    Range("Z3").Select
    Selection.PasteSpecial Paste:=xlPasteAll, Operation:=xlNone, SkipBlanks:= _
        False, Transpose:=True
    Sheets("Data").Select
    i = i + 1

Loop

End Sub
