@echo off
set pyfile=%~dp0\minecraft
set pyinst=C:\Python27\pyinstaller-1.5
python -OO "%pyinst%\Configure.py"
python -OO "%pyinst%\Makespec.py" --onefile --icon=icon.ico "%pyfile%.py"
python -OO "%pyinst%\Build.py" %pyfile%.spec
pause