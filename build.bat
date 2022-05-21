@echo off
echo Tiktok Download Build
pyinstaller TiktokDownload.py --icon=logo.ico --onefile
pyinstaller TiktokDownload_backup.py --icon=logo.ico --onefile