import requests
import os
import json
import pandas as pd

def create_embedding(text_list):
    r=requests.post("http://localhost:11434/api/embed",json={
        "model":"bge-m3",
        "input":text_list
    })
    embedding=r.json()["embeddings"]
    return embedding

jsons=os.listdir("jsons")
l=[]
chunk_id=0

for json_file in jsons:
    with open(f"jsons/{json_file}") as f:
        content=json.load(f)
    texts=[chunk.get("text","") for chunk in content]
    embeddings = []
    batch_size = 80
    for i in range(0, len(texts), batch_size):
        batch=texts[i:i +batch_size]
        print(f"Embedding {i} to {i+len(batch)-1}")
        batch_embeddings=create_embedding(batch)
        embeddings.extend(batch_embeddings)

    for i,chunk in enumerate(content):
        chunk["chunk_id"]=chunk_id
        chunk["embedding"]=embeddings[i]
        chunk_id +=1
        l.append(chunk)

df=pd.DataFrame.from_records(l)
print(df)