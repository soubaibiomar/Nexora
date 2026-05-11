/**
 * AuthContext — centralizes authentication state and helpers.
 *
 * Provides `isAuthenticated`, `username`, `fullName`, `role`,
 * `isAdmin`, `isManager`, `hasRole`, `login`, and `logout`
 * to any component via the `useAuth()` hook.
 */

import React, { createContext, useContext, useState, useCallback, useMemo, useEffect, type ReactNode } from 'react';

type UserRole = 'user' | 'manager' | 'admin';

interface AuthState {
    isAuthenticated: boolean;
    userId: string;
    username: string;
    fullName: string;
    email: string;
    role: UserRole;
    loading: boolean;
}

interface AuthContextValue extends AuthState {
    /** True when the current user has the admin role. */
    isAdmin: boolean;
    /** True when the current user has the manager OR admin role. */
    isManager: boolean;
    /** Check if the current user has at least the given role level (user < manager < admin). */
    hasRole: (minimumRole: UserRole) => boolean;
    /** Call after a successful login response to persist credentials. */
    login: (token: string, username: string, fullName: string, email: string, role?: string, userId?: string) => void;
    /** Clear all stored credentials and mark user as logged-out. */
    logout: () => void;
}

const ROLE_HIERARCHY: Record<UserRole, number> = {
    user: 0,
    manager: 1,
    admin: 2,
};

const AuthContext = createContext<AuthContextValue>({
    isAuthenticated: false,
    userId: '',
    username: '',
    fullName: '',
    email: '',
    role: 'user',
    loading: true,
    isAdmin: false,
    isManager: false,
    hasRole: () => false,
    login: () => { },
    logout: () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [auth, setAuth] = useState<AuthState>(() => ({
        isAuthenticated: !!localStorage.getItem('token'),
        userId: localStorage.getItem('userId') || '',
        username: localStorage.getItem('username') || '',
        fullName: localStorage.getItem('fullName') || '',
        email: localStorage.getItem('email') || '',
        role: (localStorage.getItem('role') as UserRole) || 'user',
        loading: !!localStorage.getItem('token'), // loading if we have a token to verify
    }));

    // Verify token on mount
    useEffect(() => {
        const verifyToken = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setAuth(prev => ({ ...prev, loading: false }));
                return;
            }

            try {
                const response = await fetch('http://localhost:8000/api/auth/verify', {
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (response.ok) {
                    const data = await response.json();
                    setAuth({
                        isAuthenticated: true,
                        userId: data.user_id || '',
                        username: data.username || '',
                        fullName: data.full_name || '',
                        email: data.email || '',
                        role: (data.role as UserRole) || 'user',
                        loading: false,
                    });
                    // Sync localStorage
                    localStorage.setItem('userId', data.user_id || '');
                    localStorage.setItem('username', data.username || '');
                    localStorage.setItem('fullName', data.full_name || '');
                    localStorage.setItem('email', data.email || '');
                    localStorage.setItem('role', data.role || 'user');
                } else {
                    // Token is invalid/expired
                    localStorage.removeItem('token');
                    localStorage.removeItem('userId');
                    localStorage.removeItem('username');
                    localStorage.removeItem('fullName');
                    localStorage.removeItem('email');
                    localStorage.removeItem('role');
                    setAuth({
                        isAuthenticated: false,
                        userId: '',
                        username: '',
                        fullName: '',
                        email: '',
                        role: 'user',
                        loading: false,
                    });
                }
            } catch {
                // Network error — keep existing state but stop loading
                setAuth(prev => ({ ...prev, loading: false }));
            }
        };

        verifyToken();
    }, []);

    const isAdmin = useMemo(() => auth.role === 'admin', [auth.role]);
    const isManager = useMemo(() => auth.role === 'manager' || auth.role === 'admin', [auth.role]);

    const hasRole = useCallback(
        (minimumRole: UserRole): boolean => {
            return ROLE_HIERARCHY[auth.role] >= ROLE_HIERARCHY[minimumRole];
        },
        [auth.role],
    );

    const login = useCallback((token: string, username: string, fullName: string, email: string, role: string = 'user', userId: string = '') => {
        const safeRole = (['admin', 'manager', 'user'].includes(role) ? role : 'user') as UserRole;
        localStorage.setItem('token', token);
        localStorage.setItem('userId', userId);
        localStorage.setItem('username', username);
        localStorage.setItem('fullName', fullName);
        localStorage.setItem('email', email);
        localStorage.setItem('role', safeRole);
        setAuth({ isAuthenticated: true, userId, username, fullName, email, role: safeRole, loading: false });
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('userId');
        localStorage.removeItem('username');
        localStorage.removeItem('fullName');
        localStorage.removeItem('email');
        localStorage.removeItem('role');
        setAuth({ isAuthenticated: false, userId: '', username: '', fullName: '', email: '', role: 'user', loading: false });
    }, []);

    return (
        <AuthContext.Provider value={{ ...auth, isAdmin, isManager, hasRole, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
