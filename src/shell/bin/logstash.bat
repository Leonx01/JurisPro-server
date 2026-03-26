@echo off
setlocal

echo ================================
echo Starting Logstash for laws...
echo ================================
start "Logstash_Laws" logstash -f D:\graduate_framework\JurisProFastAPI\src\shell\config\laws_trans.conf --path.data "logstash-data-laws"
echo Logstash (laws) started.

echo ================================
echo Starting Logstash for sections...
echo ================================
start "Logstash_Sections" logstash -f D:\graduate_framework\JurisProFastAPI\src\shell\config\sections_trans.conf --path.data "logstash-data-sections"
echo Logstash (sections) started.

endlocal
