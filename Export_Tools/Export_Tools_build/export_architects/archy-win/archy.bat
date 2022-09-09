@echo off
REM ----------------------------------------------------------------------------
REM
REM This file is maintained by Archy.  Please do not manually modify.
REM
REM         Thanks for your patronage, the Archy Management :)
REM
REM ----------------------------------------------------------------------------

REM Executing an if statement that will never be true to work around an issue when running this batch file in Windows that caused a '*' is not recognized as an internal or external command, operable program or batch file error to be displayed in the console output.
if 1 == 2 echo .
"C:\Users\vyeong\python_workspace\export_architects\archy-win\archyBin\archy-win-2.10.0.exe" %*