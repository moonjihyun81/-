#!/usr/bin/env python3
"""릴스(짧은 영상) 하나를 받아서 받아쓰기 + 장면별 사진을 만든다.

사용법:
  python3 read_reel.py <링크 또는 영상파일> [--out 폴더] [--cookies cookies.txt]
                       [--browser chrome] [--model small] [--lang ko]
                       [--threshold 0.3] [--max-frames 30]

결과 (out 폴더):
  video.mp4         내려받은 영상
  info.json         제목·계정·설명·길이
  transcript.json   받아쓰기 (구간별 시작/끝/문장)
  frames/*.jpg      장면이 바뀔 때마다 1장
  scenes.json       장면별 시간 / 사진 경로 / 그 구간에 나온 말
마지막 줄에 scenes.json 경로를 출력한다.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def fail(msg, code=1):
    print(f"[실패] {msg}", file=sys.stderr)
    sys.exit(code)


def need(cmd, hint):
    if shutil.which(cmd) is None:
        fail(f"{cmd} 가 설치돼 있지 않아요. {hint}")


def download(src, out, cookies, browser):
    p = Path(src)
    if p.exists():
        dst = out / ("video" + p.suffix)
        shutil.copy(p, dst)
        (out / "info.json").write_text(json.dumps({"title": p.name}, ensure_ascii=False))
        return dst

    need("yt-dlp", "pip install -U yt-dlp")
    cmd = [
        "yt-dlp", "--no-playlist", "--no-progress",
        "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
        "--merge-output-format", "mp4",
        "-o", str(out / "video.%(ext)s"),
        "--write-info-json", "--no-write-comments",
    ]
    if cookies:
        cmd += ["--cookies", cookies]
    if browser:
        cmd += ["--cookies-from-browser", browser]
    cmd.append(src)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        err = (r.stderr or r.stdout)[-1500:]
        low = err.lower()
        if any(k in low for k in ("login", "cookies", "rate-limit", "private", "not available", "401", "403")):
            fail("로그인이 필요해서 다운로드가 막혔어요 (LOGIN_REQUIRED).\n" + err, code=2)
        fail("다운로드 실패:\n" + err)

    vids = sorted(out.glob("video.*"))
    vids = [v for v in vids if v.suffix not in (".json", ".part")]
    if not vids:
        fail("영상 파일을 찾지 못했어요.")
    info_files = list(out.glob("video*.info.json"))
    info = {}
    if info_files:
        raw = json.loads(info_files[0].read_text())
        info = {k: raw.get(k) for k in ("title", "uploader", "channel", "description",
                                        "duration", "upload_date", "like_count",
                                        "view_count", "webpage_url")}
        info_files[0].unlink()
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2))
    return vids[0]


def duration_of(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", str(video)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def has_audio(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0", str(video)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def transcribe(video, out, model_name, lang):
    if not has_audio(video):
        (out / "transcript.json").write_text("[]")
        return []
    wav = out / "audio.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
                    "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        fail("faster-whisper 가 설치돼 있지 않아요. pip install -U faster-whisper")
    try:
        model = WhisperModel(model_name, device="auto", compute_type="auto")
        segs, _ = model.transcribe(str(wav), language=lang or None, vad_filter=True)
        rows = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
                for s in segs]
    except Exception as e:  # 모델 다운로드 실패 등 — 장면 추출은 계속한다
        print(f"[경고] 받아쓰기 실패 (TRANSCRIBE_FAILED): {e}", file=sys.stderr)
        wav.unlink(missing_ok=True)
        return None
    (out / "transcript.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    wav.unlink(missing_ok=True)
    return rows


def grab(video, t, path):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video),
                    "-frames:v", "1", "-vf", "scale=720:-2", "-q:v", "3", str(path)], check=True)


def scene_times(video, threshold):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-an",
                        "-vf", f"select='gt(scene,{threshold})',showinfo",
                        "-f", "null", "-"], capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def scenes(video, out, threshold, max_frames, dur):
    times = [0.0] + [t for t in scene_times(video, threshold) if t > 0.3]
    # 장면 전환이 거의 없으면(한 컷 영상) 2초 간격으로 보충
    if len(times) < 3 and dur > 4:
        step = 2.0
        times = [round(i * step, 2) for i in range(int(dur // step) + 1)]
    # 너무 붙어 있는 컷은 합친다 (0.5초 이내)
    merged = []
    for t in sorted(times):
        if not merged or t - merged[-1] >= 0.5:
            merged.append(t)
    # 너무 많으면 고르게 줄인다
    if len(merged) > max_frames:
        idx = [round(i * (len(merged) - 1) / (max_frames - 1)) for i in range(max_frames)]
        merged = [merged[i] for i in sorted(set(idx))]
    fdir = out / "frames"
    fdir.mkdir(exist_ok=True)
    rows = []
    for i, t in enumerate(merged):
        end = merged[i + 1] if i + 1 < len(merged) else dur
        path = fdir / f"scene_{i + 1:03d}_{t:06.2f}s.jpg"
        grab(video, min(t + 0.15, max(dur - 0.05, 0)), path)
        rows.append({"scene": i + 1, "start": round(t, 2), "end": round(end, 2),
                     "frame": str(path)})
    return rows


def attach_speech(rows, transcript):
    for r in rows:
        said = [s["text"] for s in transcript
                if s["start"] < r["end"] and s["end"] > r["start"]]
        r["speech"] = " ".join(said)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="reels/latest")
    ap.add_argument("--cookies")
    ap.add_argument("--browser", help="chrome / safari / edge / firefox 등, 브라우저 로그인 쿠키 사용")
    ap.add_argument("--model", default="small", help="tiny/base/small/medium/large-v3")
    ap.add_argument("--lang", default="ko")
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--max-frames", type=int, default=30)
    a = ap.parse_args()

    need("ffmpeg", "https://ffmpeg.org/download.html (맥: brew install ffmpeg)")
    need("ffprobe", "ffmpeg 와 같이 설치돼요")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    video = download(a.src, out, a.cookies, a.browser)
    dur = duration_of(video)
    print(f"[1/3] 다운로드 완료: {video} ({dur:.1f}초)", file=sys.stderr)
    transcript = transcribe(video, out, a.model, a.lang)
    failed = transcript is None
    transcript = transcript or []
    print(f"[2/3] 받아쓰기 {'실패' if failed else f'{len(transcript)}구간'}", file=sys.stderr)
    rows = attach_speech(scenes(video, out, a.threshold, a.max_frames, dur), transcript)
    print(f"[3/3] 장면 {len(rows)}개 추출", file=sys.stderr)
    (out / "scenes.json").write_text(json.dumps(
        {"duration": round(dur, 2), "info": json.loads((out / "info.json").read_text()),
         "transcript_failed": failed,
         "full_transcript": " ".join(s["text"] for s in transcript), "scenes": rows},
        ensure_ascii=False, indent=2))
    print(out / "scenes.json")


if __name__ == "__main__":
    main()
