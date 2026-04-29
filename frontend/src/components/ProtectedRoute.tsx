/**
 * ProtectedRoute — RBAC wrapper for React Router routes.
 *
 * Usage:
 *   <Route path="/dashboard" element={
 *     <ProtectedRoute requiredRole="manager"><Dashboard /></ProtectedRoute>
 *   } />
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
    children: React.ReactNode;
    /** Minimum role required to access this route. Defaults to 'user'. */
    requiredRole?: 'user' | 'manager' | 'admin';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole = 'user' }) => {
    const { isAuthenticated, hasRole } = useAuth();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (!hasRole(requiredRole)) {
        return <Navigate to="/forbidden" replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
