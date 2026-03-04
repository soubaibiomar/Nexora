import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Button, Chip,
    CircularProgress, Divider,
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import CommentIcon from '@mui/icons-material/Comment';
import WorkIcon from '@mui/icons-material/Work';
import CelebrationIcon from '@mui/icons-material/Celebration';
import SchoolIcon from '@mui/icons-material/School';
import GroupIcon from '@mui/icons-material/Group';
import AnnouncementIcon from '@mui/icons-material/Announcement';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import { notificationService } from '../services/api';

function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
}

function getIcon(type: string) {
    const iconMap: Record<string, React.ReactElement> = {
        connection_request: <PersonAddIcon sx={{ color: '#6C5CE7' }} />,
        connection_accepted: <PersonAddIcon sx={{ color: '#00B894' }} />,
        like: <ThumbUpIcon sx={{ color: '#74B9FF' }} />,
        comment: <CommentIcon sx={{ color: '#00CEC9' }} />,
        job_recommendation: <WorkIcon sx={{ color: '#FDCB6E' }} />,
        achievement: <CelebrationIcon sx={{ color: '#FD79A8' }} />,
        learning: <SchoolIcon sx={{ color: '#A29BFE' }} />,
        group: <GroupIcon sx={{ color: '#6C5CE7' }} />,
        system: <AnnouncementIcon sx={{ color: '#74B9FF' }} />,
        endorsement: <AutoAwesomeIcon sx={{ color: '#FFD700' }} />,
    };
    return iconMap[type] || <AnnouncementIcon sx={{ color: '#A29BFE' }} />;
}

function getIconBg(_type: string) {
    return 'action.hover';
}

export default function Notifications() {
    const [notifications, setNotifications] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'unread'>('all');

    useEffect(() => {
        const load = async () => {
            try {
                const res = await notificationService.getNotifications();
                setNotifications(res.data.notifications || []);
            } catch { /* ignore */ }
            setLoading(false);
        };
        load();
    }, []);

    const handleMarkRead = async (id: string) => {
        try {
            await notificationService.markRead(id);
            setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
        } catch { /* ignore */ }
    };

    const handleMarkAllRead = async () => {
        try {
            await notificationService.markAllRead();
            setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
        } catch { /* ignore */ }
    };

    const filtered = filter === 'unread' ? notifications.filter((n) => !n.read) : notifications;
    const unreadCount = notifications.filter((n) => !n.read).length;

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 700, mx: 'auto', p: { xs: 2, md: 3 } }}>
            {/* Header */}
            <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
                <Box>
                    <Typography variant="h4" fontWeight={800} color="primary">
                        Notifications
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {unreadCount > 0 ? `You have ${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip label="All" size="small" onClick={() => setFilter('all')}
                        color={filter === 'all' ? 'primary' : 'default'}
                        variant={filter === 'all' ? 'filled' : 'outlined'} />
                    <Chip label={`Unread (${unreadCount})`} size="small" onClick={() => setFilter('unread')}
                        color={filter === 'unread' ? 'primary' : 'default'}
                        variant={filter === 'unread' ? 'filled' : 'outlined'} />
                    {unreadCount > 0 && (
                        <Button startIcon={<DoneAllIcon />} size="small" onClick={handleMarkAllRead}
                            sx={{ color: '#A29BFE', fontWeight: 600, fontSize: '0.78rem' }}>
                            Mark all read
                        </Button>
                    )}
                </Box>
            </Box>

            <Card>
                <CardContent sx={{ p: '0 !important' }}>
                    {filtered.length === 0 && (
                        <Box sx={{ py: 6, textAlign: 'center' }}>
                            <Box sx={{
                                width: 80, height: 80, borderRadius: '50%', mx: 'auto', mb: 2,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                bgcolor: 'primary.light',
                            }}>
                                <NotificationsActiveIcon sx={{ fontSize: 36, color: 'primary.main' }} />
                            </Box>
                            <Typography variant="body1" color="text.secondary">
                                {filter === 'unread' ? 'No unread notifications' : 'No notifications yet'}
                            </Typography>
                        </Box>
                    )}
                    {filtered.map((notif, i) => (
                        <Box key={notif.id}>
                            <Box
                                onClick={() => !notif.read && handleMarkRead(notif.id)}
                                sx={{
                                    display: 'flex', gap: 1.5, p: 2, cursor: 'pointer',
                                    bgcolor: notif.read ? 'transparent' : 'action.selected',
                                    transition: 'all 0.2s',
                                    '&:hover': { bgcolor: 'action.hover' },
                                }}
                            >
                                <Box sx={{
                                    width: 44, height: 44, borderRadius: 2.5, display: 'flex',
                                    alignItems: 'center', justifyContent: 'center',
                                    bgcolor: getIconBg(notif.type), flexShrink: 0,
                                }}>
                                    {getIcon(notif.type)}
                                </Box>
                                <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Typography variant="body2" sx={{
                                        lineHeight: 1.5, fontWeight: notif.read ? 400 : 600,
                                    }}>
                                        {notif.message}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.3, display: 'block' }}>
                                        {timeAgo(notif.created_at)}
                                    </Typography>
                                </Box>
                                {!notif.read && (
                                    <FiberManualRecordIcon sx={{ fontSize: 10, color: '#6C5CE7', alignSelf: 'center', flexShrink: 0 }} />
                                )}
                            </Box>
                            {i < filtered.length - 1 && <Divider />}
                        </Box>
                    ))}
                </CardContent>
            </Card>
        </Box >
    );
}
