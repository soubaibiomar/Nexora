import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, Avatar, AvatarGroup, IconButton,
    TextField, Button, Chip, CircularProgress, Tabs, Tab, Dialog, DialogTitle,
    DialogContent, DialogActions, Fade, Badge, InputAdornment,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AddIcon from '@mui/icons-material/Add';
import ChatIcon from '@mui/icons-material/Chat';
import PeopleIcon from '@mui/icons-material/People';
import TimelineIcon from '@mui/icons-material/Timeline';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import BlockIcon from '@mui/icons-material/Block';
import WorkspacesIcon from '@mui/icons-material/Workspaces';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import GroupsIcon from '@mui/icons-material/Groups';
import LockIcon from '@mui/icons-material/Lock';
import CallIcon from '@mui/icons-material/Call';
import VideocamIcon from '@mui/icons-material/Videocam';
import CallEndIcon from '@mui/icons-material/CallEnd';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import VideocamOffIcon from '@mui/icons-material/VideocamOff';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';
import { workspaceService } from '../services/api';

// ── Helpers ───────────────────────────────────────────────────────
function formatTime(d: string) { return new Date(d).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }
function formatDate(d: string) {
    const diff = Math.floor((Date.now() - new Date(d).getTime()) / 86400000);
    if (diff === 0) return 'Today'; if (diff === 1) return 'Yesterday';
    if (diff < 7) return `${diff} days ago`;
    return new Date(d).toLocaleDateString([], { month: 'short', day: 'numeric' });
}
function timeAgo(d: string) {
    const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
    if (m < 1) return 'just now'; if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60); if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
}
function callDuration(start: string) {
    const s = Math.floor((Date.now() - new Date(start).getTime()) / 1000);
    const m = Math.floor(s / 60); const sec = s % 60;
    return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`;
}

const statusCfg: Record<string, { label: string; color: string; icon: React.ReactElement }> = {
    completed: { label: 'Completed', color: '#10B981', icon: <CheckCircleIcon sx={{ fontSize: 16 }} /> },
    in_progress: { label: 'In Progress', color: '#6C63FF', icon: <HourglassEmptyIcon sx={{ fontSize: 16 }} /> },
    blocked: { label: 'Blocked', color: '#EF4444', icon: <BlockIcon sx={{ fontSize: 16 }} /> },
};

const TeamWorkspace: React.FC = () => {
    const [workspaces, setWorkspaces] = useState<any[]>([]);
    const [activeWorkspace, setActiveWorkspace] = useState<any>(null);
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [messageInput, setMessageInput] = useState('');
    const [sending, setSending] = useState(false);
    const [createOpen, setCreateOpen] = useState(false);
    const [newWsName, setNewWsName] = useState('');
    const [newWsDesc, setNewWsDesc] = useState('');
    const [progressTitle, setProgressTitle] = useState('');
    const [progressDesc, setProgressDesc] = useState('');
    const [progressStatus, setProgressStatus] = useState('in_progress');
    const chatEndRef = useRef<HTMLDivElement>(null);
    // Call state
    const [activeCall, setActiveCall] = useState<any>(null);
    const [isMuted, setIsMuted] = useState(false);
    const [isVideoOn, setIsVideoOn] = useState(false);
    const [callTimer, setCallTimer] = useState('00:00');
    const callTimerRef = useRef<any>(null);

    const loadWorkspaces = useCallback(async () => {
        try { const r = await workspaceService.getAll(); setWorkspaces(r.data.workspaces || []); }
        catch { console.error('Failed to load workspaces'); }
        finally { setLoading(false); }
    }, []);
    useEffect(() => { loadWorkspaces(); }, [loadWorkspaces]);

    const openWorkspace = async (id: string) => {
        try {
            const r = await workspaceService.getById(id); setActiveWorkspace(r.data); setActiveTab(0);
            if (r.data.active_call?.status === 'active') setActiveCall(r.data.active_call);
        } catch { console.error('Failed to load workspace'); }
    };

    useEffect(() => {
        if (activeTab === 0 && chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }, [activeWorkspace?.messages?.length, activeTab]);

    // Call timer
    useEffect(() => {
        if (activeCall?.status === 'active') {
            callTimerRef.current = setInterval(() => setCallTimer(callDuration(activeCall.started_at)), 1000);
            return () => clearInterval(callTimerRef.current);
        } else { setCallTimer('00:00'); if (callTimerRef.current) clearInterval(callTimerRef.current); }
    }, [activeCall]);

    const handleSendMessage = async () => {
        if (!messageInput.trim() || !activeWorkspace) return;
        setSending(true);
        try {
            const r = await workspaceService.sendMessage(activeWorkspace.id, messageInput.trim());
            setActiveWorkspace((p: any) => ({ ...p, messages: [...(p.messages || []), r.data] }));
            setMessageInput('');
        } catch { console.error('Send failed'); } finally { setSending(false); }
    };

    const handleCreate = async () => {
        if (!newWsName.trim()) return;
        try {
            await workspaceService.create({ name: newWsName.trim(), description: newWsDesc.trim() });
            setCreateOpen(false); setNewWsName(''); setNewWsDesc(''); loadWorkspaces();
        } catch { console.error('Create failed'); }
    };

    const handlePostProgress = async () => {
        if (!progressTitle.trim() || !activeWorkspace) return;
        try {
            const r = await workspaceService.postProgress(activeWorkspace.id, { title: progressTitle.trim(), description: progressDesc.trim(), status: progressStatus });
            setActiveWorkspace((p: any) => ({ ...p, progress: [...(p.progress || []), r.data] }));
            setProgressTitle(''); setProgressDesc(''); setProgressStatus('in_progress');
        } catch { console.error('Progress post failed'); }
    };

    const handleStartCall = async (type: string) => {
        if (!activeWorkspace) return;
        try {
            const r = await workspaceService.startCall(activeWorkspace.id, type);
            setActiveCall(r.data); setIsVideoOn(type === 'video'); setIsMuted(false);
            // Auto-simulate members joining after 2s
            setTimeout(async () => {
                try { const r2 = await workspaceService.simulateJoin(activeWorkspace.id); setActiveCall(r2.data); } catch { }
            }, 2000);
        } catch { console.error('Start call failed'); }
    };

    const handleEndCall = async () => {
        if (!activeWorkspace) return;
        try { await workspaceService.endCall(activeWorkspace.id); setActiveCall(null); }
        catch { console.error('End call failed'); }
    };

    // ── Workspace List View ─────────────────────────────────────────
    if (!activeWorkspace) {
        return (
            <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
                <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <WorkspacesIcon sx={{ fontSize: 32, color: '#6C63FF' }} />
                            <Typography variant="h4" sx={{ fontWeight: 700, background: 'linear-gradient(135deg, #6C63FF, #A78BFA, #C4B5FD)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                                Team Workspaces
                            </Typography>
                        </Box>
                        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)}
                            sx={{ px: 3, py: 1, fontWeight: 600, fontSize: '0.85rem', background: 'linear-gradient(135deg, #6C63FF, #8B83FF)', boxShadow: '0 4px 16px rgba(108,99,255,0.3)', borderRadius: 3, '&:hover': { background: 'linear-gradient(135deg, #7C73FF, #9B93FF)', transform: 'translateY(-1px)' } }}>
                            New Workspace
                        </Button>
                    </Box>
                    <Typography color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                        Private spaces for your teams to collaborate, chat, call, and track progress
                    </Typography>
                </Box>

                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress sx={{ color: '#6C63FF' }} /></Box>
                ) : workspaces.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 8 }}>
                        <GroupsIcon sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.3, mb: 2 }} />
                        <Typography color="text.secondary">No workspaces yet. Create one to get started!</Typography>
                    </Box>
                ) : (
                    <Grid container spacing={2.5}>
                        {workspaces.map((ws, i) => (
                            <Grid size={{ xs: 12, md: 6, lg: 4 }} key={ws.id}>
                                <Fade in timeout={200 + i * 100}>
                                    <Card onClick={() => openWorkspace(ws.id)} sx={{
                                        cursor: 'pointer', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)',
                                        borderRadius: 4, transition: 'all 0.25s cubic-bezier(0.4,0,0.2,1)', position: 'relative', overflow: 'hidden',
                                        '&:hover': { borderColor: `${ws.color}44`, transform: 'translateY(-4px)', boxShadow: `0 12px 40px ${ws.color}15` },
                                        '&::before': { content: '""', position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg, ${ws.color}, ${ws.color}88)` },
                                    }}>
                                        <CardContent sx={{ p: 3 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
                                                <Box>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8, mb: 0.5 }}>
                                                        <Typography sx={{ fontWeight: 700, fontSize: '1.05rem' }}>{ws.name}</Typography>
                                                        <LockIcon sx={{ fontSize: 14, color: '#9CA3AF', opacity: 0.7 }} />
                                                    </Box>
                                                    <Typography sx={{ fontSize: '0.78rem', color: 'text.secondary', lineHeight: 1.5 }}>{ws.description}</Typography>
                                                </Box>
                                                <Box sx={{ width: 40, height: 40, borderRadius: 2.5, background: `${ws.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, ml: 1.5 }}>
                                                    <RocketLaunchIcon sx={{ fontSize: 20, color: ws.color }} />
                                                </Box>
                                            </Box>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                                                <AvatarGroup max={4} sx={{ '& .MuiAvatar-root': { width: 28, height: 28, fontSize: '0.65rem', fontWeight: 700, border: '2px solid', borderColor: 'background.paper' } }}>
                                                    {(ws.members_preview || []).map((m: any) => <Avatar key={m.id} src={m.avatar} alt={m.name} />)}
                                                </AvatarGroup>
                                                <Typography sx={{ fontSize: '0.72rem', color: 'text.secondary' }}>{ws.member_count} member{ws.member_count !== 1 ? 's' : ''}</Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', gap: 2, pt: 1.5, borderTop: '1px solid rgba(255,255,255,0.04)', alignItems: 'center' }}>
                                                {[{ icon: <ChatIcon sx={{ fontSize: 13 }} />, v: ws.message_count, l: 'messages' },
                                                { icon: <TimelineIcon sx={{ fontSize: 13 }} />, v: ws.progress_count, l: 'updates' },
                                                ].map(s => (
                                                    <Box key={s.l} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                        <Box sx={{ color: 'text.secondary', display: 'flex' }}>{s.icon}</Box>
                                                        <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary' }}><Box component="span" sx={{ fontWeight: 700, color: 'text.primary' }}>{s.v}</Box> {s.l}</Typography>
                                                    </Box>
                                                ))}
                                                {ws.active_call && (
                                                    <Chip size="small" icon={<PhoneInTalkIcon sx={{ fontSize: 12 }} />} label="In Call"
                                                        sx={{ height: 20, fontSize: '0.6rem', fontWeight: 700, bgcolor: 'rgba(16,185,129,0.15)', color: '#10B981', border: '1px solid rgba(16,185,129,0.3)', '& .MuiChip-icon': { color: '#10B981' }, animation: 'pulse 2s infinite', '@keyframes pulse': { '0%, 100%': { opacity: 1 }, '50%': { opacity: 0.6 } } }} />
                                                )}
                                                <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary', ml: 'auto' }}>{timeAgo(ws.last_activity)}</Typography>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Fade>
                            </Grid>
                        ))}
                    </Grid>
                )}

                {/* Create Dialog */}
                <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth
                    PaperProps={{ sx: { borderRadius: 4, bgcolor: 'background.paper', border: '1px solid rgba(108,99,255,0.15)' } }}>
                    <DialogTitle sx={{ fontWeight: 700, pb: 1 }}>Create Private Workspace</DialogTitle>
                    <DialogContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, p: 1.5, borderRadius: 2, bgcolor: 'rgba(108,99,255,0.06)', border: '1px solid rgba(108,99,255,0.12)' }}>
                            <LockIcon sx={{ fontSize: 16, color: '#6C63FF' }} />
                            <Typography sx={{ fontSize: '0.78rem', color: 'text.secondary' }}>Workspaces are private — only invited members can access</Typography>
                        </Box>
                        <TextField fullWidth autoFocus size="small" label="Workspace Name" placeholder="e.g. Project Alpha..."
                            value={newWsName} onChange={e => setNewWsName(e.target.value)} sx={{ mb: 2, '& .MuiOutlinedInput-root': { borderRadius: 2.5 } }} />
                        <TextField fullWidth multiline rows={3} size="small" label="Description" placeholder="What's this workspace about?"
                            value={newWsDesc} onChange={e => setNewWsDesc(e.target.value)} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2.5 } }} />
                    </DialogContent>
                    <DialogActions sx={{ px: 3, pb: 2.5 }}>
                        <Button onClick={() => setCreateOpen(false)} sx={{ borderRadius: 2.5 }}>Cancel</Button>
                        <Button variant="contained" onClick={handleCreate} disabled={!newWsName.trim()}
                            sx={{ borderRadius: 2.5, px: 3, background: 'linear-gradient(135deg, #6C63FF, #8B83FF)', '&:hover': { background: 'linear-gradient(135deg, #7C73FF, #9B93FF)' } }}>Create</Button>
                    </DialogActions>
                </Dialog>
            </Box>
        );
    }

    // ── Active Call Overlay ──────────────────────────────────────────
    const CallOverlay = () => {
        if (!activeCall || activeCall.status !== 'active') return null;
        const participants = activeCall.participants || [];
        return (
            <Fade in>
                <Box sx={{ position: 'fixed', inset: 0, zIndex: 1300, bgcolor: 'rgba(0,0,0,0.92)', display: 'flex', flexDirection: 'column' }}>
                    {/* Header */}
                    <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <PhoneInTalkIcon sx={{ color: '#10B981', fontSize: 22 }} />
                            <Box>
                                <Typography sx={{ fontWeight: 700, fontSize: '0.95rem' }}>{activeWorkspace.name}</Typography>
                                <Typography sx={{ fontSize: '0.7rem', color: '#10B981' }}>
                                    {activeCall.call_type === 'video' ? 'Video' : 'Voice'} Call · {callTimer}
                                </Typography>
                            </Box>
                        </Box>
                        <Chip size="small" label={`${participants.length} participant${participants.length !== 1 ? 's' : ''}`}
                            sx={{ bgcolor: 'rgba(255,255,255,0.08)', color: 'white', fontSize: '0.72rem', fontWeight: 600 }} />
                    </Box>

                    {/* Participant Grid */}
                    <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', p: 3 }}>
                        <Grid container spacing={2} sx={{ maxWidth: 800 }} justifyContent="center">
                            {participants.map((p: any) => (
                                <Grid size={{ xs: 6, sm: 4, md: participants.length <= 2 ? 6 : 4 }} key={p.id}>
                                    <Box sx={{
                                        aspectRatio: '1', borderRadius: 4, bgcolor: 'rgba(255,255,255,0.04)', border: '2px solid',
                                        borderColor: p.id === 'current_user' ? '#6C63FF' : 'rgba(255,255,255,0.08)',
                                        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 1.5,
                                        position: 'relative', overflow: 'hidden',
                                        ...(p.id === 'current_user' ? { boxShadow: '0 0 20px rgba(108,99,255,0.2)' } : {}),
                                    }}>
                                        {/* Speaking indicator ring */}
                                        <Box sx={{
                                            position: 'absolute', inset: -2, borderRadius: 4, border: '2px solid transparent',
                                            ...((!p.is_muted) ? { borderColor: '#10B981', animation: 'speakPulse 1.5s ease-in-out infinite', '@keyframes speakPulse': { '0%, 100%': { opacity: 0.3 }, '50%': { opacity: 1 } } } : {}),
                                        }} />
                                        <Avatar src={p.avatar} alt={p.name} sx={{ width: 72, height: 72, fontSize: '1.4rem', fontWeight: 700, border: '3px solid rgba(255,255,255,0.1)' }} />
                                        <Typography sx={{ fontWeight: 600, fontSize: '0.88rem' }}>{p.name}</Typography>
                                        <Box sx={{ display: 'flex', gap: 1 }}>
                                            {p.is_muted && <Chip size="small" icon={<MicOffIcon sx={{ fontSize: 12 }} />} label="Muted"
                                                sx={{ height: 20, fontSize: '0.58rem', bgcolor: 'rgba(239,68,68,0.15)', color: '#EF4444', '& .MuiChip-icon': { color: '#EF4444' } }} />}
                                            {activeCall.call_type === 'video' && !p.is_video_on &&
                                                <Chip size="small" icon={<VideocamOffIcon sx={{ fontSize: 12 }} />} label="Camera Off"
                                                    sx={{ height: 20, fontSize: '0.58rem', bgcolor: 'rgba(239,68,68,0.15)', color: '#EF4444', '& .MuiChip-icon': { color: '#EF4444' } }} />}
                                        </Box>
                                    </Box>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>

                    {/* Controls */}
                    <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
                        <IconButton onClick={() => setIsMuted(!isMuted)}
                            sx={{ width: 56, height: 56, bgcolor: isMuted ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.08)', color: isMuted ? '#EF4444' : 'white', '&:hover': { bgcolor: isMuted ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.15)' } }}>
                            {isMuted ? <MicOffIcon /> : <MicIcon />}
                        </IconButton>
                        {activeCall.call_type === 'video' && (
                            <IconButton onClick={() => setIsVideoOn(!isVideoOn)}
                                sx={{ width: 56, height: 56, bgcolor: !isVideoOn ? 'rgba(239,68,68,0.2)' : 'rgba(255,255,255,0.08)', color: !isVideoOn ? '#EF4444' : 'white', '&:hover': { bgcolor: !isVideoOn ? 'rgba(239,68,68,0.3)' : 'rgba(255,255,255,0.15)' } }}>
                                {isVideoOn ? <VideocamIcon /> : <VideocamOffIcon />}
                            </IconButton>
                        )}
                        <IconButton onClick={handleEndCall}
                            sx={{ width: 56, height: 56, bgcolor: '#EF4444', color: 'white', '&:hover': { bgcolor: '#DC2626' }, boxShadow: '0 4px 16px rgba(239,68,68,0.4)' }}>
                            <CallEndIcon />
                        </IconButton>
                    </Box>
                </Box>
            </Fade>
        );
    };

    // ── Workspace Detail View ───────────────────────────────────────
    const messages = activeWorkspace.messages || [];
    const members = activeWorkspace.members || [];
    const progress = activeWorkspace.progress || [];
    const wsColor = activeWorkspace.color || '#6C63FF';

    return (
        <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3, height: 'calc(100vh - 80px)', display: 'flex', flexDirection: 'column' }}>
            <CallOverlay />
            {/* Header */}
            <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                    <IconButton onClick={() => { setActiveWorkspace(null); setActiveCall(null); loadWorkspaces(); }} size="small"
                        sx={{ bgcolor: 'rgba(108,99,255,0.08)', '&:hover': { bgcolor: 'rgba(108,99,255,0.15)' } }}>
                        <ArrowBackIcon sx={{ fontSize: 20 }} />
                    </IconButton>
                    <Box sx={{ width: 36, height: 36, borderRadius: 2, background: `${wsColor}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <RocketLaunchIcon sx={{ fontSize: 18, color: wsColor }} />
                    </Box>
                    <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                            <Typography sx={{ fontWeight: 700, fontSize: '1.1rem' }}>{activeWorkspace.name}</Typography>
                            <LockIcon sx={{ fontSize: 14, color: '#9CA3AF' }} />
                            <Chip size="small" label="Private" sx={{ height: 18, fontSize: '0.58rem', fontWeight: 600, bgcolor: 'rgba(156,163,175,0.1)', color: '#9CA3AF', ml: 0.5 }} />
                        </Box>
                        <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>{activeWorkspace.description}</Typography>
                    </Box>
                    {/* Call Buttons */}
                    <Box sx={{ display: 'flex', gap: 1, mr: 1 }}>
                        <IconButton onClick={() => handleStartCall('voice')} size="small" title="Start Voice Call"
                            sx={{ bgcolor: 'rgba(16,185,129,0.1)', color: '#10B981', '&:hover': { bgcolor: 'rgba(16,185,129,0.2)', transform: 'scale(1.05)' }, transition: 'all 0.15s' }}>
                            <CallIcon sx={{ fontSize: 20 }} />
                        </IconButton>
                        <IconButton onClick={() => handleStartCall('video')} size="small" title="Start Video Call"
                            sx={{ bgcolor: 'rgba(108,99,255,0.1)', color: '#6C63FF', '&:hover': { bgcolor: 'rgba(108,99,255,0.2)', transform: 'scale(1.05)' }, transition: 'all 0.15s' }}>
                            <VideocamIcon sx={{ fontSize: 20 }} />
                        </IconButton>
                    </Box>
                    <AvatarGroup max={5} sx={{ '& .MuiAvatar-root': { width: 30, height: 30, fontSize: '0.65rem', fontWeight: 700, border: '2px solid', borderColor: 'background.paper' } }}>
                        {members.map((m: any) => <Avatar key={m.id} src={m.avatar} alt={m.name} />)}
                    </AvatarGroup>
                </Box>
                <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}
                    sx={{
                        minHeight: 40, '& .MuiTab-root': { minHeight: 40, fontSize: '0.82rem', fontWeight: 600, textTransform: 'none', borderRadius: '12px 12px 0 0' },
                        '& .Mui-selected': { color: wsColor }, '& .MuiTabs-indicator': { backgroundColor: wsColor, height: 2.5, borderRadius: '2px 2px 0 0' }
                    }}>
                    <Tab icon={<ChatIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Chat" />
                    <Tab icon={<PeopleIcon sx={{ fontSize: 18 }} />} iconPosition="start" label={`Members (${members.length})`} />
                    <Tab icon={<TimelineIcon sx={{ fontSize: 18 }} />} iconPosition="start" label={`Progress (${progress.length})`} />
                </Tabs>
            </Box>

            {/* ── Chat Tab ── */}
            {activeTab === 0 && (
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                    <Box sx={{
                        flex: 1, overflow: 'auto', px: 2, py: 1, bgcolor: 'rgba(0,0,0,0.15)', borderRadius: 3, border: '1px solid rgba(255,255,255,0.04)',
                        '&::-webkit-scrollbar': { width: 6 }, '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(108,99,255,0.2)', borderRadius: 3 }
                    }}>
                        {messages.map((msg: any, idx: number) => {
                            const isMe = msg.sender_id === 'current_user';
                            const showAv = idx === 0 || messages[idx - 1]?.sender_id !== msg.sender_id;
                            return (
                                <Box key={msg.id} sx={{ display: 'flex', justifyContent: isMe ? 'flex-end' : 'flex-start', mb: showAv ? 1.5 : 0.5, gap: 1 }}>
                                    {!isMe && <Box sx={{ width: 32, flexShrink: 0 }}>{showAv && <Avatar src={msg.sender_avatar} alt={msg.sender_name} sx={{ width: 32, height: 32, fontSize: '0.7rem' }} />}</Box>}
                                    <Box sx={{ maxWidth: '70%' }}>
                                        {showAv && !isMe && <Typography sx={{ fontSize: '0.68rem', fontWeight: 600, color: wsColor, mb: 0.3, ml: 0.5 }}>{msg.sender_name}</Typography>}
                                        <Box sx={{ px: 2, py: 1, borderRadius: 3, bgcolor: isMe ? `${wsColor}22` : 'rgba(255,255,255,0.04)', border: '1px solid', borderColor: isMe ? `${wsColor}33` : 'rgba(255,255,255,0.06)' }}>
                                            <Typography sx={{ fontSize: '0.85rem', lineHeight: 1.5 }}>{msg.content}</Typography>
                                            <Typography sx={{ fontSize: '0.58rem', color: 'text.secondary', mt: 0.5, textAlign: isMe ? 'right' : 'left' }}>{formatTime(msg.timestamp)}</Typography>
                                        </Box>
                                    </Box>
                                </Box>
                            );
                        })}
                        <div ref={chatEndRef} />
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
                        <TextField fullWidth size="small" placeholder="Type a message..." value={messageInput} onChange={e => setMessageInput(e.target.value)}
                            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 3, bgcolor: 'rgba(255,255,255,0.03)', '&:hover': { bgcolor: 'rgba(255,255,255,0.05)' } } }}
                            InputProps={{
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <IconButton onClick={handleSendMessage} disabled={!messageInput.trim() || sending} size="small"
                                            sx={{ bgcolor: messageInput.trim() ? `${wsColor}22` : 'transparent', color: messageInput.trim() ? wsColor : 'text.secondary', '&:hover': { bgcolor: `${wsColor}33` } }}>
                                            {sending ? <CircularProgress size={18} /> : <SendIcon sx={{ fontSize: 18 }} />}
                                        </IconButton>
                                    </InputAdornment>
                                )
                            }} />
                    </Box>
                </Box>
            )}

            {/* ── Members Tab ── */}
            {activeTab === 1 && (
                <Box sx={{ flex: 1, overflow: 'auto', px: 1, '&::-webkit-scrollbar': { width: 6 }, '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(108,99,255,0.2)', borderRadius: 3 } }}>
                    {members.map((member: any, idx: number) => (
                        <Fade in timeout={150 + idx * 50} key={member.id}>
                            <Card sx={{ mb: 1.5, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 3, transition: 'all 0.2s', '&:hover': { borderColor: `${wsColor}33`, bgcolor: 'rgba(255,255,255,0.03)' } }}>
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 }, display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <Badge overlap="circular" anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                                        badgeContent={<FiberManualRecordIcon sx={{ fontSize: 12, color: member.online ? '#10B981' : '#6B7280', filter: member.online ? 'drop-shadow(0 0 3px #10B981)' : 'none' }} />}>
                                        <Avatar src={member.avatar} alt={member.name} sx={{ width: 44, height: 44, fontSize: '0.9rem', fontWeight: 700 }} />
                                    </Badge>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography sx={{ fontWeight: 600, fontSize: '0.92rem' }}>{member.name}</Typography>
                                        <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>{member.role} · {member.department}</Typography>
                                    </Box>
                                    <Box sx={{ textAlign: 'right' }}>
                                        <Chip label={member.online ? 'Online' : 'Offline'} size="small"
                                            sx={{
                                                height: 22, fontSize: '0.65rem', fontWeight: 600, bgcolor: member.online ? 'rgba(16,185,129,0.1)' : 'rgba(107,114,128,0.1)',
                                                color: member.online ? '#10B981' : '#9CA3AF', border: `1px solid ${member.online ? 'rgba(16,185,129,0.2)' : 'rgba(107,114,128,0.15)'}`
                                            }} />
                                        <Typography sx={{ fontSize: '0.6rem', color: 'text.secondary', mt: 0.5 }}>Joined {formatDate(member.joined_at)}</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Fade>
                    ))}
                </Box>
            )}

            {/* ── Progress Tab ── */}
            {activeTab === 2 && (
                <Box sx={{ flex: 1, overflow: 'auto', px: 1, '&::-webkit-scrollbar': { width: 6 }, '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(108,99,255,0.2)', borderRadius: 3 } }}>
                    <Card sx={{ mb: 2.5, background: `${wsColor}08`, border: `1px solid ${wsColor}20`, borderRadius: 3 }}>
                        <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                            <Typography sx={{ fontWeight: 600, fontSize: '0.85rem', mb: 1.5, color: wsColor }}>Post a Progress Update</Typography>
                            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
                                <TextField size="small" placeholder="Milestone title..." value={progressTitle} onChange={e => setProgressTitle(e.target.value)}
                                    sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }} />
                                <TextField size="small" placeholder="Description (optional)" value={progressDesc} onChange={e => setProgressDesc(e.target.value)}
                                    sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }} />
                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                    {Object.entries(statusCfg).map(([key, cfg]) => (
                                        <Chip key={key} label={cfg.label} size="small" icon={cfg.icon} onClick={() => setProgressStatus(key)}
                                            sx={{
                                                height: 30, fontSize: '0.72rem', cursor: 'pointer', bgcolor: progressStatus === key ? `${cfg.color}20` : 'transparent',
                                                color: progressStatus === key ? cfg.color : 'text.secondary', border: `1px solid ${progressStatus === key ? `${cfg.color}44` : 'rgba(255,255,255,0.1)'}`,
                                                '& .MuiChip-icon': { color: 'inherit' }, transition: 'all 0.15s'
                                            }} />
                                    ))}
                                </Box>
                                <Button variant="contained" size="small" onClick={handlePostProgress} disabled={!progressTitle.trim()}
                                    sx={{ px: 2.5, borderRadius: 2.5, fontWeight: 600, fontSize: '0.8rem', background: `linear-gradient(135deg, ${wsColor}, ${wsColor}CC)`, '&:hover': { filter: 'brightness(1.1)' } }}>Post</Button>
                            </Box>
                        </CardContent>
                    </Card>
                    {[...progress].reverse().map((item: any, idx: number) => {
                        const cfg = statusCfg[item.status] || statusCfg.in_progress;
                        return (
                            <Fade in timeout={150 + idx * 50} key={item.id}>
                                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 24 }}>
                                        <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: `${cfg.color}22`, border: `2px solid ${cfg.color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: cfg.color, flexShrink: 0 }}>{cfg.icon}</Box>
                                        {idx < progress.length - 1 && <Box sx={{ width: 2, flex: 1, bgcolor: 'rgba(255,255,255,0.06)', mt: 0.5 }} />}
                                    </Box>
                                    <Card sx={{ flex: 1, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 3 }}>
                                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                                                <Typography sx={{ fontWeight: 700, fontSize: '0.9rem' }}>{item.title}</Typography>
                                                <Chip label={cfg.label} size="small" icon={cfg.icon} sx={{ height: 22, fontSize: '0.62rem', fontWeight: 600, bgcolor: `${cfg.color}15`, color: cfg.color, border: `1px solid ${cfg.color}33`, '& .MuiChip-icon': { color: 'inherit' } }} />
                                            </Box>
                                            {item.description && <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary', mb: 0.5 }}>{item.description}</Typography>}
                                            <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>{item.author} · {formatDate(item.created_at)}</Typography>
                                        </CardContent>
                                    </Card>
                                </Box>
                            </Fade>
                        );
                    })}
                </Box>
            )}
        </Box>
    );
};

export default TeamWorkspace;
