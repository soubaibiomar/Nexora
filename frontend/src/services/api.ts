import axios from 'axios';

// ── TypeScript Interfaces ─────────────────────────────────────────
export interface ExpertPayload {
  name?: string;
  email?: string;
  department?: string;
  role?: string;
  location?: string;
  experience_years?: number;
  expertise_level?: number;
}

export interface ExpertCreatePayload {
  name: string;
  email: string;
  department: string;
  role: string;
  location: string;
  experience_years: number;
  expertise_level: number;
}

export interface DocumentPayload {
  title?: string;
  type?: string;
  topic?: string;
  author?: string;
  date?: string | null;
  views?: number;
  rating?: number;
  content?: string | null;
}

export interface DocumentCreatePayload {
  title: string;
  type: string;
  topic: string;
  author: string;
  date?: string | null;
  views: number;
  rating: number;
  content?: string | null;
}

// Generic params record used by the serializer
type ParamsRecord = Record<string, string | number | boolean | string[] | undefined | null>;

// ── Axios Setup ───────────────────────────────────────────────────
const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    serialize: (params: ParamsRecord) => {
      const searchParams = new URLSearchParams();

      Object.entries(params).forEach(([key, value]) => {
        if (value === undefined || value === null) {
          return;
        }

        if (Array.isArray(value)) {
          value.forEach((v) => {
            searchParams.append(key, String(v));
          });
        } else {
          searchParams.append(key, String(value));
        }
      });

      return searchParams.toString();
    },
  },
});

// Request interceptor to add the auth token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authService = {
  login: (credentials: FormData) => axios.post(`${API_BASE_URL}/auth/login`, credentials),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  },
  isAuthenticated: () => !!localStorage.getItem('token'),
};

// Expert endpoints
export const expertService = {
  search: (params: {
    skill?: string;
    skills?: string[];
    level?: number;
    location?: string;
    department?: string;
    experience?: number;
    limit?: number;
    skip?: number;
  }) => api.get('/experts/search', { params }),

  getById: (id: string) => api.get(`/experts/${id}`),

  getNetwork: (id: string, hops?: number) =>
    api.get(`/experts/${id}/network`, { params: { hops } }),

  update: (id: string, data: ExpertPayload) => api.put(`/experts/${id}`, data),

  create: (data: ExpertCreatePayload) => api.post('/experts', data),

  delete: (id: string) => api.delete(`/experts/${id}`),

  getLocations: () => api.get('/experts/locations/list'),
  getDepartments: () => api.get('/experts/departments/list'),
};

// Document endpoints
export const documentService = {
  search: (params: {
    q?: string;
    type?: string;
    topic?: string;
    min_rating?: number;
    limit?: number;
    skip?: number;
  }) => api.get('/documents/search', { params }),

  getById: (id: string) => api.get(`/documents/${id}`),

  getSimilar: (id: string, limit?: number) =>
    api.get(`/documents/similar/${id}`, { params: { limit } }),

  getTypes: () => api.get('/documents/types/list'),

  getExperts: (id: string) => api.get(`/documents/experts/${id}`),

  create: (payload: DocumentCreatePayload) => api.post('/documents', payload),

  update: (id: string, payload: DocumentPayload) => api.put(`/documents/${id}`, payload),

  delete: (id: string) => api.delete(`/documents/${id}`),
};

// Graph endpoints
export const graphService = {
  getNodes: (nodeType?: string, limit?: number, q?: string) =>
    api.get('/graph/nodes', { params: { node_type: nodeType, limit, q } }),

  expand: (nodeId: string, hops?: number) =>
    api.get(`/graph/expand/${nodeId}`, { params: { hops } }),

  findPath: (fromId: string, toId: string) =>
    api.get('/graph/path', { params: { from_id: fromId, to_id: toId } }),

  getStats: () => api.get('/graph/stats'),

  // User-scoped network graph
  getMyNetwork: () => api.get('/graph/my-network'),

  // View requests for 2nd-degree connections
  requestViewConnections: (connectionId: string) =>
    api.post('/graph/view-request', { connection_id: connectionId }),

  getViewRequests: () => api.get('/graph/view-requests'),

  simulateResponse: (requestId: string, approve: boolean = true) =>
    api.post(`/graph/view-request/${requestId}/simulate-response`, null, { params: { approve } }),
};

// Learning endpoints
export const learningService = {
  generatePath: (currentSkills: string[], targetSkill: string) =>
    api.post('/learning/path', { current_skills: currentSkills, target_skill: targetSkill }),

  getMentors: (skill: string, limit?: number) =>
    api.get(`/learning/mentors/${skill}`, { params: { limit } }),

  getRecommendedSkills: (current: string[], limit: number = 5) =>
    api.get('/learning/skills/recommended', { params: { current_skills: current, limit } }),
  getSkills: () => api.get('/learning/skills/list'),
};

// Learning Resources Pipeline (YouTube + W3Schools)
export const learningResourcesService = {
  getSkills: () => api.get('/learning-resources/skills'),

  getBySkill: (skill: string, level?: string, source?: string) =>
    api.get(`/learning-resources/by-skill/${encodeURIComponent(skill)}`, { params: { level, source } }),

  search: (q: string, level?: string, source?: string, limit?: number) =>
    api.get('/learning-resources/search', { params: { q, level, source, limit } }),

  recommend: (currentSkills: string[], interests: string[], level?: string, limit?: number) =>
    api.get('/learning-resources/recommend', { params: { current_skills: currentSkills, interests, level, limit } }),

  getAll: (level?: string, limit?: number) =>
    api.get('/learning-resources/all', { params: { level, limit } }),
};

// Dashboard endpoints
export const dashboardService = {
  getStats: () => api.get('/dashboard/stats'),
  getTopSkills: (limit?: number) => api.get('/dashboard/top-skills', { params: { limit } }),
  getSkillGaps: (limit?: number) => api.get('/dashboard/skill-gaps', { params: { limit } }),
  getDepartments: () => api.get('/dashboard/departments'),
  getSkillDistribution: () => api.get('/dashboard/skill-distribution'),
  getProjectStatus: () => api.get('/dashboard/project-status'),
  getCollaborationRate: () => api.get('/dashboard/collaboration-rate'),
  getKnowledgeSilos: () => api.get('/dashboard/knowledge-silos'),
};

// AI/ML endpoints
export const aiService = {
  recommendExperts: (query: string, topK: number = 10) =>
    api.post('/ai/recommend-experts', { query, top_k: topK }),

  findSimilarExperts: (expertId: string, topK: number = 5) =>
    api.get(`/ai/similar-experts/${expertId}`, { params: { top_k: topK } }),

  classifyDocument: (title: string, content: string = '') =>
    api.post('/ai/classify-document', { title, content }),

  getClassificationReport: () => api.get('/ai/classification-report'),

  getSkillGaps: (expertId: string, topK: number = 8) =>
    api.get(`/ai/skill-gaps/${expertId}`, { params: { top_k: topK } }),

  getSkillTrends: () => api.get('/ai/skill-trends'),

  chat: (message: string, conversationId?: string) =>
    api.post('/ai/chatbot', { message, conversation_id: conversationId }),

  textSimilarity: (text1: string, text2: string) =>
    api.post('/ai/text-similarity', { text1, text2 }),

  getModelStats: () => api.get('/ai/model-stats'),

  trainAll: () => api.post('/ai/train-all'),

  // Advanced AI endpoints
  getEmergingSkills: () => api.get('/ai/emerging-skills'),

  getFutureSkills: (months: number = 12) =>
    api.get('/ai/future-skills', { params: { months } }),

  getExpertRank: (q?: string, department?: string, topK: number = 20) =>
    api.get('/ai/expert-rank', { params: { q, department, top_k: topK } }),

  getCrossDepartmentSuggestions: () => api.get('/ai/cross-department-suggestions'),

  getPersonalizedRecommendations: (userId: string, topK: number = 8) =>
    api.get(`/ai/personalized-recommendations/${userId}`, { params: { top_k: topK } }),
};

// Big Data / Spark endpoints
export const bigdataService = {
  getSkillAnalytics: () => api.get('/bigdata/skill-analytics'),
  getDocumentStats: () => api.get('/bigdata/document-stats'),
  getExpertRankings: (limit: number = 20) =>
    api.get('/bigdata/expert-rankings', { params: { limit } }),
  getPipelineStatus: () => api.get('/bigdata/pipeline-status'),
};

// Pipeline / Kafka simulation endpoints
export const pipelineService = {
  getStatus: () => api.get('/pipeline/status'),
  getMetrics: () => api.get('/pipeline/metrics'),
  simulate: (count: number = 50) =>
    api.post('/pipeline/simulate', null, { params: { count } }),
};

// Feed endpoints
export const feedService = {
  getFeed: (skip: number = 0, limit: number = 10) =>
    api.get('/feed', { params: { skip, limit } }),
  createPost: (content: string, post_type: string = 'text') =>
    api.post('/feed/posts', { content, post_type }),
  createPostWithMedia: (content: string, files: File[], post_type: string = 'text', author_name: string = 'You') => {
    const formData = new FormData();
    formData.append('content', content);
    formData.append('post_type', post_type);
    formData.append('author_name', author_name);
    files.forEach((file) => formData.append('files', file));
    return api.post('/feed/posts/with-media', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  likePost: (postId: string) =>
    api.post(`/feed/posts/${postId}/like`, { user_id: 'current_user' }),
  commentPost: (postId: string, content: string) =>
    api.post(`/feed/posts/${postId}/comment`, { content, author_name: 'You' }),
};

// Network endpoints
export const networkService = {
  getSuggestions: (limit: number = 12) =>
    api.get('/network/suggestions', { params: { limit } }),
  getConnections: (skip: number = 0, limit: number = 20) =>
    api.get('/network/connections', { params: { skip, limit } }),
  getPending: () => api.get('/network/pending'),
  connect: (targetId: string, message: string = '') =>
    api.post('/network/connect', { target_id: targetId, message }),
  acceptRequest: (requestId: string) =>
    api.post(`/network/accept/${requestId}`),
  getStats: () => api.get('/network/stats'),
};

// Messaging endpoints
export const messagingService = {
  getConversations: () => api.get('/messaging/conversations'),
  getMessages: (conversationId: string) =>
    api.get(`/messaging/conversations/${conversationId}`),
  sendMessage: (conversationId: string, content: string) =>
    api.post('/messaging/send', { conversation_id: conversationId, content }),
};

// Jobs endpoints
export const jobsService = {
  getJobs: (params?: {
    department?: string;
    location?: string;
    job_type?: string;
    level?: string;
    q?: string;
  }) => api.get('/jobs', { params }),
  getRecommended: () => api.get('/jobs/recommended'),
  getJob: (id: string) => api.get(`/jobs/${id}`),
  applyToJob: (id: string, coverLetter: string = '') =>
    api.post(`/jobs/${id}/apply`, { cover_letter: coverLetter }),
};

// Notifications endpoints
export const notificationService = {
  getNotifications: (unreadOnly: boolean = false) =>
    api.get('/notifications', { params: { unread_only: unreadOnly } }),
  markRead: (id: string) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
};

// Company endpoints
export const companyService = {
  getAll: (params?: { industry?: string; size?: string; limit?: number }) =>
    api.get('/bigdata/companies', { params }),
  getById: (id: string) => api.get(`/bigdata/companies/${id}`),
  getAnalytics: () => api.get('/bigdata/company-analytics'),
};

// Gamification endpoints
export const gamificationService = {
  getBadges: () => api.get('/gamification/badges'),
  getExpertBadges: (expertId: string) => api.get(`/gamification/badges/${expertId}`),
  getExpertEndorsements: (expertId: string) => api.get(`/gamification/endorsements/${expertId}`),
  endorseSkill: (targetExpertId: string, skillName: string) =>
    api.post('/gamification/endorse', { target_expert_id: targetExpertId, skill_name: skillName }),
  getLeaderboard: () => api.get('/gamification/leaderboard'),
};

// Workspace endpoints
export const workspaceService = {
  getAll: () => api.get('/workspaces'),
  create: (data: { name: string; description?: string; member_ids?: string[] }) =>
    api.post('/workspaces', data),
  getById: (id: string) => api.get(`/workspaces/${id}`),
  sendMessage: (id: string, content: string, senderName: string = 'You') =>
    api.post(`/workspaces/${id}/messages`, { content, sender_name: senderName }),
  getProgress: (id: string) => api.get(`/workspaces/${id}/progress`),
  postProgress: (id: string, data: { title: string; description?: string; status?: string }) =>
    api.post(`/workspaces/${id}/progress`, data),
  // Invite / join-by-code
  getInvite: (id: string) => api.get(`/workspaces/${id}/invite`),
  regenerateInvite: (id: string) => api.post(`/workspaces/${id}/invite/regenerate`),
  revokeInvite: (id: string) => api.delete(`/workspaces/${id}/invite`),
  previewByCode: (code: string) => api.get(`/workspaces/join/${encodeURIComponent(code)}/preview`),
  joinByCode: (code: string) => api.post(`/workspaces/join/${encodeURIComponent(code)}`),
  // Call management
  startCall: (id: string, callType: string = 'voice') =>
    api.post(`/workspaces/${id}/call/start`, { call_type: callType }),
  joinCall: (id: string) => api.post(`/workspaces/${id}/call/join`),
  endCall: (id: string) => api.post(`/workspaces/${id}/call/end`),
  getCallStatus: (id: string) => api.get(`/workspaces/${id}/call`),
  simulateJoin: (id: string) => api.post(`/workspaces/${id}/call/simulate-join`),
};

export default api;
