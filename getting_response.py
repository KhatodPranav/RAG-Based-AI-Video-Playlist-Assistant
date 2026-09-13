from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from read_chunks import create_embedding
import joblib
import requests

file=joblib.load("embeddings.joblib")
df=file

question=input("Enter Your Question: ")
question_embeddings=create_embedding(question)[0]

# print(np.vstack(df["embedding"].values))
# print(np.vstack(df["embedding"].shape))

similarity=cosine_similarity(np.vstack(df["embedding"]),[question_embeddings]).flatten()
# print(similarity)

top_results=5
max_indx=similarity.argsort()[::-1][0:top_results]
# print(max_indx)

top_idx_data=df.loc[max_indx]
# print(top_idx_data[["chunk_id","video_number","text"]])
# print(top_idx_data.keys())

prompt=f"""Here are video subtitle chunks containing Video Number,start time in seconds,end time in seconds, text for that time:
{top_idx_data[["video_number","start","end","text"]].to_string(index=False)}
------------------------------
Users Question: {question}
User asked this question related to the video chunk, you have to answer where and how much content is taught in which video (in which video and at what time stamp) and guide the user to go to that particular video. If user asks any unrelated question, tell him you can only answer questions related to selected videos."""

with open("prompt.txt","w") as f:
    f.write(prompt)

def inference(promp):
    r=requests.post("http://localhost:11434/api/generate",json={
        "model":"llama3.1",
        "prompt":promp,
        "stream":False
    })
    response=r.text
    return response

answer=inference(prompt)

with open("response.txt","w") as f:
    f.write(answer)