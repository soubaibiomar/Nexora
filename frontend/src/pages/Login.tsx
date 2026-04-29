import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Box, Typography, Card, CardContent, TextField, Button, Alert,
    CircularProgress, InputAdornment, IconButton,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import { useAuth } from '../contexts/AuthContext';



/** Redirect destination based on user role after login. */
function getRedirectForRole(role: string): string {
    switch (role) {
        case 'admin':
        case 'manager':
            return '/dashboard';
        default:
            return '/';
    }
}

const Login: React.FC = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Client-side validation
        const trimmedUser = username.trim();
        if (!trimmedUser) {
            setError('Please enter your username.');
            return;
        }
        if (!password) {
            setError('Please enter your password.');
            return;
        }

        setLoading(true);

        try {
            const formData = new URLSearchParams();
            formData.append('username', trimmedUser);
            formData.append('password', password);

            const response = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => null);
                const detail = errData?.detail || 'Invalid credentials. Please try again.';
                setError(detail);
                setLoading(false);
                return;
            }

            const data = await response.json();
            const role = data.role || 'user';
            login(data.access_token, data.username, data.full_name, data.email, role);
            navigate(getRedirectForRole(role), { replace: true });
        } catch {
            setError('Unable to connect to the server. Please make sure the backend is running.');
        }
        setLoading(false);
    };


    return (
        <Box sx={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'linear-gradient(135deg, #0a0a1a 0%, #141428 50%, #1a1040 100%)',
            p: 2,
        }}>
            <Card sx={{
                width: '100%', maxWidth: 420,
                background: 'linear-gradient(145deg, rgba(108,99,255,0.06), rgba(20,20,40,0.95))',
                border: '1px solid rgba(108,99,255,0.15)',
                backdropFilter: 'blur(20px)',
                borderRadius: 4,
            }}>
                <CardContent sx={{ p: 4 }}>
                    {/* Logo */}
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Box sx={{
                            width: 72, height: 72, mx: 'auto', mb: 2,
                            borderRadius: 3,
                            background: 'linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 8px 32px rgba(108,99,255,0.35)',
                        }}>
                            <Typography sx={{ color: '#fff', fontWeight: 900, fontSize: '2rem' }}>N</Typography>
                        </Box>
                        <Typography variant="h4" sx={{
                            fontWeight: 800,
                            background: 'linear-gradient(135deg, #E8E8F0, #A78BFA)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                        }}>
                            Nexora
                        </Typography>
                        <Typography color="text.secondary" sx={{ fontSize: '0.85rem', mt: 0.5 }}>
                            Sign in to your workspace
                        </Typography>
                    </Box>

                    {/* Error */}
                    {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

                    {/* Form */}
                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth size="small" label="Username"
                            value={username} onChange={e => setUsername(e.target.value)}
                            required autoFocus
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Password"
                            type={showPassword ? 'text' : 'password'}
                            value={password} onChange={e => setPassword(e.target.value)}
                            required
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><LockIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton size="small" onClick={() => setShowPassword(!showPassword)}>
                                            {showPassword ? <VisibilityOffIcon sx={{ fontSize: 18 }} /> : <VisibilityIcon sx={{ fontSize: 18 }} />}
                                        </IconButton>
                                    </InputAdornment>
                                ),
                            }}
                            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <Button
                            type="submit" fullWidth variant="contained"
                            disabled={loading || !username || !password}
                            startIcon={loading ? <CircularProgress size={18} sx={{ color: 'white' }} /> : undefined}
                            sx={{
                                py: 1.3, fontWeight: 700, fontSize: '0.95rem', borderRadius: 2.5,
                                background: 'linear-gradient(135deg, #6C63FF, #5A52D5)',
                                boxShadow: '0 4px 20px rgba(108,99,255,0.3)',
                                '&:hover': { background: 'linear-gradient(135deg, #8B83FF, #6C63FF)', transform: 'translateY(-1px)' },
                            }}
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                        </Button>
                    </form>


                    {/* Register Link */}
                    <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                            Don't have an account?{' '}
                            <Link to="/register" style={{ color: '#A78BFA', fontWeight: 600, textDecoration: 'none' }}>
                                Create one
                            </Link>
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default Login;
