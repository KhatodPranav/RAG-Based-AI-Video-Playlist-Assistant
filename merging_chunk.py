import os
import json
import math

jsons=os.listdir("jsons")

chunks_to_merge=7
for json_file in jsons:
    with open(f"jsons/{json_file}","r") as f:
        data=json.load(f)
        data=[c for c in data if "video_number" in c]
        new_chunks=[]
        num_chunks=len(data)
        num_groups=math.ceil(num_chunks/chunks_to_merge)
        for i in range(num_groups):
            start_idx=i*chunks_to_merge
            end_idx=min((i+1)*chunks_to_merge,num_chunks)
            chunk_group=data[start_idx:end_idx]

            new_chunks.append({
                "video_number":chunk_group[0]["video_number"],
                "start":chunk_group[0]["start"],
                "end":chunk_group[-1]["end"],
                "text":" ".join(c["text"] for c in chunk_group)
            })

        with open(f"jsons/{json_file}","w") as f:
            json.dump(new_chunks,f,indent=4)