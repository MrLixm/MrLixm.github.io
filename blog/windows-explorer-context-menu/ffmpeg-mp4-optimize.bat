@echo off

set ask_user=1
if not "%~2" == "" (
    set ask_user=%2
)

if %ask_user% equ 0 (
    set framerate=%3
) else (
    echo "[framerate] usually ntsc-film (23.98), 24, ntsc (29.97), 60000/1001 (59.94)"
    set /P framerate=^> framerate=
)

if %ask_user% equ 0 (
    set preset=%4
) else (
    echo "[presets] ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow"
    set /P preset=^> preset=
)

if %ask_user% equ 0 (
    set tune=%5
) else (
    echo " [tune]"
    echo "     - film : use for high quality movie content; lowers deblocking"
    echo "     - animation : good for cartoons; uses higher deblocking and more reference frames"
    echo "     - grain : preserves the grain structure in old, grainy film material"
    set /P tune=^> tune=
)

if %ask_user% equ 0 (
    set crf=%6
) else (
    echo "[crf] Constant Rate Factor. Between 0 (lossless) <- 18 <- 23 <- 28 (worse)"
    set /P crf=^> crf=
)

if %ask_user% equ 0 (
    set reso_width=%7
) else (
    echo "[resolution] Target will be rescaled to the given width, while maintaining aspect ratio."
    set /P reso_width=^> resolution=
)

set "file_suffix="
if %ask_user% equ 0 (
    if not "%~8" == "" (
        set file_suffix=%8
    )
) else (
    echo "[file_suffix] File name suffix (optional)"
    set /P "file_suffix=> file_suffix="
)

set "output=%~n1%file_suffix%.mp4"
set "filter_graph=scale=%reso_width%:trunc(ow/a/2)*2:flags=lanczos:in_color_matrix=bt709:out_color_matrix=bt709"

:: -y : overwite existing, else use -n
%FFMPEG% -n -i "%1" -threads 0 -r %framerate% -vf %filter_graph% -c:v libx264 -preset %preset% -tune %tune% -crf %crf% -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc iec61966-2-1 %output%
