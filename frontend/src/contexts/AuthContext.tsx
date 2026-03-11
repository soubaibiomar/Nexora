/**
 * AuthContext — centralizes authentication state and helpers.
 *
 * Provides `isAuthenticated`, `username`, `fullName`, `login`, and `logout`
 * to any component via the `useAuth()` hook.
 */

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

interface AuthState {
    isAuthenticated: boolean;
    username: string;
    fullName: string;
}

interface AuthContextValue extends AuthState {
    /** Call after a successful login response to persist credentials. */
    login: (token: string, username: string, fullName: string, email: string) => void;
    /** Clear all stored credentials and mark user as logged-out. */
    logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
    isAuthenticated: false,
    username: '',
    fullName: '',
    login: () => { },
    logout: () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [auth, setAuth] = useState<AuthState>(() => ({
        isAuthenticated: !!localStorage.getItem('token'),
        username: localStorage.getItem('username') || '',
        fullName: localStorage.getItem('fullName') || '',
    }));

    const login = useCallback((token: string, username: string, fullName: string, email: string) => {
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        localStorage.setItem('fullName', fullName);
        localStorage.setItem('email', email);
        setAuth({ isAuthenticated: true, username, fullName });
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('fullName');
        localStorage.removeItem('email');
        setAuth({ isAuthenticated: false, username: '', fullName: '' });
    }, []);

    return (
        <AuthContext.Provider value={{ ...auth, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
