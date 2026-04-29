/**
 * AuthContext — centralizes authentication state and helpers.
 *
 * Provides `isAuthenticated`, `username`, `fullName`, `role`,
 * `isAdmin`, `isManager`, `hasRole`, `login`, and `logout`
 * to any component via the `useAuth()` hook.
 */

import React, { createContext, useContext, useState, useCallback, useMemo, type ReactNode } from 'react';

type UserRole = 'user' | 'manager' | 'admin';

interface AuthState {
    isAuthenticated: boolean;
    username: string;
    fullName: string;
    email: string;
    role: UserRole;
}

interface AuthContextValue extends AuthState {
    /** True when the current user has the admin role. */
    isAdmin: boolean;
    /** True when the current user has the manager OR admin role. */
    isManager: boolean;
    /** Check if the current user has at least the given role level (user < manager < admin). */
    hasRole: (minimumRole: UserRole) => boolean;
    /** Call after a successful login response to persist credentials. */
    login: (token: string, username: string, fullName: string, email: string, role?: string) => void;
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
    username: '',
    fullName: '',
    email: '',
    role: 'user',
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
        username: localStorage.getItem('username') || '',
        fullName: localStorage.getItem('fullName') || '',
        email: localStorage.getItem('email') || '',
        role: (localStorage.getItem('role') as UserRole) || 'user',
    }));

    const isAdmin = useMemo(() => auth.role === 'admin', [auth.role]);
    const isManager = useMemo(() => auth.role === 'manager' || auth.role === 'admin', [auth.role]);

    const hasRole = useCallback(
        (minimumRole: UserRole): boolean => {
            return ROLE_HIERARCHY[auth.role] >= ROLE_HIERARCHY[minimumRole];
        },
        [auth.role],
    );

    const login = useCallback((token: string, username: string, fullName: string, email: string, role: string = 'user') => {
        const safeRole = (['admin', 'manager', 'user'].includes(role) ? role : 'user') as UserRole;
        localStorage.setItem('token', token);
        localStorage.setItem('username', username);
        localStorage.setItem('fullName', fullName);
        localStorage.setItem('email', email);
        localStorage.setItem('role', safeRole);
        setAuth({ isAuthenticated: true, username, fullName, email, role: safeRole });
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('fullName');
        localStorage.removeItem('email');
        localStorage.removeItem('role');
        setAuth({ isAuthenticated: false, username: '', fullName: '', email: '', role: 'user' });
    }, []);

    return (
        <AuthContext.Provider value={{ ...auth, isAdmin, isManager, hasRole, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
