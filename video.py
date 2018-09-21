import sys
import os
import shutil
import subprocess
import re
import glob
import shlex

video_codec = 'libx264'
audio_codec = 'libfdk_aac'
preset = 'medium' # medium, veryslow

def kbsfromline(line):
    m = re.search('(,\s*)(\d+)(\s*kb/s)', line)
    if (m!= None):
        answer = m.group(2)
    else:
        answer = ''
    return answer

def bitrate(input_video_file_name):

    video_bitrate = ''
    audio_bitrate = ''

    query_command = "ffmpeg -i " + input_video_file_name
    process = subprocess.Popen(shlex.split(query_command), stderr=subprocess.PIPE)
    text = process.stderr.read()
    retcode = process.wait()

    lines = text.split("\n")
    for line in lines:
        m = re.search('Stream.*Video', line)
        if(m != None):
            video_bitrate = kbsfromline(line)
        m = re.search('Stream.*Audio', line)
        if(m != None):
            audio_bitrate = kbsfromline(line)

    return [video_bitrate, audio_bitrate]

# convert video from one format to another
def ffmpeg_convert(input_video_file_name, output_video_file_name, two_pass=True):

#qp is the quantization parameter for the fixed-quality setting (0 = lossless). I cannot be sure if x264 is acceptable to the system yet, but it can be opened by Quicktime so I guess it is fine.
#command = "ffmpeg -i " + input_video_file_name + " -vcodec libx264 -preset veryslow -qp 3 -pix_fmt yuv420p -loglevel warning " + output_video_file_name

    [video_bitrate, audio_bitrate] = bitrate(input_video_file_name)

    if video_bitrate == "":
        two_pass = False

    if two_pass:
        # two pass to control output size
        # https://trac.ffmpeg.org/wiki/Encode/H.264
        spec = " -c:v " + video_codec + " -preset " + preset + " -b:v " + video_bitrate + 'k'

        command_pass1 = "ffmpeg -loglevel warning -y -i " + input_video_file_name + spec + " -pass 1 " + " -f mp4 NUL"
        command_pass2 = "ffmpeg -loglevel warning -i " + input_video_file_name + spec + " -pass 2 " +  output_video_file_name

        command = command_pass1 + " && " + command_pass2

    else:
        input_video_file_size = os.path.getsize(input_video_file_name)
        spec = " -fs " + str(input_video_file_size) + " -preset " + preset + " "

        command = "ffmpeg -loglevel warning -i " + input_video_file_name + spec + output_video_file_name

    os.system(command)

    if two_pass: 
        remove_file_list = glob.glob("ffmpeg*pass*log*")
        for remove_file in remove_file_list:
            os.remove(remove_file)
