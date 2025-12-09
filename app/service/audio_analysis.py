from typing import Literal
from numpy import np
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


def analyze_audio(audio_bytes: bytes):
    audio = np.frombuffer(audio_bytes, dtype=np.float32)
    key, scale = es.KeyExtractor()(audio)
    bpm, _, _, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)

    return dict(bpm=bpm, key=key, chamelot_key=key_to_camelot(key, scale), scale=scale)
