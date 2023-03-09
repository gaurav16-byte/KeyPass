@echo off

set PYTHON_URL=https://www.python.org/ftp/python/latest/python-%PROCESSOR_ARCHITECTURE%-%PROCESSOR_ARCHITECTURE:_=.%_%PYTHON_VERSION%.exe
set PYTHON_INSTALLER=python-%PROCESSOR_ARCHITECTURE%-%PROCESSOR_ARCHITECTURE:_=.%_%PYTHON_VERSION%.exe

echo Checking for latest version of Python...
curl --silent https://www.python.org/downloads/ | findstr /i /c:"Latest Python 3 Release" > latest.txt
for /f "tokens=3" %%i in (latest.txt) do set LATEST_VERSION=%%i
del latest.txt
echo Latest version of Python is %LATEST_VERSION%

if exist %PYTHON_INSTALLER% (
  echo Python %PYTHON_VERSION% is already installed, skipping installation...
) else (
  echo Downloading Python %LATEST_VERSION% installer from %PYTHON_URL%...
  curl -o %PYTHON_INSTALLER% %PYTHON_URL%
  
  echo Installing Python %LATEST_VERSION%...
  start /wait %PYTHON_INSTALLER% /quiet AddToPath=1
  
  echo Cleaning up...
  del %PYTHON_INSTALLER%
  
  echo Python %LATEST_VERSION% installation complete!
)

echo Installing packages with pip...
pip install wmi cryptography flask prettytable

echo All packages installed!
pause
