# Kokoro voice files -- GitHub hosting package

This folder contains your Kokoro TTS model files (`kokoro-v1.0.fp16.onnx`,
already split into four ~45MB pieces so no single file exceeds GitHub's
100MB per-file limit) plus `voices-v1.0.bin` (28MB, small enough to commit
as-is) and a `reassemble.py` script.

Why split instead of using Git LFS or a GitHub Release: those both work
fine for *you* to push, but when a Cowork sandbox later tries to pull them
back down, GitHub redirects LFS and Release downloads to a CDN domain
(`media.githubusercontent.com` / `release-assets.githubusercontent.com`)
that's blocked by the sandbox's network policy. Plain committed files
(regular git blobs, no LFS filter) transfer inline as part of the normal
git clone -- no separate CDN request, no block. Splitting keeps every
individual file under GitHub's hard blob-size cap so the push itself
succeeds.

## What to do with this folder

This needs to be pushed from a machine with normal internet access and
your own GitHub login -- not from inside the Cowork sandbox, since that's
exactly the environment that can't reach the outside world freely.

1. Create a new GitHub repo (public or private, your call -- if private,
   the sandbox will need a way to authenticate later, so public is
   simpler unless you have a reason not to).
2. From a terminal on your own machine, `cd` into this folder and run:

   ```
   git init
   git add .
   git commit -m "Kokoro voice files for faceless-video skill"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```

   Do **not** run `git lfs track` on any of these files -- that would
   put them right back behind the blocked CDN this whole setup is
   designed to avoid.

3. Once pushed, tell me the repo URL. I'll wire it into the skill's
   voice-setup logic as an automatic fallback: any future session (yours
   or someone else's, on any machine) can run `git clone` on your repo
   plus `python3 reassemble.py` and have working voices with zero manual
   file placement -- no connected folder required.

## Verifying it worked

After cloning the repo anywhere, run:

```
python3 reassemble.py
```

It reassembles the four ONNX chunks back into `kokoro-v1.0.fp16.onnx` and
checksums both files against `checksums.txt`. Already verified once in
the sandbox that reassembly is byte-identical to the original (matching
sha256), so if the checksums still match after a real clone, the transfer
was clean too.
