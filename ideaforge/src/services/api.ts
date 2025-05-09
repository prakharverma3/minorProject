import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// Helper function to decode JWT tokens
function decodeJwt(token: string): any {
  try {
    // Validate token format first
    if (!token || typeof token !== 'string' || !token.includes('.')) {
      console.error('Invalid token format provided:', token ? 'token exists but has invalid format' : 'token is null/undefined');
      return null;
    }

    // Split the token and get the payload part
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Invalid JWT token format: token must have 3 parts');
      return null;
    }

    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    
    try {
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          })
          .join('')
      );
      
      const parsed = JSON.parse(jsonPayload);
      if (!parsed || typeof parsed !== 'object') {
        throw new Error('Token payload is not a valid JSON object');
      }
      return parsed;
    } catch (decodeError) {
      console.error('Error decoding token payload:', decodeError);
      return null;
    }
  } catch (error) {
    console.error('Error decoding JWT token:', error);
    return null;
  }
}

// Define API types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  bio?: string;
  profile_image_url?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  bio?: string;
  profile_image_url?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UpdateUserRequest {
  full_name?: string;
  bio?: string;
  profile_image_url?: string;
  email?: string;
}

export interface Project {
  id: number;
  title: string;
  summary: string;
  description: string;
  category: string;
  github_link?: string;
  skills_needed?: string;
  tags: string[];
  progress: number;
  is_completed: boolean;
  is_active: boolean;
  creator_id: number;
  creator: User;
  collaborators: User[];
  created_at: string;
  updated_at?: string;
}

export interface CreateProjectRequest {
  title: string;
  summary: string;
  description: string;
  category: string;
  github_link?: string;
  skills_needed?: string;
  tags?: string[];
}

export interface UpdateProjectRequest {
  title?: string;
  summary?: string;
  description?: string;
  category?: string;
  github_link?: string;
  skills_needed?: string;
  tags?: string[];
  progress?: number;
  is_completed?: boolean;
  is_active?: boolean;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CollaborationRequest {
  id: number;
  user_id: number;
  project_id: number;
  message?: string;
  role?: string;
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  updated_at?: string;
  responded_at?: string;
  user?: User;
  project?: {
    id: number;
    title: string;
    category: string;
  };
}

export interface CreateCollaborationRequest {
  project_id: number;
  message?: string;
  role?: string;
}

export interface UpdateCollaborationRequest {
  status: 'accepted' | 'rejected';
  response_message?: string;
}

export interface CollaborationRequestListResponse {
  requests: CollaborationRequest[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaperRecommendation {
  title: string;
  score: number;
  arxiv_id?: string;
  url?: string;
}

export interface RecommendationRequest {
  text: string;
  max_results?: number;
}

export interface RecommendationResponse {
  query: string;
  recommendations: PaperRecommendation[];
  count: number;
}

// API configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create the API class
class API {
  private api: AxiosInstance;
  private authTokens: AuthTokens | null = null;

  // Helper method to check if token is expired
  private isTokenExpired(token: string): boolean {
    try {
      if (!token || typeof token !== 'string') {
        console.warn("Invalid token format provided to isTokenExpired");
        return true;
      }

      const payload = decodeJwt(token);
      if (!payload || !payload.exp) {
        console.warn("Token doesn't have an expiration claim or couldn't be decoded");
        return true;
      }
      
      // Add a small buffer (30 seconds) to refresh slightly before expiration
      const currentTime = Math.floor(Date.now() / 1000) + 30;
      const isExpired = payload.exp < currentTime;
      
      // Log expiration details for debugging
      if (isExpired) {
        console.warn(`Token is expired. Expiration: ${new Date(payload.exp * 1000).toISOString()}, Current: ${new Date(currentTime * 1000).toISOString()}`);
      }
      
      return isExpired;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  }
  
  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to add auth token to requests
    this.api.interceptors.request.use(
      async (config) => {
        // Skip token check for login and register endpoints
        const isAuthEndpoint = config.url?.includes('/auth/login') || config.url?.includes('/auth/register');
        if (isAuthEndpoint) {
          return config;
        }
        
        const tokens = this.getTokensFromStorage();
        
        if (tokens && config.headers) {
          // Ensure Authorization header is properly formatted
          const formatAuthHeader = (token_type: string, token: string): string => {
            // Normalize token type to ensure 'Bearer' is properly capitalized
            const formattedType = token_type.charAt(0).toUpperCase() + token_type.slice(1).toLowerCase();
            return `${formattedType} ${token}`;
          };
          
          // Check if access token is expired or will expire soon
          if (this.isTokenExpired(tokens.access_token)) {
            console.log('Access token expired or expiring soon, attempting refresh');
            
            // Don't try to refresh token when already requesting a refresh
            if (config.url?.includes('/auth/refresh')) {
              console.log('Skipping token refresh for refresh token request');
              // Use refresh token for refresh requests
              config.headers['Authorization'] = formatAuthHeader(tokens.token_type, tokens.refresh_token);
            } else {
              try {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                  console.log('Token refreshed successfully');
                  // Get the new tokens after refresh
                  const newTokens = this.getTokensFromStorage();
                  if (newTokens) {
                    config.headers['Authorization'] = formatAuthHeader(newTokens.token_type, newTokens.access_token);
                  }
                } else {
                  console.warn('Token refresh failed, clearing auth state');
                  this.clearTokensFromStorage();
                  // Allow request to proceed without token, server will reject with 401
                }
              } catch (error) {
                console.error('Error during token refresh:', error);
                this.clearTokensFromStorage();
              }
            }
          } else {
            // Token is still valid
            config.headers['Authorization'] = formatAuthHeader(tokens.token_type, tokens.access_token);
            
            // Debug log for all authenticated requests
            console.log(`Setting authorization header for ${config.url}`);
          }
        } else if (!isAuthEndpoint) {
          console.warn(`No auth tokens available for authenticated request: ${config.url}`);
        }
        
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          console.log("Received 401 error, attempting token refresh:", {
            url: originalRequest.url,
            hasAuthTokens: !!this.authTokens,
            hasRefreshToken: !!this.authTokens?.refresh_token
          });
          
          originalRequest._retry = true;
          try {
            const refreshed = await this.refreshToken();
            if (refreshed) {
              console.log("Token refresh successful, retrying request");
              return this.api(originalRequest);
            } else {
              console.warn("Token refresh failed but didn't throw an error");
              this.logout();
            }
          } catch (refreshError) {
            // If refresh fails, log out the user
            console.error("Token refresh failed with error:", refreshError);
            this.logout();
          }
        } else if (error.response?.status === 401) {
          console.warn("Authentication error but not attempting refresh (retry already attempted)");
        } else if (error.response?.status === 403) {
          console.error("Permission denied (403 Forbidden):", error.config?.url);
        }
        return Promise.reject(error);
      }
    );

    // Load tokens from storage on initialization
    this.loadTokensFromStorage();
  }

  // Helper method to determine if user is authenticated
  public isAuthenticated(): boolean {
    return !!this.authTokens;
  }

  // Token management methods
  private getTokensFromStorage(): AuthTokens | null {
    try {
      const tokensJson = localStorage.getItem('auth_tokens');
      if (!tokensJson) {
        return null;
      }
      
      const tokens = JSON.parse(tokensJson);
      
      // Validate token structure
      if (!tokens || typeof tokens !== 'object') {
        console.error('Invalid token format in storage');
        localStorage.removeItem('auth_tokens');
        return null;
      }
      
      // Validate required fields
      if (!tokens.access_token || !tokens.refresh_token || !tokens.token_type) {
        console.error('Missing required token fields in storage');
        localStorage.removeItem('auth_tokens');
        return null;
      }
      
      return tokens;
    } catch (error) {
      console.error('Error parsing tokens from storage:', error);
      localStorage.removeItem('auth_tokens');
      return null;
    }
  }

  private saveTokensToStorage(tokens: AuthTokens): void {
    try {
      // Ensure token has all required fields
      if (!tokens.access_token || !tokens.refresh_token || !tokens.token_type) {
        console.error('Attempting to save incomplete token data:', tokens);
        throw new Error('Invalid token data');
      }
      
      // Normalize token type to ensure consistent format
      tokens.token_type = tokens.token_type.charAt(0).toUpperCase() + tokens.token_type.slice(1).toLowerCase();
      
      localStorage.setItem('auth_tokens', JSON.stringify(tokens));
      this.authTokens = tokens;
      
      console.log('Tokens saved successfully to storage');
    } catch (error) {
      console.error('Error saving tokens to storage:', error);
    }
  }

  private loadTokensFromStorage(): void {
    this.authTokens = this.getTokensFromStorage();
    console.log('Loaded tokens from storage:', this.authTokens ? 'Found' : 'Not found');
  }

  private clearTokensFromStorage(): void {
    localStorage.removeItem('auth_tokens');
    this.authTokens = null;
    console.log('Tokens cleared from storage');
  }

  private async refreshToken(): Promise<boolean> {
    if (!this.authTokens?.refresh_token) {
      console.warn("No refresh token available");
      return false;
    }
    
    // Check if refresh token is expired
    if (this.isTokenExpired(this.authTokens.refresh_token)) {
      console.warn("Refresh token is expired, cannot refresh");
      this.clearTokensFromStorage();
      return false;
    }
    
    try {
      const response = await axios.post<AuthTokens>(
        `${API_URL}/auth/refresh`,
        { token: this.authTokens.refresh_token },
        { headers: { 'Content-Type': 'application/json' } }
      );
      
      if (response.data?.access_token) {
        console.log("Token refresh successful, saving new tokens");
        this.saveTokensToStorage(response.data);
        return true;
      } else {
        console.error("Token refresh response missing access_token", response.data);
        this.clearTokensFromStorage();
        return false;
      }
    } catch (error: any) {
      console.error("Error refreshing token:", error.message);
      if (error.response) {
        console.error("Server response:", error.response.status, error.response.data);
      }
      this.clearTokensFromStorage();
      return false;
    }
  }

  // Auth methods
  public async login(credentials: LoginRequest): Promise<User> {
    try {
      console.log(`Attempting login for user: ${credentials.username}`);
      
      // Clear any existing tokens before attempting login
      this.clearTokensFromStorage();
      
      const response = await this.api.post<AuthTokens>('/auth/login', credentials);
      
      // Validate token response
      if (!response.data || !response.data.access_token || !response.data.refresh_token) {
        console.error('Login response missing required token data:', response.data);
        throw new Error('Invalid authentication response from server');
      }
      
      console.log('Login successful, saving tokens');
      this.saveTokensToStorage(response.data);
      
      // Validate that tokens were properly saved
      const savedTokens = this.getTokensFromStorage();
      if (!savedTokens) {
        console.error('Failed to save tokens to storage after login');
        throw new Error('Failed to save authentication data');
      }
      
      return this.getCurrentUser();
    } catch (error: any) {
      console.error('Login error:', error.message);
      if (error.response) {
        console.error('Server response:', error.response.status, error.response.data);
      }
      
      // Clear any partial authentication state
      this.clearTokensFromStorage();
      
      // Rethrow with clear message
      if (error.response?.status === 401) {
        throw new Error('Invalid username or password');
      } else if (error.response?.status === 403) {
        throw new Error('Account is locked or inactive');
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      } else {
        throw new Error('Login failed. Please try again later.');
      }
    }
  }

  public async register(userData: RegisterRequest): Promise<User> {
    const response = await this.api.post<User>('/auth/register', userData);
    return response.data;
  }

  public logout(): void {
    console.log('Logging out user and clearing authentication state');
    this.clearTokensFromStorage();
  }

  public async getCurrentUser(): Promise<User> {
    try {
      console.log('Fetching current user profile');
      
      if (!this.isAuthenticated()) {
        console.error('Attempting to get current user while not authenticated');
        throw new Error('Not authenticated');
      }
      
      const response = await this.api.get<User>('/auth/me');
      
      if (!response.data || !response.data.id) {
        console.error('Invalid user data received:', response.data);
        throw new Error('Invalid user data received from server');
      }
      
      console.log(`Successfully retrieved user profile for ${response.data.username}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching current user:', error.message);
      
      if (error.response?.status === 401) {
        console.warn('Authentication failed when fetching user profile, logging out');
        this.clearTokensFromStorage();
        throw new Error('Your session has expired. Please log in again.');
      }
      
      throw error;
    }
  }

  // User methods
  public async updateUser(userData: UpdateUserRequest): Promise<User> {
    const response = await this.api.put<User>('/users/me', userData);
    return response.data;
  }

  public async getUser(userId: number): Promise<User> {
    const response = await this.api.get<User>(`/users/${userId}`);
    return response.data;
  }

  public async searchUsers(query: string, limit: number = 10): Promise<User[]> {
    const response = await this.api.get<User[]>('/users/search', {
      params: { query, limit },
    });
    return response.data;
  }

  // Project methods
  public async createProject(projectData: CreateProjectRequest): Promise<any> {
    const response = await this.api.post('/projects', projectData);
    return response.data;
  }

  public async getProjects(
    page: number = 1,
    limit: number = 10,
    search?: string,
    category?: string,
    tags?: string
  ): Promise<ProjectListResponse> {
    // Calculate skip value based on page number and limit
    const skip = (page - 1) * limit;
    
    // Check and log auth state for debugging
    const tokens = this.getTokensFromStorage();
    console.log("Auth state during getProjects:", {
      isAuthenticated: this.isAuthenticated(),
      hasTokens: !!tokens,
      tokenType: tokens?.token_type,
      tokenLength: tokens?.access_token?.length || 0,
    });
    
    try {
      console.log("API Request params:", { skip, limit, search, category, tags });
      
      const response = await this.api.get<ProjectListResponse>('/projects', {
        params: {
          skip,
          limit,
          search,
          category,
          tags,
        },
      });
      
      // Log the raw response data for debugging
      console.log("API Raw Response:", response.data);
      
      // Validate response structure
      if (!response.data.projects || !Array.isArray(response.data.projects)) {
        console.error("Invalid response format - missing projects array:", response.data);
        throw new Error("Invalid response format - missing projects array");
      }
      
      // Process the response data to ensure tags are handled correctly
      const processedResponse: ProjectListResponse = {
        ...response.data,
        projects: response.data.projects.map(project => ({
          ...project,
          // Ensure tags are always in a consistent format
          tags: typeof project.tags === 'string' 
            ? project.tags.split(',').filter(Boolean) 
            : (Array.isArray(project.tags) ? project.tags : [])
        }))
      };
      
      return processedResponse;
    } catch (error: any) {
      console.error("Error in getProjects:", error);
      
      // Additional detailed error logging
      if (error.response) {
        console.error("Response error details:", {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        });
        
        // Handle specific error cases
        if (error.response.status === 401) {
          console.error("Authentication error: User is not authenticated or token is invalid");
          // Clear tokens if there's an authentication error
          if (this.isAuthenticated()) {
            console.warn("Clearing invalid auth tokens");
            this.clearTokensFromStorage();
          }
        }
      } else {
        console.error("Error details:", error.message);
      }
      
      throw error;
    }
  }

  public async getMyProjects(
    page: number = 1,
    limit: number = 10,
    includeCollaborations: boolean = false
  ): Promise<ProjectListResponse> {
    const response = await this.api.get<ProjectListResponse>('/projects/my-projects', {
      params: {
        skip: (page - 1) * limit,
        limit,
        include_collaborations: includeCollaborations,
      },
    });
    return response.data;
  }

  public async getProject(projectId: number): Promise<Project> {
    const response = await this.api.get<Project>(`/projects/${projectId}`);
    return response.data;
  }

  public async updateProject(
    projectId: number,
    projectData: UpdateProjectRequest
  ): Promise<Project> {
    const response = await this.api.put<Project>(`/projects/${projectId}`, projectData);
    return response.data;
  }

  public async deleteProject(projectId: number): Promise<void> {
    await this.api.delete(`/projects/${projectId}`);
  }

  public async addCollaborator(projectId: number, userId: number): Promise<Project> {
    const response = await this.api.post<Project>(
      `/projects/${projectId}/collaborators/${userId}`
    );
    return response.data;
  }

  public async removeCollaborator(projectId: number, userId: number): Promise<Project> {
    const response = await this.api.delete<Project>(
      `/projects/${projectId}/collaborators/${userId}`
    );
    return response.data;
  }

  // Collaboration request methods
  public async createCollaborationRequest(
    requestData: CreateCollaborationRequest
  ): Promise<CollaborationRequest> {
    const response = await this.api.post<CollaborationRequest>(
      '/collaborations',
      requestData
    );
    return response.data;
  }

  public async getSentRequests(
    page: number = 1,
    limit: number = 10,
    status?: 'pending' | 'accepted' | 'rejected'
  ): Promise<CollaborationRequestListResponse> {
    const response = await this.api.get<CollaborationRequestListResponse>('/collaborations/sent', {
      params: {
        skip: (page - 1) * limit,
        limit,
        status,
      },
    });
    return response.data;
  }

  public async getReceivedRequests(
    page: number = 1,
    limit: number = 10,
    status?: 'pending' | 'accepted' | 'rejected'
  ): Promise<CollaborationRequestListResponse> {
    const response = await this.api.get<CollaborationRequestListResponse>(
      '/collaborations/received',
      {
        params: {
          skip: (page - 1) * limit,
          limit,
          status,
        },
      }
    );
    return response.data;
  }

  public async getCollaborationRequest(requestId: number): Promise<CollaborationRequest> {
    const response = await this.api.get<CollaborationRequest>(`/collaborations/${requestId}`);
    return response.data;
  }

  public async updateCollaborationRequest(
    requestId: number,
    requestData: UpdateCollaborationRequest
  ): Promise<CollaborationRequest> {
    const response = await this.api.put<CollaborationRequest>(
      `/collaborations/${requestId}`,
      requestData
    );
    return response.data;
  }

  public async deleteCollaborationRequest(requestId: number): Promise<void> {
    await this.api.delete(`/collaborations/${requestId}`);
  }

  // Recommendation methods
  public async getRecommendations(
    requestData: RecommendationRequest
  ): Promise<RecommendationResponse> {
    const response = await this.api.post<RecommendationResponse>(
      '/recommendations',
      requestData
    );
    return response.data;
  }

  public async getProjectRecommendations(
    projectId: number,
    maxResults: number = 5
  ): Promise<RecommendationResponse> {
    const response = await this.api.get<RecommendationResponse>(
      `/recommendations/project/${projectId}`,
      {
        params: { max_results: maxResults },
      }
    );
    return response.data;
  }
}

// Export a singleton instance
export const api = new API();

