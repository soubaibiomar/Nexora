import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Box, Typography, Card, CardContent, TextField, Button, Alert,
    CircularProgress, InputAdornment, IconButton, LinearProgress,
    FormControl, InputLabel, Select, MenuItem,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import EmailIcon from '@mui/icons-material/Email';
import LockIcon from '@mui/icons-material/Lock';
import PersonIcon from '@mui/icons-material/Person';
import WorkIcon from '@mui/icons-material/Work';
import BadgeIcon from '@mui/icons-material/Badge';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useAuth } from '../contexts/AuthContext';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

/** Return 0–4 representing password strength. */
function getPasswordStrength(pw: string): number {
    let score = 0;
    if (pw.length >= 6) score++;
    if (pw.length >= 10) score++;
    if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    return Math.min(score, 4);
}

const STRENGTH_LABELS = ['', 'Weak', 'Fair', 'Good', 'Strong'];
const STRENGTH_COLORS = ['', '#FF4757', '#FFA502', '#2ED573', '#00CEC9'];

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

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

const Register: React.FC = () => {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [headline, setHeadline] = useState('');
    const [role, setRole] = useState('user');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    // Real-time validation states
    const emailValid = useMemo(() => !email || EMAIL_REGEX.test(email), [email]);
    const passwordStrength = useMemo(() => getPasswordStrength(password), [password]);
    const passwordsMatch = useMemo(() => !confirmPassword || password === confirmPassword, [password, confirmPassword]);
    const usernameValid = useMemo(() => !username || (username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username)), [username]);

    const canSubmit = fullName.trim() && username.trim() && email && emailValid && password.length >= 6 && passwordsMatch && usernameValid;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Final client-side validation
        if (!EMAIL_REGEX.test(email)) {
            setError('Please enter a valid email address.');
            return;
        }
        if (password.length < 6) {
            setError('Password must be at least 6 characters.');
            return;
        }
        if (password !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (username.length < 3) {
            setError('Username must be at least 3 characters.');
            return;
        }

        setLoading(true);

        try {
            // Call backend /api/auth/register
            const regResponse = await fetch('http://localhost:8000/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username.trim().toLowerCase(),
                    email: email.trim(),
                    password,
                    full_name: fullName.trim(),
                    headline: headline.trim(),
                    role,
                }),
            });

            if (!regResponse.ok) {
                const errData = await regResponse.json().catch(() => null);
                setError(errData?.detail || 'Registration failed. Please try again.');
                setLoading(false);
                return;
            }

            setSuccess('Account created successfully! Signing you in...');

            // Auto-login after registration
            const formData = new URLSearchParams();
            formData.append('username', username.trim().toLowerCase());
            formData.append('password', password);

            const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            if (loginResponse.ok) {
                const data = await loginResponse.json();
                const role = data.role || 'user';
                login(data.access_token, data.username, data.full_name, data.email, role);
                navigate(getRedirectForRole(role), { replace: true });
            } else {
                // Registration succeeded but auto-login failed; redirect to login
                navigate('/login');
            }
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
                            Create your account
                        </Typography>
                    </Box>

                    {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}
                    {success && <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }} icon={<CheckCircleIcon />}>{success}</Alert>}

                    <form onSubmit={handleSubmit}>
                        <TextField
                            fullWidth size="small" label="Full Name"
                            value={fullName} onChange={e => setFullName(e.target.value)}
                            required autoFocus
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Username"
                            value={username} onChange={e => setUsername(e.target.value)}
                            required
                            error={!!username && !usernameValid}
                            helperText={username && !usernameValid ? 'Min 3 chars, letters/numbers/underscore only' : ''}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><PersonIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Email" type="email"
                            value={email} onChange={e => setEmail(e.target.value)}
                            required
                            error={!!email && !emailValid}
                            helperText={email && !emailValid ? 'Please enter a valid email address' : ''}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><EmailIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <TextField
                            fullWidth size="small" label="Headline (optional)"
                            value={headline} onChange={e => setHeadline(e.target.value)}
                            placeholder="e.g. Software Engineer at ..."
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><WorkIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />

                        {/* Role Selector */}
                        <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                            <InputLabel id="role-select-label" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <BadgeIcon sx={{ fontSize: 16 }} /> Account Type
                            </InputLabel>
                            <Select
                                labelId="role-select-label"
                                id="role-select"
                                value={role}
                                label="⬜ Account Type"
                                onChange={e => setRole(e.target.value)}
                                sx={{
                                    borderRadius: 2.5,
                                    bgcolor: 'rgba(108,99,255,0.04)',
                                    '& .MuiSelect-icon': { color: 'text.secondary' },
                                }}
                            >
                                <MenuItem value="user">
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <PersonIcon sx={{ fontSize: 18, color: '#6C63FF' }} />
                                        <Box>
                                            <Typography sx={{ fontSize: '0.9rem', fontWeight: 600 }}>User</Typography>
                                            <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>Standard access — dashboard, profile, AI chatbot</Typography>
                                        </Box>
                                    </Box>
                                </MenuItem>
                                <MenuItem value="manager">
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <WorkIcon sx={{ fontSize: 18, color: '#A78BFA' }} />
                                        <Box>
                                            <Typography sx={{ fontSize: '0.9rem', fontWeight: 600 }}>Manager</Typography>
                                            <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>Full access — graph explorer, team builder, analytics</Typography>
                                        </Box>
                                    </Box>
                                </MenuItem>
                            </Select>
                        </FormControl>
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
                            sx={{ mb: 0.5, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />

                        {/* Password strength bar */}
                        {password && (
                            <Box sx={{ mb: 2, px: 0.5 }}>
                                <LinearProgress
                                    variant="determinate"
                                    value={passwordStrength * 25}
                                    sx={{
                                        height: 4,
                                        borderRadius: 2,
                                        bgcolor: 'rgba(255,255,255,0.06)',
                                        '& .MuiLinearProgress-bar': {
                                            bgcolor: STRENGTH_COLORS[passwordStrength] || 'grey',
                                            borderRadius: 2,
                                            transition: 'all 0.3s',
                                        },
                                    }}
                                />
                                <Typography sx={{
                                    fontSize: '0.65rem',
                                    mt: 0.3,
                                    color: STRENGTH_COLORS[passwordStrength] || 'text.secondary',
                                    fontWeight: 600,
                                }}>
                                    {STRENGTH_LABELS[passwordStrength]}
                                    {password.length < 6 && ' — minimum 6 characters'}
                                </Typography>
                            </Box>
                        )}

                        <TextField
                            fullWidth size="small" label="Confirm Password"
                            type={showPassword ? 'text' : 'password'}
                            value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)}
                            required
                            error={!!confirmPassword && !passwordsMatch}
                            helperText={confirmPassword && !passwordsMatch ? 'Passwords do not match' : ''}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><LockIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ mb: 3, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(108,99,255,0.04)' } }}
                        />
                        <Button
                            type="submit" fullWidth variant="contained"
                            disabled={loading || !canSubmit}
                            startIcon={loading ? <CircularProgress size={18} sx={{ color: 'white' }} /> : undefined}
                            sx={{
                                py: 1.3, fontWeight: 700, fontSize: '0.95rem', borderRadius: 2.5,
                                background: 'linear-gradient(135deg, #6C63FF, #5A52D5)',
                                boxShadow: '0 4px 20px rgba(108,99,255,0.3)',
                                '&:hover': { background: 'linear-gradient(135deg, #8B83FF, #6C63FF)', transform: 'translateY(-1px)' },
                            }}
                        >
                            {loading ? 'Creating account...' : 'Create Account'}
                        </Button>
                    </form>

                    {/* Login Link */}
                    <Box sx={{ mt: 3, textAlign: 'center' }}>
                        <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                            Already have an account?{' '}
                            <Link to="/login" style={{ color: '#A78BFA', fontWeight: 600, textDecoration: 'none' }}>
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
