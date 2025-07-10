set input=%1
set file=%~dpn1
set fileName=%~n1
set xmlConfig=%file%.XMLCON
set cruise=%fileName:~0,6%

rem paths and/variables
set path_root=D:\CTD_Data
set path_work=D:\CTD_Processing
set path_data=%path_work%\%cruise%
set path_IOW=%path_work%\iow
set path_psaFiles=%path_work%\psaFiles
set path_tmp=%path_work%\tmp
set path_software="C:\Program Files (x86)\Sea-Bird\SBEDataProcessing-Win32"

rem display paths and variables
echo file           =   %file%
echo fileName       =   %fileName%
echo cruise         =   %cruise%
echo used config    =   %xmlConfig% 
echo path_root      =   %path_root%
echo path_data      =   %path_data%
echo path_tmp       =   %path_tmp%
echo path_IOW       =   %path_IOW%
echo path_software  =   %path_software%
echo path_psaFiles  =   %path_psaFiles%
echo.

echo temporary copies of raw files for processing
copy %file%.* %path_tmp%\*.*
copy %file%.bl %path_tmp%\output.bl
echo.

echo  processing steps               file
echo  ----------------------------------------
echo  data conversion raw to cnv     %file%
%path_software%\datcnvW  /i%file%.hex  /c%xmlConfig% /o%path_tmp%\ /foutput.cnv /p%path_psaFiles%\DatCnv.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  air pressure correction        %file%
%path_IOW%\apc.exe /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput.cnv /p%path_psaFiles%\apc.par /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  find outliers std              %file%
%path_software%\wildeditW /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput.cnv /p%path_psaFiles%\WildEdit.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  find outliers median           %file%
%path_software%\w_filterW /i%path_tmp%\input.cnv /c%xmlConfig% /o%path_tmp%\ /foutput.cnv /p%path_psaFiles%\W_Filter.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  align sensors                  %file%
%path_software%\alignctdW /i%path_tmp%\input.cnv /c%xmlConfig% /o%path_tmp%\ /foutput.cnv /p%path_psaFiles%\AlignCTD.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  cell thermal mass correction   %file%
%path_software%\celltmW /i%path_tmp%\input.cnv /c%xmlConfig% /o%path_tmp%\ /foutput.cnv  /p%path_psaFiles%\CellTM.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  derive additional parameters   %file%
%path_software%\deriveW /i%path_tmp%\input.cnv /c%xmlConfig% /o%path_tmp%\ /foutput.cnv  /p%path_psaFiles%\Derive.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  create bottlefile if exists    %file%
if exist %path_tmp%\output.ros %path_software%\bottlesumW /i%path_tmp%\output.ros /c%xmlConfig% /o%path_tmp%\ /foutput.btl /p%path_psaFiles%\BottleSum.psa /s /m
rem create BottleID
echo  inject bottle id if bottle exist
if exist %path_tmp%\output.btl %path_IOW%\btl_id_win.exe -i%path_tmp%\output.btl -o%path_tmp%\output.btl  /s /m
rem pause  
echo  bin averaging 1 second         %file%
rem 1s binsize
%path_software%\binavgW /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput_3.cnv /p%path_psaFiles%\BinAvg_3.psa /s /m
rem %path_IOW%\cnv2dat.exe /i%path_tmp%\output_3.cnv /o%path_tmp%\ /foutput_3.csv /s /m
rem pause 
echo  loop edit                      %file%
%path_software%\loopeditW /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput.cnv  /p%path_psaFiles%\LoopEdit.psa /s /m
copy %path_tmp%\output.cnv %path_tmp%\input.cnv >NUL
rem pause
echo  bin averaging 1m               %file%
rem 1m binsize
%path_software%\binavgW /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput_1.cnv /p%path_psaFiles%\BinAvg_1.psa /s /m
rem %path_IOW%\cnv2dat.exe /i%path_tmp%\output_1.cnv /o%path_tmp%\ /foutput_1.csv /s /m
rem pause
echo  bin averaging 0.25m            %file%
rem 0.25m binsize
%path_software%\binavgW /i%path_tmp%\input.cnv /o%path_tmp%\ /foutput_2.cnv /p%path_psaFiles%\BinAvg_2.psa /s /m 
rem %path_IOW%\cnv2dat.exe /i%path_tmp%\output_2.cnv /o%path_tmp%\ /foutput_2.csv /s /m
rem pause
rem plot data
REM echo  seaplot                        %file%
REM %path_IOW%\Seaplot_conf.exe /ic:\Geraete\Seabird\SeasaveV7\Seasave.psa /o%path_psaFiles%\SeaPlot.psa /s /m
REM %path_software%\SeaPlotW /i%path_tmp%\output_1.cnv /p%path_psaFiles%\SeaPlot.psa /s /m
rem pause
echo.
echo  copy data to local data directory
echo  ---------------------------------
IF not exist %path_data% (mkdir %path_data%)
copy %path_tmp%\output_1.cnv %path_data%\%fileName%_1.cnv  
copy %path_tmp%\output_2.cnv %path_data%\%fileName%_2.cnv    
copy %path_tmp%\output_3.cnv %path_data%\%fileName%_3.cnv
if exist %path_tmp%\output.ros  copy %path_tmp%\output.ros  %path_data%\%fileName%.ros
if exist %path_tmp%\output.btl  copy %path_tmp%\output.btl  %path_data%\%fileName%.btl
rem copy %path_tmp%\output_1.csv %path_data%\%fileName%_1.csv  
rem copy %path_tmp%\output_2.csv %path_data%\%fileName%_2.csv   
rem copy %path_tmp%\output_3.csv %path_data%\%fileName%_3.csv
echo.
rem pause

rem delete old files in temp folder
echo  housekeeping
echo  ------------
echo  delete all tempory files
del %path_tmp%\*.* /q
echo.

echo  ^>^> processing finished. Goodbye.
echo.
rem pause
