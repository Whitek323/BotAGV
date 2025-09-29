@echo off
rem Set the code page to UTF-8 to handle Thai characters correctly
chcp 65001 > nul

rem Define the output file name
set "OUT_FILE=result.csv"

echo Starting to send 10 POST requests and saving results to %OUT_FILE%...
echo.

rem Check if the output file exists and delete it to start fresh
if exist %OUT_FILE% (
    del %OUT_FILE%
    echo Old %OUT_FILE% deleted.
)

rem Loop from 1 to 10
for /l %%i in (1, 1, 10) do (
    echo ===================================
    echo Sending request #%%i
    
    rem Execute curl and append the output to the specified file.
    rem The -s flag makes curl run in silent mode to avoid progress meters.
    curl -s -X POST http://127.0.0.1:7001/ai -H "Content-Type: application/json" -d "{\"sentence\": \"ลงทะเบียนล่าช้าทำอะไรได้บ้าง\"}" >> %OUT_FILE%
    
    rem Add a new line to the CSV file for better separation of JSON results
    echo. >> %OUT_FILE%
    
    echo Request #%%i sent and result saved to %OUT_FILE%.
    echo ===================================
    echo.
)

echo All 10 requests have been sent. Results are in %OUT_FILE%.
pause