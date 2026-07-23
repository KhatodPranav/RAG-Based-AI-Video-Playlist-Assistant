import whisper
import os
import json

model=whisper.load_model("large-v2")

files=os.listdir("audios")

# output_file=os.mkdir("jsons")

for file in files:
    audio_path=os.path.join("audios",file)
    filename=file.split(".mp3")[0]
    result=model.transcribe(audio=audio_path,language="hi",task="translate")
    with open (f"jsons/{filename}.json","w") as f:
        json.dump(result,f,index=4,ensure_ascii=False)
    print(result)
    