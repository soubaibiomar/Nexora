import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Box, Typography, Card, CardContent, TextField, Button, Alert,
    CircularProgress, InputAdornment, IconButton,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import WorkIcon from '@mui/icons-material/Work';

const Register: React.FC = () => {
    const navigate = useNavigate();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [role, setRole] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        await new Promise(r => setTimeout(r, 800));

        // Save to localStorage registered users
        const registeredUsers = JSON.parse(localStorage.getItem('nexora_registered_users') || '[]');
        const exists = registeredUsers.some((u: any) => u.email.toLowerCase() === email.toLowerCase());
        if (exists) {
            setError('An account with this email already exists');
            setLoading(false);
            return;
        }

        const newUser = {
            email,
            password,
            username: email.split('@')[0],
            fullName,
            role: role || 'Developer',
        };
        registeredUsers.push(newUser);
        localStorage.setItem('nexora_registered_users', JSON.stringify(registeredUsers));

        // Auto-login
        localStorage.setItem('token', 'nexora-token-' + Date.now());
        localStorage.setItem('username', newUser.username);
        localStorage.setItem('fullName', newUser.fullName);
        localStorage.setItem('email', newUser.email);
        localStorage.setItem('role', newUser.role);
        navigate('/');
        window.location.reload();
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
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
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
                            Create your account
                        </Typography>
                    </Box>

                    {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth size="small" label="Full Name"
                            value={fullName} onChange={e => setFullName(e.target.value)}
                            required autoFocus
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Email" type="email"
                            value={email} onChange={e => setEmail(e.target.value)}
                            required
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Role (optional)"
                            value={role} onChange={e => setRole(e.target.value)}
                            placeholder="e.g. Developer, Designer, Manager..."
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><WorkIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
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
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Confirm Password"
                            type={showPassword ? 'text' : 'password'}
                            value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)}
                            required
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><LockIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                        />
                        <Button
                            type="submit" fullWidth variant="contained"
                            disabled={loading || !fullName || !email || !password || !confirmPassword}
                            startIcon={loading ? <CircularProgress size={18} sx={{ color: 'white' }} /> : undefined}
                            sx={{
                                py: 1.3, fontWeight: 700, fontSize: '0.95rem', borderRadius: 2.5,
                                background: 'linear-gradient(135deg, #f97316, #ea580c)',
                                boxShadow: '0 4px 20px rgba(249,115,22,0.3)',
                                '&:hover': { background: 'linear-gradient(135deg, #fb923c, #f97316)', transform: 'translateY(-1px)' },
                            }}
                        >
                            {loading ? 'Creating account...' : 'Create Account'}
                        </Button>
                    </form>

                    {/* Login Link */}
                    <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                            Already have an account?{' '}
                            <Link to="/login" style={{ color: '#f97316', fontWeight: 600, textDecoration: 'none' }}>
                                Sign in
                            </Link>
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        </Box>
    );
};

export default Register;
