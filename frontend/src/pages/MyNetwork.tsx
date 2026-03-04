import { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Avatar, Button, Grid, Chip,
    CircularProgress, Tab, Tabs,
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CheckIcon from '@mui/icons-material/Check';
import PeopleIcon from '@mui/icons-material/People';
import GroupsIcon from '@mui/icons-material/Groups';
import PersonOutlineIcon from '@mui/icons-material/PersonOutline';
import { networkService } from '../services/api';

export default function MyNetwork() {
    const [tab, setTab] = useState(0);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [connections, setConnections] = useState<any[]>([]);
    const [pendingRequests, setPendingRequests] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [sentRequests, setSentRequests] = useState<Set<string>>(new Set());
    const [acceptedRequests, setAcceptedRequests] = useState<Set<string>>(new Set());

    useEffect(() => {
        const load = async () => {
            try {
                const [sugRes, connRes, reqRes, statsRes] = await Promise.all([
                    networkService.getSuggestions(),
                    networkService.getConnections(),
                    networkService.getPending(),
                    networkService.getStats(),
                ]);
                setSuggestions(sugRes.data.suggestions || []);
                setConnections(connRes.data.connections || []);
                setPendingRequests(reqRes.data.requests || []);
                setStats(statsRes.data);
            } catch { /* ignore */ }
            setLoading(false);
        };
        load();
    }, []);

    const handleConnect = async (id: string) => {
        try { await networkService.connect(id); setSentRequests((prev) => new Set(prev).add(id)); } catch { /* ignore */ }
    };

    const handleAccept = async (requestId: string) => {
        try { await networkService.acceptRequest(requestId); setAcceptedRequests((prev) => new Set(prev).add(requestId)); } catch { /* ignore */ }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 950, mx: 'auto', p: { xs: 2, md: 3 } }}>
            {/* Header */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h4" fontWeight={800} color="primary">My Network</Typography>
                <Typography variant="body2" color="text.secondary">Grow your professional network</Typography>
            </Box>

            {/* Stats */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                {[
                    { icon: <PeopleIcon />, label: 'Connections', value: stats?.total_connections || connections.length, color: 'primary.main' },
                    { icon: <PersonOutlineIcon />, label: 'Pending', value: pendingRequests.length, color: 'warning.main' },
                    { icon: <GroupsIcon />, label: 'Suggestions', value: suggestions.length, color: 'info.main' },
                ].map((stat) => (
                    <Grid key={stat.label} size={{ xs: 4 }}>
                        <Card>
                            <CardContent sx={{ textAlign: 'center', py: 2 }}>
                                <Box sx={{
                                    width: 44, height: 44, borderRadius: 2.5, mx: 'auto', mb: 1,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    bgcolor: 'action.hover',
                                    color: stat.color,
                                }}>
                                    {stat.icon}
                                </Box>
                                <Typography variant="h4" fontWeight={800} sx={{ color: stat.color }}>{stat.value}</Typography>
                                <Typography variant="caption" color="text.secondary">{stat.label}</Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Tabs */}
            <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2.5 }}>
                <Tab label={`Suggestions (${suggestions.length})`} />
                <Tab label={`Connections (${connections.length})`} />
                <Tab label={`Pending (${pendingRequests.length})`} />
            </Tabs>

            {/* Tab 0: Suggestions */}
            {tab === 0 && (
                <Grid container spacing={2}>
                    {suggestions.map((person: any) => (
                        <Grid key={person.id} size={{ xs: 12, sm: 6, md: 4 }}>
                            <Card>
                                {/* Mini banner */}
                                <Box sx={{
                                    height: 60,
                                    bgcolor: 'primary.dark',
                                    borderRadius: '12px 12px 0 0',
                                }} />
                                <CardContent sx={{ textAlign: 'center', mt: -4, pb: '16px !important' }}>
                                    <Avatar
                                        src={person.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(person.name || '')}&background=1976d2&color=fff&size=128&bold=true`}
                                        sx={{
                                            width: 72, height: 72, mx: 'auto', mb: 1,
                                            border: '3px solid', borderColor: 'background.paper',
                                            bgcolor: 'primary.main', fontSize: '1.5rem', fontWeight: 700,
                                        }}
                                    >{person.name?.charAt(0)}</Avatar>
                                    <Typography variant="body2" fontWeight={600} noWrap>{person.name}</Typography>
                                    <Typography variant="caption" color="text.secondary" noWrap display="block">{person.role}</Typography>
                                    <Typography variant="caption" color="text.secondary" noWrap display="block" sx={{ mb: 1.5 }}>
                                        {person.department}
                                    </Typography>
                                    {person.mutual_connections > 0 && (
                                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1, fontSize: '0.7rem' }}>
                                            👥 {person.mutual_connections} mutual connection{person.mutual_connections > 1 ? 's' : ''}
                                        </Typography>
                                    )}
                                    {sentRequests.has(person.id) ? (
                                        <Button fullWidth variant="outlined" startIcon={<CheckIcon />} disabled
                                            sx={{ borderRadius: 2.5, fontWeight: 600 }}>
                                            Pending
                                        </Button>
                                    ) : (
                                        <Button fullWidth variant="contained" startIcon={<PersonAddIcon />}
                                            onClick={() => handleConnect(person.id)}
                                            sx={{ borderRadius: 2.5, fontWeight: 600 }}>
                                            Connect
                                        </Button>
                                    )}
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                    {suggestions.length === 0 && (
                        <Grid size={{ xs: 12 }}>
                            <Box sx={{ py: 6, textAlign: 'center' }}>
                                <Typography color="text.secondary">No suggestions available right now</Typography>
                            </Box>
                        </Grid>
                    )}
                </Grid>
            )}

            {/* Tab 1: Connections */}
            {tab === 1 && (
                <Card>
                    <CardContent sx={{ p: '0 !important' }}>
                        {connections.map((conn: any, i: number) => (
                            <Box key={conn.id || i}>
                                <Box sx={{
                                    display: 'flex', gap: 1.5, p: 2, alignItems: 'center',
                                    '&:hover': { bgcolor: 'action.hover' },
                                }}>
                                    <Avatar
                                        src={conn.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(conn.name || '')}&background=1976d2&color=fff&size=128&bold=true`}
                                        sx={{ width: 52, height: 52, bgcolor: 'primary.main', fontWeight: 600 }}
                                    >{conn.name?.charAt(0)}</Avatar>
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                        <Typography variant="body2" fontWeight={600}>{conn.name}</Typography>
                                        <Typography variant="caption" color="text.secondary">{conn.role}</Typography>
                                        <Typography variant="caption" color="text.secondary" display="block">{conn.department}</Typography>
                                    </Box>
                                    <Button variant="outlined" size="small" sx={{ borderRadius: 2.5, fontWeight: 600, fontSize: '0.75rem' }}>
                                        Message
                                    </Button>
                                </Box>
                                {i < connections.length - 1 && <Box sx={{ borderBottom: '1px solid', borderColor: 'divider', mx: 2 }} />}
                            </Box>
                        ))}
                        {connections.length === 0 && (
                            <Box sx={{ py: 6, textAlign: 'center' }}>
                                <Typography color="text.secondary">No connections yet. Start networking!</Typography>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            )}

            {/* Tab 2: Pending */}
            {tab === 2 && (
                <Card>
                    <CardContent sx={{ p: '0 !important' }}>
                        {pendingRequests.map((req: any, i: number) => (
                            <Box key={req.id || i}>
                                <Box sx={{
                                    display: 'flex', gap: 1.5, p: 2, alignItems: 'center',
                                    '&:hover': { bgcolor: 'action.hover' },
                                }}>
                                    <Avatar
                                        src={req.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(req.sender_name || '')}&background=1976d2&color=fff&size=128&bold=true`}
                                        sx={{ width: 52, height: 52, bgcolor: 'primary.main', fontWeight: 600 }}
                                    >{req.sender_name?.charAt(0)}</Avatar>
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                        <Typography variant="body2" fontWeight={600}>{req.sender_name}</Typography>
                                        <Typography variant="caption" color="text.secondary">{req.sender_role}</Typography>
                                    </Box>
                                    {acceptedRequests.has(req.id) ? (
                                        <Chip label="Accepted" icon={<CheckIcon sx={{ fontSize: 14 }} />} color="success" size="small" />
                                    ) : (
                                        <Box sx={{ display: 'flex', gap: 1 }}>
                                            <Button variant="contained" size="small" onClick={() => handleAccept(req.id)}
                                                sx={{ borderRadius: 2.5, fontWeight: 600 }}>Accept</Button>
                                            <Button variant="outlined" size="small" sx={{ borderRadius: 2.5, fontWeight: 600 }}>Ignore</Button>
                                        </Box>
                                    )}
                                </Box>
                                {i < pendingRequests.length - 1 && <Box sx={{ borderBottom: '1px solid', borderColor: 'divider', mx: 2 }} />}
                            </Box>
                        ))}
                        {pendingRequests.length === 0 && (
                            <Box sx={{ py: 6, textAlign: 'center' }}>
                                <Typography color="text.secondary">No pending requests</Typography>
                            </Box>
                        )}
                    </CardContent>
                </Card>
            )}
        </Box>
    );
}
