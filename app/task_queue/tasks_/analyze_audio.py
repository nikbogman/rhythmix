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


@celery_app.task
def analyze_audio_task(audio_bytes: bytes):
    # load audio from redis

    audio = np.frombuffer(audio_bytes, dtype=np.float32)
    key, scale = es.KeyExtractor()(audio)
    bpm, _, _, _, _ = es.RhythmExtractor2013(method="multifeature")(audio)

    return dict(bpm=bpm, key=key, camelot_key=key_to_camelot(key, scale), scale=scale)
