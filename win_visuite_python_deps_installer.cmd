@echo off
setlocal

:: !! VERSION OHNE OPENIMAGEIO MACHT DAS LEBEN AUF DEN HBC-RECHNERN EINFACHER !!
:: !! VERSION OHNE OPENIMAGEIO MACHT DAS LEBEN AUF DEN HBC-RECHNERN EINFACHER !!

:: ##################################################################
:: ##                                                              ##
:: ##               CONFIGURATION - PLEASE EDIT THIS!              ##
:: ##                                                              ##
:: ##################################################################

:: 1. Set your Blender version number.
set BLENDER_VERSION=4.4
set BLENDER_FULL_VERSION=4.4.3

:: 2. Set the full path to your Blender installation folder.
::    This is the folder that contains "blender.exe".
::    The default is usually in "C:\Program Files\Blender Foundation\".
::    !! IMPORTANT: YOU MUST CHANGE THIS PATH TO MATCH YOUR SYSTEM !!
set TARGET_ROOT_PATH=%USERPROFILE%\Documents
:: set DOWNLOAD_PATH=U:\...

:: ##################################################################
:: ##                                                              ##
:: ##                  SCRIPT EXECUTION - NO EDITS NEEDED          ##
:: ##                                                              ##
:: ##################################################################

:: --- Derive Paths and URLs from Configuration ---
set BLENDER_VERSION=%BLENDER_FULL_VERSION:~0,3%
set BLENDER_ZIP_NAME=blender-%BLENDER_FULL_VERSION%-windows-x64.zip
set BLENDER_FOLDER_NAME=blender-%BLENDER_FULL_VERSION%-windows-x64
set BLENDER_DOWNLOAD_URL=https://download.blender.org/release/Blender%BLENDER_VERSION%/%BLENDER_ZIP_NAME%

:: Final path for the unzipped Blender installation
set BLENDER_INSTALL_PATH=%TARGET_ROOT_PATH%\%BLENDER_FOLDER_NAME%

:: Path for the downloaded .zip file
set DOWNLOAD_DEST_FILE=%TARGET_ROOT_PATH%\%BLENDER_ZIP_NAME%

echo [*] Blender Version to Setup: %BLENDER_FULL_VERSION%
echo [*] Target Folder: %BLENDER_INSTALL_PATH%
echo.

:: --- Download and Unzip Logic ---
if exist "%BLENDER_INSTALL_PATH%\blender.exe" (
    echo [INFO] Blender is already unzipped. Skipping download and unzip.
) else (
    echo [INFO] Blender installation not found. Proceeding with setup...

    if exist "%DOWNLOAD_DEST_FILE%" (
        echo [INFO] Blender ZIP file already exists. Skipping download.
    ) else (
        echo [ACTION] Downloading %BLENDER_ZIP_NAME%...
        echo [ACTION] From: %DOWNLOAD_URL%
        echo [ACTION] To:   %DOWNLOAD_DEST_FILE%
        powershell -Command "Invoke-WebRequest -Uri '%BLENDER_DOWNLOAD_URL%' -OutFile '%DOWNLOAD_DEST_FILE%'"
        if %ERRORLEVEL% neq 0 (
            echo [ERROR] Download failed. Please check the URL and your internet connection.
            goto :eof
        )
        echo [SUCCESS] Download complete.
    )

    echo.
    echo [ACTION] Unzipping %BLENDER_ZIP_NAME%...
    powershell -Command "Expand-Archive -Path '%DOWNLOAD_DEST_FILE%' -DestinationPath '%TARGET_ROOT_PATH%' -Force"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to unzip the file. The file might be corrupt or you may lack permissions.
        goto :eof
    )
    echo [SUCCESS] Blender has been unzipped to: %BLENDER_INSTALL_PATH%
)

:: --- Python Module Installation Logic ---
echo.
echo [INFO] Proceeding with Python module installation...

:: Path to Blender's internal Python executable.
set BLENDER_PYTHON_EXE=%BLENDER_INSTALL_PATH%\%BLENDER_VERSION%\python\bin\python.exe

:: For a portable install, the modules path is INSIDE the Blender folder.
:: set MODULE_TARGET_PATH=%BLENDER_INSTALL_PATH%\%BLENDER_VERSION%\scripts\modules

:: Path where Blender for Windows looks for user-installed modules.
:: This corresponds to bpy.utils.user_resource("SCRIPTS", path="modules")
:: The %APPDATA% variable typically points to "C:\Users\<YourUsername>\AppData\Roaming"
set MODULE_TARGET_PATH="%APPDATA%\Blender Foundation\Blender\%BLENDER_VERSION%\scripts\modules"

:: --- Verify Paths ---
echo.
echo [*] Blender Version: %BLENDER_VERSION%
echo [*] Using Blender Python: %BLENDER_PYTHON_EXE%
echo [*] Installing modules to: %MODULE_TARGET_PATH%
echo.

if not exist %BLENDER_PYTHON_EXE% (
    echo [ERROR] Blender's Python executable not found at the specified path.
    echo [ERROR] Please correct the BLENDER_INSTALL_PATH variable in this script.
    goto :eof
)

if not exist %MODULE_TARGET_PATH% (
    echo [INFO] Module directory does not exist. Creating it now...
    mkdir %MODULE_TARGET_PATH%
)

echo [!] Please Verify Paths...
pause

:: --- Tell pip to trust Pypi.org ---
echo.
echo [*] Upgrading pip for Blender's Python...
%BLENDER_PYTHON_EXE% -m pip config --global set global.trusted-host "pypi.org files.pythonhosted.org"

:: --- Upgrade pip ---
echo.
echo [*] Upgrading pip for Blender's Python...
%BLENDER_PYTHON_EXE% -m pip install --upgrade pip

:: --- Install Python Modules ---
echo.
echo [*] Installing matplotlib, kivy, openimageio, pyside6...
%BLENDER_PYTHON_EXE% -m pip install --trusted-host=pypi.org matplotlib kivy openimageio pyside6 pyroomacoustics scipy --target=%MODULE_TARGET_PATH%

echo.
echo [*] Trying install of OpenImageIO
%BLENDER_PYTHON_EXE% -m pip install OpenImageIO --target=%MODULE_TARGET_PATH%

echo.
echo [*] Installing and upgrading numpy to fix potential conflicts...
:: This is crucial to overwrite Blender's built-in numpy and avoid the "numpy.core.multiarray failed to import" error.
%BLENDER_PYTHON_EXE% -m pip install numpy==1.26.4 --target=%MODULE_TARGET_PATH% --upgrade

echo.
echo [SUCCESS] Script finished. All modules should now be available in Blender.

:: --- Download and Unzip Logic for EnergyPlus ---
:: Kaputt

REM set EPLUS_INSTALL_PATH = %TARGET_ROOT_PATH%\energyplus
REM set EPLUS_DL_FILE = %TARGET_ROOT_PATH%\energyplus.zip
REM set EPLUS_DOWNLOAD_URL = https://github.com/NREL/EnergyPlus/releases/download/v22.1.0/EnergyPlus-22.1.0-ed759b17ee-Windows-x86_64.zip

REM if exist "%EPLUS_INSTALL_PATH%\energyplus.exe" (
    REM echo [INFO] Energyplus is already unzipped. Skipping download and unzip.
REM ) else (
    REM echo [INFO] Energyplus installation not found. Proceeding with setup...

    REM if exist "%EPLUS_DL_FILE%" (
        REM echo [INFO] Energyplus ZIP file already exists. Skipping download.
    REM ) else (
        REM echo [ACTION] Downloading EnergyPlus...
        REM echo [ACTION] From: %EPLUS_DOWNLOAD_URL%
        REM echo [ACTION] To:   %EPLUS_DL_FILE%
        REM powershell -Command "Invoke-WebRequest -Uri '%EPLUS_DOWNLOAD_URL%' -OutFile '%EPLUS_DEST_FILE%'"
        REM if %ERRORLEVEL% neq 0 (
            REM echo [ERROR] Download failed. Please check the URL and your internet connection.
            REM goto :eof
        REM )
        REM echo [SUCCESS] Download complete.
    REM )

    REM echo.
    REM echo [ACTION] Unzipping %EPLUS_DL_FILE%...
    REM powershell -Command "Expand-Archive -Path '%EPLUS_DL_FILE%' -DestinationPath '%TARGET_ROOT_PATH%' -Force"
    REM if %ERRORLEVEL% neq 0 (
        REM echo [ERROR] Failed to unzip the file. The file might be corrupt or you may lack permissions.
        REM goto :eof
    REM )
    REM echo [SUCCESS] Blender has been unzipped to: %EPLUS_INSTALL_PATH%
REM )

pause

endlocal
