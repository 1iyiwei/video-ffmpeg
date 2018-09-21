import sys
import os
import shutil
import subprocess
import re
import glob
import shlex
from video import *

# main

argc = len(sys.argv)

if argc < 3:
    error_message = "python input_video_file output_video_file";
    print(error_message)
    raise Exception(error_message)

input_video_file_name = sys.argv[1]
output_video_file_name = sys.argv[2]

two_pass = True

ffmpeg_convert(input_video_file_name, output_video_file_name, two_pass)
