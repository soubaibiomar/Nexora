import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Box, Typography, Card, CardContent, TextField, Button, Alert,
    CircularProgress, InputAdornment, IconButton, Chip,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';

// Pre-defined users
const USERS = [
    { email: 'admin@nexora.com', password: 'admin123', username: 'admin', fullName: 'Admin User', role: 'Administrator' },
    { email: 'demo@nexora.com', password: 'demo123', username: 'demo', fullName: 'Demo User', role: 'Developer' },
    { email: 'manager@nexora.com', password: 'manager123', username: 'manager', fullName: 'Sarah Manager', role: 'Engineering Manager' },
];

const Login: React.FC = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        // Simulate network delay
        await new Promise(r => setTimeout(r, 800));

        // Check pre-defined credentials
        const user = USERS.find(
            u => u.email.toLowerCase() === email.toLowerCase() && u.password === password
        );

        // Also allow registered users from localStorage
        const registeredUsers = JSON.parse(localStorage.getItem('nexora_registered_users') || '[]');
        const regUser = registeredUsers.find(
            (u: any) => u.email.toLowerCase() === email.toLowerCase() && u.password === password
        );

        const matchedUser = user || regUser;

        if (matchedUser) {
            localStorage.setItem('token', 'nexora-token-' + Date.now());
            localStorage.setItem('username', matchedUser.username);
            localStorage.setItem('fullName', matchedUser.fullName);
            localStorage.setItem('email', matchedUser.email);
            localStorage.setItem('role', matchedUser.role || 'User');
            navigate('/');
            window.location.reload();
        } else {
            setError('Invalid email or password. Try admin@nexora.com / admin123');
        }
        setLoading(false);
    };

    const quickLogin = (user: typeof USERS[0]) => {
        setEmail(user.email);
        setPassword(user.password);
    };

    return (
        <Box sx={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 50%, #1f1510 100%)',
            p: 2,
        }}>
            <Card sx={{
                width: '100%', maxWidth: 420,
                background: 'linear-gradient(145deg, rgba(249,115,22,0.05), rgba(30,30,30,0.95))',
                border: '1px solid rgba(249,115,22,0.15)',
                backdropFilter: 'blur(20px)',
                borderRadius: 4,
            }}>
                <CardContent sx={{ p: 4 }}>
                    {/* Logo */}
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Box
                            component="img"
                            src="/nexora-logo.png"
                            alt="Nexora"
                            sx={{
                                width: 80, height: 80, mx: 'auto', mb: 2,
                                borderRadius: 3,
                                objectFit: 'contain',
                                filter: 'drop-shadow(0 8px 32px rgba(249,115,22,0.3))',
                            }}
                        />
                        <Typography variant="h4" sx={{ fontWeight: 800, background: 'linear-gradient(135deg, #f97316, #f59e0b, #fbbf24)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
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
                            fullWidth size="small" label="Email" type="email"
                            value={email} onChange={e => setEmail(e.target.value)}
                            required autoFocus
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
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
                            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                        />
                        <Button
                            type="submit" fullWidth variant="contained"
                            disabled={loading || !email || !password}
                            startIcon={loading ? <CircularProgress size={18} sx={{ color: 'white' }} /> : undefined}
                            sx={{
                                py: 1.3, fontWeight: 700, fontSize: '0.95rem', borderRadius: 2.5,
                                background: 'linear-gradient(135deg, #f97316, #ea580c)',
                                boxShadow: '0 4px 20px rgba(249,115,22,0.3)',
                                '&:hover': { background: 'linear-gradient(135deg, #fb923c, #f97316)', transform: 'translateY(-1px)' },
                            }}
                        >
                            {loading ? 'Signing in...' : 'Sign In'}
                        </Button>
                    </form>

                    {/* Quick Login */}
                    <Box sx={{ mt: 3 }}>
                        <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary', textAlign: 'center', mb: 1.5 }}>
                            Quick access with demo accounts:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 0.8, flexWrap: 'wrap', justifyContent: 'center' }}>
                            {USERS.map(u => (
                                <Chip
                                    key={u.email}
                                    label={u.username}
                                    size="small"
                                    onClick={() => quickLogin(u)}
                                    sx={{
                                        cursor: 'pointer', fontSize: '0.7rem', fontWeight: 600,
                                        bgcolor: 'rgba(249,115,22,0.1)', color: '#fb923c',
                                        border: '1px solid rgba(249,115,22,0.2)',
                                        '&:hover': { bgcolor: 'rgba(249,115,22,0.2)' },
                                    }}
                                />
                            ))}
                        </Box>
                    </Box>

                    {/* Register Link */}
                    <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                            Don't have an account?{' '}
                            <Link to="/register" style={{ color: '#f97316', fontWeight: 600, textDecoration: 'none' }}>
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
