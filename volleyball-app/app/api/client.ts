import AsyncStorage from '@react-native-async-storage/async-storage';
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import * as mockData from './mockData';

const API_BASE_URL = 'http://127.0.0.1:8000/api';
const USE_MOCK_DATA = true; // Set to true to use mock data when backend is unavailable

interface LoginResponse {
  token: string;
  user: any;
  profile?: any;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });

    // Request interceptor - add token to all requests
    this.client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
      const token = await AsyncStorage.getItem('authToken');
      if (token) {
        // Use Token format (not Bearer) for DRF token auth
        config.headers.Authorization = `Token ${token}`;
      }
      return config;
    });

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response.data as any,
      (error) => {
        if (error.response?.status === 401) {
          // Clear token on unauthorized
          AsyncStorage.removeItem('authToken');
        }
        // If USE_MOCK_DATA is true, return mock data on error
        if (USE_MOCK_DATA && error.config?.url) {
          console.log(`Backend unavailable, using mock data for: ${error.config.url}`);
          return this.getMockDataForEndpoint(error.config.url);
        }
        throw error.response?.data || error;
      }
    );
  }

  private getMockDataForEndpoint(url: string): any {
    if (url.includes('/login/')) return mockData.MOCK_LOGIN_RESPONSE;
    if (url.includes('/player/profile/')) return mockData.MOCK_PLAYER_PROFILE;
    if (url.includes('/player/stats/')) return mockData.MOCK_PLAYER_STATS;
    if (url.includes('/player/summary/')) return mockData.MOCK_AI_SUMMARY;
    if (url.includes('/announcements/')) return mockData.MOCK_ANNOUNCEMENTS;
    if (url.includes('/videos/')) return mockData.MOCK_VIDEOS;
    return null;
  }

  // Authentication endpoints
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/login/', {
      username,
      password
    });
    return response as any;
  }

  async logout() {
    return this.client.post('/logout/');
  }

  // Player profile endpoints
  async getPlayerProfile(): Promise<any> {
    const response = await this.client.get('/player/profile/');
    // Ensure consistent response structure
    if (response && typeof response === 'object') {
      return { data: response };
    }
    return response;
  }

  async getPlayerStats(): Promise<any> {
    const response = await this.client.get('/player/stats/');
    // Ensure consistent response structure
    if (response && typeof response === 'object') {
      return { data: response };
    }
    return response;
  }

  async getAISummary(): Promise<any> {
    const response = await this.client.get('/player/summary/');
    // Ensure consistent response structure
    if (response && typeof response === 'object') {
      return { data: response };
    }
    return response;
  }

  // Team endpoints
  async getAnnouncements(): Promise<any> {
    const response = await this.client.get('/announcements/');
    // Announcements should always be an array or wrapped in data
    if (Array.isArray(response)) {
      return { data: response };
    }
    if (response && response.results) {
      return { data: response.results };
    }
    return { data: response || [] };
  }

  async getGameVideos(): Promise<any> {
    const response = await this.client.get('/videos/');
    // Videos should always be an array or wrapped in data
    if (Array.isArray(response)) {
      return { data: response };
    }
    if (response && response.results) {
      return { data: response.results };
    }
    return { data: response || [] };
  }
}

export const apiClient = new APIClient();
