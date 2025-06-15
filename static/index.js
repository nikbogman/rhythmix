class TrackCache {
    constructor() {
        this.trackIds = [];
    }

    getTrackIds() {
        if (this.trackIds.length === 0) {
            const stored = localStorage.getItem('trackIds');
            if (stored) {
                try {
                    this.trackIds = JSON.parse(stored);
                } catch {
                    this.trackIds = [];
                }
            }
        }
        return this.trackIds;
    }

    addTrackId(trackId) {
        if (this.trackIds.indexOf(trackId) !== -1) {
            this.trackIds.splice(index, 1);
        }
        this.trackIds.push(trackId);
        localStorage.setItem('trackIds', JSON.stringify(this.trackIds));
    }
}