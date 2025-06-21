let _history = [];

function getHistory() {
    if (_history.length === 0) {
        const stored = localStorage.getItem('history');
        if (stored) {
            try {
                _history = JSON.parse(stored);
            } catch {
                _history = [];
            }
        }
    }
    return _history;
}

function pushToHistory(key) {
    if (_history.indexOf(key) !== -1) {
        _history.splice(index, 1);
    }
    _history.push(key);
    localStorage.setItem('history', JSON.stringify(_history));
}

const input = document.getElementById('track-input');
const inputFeedback = document.getElementById('track-input-feedback');
const submit = document.getElementById('track-submit');
const tracks = document.getElementById('tracks');

function createTrackComponent({ artwork_url, artist_display, title, full_duration, bpm, key, camelot_key }) {
    const article = document.createElement("article");

    const imgContainer = document.createElement("div");
    imgContainer.className = "img-container";

    const img = document.createElement("img");
    img.src = artwork_url;
    img.width = 150;
    img.height = 150;
    imgContainer.appendChild(img);
    article.appendChild(imgContainer);

    const infoDiv = document.createElement("div");

    const artistP = document.createElement("p");
    artistP.id = "artist";
    artistP.textContent = artist_display;

    const titleP = document.createElement("p");
    titleP.id = "title";
    titleP.textContent = title;

    const durationP = document.createElement("p");
    durationP.id = "duration";
    durationP.textContent = full_duration;

    infoDiv.append(artistP, titleP, durationP);
    article.appendChild(infoDiv);

    const bpmDiv = document.createElement("div");
    const bpmP = document.createElement("p");
    bpmP.textContent = `${bpm} BPM`;
    bpmDiv.appendChild(bpmP);
    article.appendChild(bpmDiv);

    const keyDiv = document.createElement("div");

    const keyP = document.createElement("p");
    keyP.textContent = key;

    const camelotP = document.createElement("p");
    camelotP.textContent = camelot_key;

    keyDiv.append(keyP, camelotP);
    article.appendChild(keyDiv);

    return article;
}

function tryMatchURL() {
    const url = input.value.trim();
    if (!url) {
        return null;
    }
    return url.split('?')[0].match(/^https:\/\/soundcloud\.com\/([^/]+)\/([^/]+)\/?$/) || null;
}


function parseData(track) {
    const copy = { ...track };

    const duration = track["full_duration"];
    const totalSeconds = Math.floor(duration / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    copy["full_duration"] = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    copy["bpm"] = track["bpm"].toFixed(1);

    return copy;
}

async function fetchTrack(trackKey) {
    const response = await fetch(`/track/${trackKey}`, {
        method: 'POST',
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch track ${trackKey}`);
    }

    const data = await response.json();
    return parseData(data);
}

async function handleSubmit(event) {
    event.preventDefault();

    const match = tryMatchURL();
    if (!match) {
        input.setAttribute("aria-invalid", "true");
        inputFeedback.textContent = "Please provide a valid SoundCloud track URL!";
        inputFeedback.style.display = 'block';
        return;
    }

    const [, artist, trackName] = match;
    const trackKey = `${artist}/${trackName}`;

    input.removeAttribute("aria-invalid");
    inputFeedback.style.display = 'none';

    submit.setAttribute("aria-busy", "true");
    submit.disabled = true;

    try {
        const track = await fetchTrack(trackKey);
        tracks.appendChild(createTrackComponent(track));
    } catch (err) {
        console.error(err);

        input.setAttribute("aria-invalid", "true");
        inputFeedback.textContent = err.message;
        inputFeedback.style.display = 'block';
    } finally {
        submit.setAttribute("aria-busy", "false");
        submit.disabled = false;

        input.value = '';

        pushToHistory(trackKey);
    }

}


async function loadTracks() {
    tracks.innerHTML = '';

    const fetchedTracks = await Promise.all(getHistory().map(fetchTrack));


    for (let i = 0; i < fetchedTracks.length; i++) {
        const trackComponent = createTrackComponent(fetchedTracks[i]);
        tracks.insertBefore(trackComponent, tracks.firstChild);
    }
}

loadTracks()