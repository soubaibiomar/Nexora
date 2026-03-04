import React, { useState, useRef, useEffect } from 'react';
import {
    Box, IconButton, Typography, TextField,
    Fab, Tooltip, Grow, Fade, Chip,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import PersonIcon from '@mui/icons-material/Person';
import MinimizeIcon from '@mui/icons-material/Remove';
import { aiService } from '../services/api';

interface Message {
    text: string;
    sender: 'user' | 'bot';
    timestamp?: string;
    suggestions?: string[];
}

const AIChatbot: React.FC = () => {
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        {
            text: "Hi! I'm Veda, your intelligent AI assistant. Ask me anything — from finding experts and skills to general knowledge about companies and technologies! ✨",
            sender: 'bot',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            suggestions: ['Who are the top experts?', 'What skills are trending?', 'Tell me about Google'],
        }
    ]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<null | HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (text?: string) => {
        const userMsg = (text || input).trim();
        if (!userMsg) return;

        const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        setMessages(prev => [...prev, { text: userMsg, sender: 'user', timestamp: now }]);
        setInput('');
        setLoading(true);

        try {
            const response = await aiService.chat(userMsg);
            const botMsg = response.data.message || "I don't understand.";
            const suggestions = response.data.suggestions || [];
            setMessages(prev => [...prev, {
                text: botMsg,
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                suggestions,
            }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                text: "Sorry, I'm having trouble connecting right now. Please try again.",
                sender: 'bot',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            {/* Floating Action Button */}
            <Tooltip title="Ask Veda ✨" placement="left" arrow>
                <Fab
                    aria-label="chat"
                    onClick={() => setOpen(true)}
                    sx={{
                        position: 'fixed',
                        bottom: 24,
                        right: 24,
                        zIndex: 1200,
                        width: 58,
                        height: 58,
                        bgcolor: 'primary.main',
                        '&:hover': {
                            bgcolor: 'primary.dark',
                        },
                        display: open ? 'none' : 'flex',
                    }}
                >
                    <AutoAwesomeIcon sx={{ fontSize: 26, color: 'white' }} />
                </Fab>
            </Tooltip>

            {/* Chat Window */}
            <Grow in={open} timeout={300}>
                <Box
                    sx={{
                        position: 'fixed',
                        bottom: 24,
                        right: 24,
                        width: { xs: 'calc(100vw - 48px)', sm: 380 },
                        height: { xs: 'calc(100vh - 100px)', sm: 560 },
                        zIndex: 1300,
                        display: open ? 'flex' : 'none',
                        flexDirection: 'column',
                        overflow: 'hidden',
                        borderRadius: '8px',
                        border: '1px solid rgba(255,255,255,0.08)',
                        bgcolor: 'background.paper',
                        boxShadow: 3,
                    }}
                >
                    {/* Header */}
                    <Box sx={{
                        p: 2,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        bgcolor: 'primary.dark',
                    }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2 }}>
                            <Box sx={{
                                width: 36, height: 36, borderRadius: '12px',
                                bgcolor: 'primary.main',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                <AutoAwesomeIcon sx={{ fontSize: 20, color: 'white' }} />
                            </Box>
                            <Box>
                                <Typography sx={{ fontSize: '0.95rem', fontWeight: 700, color: 'white', lineHeight: 1.2 }}>
                                    Veda
                                </Typography>
                                <Typography sx={{ fontSize: '0.65rem', color: 'rgba(162,155,254,0.8)', fontWeight: 500, letterSpacing: 0.5 }}>
                                    AI Assistant • Online
                                </Typography>
                            </Box>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 0.3 }}>
                            <IconButton size="small" onClick={() => setOpen(false)} sx={{
                                color: 'rgba(255,255,255,0.4)',
                                '&:hover': { color: 'white', bgcolor: 'rgba(255,255,255,0.05)' },
                            }}>
                                <MinimizeIcon sx={{ fontSize: 18 }} />
                            </IconButton>
                            <IconButton size="small" onClick={() => setOpen(false)} sx={{
                                color: 'rgba(255,255,255,0.4)',
                                '&:hover': { color: '#ef4444', bgcolor: 'rgba(239,68,68,0.1)' },
                            }}>
                                <CloseIcon sx={{ fontSize: 18 }} />
                            </IconButton>
                        </Box>
                    </Box>

                    {/* Messages */}
                    <Box sx={{
                        flex: 1, px: 2, py: 1.5, overflowY: 'auto',
                        display: 'flex', flexDirection: 'column', gap: 2,
                        '&::-webkit-scrollbar': { width: 4 },
                        '&::-webkit-scrollbar-thumb': {
                            bgcolor: 'rgba(108,92,231,0.3)', borderRadius: 10,
                        },
                    }}>
                        {messages.map((msg, idx) => (
                            <Fade in key={idx} timeout={400}>
                                <Box sx={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                                }}>
                                    {/* Sender label */}
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.4, px: 0.5 }}>
                                        {msg.sender === 'bot' ? (
                                            <AutoAwesomeIcon sx={{ fontSize: 12, color: '#A29BFE' }} />
                                        ) : (
                                            <PersonIcon sx={{ fontSize: 12, color: '#6C5CE7' }} />
                                        )}
                                        <Typography sx={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.35)', fontWeight: 500 }}>
                                            {msg.sender === 'bot' ? 'Veda' : 'You'}
                                            {msg.timestamp && ` · ${msg.timestamp}`}
                                        </Typography>
                                    </Box>

                                    {/* Message bubble */}
                                    <Box sx={{
                                        maxWidth: '88%',
                                        p: 1.5,
                                        borderRadius: '16px',
                                        borderTopLeftRadius: msg.sender === 'bot' ? '4px' : '16px',
                                        borderTopRightRadius: msg.sender === 'user' ? '4px' : '16px',
                                        bgcolor: msg.sender === 'user' ? 'primary.main' : 'action.selected',
                                        border: msg.sender === 'bot' ? '1px solid rgba(255,255,255,0.06)' : 'none',
                                    }}>
                                        <Typography sx={{
                                            fontSize: '0.82rem', color: 'rgba(255,255,255,0.9)',
                                            whiteSpace: 'pre-wrap', lineHeight: 1.55,
                                        }}>
                                            {msg.text}
                                        </Typography>
                                    </Box>

                                    {/* Suggestion chips */}
                                    {msg.sender === 'bot' && msg.suggestions && msg.suggestions.length > 0 && (
                                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.8, px: 0.5 }}>
                                            {msg.suggestions.map((s, i) => (
                                                <Chip
                                                    key={i}
                                                    label={s}
                                                    size="small"
                                                    onClick={() => handleSend(s)}
                                                    sx={{
                                                        height: 24,
                                                        fontSize: '0.68rem',
                                                        fontWeight: 500,
                                                        bgcolor: 'rgba(108,92,231,0.08)',
                                                        color: '#A29BFE',
                                                        border: '1px solid rgba(108,92,231,0.15)',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.2s',
                                                        '&:hover': {
                                                            bgcolor: 'rgba(108,92,231,0.15)',
                                                            borderColor: 'rgba(108,92,231,0.3)',
                                                            transform: 'translateY(-1px)',
                                                        },
                                                    }}
                                                />
                                            ))}
                                        </Box>
                                    )}
                                </Box>
                            </Fade>
                        ))}

                        {/* Typing indicator */}
                        {loading && (
                            <Fade in timeout={300}>
                                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.4, px: 0.5 }}>
                                        <AutoAwesomeIcon sx={{ fontSize: 12, color: '#A29BFE' }} />
                                        <Typography sx={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.35)', fontWeight: 500 }}>
                                            Veda is thinking…
                                        </Typography>
                                    </Box>
                                    <Box sx={{
                                        p: 1.5, borderRadius: '16px', borderTopLeftRadius: '4px',
                                        bgcolor: 'rgba(255,255,255,0.04)',
                                        border: '1px solid rgba(255,255,255,0.06)',
                                        display: 'flex', alignItems: 'center', gap: 1,
                                    }}>
                                        <Box sx={{ display: 'flex', gap: 0.4 }}>
                                            {[0, 1, 2].map(i => (
                                                <Box key={i} sx={{
                                                    width: 6, height: 6, borderRadius: '50%',
                                                    bgcolor: '#A29BFE',
                                                    animation: 'vedaBounce 1.4s infinite',
                                                    animationDelay: `${i * 0.2}s`,
                                                    '@keyframes vedaBounce': {
                                                        '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
                                                        '40%': { transform: 'scale(1)', opacity: 1 },
                                                    },
                                                }} />
                                            ))}
                                        </Box>
                                    </Box>
                                </Box>
                            </Fade>
                        )}
                        <div ref={messagesEndRef} />
                    </Box>

                    {/* Input Area */}
                    <Box sx={{
                        px: 2, py: 1.5,
                        borderTop: '1px solid rgba(255,255,255,0.06)',
                        bgcolor: 'background.default',
                    }}>
                        <Box sx={{
                            display: 'flex', alignItems: 'center', gap: 0.8,
                            bgcolor: 'rgba(255,255,255,0.04)',
                            borderRadius: '14px',
                            border: '1px solid rgba(255,255,255,0.06)',
                            px: 1.5, py: 0.3,
                            transition: 'all 0.2s',
                            '&:focus-within': {
                                borderColor: 'rgba(108,92,231,0.4)',
                                boxShadow: '0 0 0 3px rgba(108,92,231,0.08)',
                            },
                        }}>
                            <TextField
                                fullWidth
                                variant="standard"
                                placeholder="Ask Veda anything…"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                                InputProps={{ disableUnderline: true }}
                                sx={{
                                    '& .MuiInputBase-input': {
                                        color: 'rgba(255,255,255,0.85)',
                                        fontSize: '0.83rem',
                                        py: 0.8,
                                        '&::placeholder': { color: 'rgba(255,255,255,0.25)', opacity: 1 },
                                    },
                                }}
                            />
                            <IconButton
                                onClick={() => handleSend()}
                                disabled={!input.trim() || loading}
                                sx={{
                                    width: 34, height: 34,
                                    bgcolor: input.trim() ? 'primary.main' : 'action.disabledBackground',
                                    transition: 'all 0.2s',
                                    '&:hover': {
                                        bgcolor: 'primary.dark',
                                    },
                                    '&:disabled': { opacity: 0.4 },
                                }}
                            >
                                <SendIcon sx={{ fontSize: 16, color: 'white' }} />
                            </IconButton>
                        </Box>
                        <Typography sx={{ fontSize: '0.6rem', color: 'rgba(255,255,255,0.15)', textAlign: 'center', mt: 0.6 }}>
                            Powered by Veda AI • Nexora
                        </Typography>
                    </Box>
                </Box>
            </Grow>
        </>
    );
};

export default AIChatbot;
