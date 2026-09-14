# RAG-Based AI Video Playlist Assistant

Local RAG pipeline for a video playlist. Put lecture videos in `videos/`, index them once, then ask a question. The assistant returns **which video** to open and **at what timestamp**. Answers come only from the indexed playlist, not from the internet.

This repository already includes a **worked example**: two Hindi lectures (Pandas and MongoDB), extracted audio, merged English transcript chunks, embeddings, and a sample Q&A (`one-dimensional array`).

---

## Example playlist (this repo)

The pipeline was built and tested on these two files. Folder order from `os.listdir` assigns `video_number` (`0` = MongoDB, `1` = Pandas).

| `video_number` | Folder | File | Role |
|----------------|--------|------|------|
| 0 | `videos/` | `MongoDB for Data Professionals _ Data Analysis Tools in MongoDB 🔥(144p).mp4` | Source lecture (~58 MB) |
| 0 | `audios/` | same basename `.mp3` | ffmpeg extract (~46 MB) |
| 0 | `jsons/` | same basename `.json` | Merged Whisper chunks |
| 1 | `videos/` | `Python Pandas Crash Course (2025)(144p).mp4` | Source lecture (~39 MB) |
| 1 | `audios/` | same basename `.mp3` | ffmpeg extract (~34 MB) |
| 1 | `jsons/` | same basename `.json` | Merged Whisper chunks |

`embeddings.joblib` is the indexed DataFrame for this playlist (chunks + `bge-m3` vectors). `prompt.txt` and `response.txt` are the last LLM call for the example question below.

### Sample merged chunk (Pandas, `video_number` 1)

```json
{
    "video_number": 1,
    "start": 0.0,
    "end": 40.0,
    "text": " In today's video, I will tell you what is Python Pandas and how you can use Python Pandas effectively in your data science projects.  Pandas is a Python library that helps you in data analysis. ..."
}
```

Times are **seconds**. Seven Whisper segments are joined into each chunk (`merging_chunk.py`).

### Sample question

```text
Enter Your Question: one-dimensional array
```

Retrieved context (top 5 chunks, all from video 1) is written to `prompt.txt`. Example hits:

- video 1, **1011–1032 s** (~16:51–17:12) — `df.id` as a Pandas Series (1D)
- video 1, **503–529 s** (~8:23–8:49) — Series as a labeled array
- video 1, **1079–1119 s** (~17:59–18:39) — one row / 1D data as a Series

Llama 3.1 then points the user to those timestamps. Example from `response.txt`:

> Watch **Video 1** from **10:11–10:32** (`df.id` is a Series / one-dimensional structure) and **18:00–18:19** (one-dimensional data is a pandas Series). In this playlist, “one-dimensional array” is taught as a **Series**.

An unrelated question is refused; the model is instructed to answer only from these videos.

---

## How RAG works

1. Each video becomes text chunks: `video_number`, `start`, `end`, `text`.
2. Each chunk is converted to an embedding vector with Ollama `bge-m3`.
3. The user question is embedded with the same model.
4. Cosine similarity ranks chunks (similar meaning → similar vectors).
5. The top chunks go to Llama 3.1, which answers using that context only.
6. If the question is unrelated to the videos, the model is told to refuse.

---

## Project layout

```
videos/                 playlist videos (input)
audios/                 MP3 files from ffmpeg
jsons/                  Whisper JSON, then cleaned and merged chunks
video_to_audio.py       step 1 — video to audio
audio_to_json.py        step 2 — audio to transcript
cleaning_jsons.py       step 3 — keep useful fields
merging_chunk.py        step 4 — merge short segments
read_chunks.py          step 5 — create embeddings
getting_response.py     step 6 — ask a question
embeddings.joblib       saved chunks + vectors
prompt.txt              last prompt sent to the LLM
response.txt            last model reply
requirements.txt        Python packages
```

---

## How this repo was built (git history)

Commits on `main` follow the pipeline in order. Use this as a map of what each step produced:

| Commit | What landed |
|--------|-------------|
| **input videos folder** | Example lectures in `videos/` (MongoDB `.mp4`, Pandas `.mp4`) |
| **convert vid to aud** | `video_to_audio.py` (ffmpeg over `videos/` → `audios/`) |
| **audio files using ffmpeg** | Example `.mp3` files |
| **json files from audios** | Raw Whisper transcripts in `jsons/` |
| **cleaned json files** | `cleaning_jsons.py` — keep `video_number`, `start`, `end`, `text` |
| **dataframe for embeddings (batch wise)** | `read_chunks.py` — Ollama `bge-m3` in batches of 30 |
| **saving dataframe to joblib and creating prompt** | `embeddings.joblib` + prompt construction |
| **getting response from LLM** | `getting_response.py` — cosine top-5 → Llama 3.1 |
| **merging chunks and updating json files** | `merging_chunk.py` (7 segments per chunk) + rewritten `jsons/` |
| **updating joblib file wrt updated chunks** | Re-embed after merge |
| **changing prompt and getting result wrt updated merged chunks** | Prompt + `response.txt` for the merged index (example: `one-dimensional array`) |

To re-run on a **new** playlist, replace `videos/` and execute steps 1–5 again. To only query this example index, keep Ollama running and use step 6.

---

## Setup

Install Python packages:

```bash
pip install -r requirements.txt
```

Install **FFmpeg** and add it to PATH (needed for video → MP3). Test with:

```bash
ffmpeg -i input.mp4 output.mp3
```

On Windows: unzip FFmpeg, copy it to a folder such as `C:\Program Files (x86)\ffmpeg`, and add the `bin` folder to system environment variables.

Install **Ollama** and keep it running. Pull the models used by this project:

```bash
ollama pull bge-m3
ollama pull llama3.1
```

`bge-m3` is used for embeddings. `llama3.1` generates the final answer. Whisper uses `large-v2` (downloaded on first run; slow on CPU). Audio is transcribed as Hindi and translated to English (`language="hi"`, `task="translate"`).

---

## How to run the pipeline

Put videos in `videos/`. Create `audios/` if it does not exist. Run scripts **in order**.

**Step 1 — Video to audio**

```bash
python video_to_audio.py
```

Converts each file in `videos/` to an MP3 in `audios/` using ffmpeg.

**Step 2 — Audio to JSON**

```bash
python audio_to_json.py
```

Whisper `large-v2` transcribes Hindi audio and translates it to English. Output is saved in `jsons/`. If `jsons/` already exists, create it once yourself so `os.mkdir` does not fail.

**Step 3 — Clean JSON**

```bash
python cleaning_jsons.py
```

Keeps only `video_number`, `start`, `end`, and `text` from Whisper segments. `video_number` is assigned in folder order (0, 1, 2, …).

**Step 4 — Merge chunks**

```bash
python merging_chunk.py
```

Groups **7** short Whisper segments into one chunk so context is not lost. Each merged chunk uses the first start time, last end time, and joined text.

**Step 5 — Embeddings**

```bash
python read_chunks.py
```

Sends chunk text to Ollama `bge-m3` in batches of 30. Adds `chunk_id` and `embedding`, then saves a pandas DataFrame as `embeddings.joblib`. Ollama must be running.

**Step 6 — Ask a question**

```bash
python getting_response.py
```

Example: `Enter Your Question: one-dimensional array`

The script embeds the question, takes the **top 5** similar chunks, builds a prompt, and calls Llama 3.1. It writes `prompt.txt` (context + question) and `response.txt` (Ollama JSON; the answer is in `"response"`).

Run steps 1–5 once per playlist. Run step 6 for every new question. Re-index (1–5) only when videos or chunking change.

---

## Data flow

```
videos → ffmpeg → audios → Whisper → jsons (raw)
      → clean → jsons (segments) → merge (7) → jsons (chunks)
      → bge-m3 → embeddings.joblib
      → question → cosine similarity → top 5 chunks → llama3.1 → answer
```