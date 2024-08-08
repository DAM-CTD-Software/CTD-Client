rem wait a moment for all threads to finish and the exe to finish gracefully
TIMEOUT /T 1

rem kill the exe by force if its still running
TASKKILL /IM "ctdclient.exe"

rem delete the old renamed exe
DEL %1

rem Script deletes itself after execution, leaving not traces.
(goto) 2>nul & del "%~f0"