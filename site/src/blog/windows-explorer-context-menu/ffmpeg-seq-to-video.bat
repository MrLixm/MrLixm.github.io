@echo off

echo "Image sequence to video conversion started."
echo "  active OCIO config=%OCIO% "
echo:

echo "[abstract_file_name] Enter the file name with the frame number replace by a %d (no padding) or a %0Nd (with padding) "
echo "                     Example: asset-lookdev.v0001.0012 -> asset-lookdev.v0001.%%04d                                   "
echo "current file name is: %~n1"
set /P abstract_file_name=^> abstract_file_name=
echo:

echo "[file_suffix] File name suffix (optional)"
set /P "file_suffix=> file_suffix="
echo:

echo "[frame_expression] Enter the frame sequence expression specifying which frames to render for OIIO."
echo "                   Example: 1001-1100 render from frame 1001 to 1100                     "
set /P frame_expression=^> frame_expression=
echo:

echo "[frame_start] Enter the number of the first frame of the sequence for ffmpeg."
set /P frame_start=^> frame_start=
echo:

echo "[framerate] usually ntsc-film (23.98), 24, ntsc (29.97), 60000/1001 (59.94)"
set /P framerate=^> framerate=
echo:

echo // QUALITY :
echo:

echo "[presets] ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow"
set /P preset=^> preset=
echo:

echo " [tune]"
echo "     - film : use for high quality movie content; lowers deblocking"
echo "     - animation : good for cartoons; uses higher deblocking and more reference frames"
echo "     - grain : preserves the grain structure in old, grainy film material"
set /P tune=^> tune=
echo:

echo "[crf] Constant Rate Factor. Between 0 (lossless) <- 18 <- 23 <- 28 (worse)"
set /P crf=^> crf=
echo:

echo "[resolution] Target will be rescaled to the given width, while maintaining aspect ratio."
set /P reso_width=^> resolution=
echo:

echo "[source_colorspace] OCIO colorspace name in which the input file is encoded in."
set /P source_colorspace=^> source_colorspace=
echo

echo "[target_colorspace] OCIO colorspace name in which the target file must be encoded in."
set /P target_colorspace=^> target_colorspace=
echo:

set "oiio_input=%~dp1%abstract_file_name%%~x1"
set "oiio_output_dir=%~dp1tempoiio"
set "oiio_output=%oiio_output_dir%\%abstract_file_name%.tif"

echo "[oiio_output_dir] writing %oiio_output_dir%"
MD %oiio_output_dir%

echo "(oiiotool) about to start ..."
%OIIOTOOL% -v --frames %frame_expression% %oiio_input% --colorconvert %source_colorspace% %target_colorspace% -d uint16 -o %oiio_output%

set "ffmpeg_input=%oiio_output%"

set "output=%~dpn1%file_suffix%.mp4"
set "filter_graph=scale=%reso_width%:trunc(ow/a/2)*2:flags=lanczos:in_color_matrix=bt709:out_color_matrix=bt709"

:: -y : overwite existing, else use -n
%FFMPEG% -n -start_number %frame_start% -i %ffmpeg_input% -threads 0 -r %framerate% -vf %filter_graph% -c:v libx264 -preset %preset% -tune %tune% -crf %crf% -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc iec61966-2-1 %output%

echo "(ffmpeg) file written to %output%"

echo "[oiio_output_dir] removing %oiio_output_dir%"
RD /q /s %oiio_output_dir%