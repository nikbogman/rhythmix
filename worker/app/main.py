import ffmpeg

from typing import Literal

import essentia.standard as es
import numpy as np

_base_camelot_map = {
    ("C", "major"): "8B",
    ("C#", "major"): "3B",
    ("D", "major"): "10B",
    ("D#", "major"): "5B",
    ("E", "major"): "12B",
    ("F", "major"): "7B",
    ("F#", "major"): "2B",
    ("G", "major"): "9B",
    ("G#", "major"): "4B",
    ("A", "major"): "11B",
    ("A#", "major"): "6B",
    ("B", "major"): "1B",
    ("C", "minor"): "5A",
    ("C#", "minor"): "12A",
    ("D", "minor"): "7A",
    ("D#", "minor"): "2A",
    ("E", "minor"): "9A",
    ("F", "minor"): "4A",
    ("F#", "minor"): "11A",
    ("G", "minor"): "6A",
    ("G#", "minor"): "1A",
    ("A", "minor"): "8A",
    ("A#", "minor"): "3A",
    ("B", "minor"): "10A",
}

_flat_to_sharp = {
    "Db": "C#",
    "Eb": "D#",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
}


def key_to_camelot(key: str, scale: Literal["minor", "major"]) -> str:
    key_normalized = _flat_to_sharp.get(key, key)
    return _base_camelot_map.get((key_normalized, scale), "Unknown")


def extract_audio_features(audio_bytes: bytes):
    audio = np.frombuffer(audio_bytes, dtype=np.float32)
    key, scale, _ = es.KeyExtractor()(audio)
    bpm, _, _, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)

    return dict(bpm=bpm, key=key, camelot_key=key_to_camelot(key, scale), scale=scale)


def download_audio_bytes_from_url(url: str, duration: int) -> bytes:
    out, _ = (
        ffmpeg.input(url, t=duration)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out

def main():

    url = "" 
    audio_bytes = download_audio_bytes_from_url(url, 30)
    features = extract_audio_features(audio_bytes)
    
    print("Hello from worker!")

    return features

if __name__ == "__main__":
    main()
