import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Box, Typography, Card, CardContent, TextField, Button, Alert,
    CircularProgress, InputAdornment, IconButton, Tabs, Tab,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState(0); // 0 = Email login, 1 = Admin login

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        const trimmedId = identifier.trim();
        if (!trimmedId) {
            setError(tab === 0 ? 'Please enter your email address.' : 'Please enter admin username.');
            return;
        }
        if (tab === 0 && !trimmedId.includes('@')) {
            setError('Please enter a valid email address.');
            return;
        }
        if (!password) {
            setError('Please enter your password.');
            return;
        }

        setLoading(true);

        try {
            const response = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    identifier: trimmedId,
                    password,
                }),
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
            login(data.access_token, data.username, data.full_name, data.email, role, data.user_id);
            navigate('/dashboard', { replace: true });
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
                width: '100%', maxWidth: 440,
                background: 'linear-gradient(145deg, rgba(108,99,255,0.06), rgba(20,20,40,0.95))',
                border: '1px solid rgba(108,99,255,0.15)',
                backdropFilter: 'blur(20px)',
                borderRadius: 4,
            }}>
                <CardContent sx={{ p: 4 }}>
                    {/* Logo */}
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
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

                    {/* Tabs: Email vs Admin */}
                    <Tabs
                        value={tab}
                        onChange={(_, v) => { setTab(v); setIdentifier(''); setError(''); }}
                        variant="fullWidth"
                        sx={{
                            mb: 2.5,
                            minHeight: 36,
                            '& .MuiTabs-indicator': {
                                background: 'linear-gradient(90deg, #6C63FF, #A78BFA)',
                                height: 2,
                                borderRadius: 1,
                            },
                            '& .MuiTab-root': {
                                minHeight: 36,
                                textTransform: 'none',
                                fontWeight: 600,
                                fontSize: '0.8rem',
                                color: 'text.secondary',
                                '&.Mui-selected': { color: '#A78BFA' },
                            },
                        }}
                    >
                        <Tab icon={<EmailIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Email Login" />
                        <Tab icon={<AdminPanelSettingsIcon sx={{ fontSize: 16 }} />} iconPosition="start" label="Admin" />
                    </Tabs>

                    {/* Error */}
                    {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

                    {/* Form */}
                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth size="small"
                            label={tab === 0 ? 'Email Address' : 'Admin Username'}
                            type={tab === 0 ? 'email' : 'text'}
                            value={identifier}
                            onChange={e => setIdentifier(e.target.value)}
                            required autoFocus
                            placeholder={tab === 0 ? 'your.email@company.com' : 'admin'}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        {tab === 0
                                            ? <EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                                            : <PersonIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                                        }
                                    </InputAdornment>
                                ),
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
                            disabled={loading || !identifier || !password}
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

                    {/* Info about login method */}
                    {tab === 0 && (
                        <Box sx={{ mt: 2, p: 1.5, borderRadius: 2, bgcolor: 'rgba(108,99,255,0.06)', border: '1px solid rgba(108,99,255,0.1)' }}>
                            <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary', textAlign: 'center' }}>
                                💡 Sign in with your registered email address
                            </Typography>
                        </Box>
                    )}
                    {tab === 1 && (
                        <Box sx={{ mt: 2, p: 1.5, borderRadius: 2, bgcolor: 'rgba(255,71,87,0.06)', border: '1px solid rgba(255,71,87,0.1)' }}>
                            <Typography sx={{ fontSize: '0.7rem', color: '#FF6B81', textAlign: 'center' }}>
                                🔒 Admin access only — use your admin username
                            </Typography>
                        </Box>
                    )}

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
