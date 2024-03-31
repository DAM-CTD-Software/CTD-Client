set pdir=D:\mig\tests\data
set sdir="C:\Program Files (x86)\Sea-Bird\SBEDataProcessing-Win32"
set fnam=%1
set cfile=%fnam%.XMLCON
set ppsa=%pdir%\psas
echo.
echo  processing steps               file
echo  ----------------------------------------
echo  data conversion raw to cnv     %fnam%
%sdir%\datcnvW  /i%fnam%.hex  /c%cfile% /o%pdir%\out /f%fnam%.cnv /p%ppsa%\DatCnv1.psa /s
