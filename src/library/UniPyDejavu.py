import subprocess
import sys
import argparse
import os

# Prepare Stage
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-f', '--input_file_name')
    parser.add_argument ('-o', '--output_file_name')
    #parser.add_argument("-V", "add", action="store_true")
        
    return  parser
        
parser = parse_arguments()
namespace = parser.parse_args(sys.argv[1:])
args = parser.parse_args()

input_file = str(namespace.input_file_name)
output_file = str(namespace.output_file_name)

input_filename, input_file_extension = os.path.splitext(input_file)
output_filename, output_file_extension = os.path.splitext(output_file)

print(f"Input : {input_file}")
print(f"Output : {output_file}")

#if args.version:
#    print("This is myprogram version 0.1")

# Stage 1 : check audio files for integrity and convert them
if input_file_extension == ".mp3":
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-i', input_file, output_file]
elif input_file_extension in (".wma", ".ogg", ".wav"):
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-i', input_file, '-acodec', 'libmp3lame', output_file]
else:
    print("Ты чё!? Ебо-бо штоли !?")
    exit()

process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
 
data = process.communicate()

if data[1] == "":
    print("Succes ! ")
elif data[1] == f"{input_file}: Invalid data found when processing input\n":
    print("Critical error! File corrupted!")
    exit()
else:
    print(f"Error : {data[1]}")

if os.path.exists(output_file) is True:
        print("File succeful created!")
else:
        print("Critical error! File corrupted!")
        exit()
        
# Stage 2 : mormalize audio
#print("Normalizing audio file ...")
#args = ['ffmpeg-normalize', output_file, '-c:a', 'libmp3lame', '-o', output_filename + "_norm" + output_file_extension]
#process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
#
#data = process.communicate()
#print(data[1])

# Stage 3 : register current audio sample hashes


# Stage 4 : recognize audio
# dejavu output:
'''
{'song_id': 4, 'song_name': '01_Абай_сегіз аяқ_norm', 'confidence': 1, 'offset': 1715, 'offset_seconds': 79.64444, 'file_sha1': '5432496134783669786e68746e677077636f506c423754324b37343d0a', 'match_time': 5.433079481124878}
'''