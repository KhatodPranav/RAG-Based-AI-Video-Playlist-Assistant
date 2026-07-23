import os
import json

jsons=os.listdir("jsons")
file_no=0

for json_file in jsons:

    with open(f"jsons/{json_file}") as f:
        data=json.load(f)

    chunk=[]
    for segment in data["segments"]:
        chunk.append({"video_number":file_no,
                      "start":segment["start"],
                      "end":segment["end"],
                      "text":segment["text"]
                      })
    chunk.append({"Video_text":data["text"]})

    with open(f"jsons/{json_file}","w") as f:
        json.dump(chunk,f,indent=4,ensure_ascii=False)

    file_no+=1

# print(chunk)