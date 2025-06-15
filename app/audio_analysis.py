from typing import Literal
import ffmpeg
import numpy as np
import essentia.standard as es

camelot_map = {
    ("C", "major"): "8B",
    ("C#", "major"): "3B",
    ("Db", "major"): "3B",
    ("D", "major"): "10B",
    ("D#", "major"): "5B",
    ("Eb", "major"): "5B",
    ("E", "major"): "12B",
    ("F", "major"): "7B",
    ("F#", "major"): "2B",
    ("Gb", "major"): "2B",
    ("G", "major"): "9B",
    ("G#", "major"): "4B",
    ("Ab", "major"): "4B",
    ("A", "major"): "11B",
    ("A#", "major"): "6B",
    ("Bb", "major"): "6B",
    ("B", "major"): "1B",
    ("C", "minor"): "5A",
    ("C#", "minor"): "12A",
    ("Db", "minor"): "12A",
    ("D", "minor"): "7A",
    ("D#", "minor"): "2A",
    ("Eb", "minor"): "2A",
    ("E", "minor"): "9A",
    ("F", "minor"): "4A",
    ("F#", "minor"): "11A",
    ("Gb", "minor"): "11A",
    ("G", "minor"): "6A",
    ("G#", "minor"): "1A",
    ("Ab", "minor"): "1A",
    ("A", "minor"): "8A",
    ("A#", "minor"): "3A",
    ("Bb", "minor"): "3A",
    ("B", "minor"): "10A",
}


def key_to_camelot(key: str, scale: Literal["minor", "major"]):
    return camelot_map.get((key, scale), "Unknown")


def download_audio_segment(url: str, duration_sec: int = 60):
    out, _ = (
        ffmpeg.input(url, t=duration_sec)
        .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=44100)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return np.frombuffer(out, dtype=np.float32)


def analyze_audio(audio: np.ndarray):
    key, scale, strength = es.KeyExtractor()(audio)
    bpm, _, _, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)
    return {
        "bpm": bpm,
        "key": key,
        "scale": scale,
        "camelot_key": key_to_camelot(key, scale),
        "strength": strength,
    }
