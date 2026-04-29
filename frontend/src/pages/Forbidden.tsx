import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useAuth } from '../contexts/AuthContext';

const Forbidden: React.FC = () => {
    const navigate = useNavigate();
    const { role } = useAuth();

    return (
        <Box sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #0a0a1a 0%, #141428 50%, #1a1040 100%)',
            p: 3,
            textAlign: 'center',
        }}>
            {/* Icon */}
            <Box sx={{
                width: 100,
                height: 100,
                borderRadius: '50%',
                background: 'linear-gradient(135deg, rgba(255,71,87,0.15), rgba(255,71,87,0.05))',
                border: '2px solid rgba(255,71,87,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                    '0%, 100%': { boxShadow: '0 0 0 0 rgba(255,71,87,0.2)' },
                    '50%': { boxShadow: '0 0 0 20px rgba(255,71,87,0)' },
                },
            }}>
                <BlockIcon sx={{ fontSize: 48, color: '#FF4757' }} />
            </Box>

            {/* Title */}
            <Typography variant="h3" sx={{
                fontWeight: 800,
                background: 'linear-gradient(135deg, #FF4757, #FF6B81)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 1.5,
            }}>
                403
            </Typography>

            <Typography variant="h5" sx={{
                fontWeight: 700,
                color: 'rgba(255,255,255,0.9)',
                mb: 1,
            }}>
                Access Denied
            </Typography>

            <Typography sx={{
                color: 'rgba(255,255,255,0.5)',
                fontSize: '0.95rem',
                maxWidth: 420,
                mb: 1,
                lineHeight: 1.6,
            }}>
                You don't have permission to access this page.
                Your current role ({role}) doesn't have sufficient privileges.
            </Typography>

            <Typography sx={{
                color: 'rgba(255,255,255,0.3)',
                fontSize: '0.8rem',
                mb: 4,
            }}>
                Contact your administrator if you believe this is an error.
            </Typography>

            {/* Actions */}
            <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                    variant="contained"
                    startIcon={<ArrowBackIcon />}
                    onClick={() => navigate('/')}
                    sx={{
                        px: 3, py: 1.2,
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        borderRadius: 2.5,
                        background: 'linear-gradient(135deg, #6C63FF, #5A52D5)',
                        boxShadow: '0 4px 20px rgba(108,99,255,0.3)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #8B83FF, #6C63FF)',
                            transform: 'translateY(-1px)',
                        },
                    }}
                >
                    Go Home
                </Button>
                <Button
                    variant="outlined"
                    onClick={() => navigate(-1)}
                    sx={{
                        px: 3, py: 1.2,
                        fontWeight: 600,
                        fontSize: '0.9rem',
                        borderRadius: 2.5,
                        borderColor: 'rgba(255,255,255,0.15)',
                        color: 'rgba(255,255,255,0.7)',
                        '&:hover': {
                            borderColor: 'rgba(255,255,255,0.3)',
                            bgcolor: 'rgba(255,255,255,0.05)',
                        },
                    }}
                >
                    Go Back
                </Button>
            </Box>
        </Box>
    );
};

export default Forbidden;
