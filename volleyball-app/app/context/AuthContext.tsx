import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, ReactNode, useEffect, useState } from 'react';
import { apiClient } from '../api/client';

interface AuthContextType {
  isSignedIn: boolean;
  isLoading: boolean;
  user: any | null;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  signUp: (accessCode: string, password: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType>({
  isSignedIn: false,
  isLoading: true,
  user: null,
  signIn: async () => { },
  signOut: async () => { },
  signUp: async () => { },
});

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useState({
    isLoading: true,
    isSignedIn: false,
    user: null,
  });

  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const token = await AsyncStorage.getItem('authToken');
        const userData = await AsyncStorage.getItem('user');

        if (token && userData) {
          dispatch({
            isLoading: false,
            isSignedIn: true,
            user: JSON.parse(userData),
          });
        } else {
          dispatch({
            isLoading: false,
            isSignedIn: false,
            user: null,
          });
        }
      } catch (e) {
        dispatch({
          isLoading: false,
          isSignedIn: false,
          user: null,
        });
      }
    };

    bootstrapAsync();
  }, []);

  const authContext: AuthContextType = {
    isSignedIn: state.isSignedIn,
    isLoading: state.isLoading,
    user: state.user,
    signIn: async (username: string, password: string) => {
      try {
        const response = await apiClient.login(username, password);
        // Handle both direct response and wrapped response structure
        const loginData = (response && response.data) ? response.data : response;
        const { token, user } = loginData;
        await AsyncStorage.setItem('authToken', token);
        await AsyncStorage.setItem('user', JSON.stringify(user));
        dispatch({
          isLoading: false,
          isSignedIn: true,
          user,
        });
      } catch (error) {
        throw new Error('Invalid credentials');
      }
    },
    signOut: async () => {
      try {
        await apiClient.logout();
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        console.error('Logout error:', errorMsg);
      } finally {
        await AsyncStorage.removeItem('authToken');
        await AsyncStorage.removeItem('user');
        dispatch({
          isLoading: false,
          isSignedIn: false,
          user: null,
        });
      }
    },
    signUp: async (accessCode: string, password: string) => {
      try {
        throw new Error('Signup not yet implemented');
      } catch (error) {
        throw error;
      }
    },
  };

  return (
    <AuthContext.Provider value={authContext}>
      {children}
    </AuthContext.Provider>
  );
}
