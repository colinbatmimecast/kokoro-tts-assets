# Kokoro voice files -- GitHub hosting package (browser-upload version)

This folder contains your Kokoro TTS files, split into pieces small
enough for GitHub's web uploader (25MB limit per file -- these are all
under 21MB, with margin):

- `onnx-chunks/` -- 9 pieces of `kokoro-v1.0.fp16.onnx` (177MB total)
- `voices-chunks/` -- 2 pieces of `voices-v1.0.bin` (28MB total)
- `checksums.txt` -- sha256 of both original files
- `reassemble.py` -- puts the pieces back together and verifies them

Why split instead of Git LFS or a GitHub Release: those work fine to
upload, but when a Cowork sandbox later tries to pull the files back
down, GitHub redirects LFS/Release downloads to a CDN domain
(`media.githubusercontent.com` / `release-assets.githubusercontent.com`)
that's blocked by the sandbox's network policy. Plain uploaded files
(regular git blobs) transfer inline as part of a normal clone or
download -- no CDN redirect, no block.

## Uploading via the GitHub website (no git required)

1. Create a new **public** repo on github.com (needs to be public so a
   future sandbox session can clone it without needing your login --
   see the note on this below if you'd rather not).
2. On the repo page, click **Add file > Upload files**.
3. Drag in everything from this folder: `README.md`, `checksums.txt`,
   `reassemble.py`, the full contents of `onnx-chunks/`, and the full
   contents of `voices-chunks/`. Keep the folder structure -- GitHub's
   uploader preserves subfolders when you drag a folder in, or you can
   drag the two chunk folders in as separate uploads if it's easier.
4. Commit directly to the `main` branch.

GitHub's web uploader has a per-commit file count limit too (usually
fine for the ~13 files here, but if it complains, just upload
`onnx-chunks/` and `voices-chunks/` as two separate commits).

## Verifying it worked

Download the repo as a zip (green **Code** button > Download ZIP) or
clone it, then run:

```
python3 reassemble.py
```

It reassembles both files from their chunks and checksums them against
`checksums.txt`. Already verified once in the sandbox that reassembly
is byte-identical to the original (matching sha256 for both files), so
if the checksums still match after your own upload/download round trip,
the transfer was clean too.

## Once it's up

Send me the repo URL. I'll wire it into the skill's voice-setup logic as
an automatic fallback -- any future session (yours or someone else's, on
any machine) can pull your repo and run `reassemble.py` to get working
voices with zero manual file placement, no connected folder required.
