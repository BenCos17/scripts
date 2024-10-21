@echo off
:: Prompt user for output file name
set /p outputFileName="Enter the name for the output PDF file (without extension): "

:: Rename all .jpeg files to .jpg
for %%f in (*.jpeg) do (
    ren "%%f" "%%~nf.jpg"
)

:: Apply auto-orient to ensure the latest version of the images is used
mogrify -auto-orient *.jpg

:: Run ImageMagick to convert all .jpg files to a single PDF
magick *.jpg "%outputFileName%.pdf"

:: Notify user of completion
echo Conversion complete! Your file is saved as "%outputFileName%.pdf"
pause
