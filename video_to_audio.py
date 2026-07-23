import os
import subprocess

files=os.listdir("videos")

print(files)

for file in files:
    filename=file.split(".mp4")[0]
    subprocess.run(["ffmpeg","-i",f"videos/{file}",f"audios/{filename}.mp3"])