import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { api, User, LoginRequest, RegisterRequest } from '../services/api';

// Define the shape of our authentication context
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  clearError: () => {},
});

// Props for the AuthProvider component
interface AuthProviderProps {
  children: ReactNode;
}

// Authentication provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Effect to check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      // Check for tokens in localStorage
      const tokens = localStorage.getItem('auth_tokens');
      const hasTokens = !!tokens;
      
      console.log("Checking auth state:", { 
        hasTokens, 
        apiIsAuthenticated: api.isAuthenticated() 
      });
      
      if (hasTokens && api.isAuthenticated()) {
        try {
          // Attempt to get user data to verify the token is valid
          const userData = await api.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          console.log("User authenticated successfully:", userData.username);
        } catch (err: any) {
          console.error('Error validating authentication:', err);
          
          // If we get a 401 error, the token is invalid or expired
          if (err.response?.status === 401) {
            console.warn("Token is invalid or expired, logging out");
            // Clear invalid tokens
            api.logout();
          }
          
          // Reset authentication state
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        // No tokens or API reports not authenticated
        setUser(null);
        setIsAuthenticated(false);
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const userData = await api.login(credentials);
      setUser(userData);
      setIsAuthenticated(true);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to login. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (userData: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      await api.register(userData);
      // Automatically log in after successful registration
      await login({
        username: userData.username,
        password: userData.password,
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to register. Please try again.';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    api.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  // Clear error function
  const clearError = () => {
    setError(null);
  };

  // Provide the auth context value
  const value = {
    user,
    isAuthenticated: isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Export the context for potential direct access
export default AuthContext;

