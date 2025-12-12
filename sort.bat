@echo off
mkdir "avi" 2>nul
mkdir "mp4" 2>nul

for %%f in (*.avi) do move "%%f" "avi"
for %%f in (*.mp4) do move "%%f" "mp4"
