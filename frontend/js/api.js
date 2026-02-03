/**
 * RVSync API Client
 */
const API_BASE = 'http://127.0.0.1:8080';

const api = {
    /**
     * Make authenticated API request
     */
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('rvsync_token');
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('rvsync_token');
                localStorage.removeItem('rvsync_user');
                window.location.href = 'login.html';
                throw new Error('Session expired');
            }
            
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Request failed');
        }
        
        return response.json();
    },

    // Auth endpoints
    async login(email, password) {
        return this.request('/api/auth/login/json', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    },

    async register(data) {
        return this.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getProfile() {
        return this.request('/api/users/profile/me');
    },

    async updateProfile(userId, data) {
        return this.request(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // Classroom endpoints
    async createClassroom(data) {
        return this.request('/api/classroom/create', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getClassroomHub(classroomId) {
        return this.request(`/api/classroom/${classroomId}/hub`);
    },

    async listClassrooms(branch = null, yearLevel = null) {
        let url = '/api/classroom/list/by-branch';
        const params = new URLSearchParams();
        if (branch) params.append('branch', branch);
        if (yearLevel) params.append('year_level', yearLevel);
        if (params.toString()) url += `?${params}`;
        return this.request(url);
    },

    async enrollInClassroom(classroomId) {
        return this.request(`/api/classroom/${classroomId}/enroll`, {
            method: 'POST'
        });
    },

    // Course endpoints
    async getMyCourses() {
        return this.request('/api/classroom/courses/my');
    },

    async getCourseDetail(courseId) {
        return this.request(`/api/classroom/course/${courseId}`);
    },

    async postCourseUpdate(courseId, data) {
        return this.request(`/api/classroom/course/${courseId}/update`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async addMaterial(classroomId, courseId, data) {
        return this.request(`/api/classroom/${classroomId}/course/${courseId}/material/add`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async postAiChat(message, context = {}) {
        return this.request('/api/ai-support/chat', {
            method: 'POST',
            body: JSON.stringify({ message, context })
        });
    },

    // Assignment endpoints
    async submitAssignment(assignmentId, data) {
        return this.request(`/api/classroom/submission/${assignmentId}/submit`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getMySubmission(assignmentId) {
        return this.request(`/api/classroom/submission/${assignmentId}/my`);
    },

    // Test endpoints
    async getTestDetails(testId) {
        return this.request(`/api/test/${testId}/details`);
    },

    async submitTest(testId, answers) {
        return this.request(`/api/test/${testId}/submit`, {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    },

    async getTestResults(userId) {
        return this.request(`/api/test-result/${userId}/all`);
    },

    // Chat endpoints
    async sendMessage(toUserId, message) {
        return this.request('/api/messages/send', {
            method: 'POST',
            body: JSON.stringify({
                to_user_id: toUserId,
                message: message,
                message_type: 'text'
            })
        });
    },

    async getInbox(userId) {
        return this.request(`/api/messages/inbox/${userId}`);
    },

    async getConversation(user1Id, user2Id) {
        return this.request(`/api/messages/conversation/${user1Id}/${user2Id}`);
    },

    // Announcement endpoints
    async createAnnouncement(data) {
        return this.request('/api/announcement/create', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getAnnouncements(classroomId) {
        return this.request(`/api/announcement/list/${classroomId}`);
    },

    async markAnnouncementRead(announcementId) {
        return this.request(`/api/announcement/${announcementId}/read`, {
            method: 'PUT'
        });
    },

    // Career endpoints
    async syncGitHub(userId) {
        return this.request(`/api/sync/github/${userId}`, {
            method: 'POST'
        });
    },

    async getOpportunityMatches(userId) {
        return this.request(`/api/opportunities/match/${userId}`);
    },

    async getCareerPrediction(userId) {
        return this.request(`/api/predict-career/${userId}`);
    },

    async getDashboardMetrics(userId) {
        return this.request(`/api/dashboard/metrics/${userId}`);
    },

    // Skills
    async addSkill(userId, skillData) {
        return this.request(`/api/users/${userId}/skills`, {
            method: 'POST',
            body: JSON.stringify(skillData)
        });
    },

    async getSkills(userId) {
        return this.request(`/api/users/${userId}/skills`);
    },

    // Event endpoints
    async getMyEvents() {
        return this.request('/api/events/my');
    },

    async getUpcomingEvents(limit = 5) {
        return this.request(`/api/events/upcoming?limit=${limit}`);
    },

    async getClassroomEvents(classroomId) {
        return this.request(`/api/events/classroom/${classroomId}`);
    },

    async createEvent(data) {
        return this.request('/api/events/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// WebSocket helper for real-time chat
function createChatWebSocket(fromUserId, toUserId, onMessage) {
    const ws = new WebSocket(`ws://localhost:8080/api/messages/ws/chat/${fromUserId}/${toUserId}`);
    
    ws.onopen = () => console.log('Chat connected');
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
    };
    ws.onerror = (error) => console.error('WebSocket error:', error);
    ws.onclose = () => console.log('Chat disconnected');
    
    return {
        send: (message) => ws.send(JSON.stringify({ message })),
        close: () => ws.close()
    };
}
