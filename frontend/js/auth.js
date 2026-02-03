/**
 * RVSync Auth Utilities
 */
const auth = {
    TOKEN_KEY: 'rvsync_token',
    USER_KEY: 'rvsync_user',

    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    setUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    getUser() {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        window.location.href = 'login.html';
    },

    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    },

    getUserInitials() {
        const user = this.getUser();
        if (!user || !user.name) return '?';
        return user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
};
