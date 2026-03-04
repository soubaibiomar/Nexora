import { useState, useEffect, useRef } from 'react';
import {
    Box, Typography, Card, Avatar, TextField, IconButton,
    CircularProgress, Badge, InputAdornment,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SearchIcon from '@mui/icons-material/Search';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import { messagingService } from '../services/api';

function formatTime(dateStr: string) {
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDate(dateStr: string) {
    const d = new Date(dateStr);
    const today = new Date();
    if (d.toDateString() === today.toDateString()) return 'Today';
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return d.toLocaleDateString();
}

export default function Messaging() {
    const [conversations, setConversations] = useState<any[]>([]);
    const [selectedConvo, setSelectedConvo] = useState<any>(null);
    const [messages, setMessages] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [newMessage, setNewMessage] = useState('');
    const [search, setSearch] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await messagingService.getConversations();
                const convos = res.data.conversations || [];
                setConversations(convos);
                if (convos.length > 0) {
                    setSelectedConvo(convos[0]);
                    const msgRes = await messagingService.getMessages(convos[0].id);
                    setMessages(msgRes.data.messages || []);
                }
            } catch { /* ignore */ }
            setLoading(false);
        };
        load();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const selectConvo = async (convo: any) => {
        setSelectedConvo(convo);
        setConversations((prev) => prev.map((c) => c.id === convo.id ? { ...c, unread: 0 } : c));
        try {
            const res = await messagingService.getMessages(convo.id);
            setMessages(res.data.messages || []);
        } catch { /* ignore */ }
    };

    const handleSend = async () => {
        const text = newMessage.trim();
        if (!text || !selectedConvo) return;
        setNewMessage('');
        try {
            const res = await messagingService.sendMessage(selectedConvo.id, text);
            setMessages((prev) => [...prev, res.data]);
            setConversations((prev) =>
                prev.map((c) =>
                    c.id === selectedConvo.id ? { ...c, last_message: text, last_timestamp: new Date().toISOString() } : c
                )
            );
        } catch { /* ignore */ }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    const filtered = conversations.filter((c) => !search || c.participant_name?.toLowerCase().includes(search.toLowerCase()));

    return (
        <Box sx={{ maxWidth: 1100, mx: 'auto', p: { xs: 1, md: 3 } }}>
            <Card sx={{ display: 'flex', height: 'calc(100vh - 48px)', overflow: 'hidden' }}>
                {/* Conversation List */}
                <Box sx={{
                    width: { xs: selectedConvo ? 0 : '100%', md: 340 },
                    borderRight: '1px solid', borderColor: 'divider',
                    display: 'flex', flexDirection: 'column',
                    transition: 'width 0.3s',
                    overflow: 'hidden',
                }}>
                    <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                        <Typography variant="h6" fontWeight={700} color="primary" sx={{
                            mb: 1.5,
                        }}>Messaging</Typography>
                        <TextField
                            fullWidth size="small" placeholder="Search conversations..."
                            value={search} onChange={(e) => setSearch(e.target.value)}
                            InputProps={{
                                startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" sx={{ color: 'text.secondary' }} /></InputAdornment>,
                            }}
                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(108,92,231,0.03)' } }}
                        />
                    </Box>

                    <Box sx={{ overflow: 'auto', flex: 1 }}>
                        {filtered.map((convo) => (
                            <Box
                                key={convo.id}
                                onClick={() => selectConvo(convo)}
                                sx={{
                                    display: 'flex', gap: 1.5, p: 1.5, cursor: 'pointer',
                                    bgcolor: selectedConvo?.id === convo.id ? 'action.selected' : 'transparent',
                                    borderLeft: selectedConvo?.id === convo.id ? '3px solid' : '3px solid transparent',
                                    borderColor: 'primary.main',
                                    '&:hover': {
                                        bgcolor: 'action.hover',
                                    },
                                    transition: 'all 0.15s',
                                }}
                            >
                                <Badge
                                    overlap="circular"
                                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                    badgeContent={convo.online ? <FiberManualRecordIcon sx={{ fontSize: 10, color: '#00B894' }} /> : null}
                                >
                                    <Avatar
                                        src={convo.participant_avatar}
                                        sx={{ width: 44, height: 44, bgcolor: '#6C5CE7', fontSize: '1rem', fontWeight: 600 }}
                                    >{convo.participant_name?.charAt(0)}</Avatar>
                                </Badge>
                                <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Typography variant="body2" fontWeight={convo.unread > 0 ? 700 : 500} noWrap>
                                            {convo.participant_name}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary" sx={{ whiteSpace: 'nowrap', ml: 1, fontSize: '0.65rem' }}>
                                            {formatDate(convo.last_timestamp)}
                                        </Typography>
                                    </Box>
                                    <Typography variant="caption" color="text.secondary" noWrap display="block" sx={{ fontSize: '0.7rem' }}>
                                        {convo.participant_role}
                                    </Typography>
                                    <Typography
                                        variant="caption" noWrap display="block"
                                        sx={{ color: convo.unread ? 'text.primary' : 'text.secondary', fontWeight: convo.unread ? 600 : 400, fontSize: '0.75rem' }}
                                    >
                                        {convo.last_message}
                                    </Typography>
                                </Box>
                                {convo.unread > 0 && (
                                    <Box sx={{
                                        width: 20, height: 20, borderRadius: '50%', display: 'flex',
                                        alignItems: 'center', justifyContent: 'center',
                                        bgcolor: 'primary.main', color: 'white', fontSize: '0.6rem', fontWeight: 700,
                                        alignSelf: 'center', flexShrink: 0,
                                    }}>
                                        {convo.unread}
                                    </Box>
                                )}
                            </Box>
                        ))}
                        {filtered.length === 0 && (
                            <Box sx={{ p: 3, textAlign: 'center' }}>
                                <Typography variant="body2" color="text.secondary">No conversations found</Typography>
                            </Box>
                        )}
                    </Box>
                </Box>

                {/* Message Thread */}
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    {selectedConvo ? (
                        <>
                            {/* Header */}
                            <Box sx={{
                                p: 2, borderBottom: '1px solid', borderColor: 'divider',
                                display: 'flex', alignItems: 'center', gap: 1.5,
                                backdropFilter: 'blur(10px)',
                            }}>
                                <Badge
                                    overlap="circular"
                                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                    badgeContent={selectedConvo.online ? <FiberManualRecordIcon sx={{ fontSize: 10, color: '#00B894' }} /> : null}
                                >
                                    <Avatar
                                        src={selectedConvo.participant_avatar}
                                        sx={{ bgcolor: 'primary.main', fontWeight: 600 }}
                                    >{selectedConvo.participant_name?.charAt(0)}</Avatar>
                                </Badge>
                                <Box>
                                    <Typography variant="body1" fontWeight={600}>{selectedConvo.participant_name}</Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        {selectedConvo.participant_role}
                                        {selectedConvo.online && (
                                            <Typography component="span" variant="caption" sx={{ color: '#00B894', fontWeight: 600 }}> • Online</Typography>
                                        )}
                                    </Typography>
                                </Box>
                            </Box>

                            {/* Messages */}
                            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
                                {messages.map((msg: any) => (
                                    <Box
                                        key={msg.id}
                                        sx={{ display: 'flex', justifyContent: msg.sender === 'You' ? 'flex-end' : 'flex-start', mb: 1.5 }}
                                    >
                                        {msg.sender !== 'You' && (
                                            <Avatar
                                                src={selectedConvo?.participant_avatar}
                                                sx={{ width: 30, height: 30, mr: 1, bgcolor: '#6C5CE7', fontSize: '0.75rem', fontWeight: 600 }}
                                            >{msg.sender?.charAt(0)}</Avatar>
                                        )}
                                        <Box sx={{
                                            maxWidth: '65%', p: 1.8, borderRadius: 3,
                                            bgcolor: msg.sender === 'You' ? 'primary.main' : 'action.hover',
                                            color: msg.sender === 'You' ? 'white' : 'text.primary',
                                        }}>
                                            <Typography variant="body2" sx={{ lineHeight: 1.6 }}>{msg.content}</Typography>
                                            <Typography
                                                variant="caption"
                                                sx={{ display: 'block', textAlign: 'right', mt: 0.3, opacity: 0.6, fontSize: '0.6rem' }}
                                            >
                                                {formatTime(msg.timestamp)}
                                            </Typography>
                                        </Box>
                                    </Box>
                                ))}
                                <div ref={messagesEndRef} />
                            </Box>

                            {/* Input */}
                            <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                    <TextField
                                        fullWidth size="small" placeholder="Write a message..."
                                        value={newMessage} onChange={(e) => setNewMessage(e.target.value)}
                                        onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                                        multiline maxRows={3}
                                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3, bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)' } }}
                                    />
                                    <IconButton
                                        onClick={handleSend} disabled={!newMessage.trim()}
                                        sx={{
                                            bgcolor: newMessage.trim() ? '#6C5CE7' : 'transparent',
                                            color: newMessage.trim() ? 'white' : 'text.secondary',
                                            width: 40, height: 40,
                                            '&:hover': { bgcolor: '#5A4BD1' },
                                            transition: 'all 0.2s',
                                        }}
                                    >
                                        <SendIcon fontSize="small" />
                                    </IconButton>
                                </Box>
                            </Box>
                        </>
                    ) : (
                        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1, flexDirection: 'column', gap: 2 }}>
                            <Box sx={{
                                width: 80, height: 80, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                background: 'linear-gradient(135deg, rgba(108,92,231,0.1), rgba(0,206,201,0.05))',
                            }}>
                                <ChatBubbleOutlineIcon sx={{ fontSize: 36, color: '#A29BFE' }} />
                            </Box>
                            <Typography color="text.secondary">Select a conversation to start messaging</Typography>
                        </Box>
                    )}
                </Box>
            </Card>
        </Box>
    );
}
