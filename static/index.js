class History {
    constructor() {
        this.history = [];
    }

    get() {
        if (this.history.length === 0) {
            const stored = localStorage.getItem('history');
            if (stored) {
                try {
                    this.history = JSON.parse(stored);
                } catch {
                    this.history = [];
                }
            }
        }
        return this.history;
    }

    push(key) {
        if (this.history.indexOf(key) !== -1) {
            this.history.splice(index, 1);
        }
        this.history.push(key);
        localStorage.setItem('history', JSON.stringify(this.history));
    }
}