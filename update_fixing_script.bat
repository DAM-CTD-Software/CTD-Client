rem custom code here:
mkdir hola

rem Script deletes itself after execution, leaving not traces.
(goto) 2>nul & del "%~f0"