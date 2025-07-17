@echo off

set ask_user=1
if not "%~2" == "" (
    set ask_user=%2
)

if %ask_user% equ 0 (
    set framerate=%3
) else (
    set /P framerate=- Target framerate:
)

if %ask_user% equ 0 (
    set scale_divide=%4
) else (
    set /P scale_divide=- Target Size Divider:
)

set "file_suffix="
if %ask_user% equ 0 (
    if not "%~5" == "" (
        set file_suffix=%5
    )
) else (
    set /P "file_suffix=- File name suffix (optional):"
)

set "dithering=sierra2_4a"
if %ask_user% equ 0 (
    if not "%~6" == "" (
        set dithering=%6
    )
) else (
    echo " # DITHERING methods"
    echo "     none"
    echo " # higher scale = less visible dotted pattern but more banding"
    echo "     bayer:bayer_scale=0"
    echo "     bayer:bayer_scale=1"
    echo "     bayer:bayer_scale=2"
    echo "     bayer:bayer_scale=3"
    echo "     bayer:bayer_scale=4"
    echo "     bayer:bayer_scale=5"
    echo " # (popular) lighter than bayer"
    echo "     floyd_steinberg"
    echo " # even lighter, very pronounced banding"
    echo "     sierra2"
    echo " # (default) heavy, subttle dot pattern with few banding."
    echo "     sierra2_4a"
    set /P dithering=- Dithering method:
)

set "output=%~n1%file_suffix%.gif"
set "filter_graph=fps=%framerate%,scale=iw/%scale_divide%:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse=dither=%dithering%"


:: -y : overwite existing, else use -n
%FFMPEG% -y -i "%1" -threads 0 -loop 0 -vf %filter_graph% %output%
