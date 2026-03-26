@echo off
setlocal


call "bin\elasticsearch.bat"
call "bin\kibana.bat"
REM call "bin\logstash.bat"
call "bin\redis.bat"

echo ================================
echo All scripts executed successfully.
echo ================================

endlocal
REM This batch file is used to start all the necessary services for the application.
