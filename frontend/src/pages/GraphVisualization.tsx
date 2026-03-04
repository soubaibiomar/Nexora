import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, Button, CircularProgress, Chip,
    Paper, Avatar, Divider, List, ListItem, ListItemAvatar, ListItemText,
    ListItemSecondaryAction, IconButton, Tooltip, Alert, Snackbar, TextField,
    ToggleButtonGroup, ToggleButton,
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import LockIcon from '@mui/icons-material/Lock';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import RefreshIcon from '@mui/icons-material/Refresh';
import HubIcon from '@mui/icons-material/Hub';
import GroupsIcon from '@mui/icons-material/Groups';
import SendIcon from '@mui/icons-material/Send';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import ForceGraph3D from 'react-force-graph-3d';
import { graphService } from '../services/api';

interface GraphNode { id: string; label: string; type: string; properties?: any; }
interface GraphLink { source: string; target: string; type: string; }
interface GraphData { nodes: GraphNode[]; links: GraphLink[]; }
interface ViewRequest {
    id: string; connection_id: string; connection_name: string;
    connection_role: string; status: 'pending' | 'approved' | 'denied';
    requested_at: string; responded_at: string | null;
}

const GraphVisualization: React.FC = () => {
    const isAdmin = localStorage.getItem('username') === 'admin';
    const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
    const [loading, setLoading] = useState(false);
    const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
    const [viewRequests, setViewRequests] = useState<ViewRequest[]>([]);
    const [totalConnections, setTotalConnections] = useState(0);
    const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
        open: false, message: '', severity: 'info',
    });
    const [nodeFilter, setNodeFilter] = useState<string>('');
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [stats, setStats] = useState<any>(null);
    const fgRef = useRef<any>(null);

    useEffect(() => {
        if (isAdmin) { loadFullGraph(); loadStats(); }
        else { loadMyNetwork(); loadViewRequests(); }
    }, [isAdmin]);

    useEffect(() => {
        if (isAdmin) { const timer = setTimeout(() => loadFullGraph(), 500); return () => clearTimeout(timer); }
    }, [nodeFilter, searchQuery]);

    const loadFullGraph = async () => {
        setLoading(true);
        try {
            const response = await graphService.getNodes(nodeFilter || undefined, 200, searchQuery || undefined);
            const nodes = response.data.nodes;
            const links: GraphLink[] = [];
            for (let i = 0; i < Math.min(nodes.length * 2, 300); i++) {
                const sourceIdx = Math.floor(Math.random() * nodes.length);
                const targetIdx = Math.floor(Math.random() * nodes.length);
                if (sourceIdx !== targetIdx) {
                    links.push({ source: nodes[sourceIdx].id, target: nodes[targetIdx].id, type: 'CONNECTED_TO' });
                }
            }
            setGraphData({ nodes, links });
        } catch (error) { console.error('Error loading graph:', error); }
        finally { setLoading(false); }
    };

    const loadStats = async () => {
        try { const response = await graphService.getStats(); setStats(response.data); }
        catch (error) { console.error('Error loading stats:', error); }
    };

    const handleAdminNodeClick = useCallback(async (node: any) => {
        setSelectedNode(node);
        try {
            const response = await graphService.expand(node.id, 1);
            const newNodes = response.data.nodes.filter(
                (n: GraphNode) => !graphData.nodes.find((existing) => existing.id === n.id)
            );
            setGraphData((prev) => ({ nodes: [...prev.nodes, ...newNodes], links: [...prev.links, ...response.data.links] }));
        } catch (error) { console.error('Error expanding node:', error); }
    }, [graphData.nodes]);

    const loadMyNetwork = async () => {
        setLoading(true);
        try {
            const response = await graphService.getMyNetwork();
            const { nodes, links, total_connections } = response.data;
            setGraphData({ nodes, links }); setTotalConnections(total_connections);
        } catch (error) { console.error('Error loading network:', error); }
        finally { setLoading(false); }
    };

    const loadViewRequests = async () => {
        try { const response = await graphService.getViewRequests(); setViewRequests(response.data.requests); }
        catch (error) { console.error('Error loading view requests:', error); }
    };

    const handleRequestView = async (connectionId: string) => {
        try {
            const response = await graphService.requestViewConnections(connectionId);
            setSnackbar({ open: true, message: response.data.message, severity: 'success' }); loadViewRequests();
        } catch (error: any) {
            setSnackbar({ open: true, message: error.response?.data?.detail || 'Failed to send request', severity: 'error' });
        }
    };

    const handleSimulateApproval = async (requestId: string) => {
        try {
            const response = await graphService.simulateResponse(requestId, true);
            setSnackbar({ open: true, message: response.data.message, severity: 'success' });
            loadViewRequests(); loadMyNetwork();
        } catch { setSnackbar({ open: true, message: 'Failed to simulate approval', severity: 'error' }); }
    };

    const handleUserNodeClick = useCallback((node: any) => { setSelectedNode(node); }, []);

    const getNodeColor = (node: GraphNode) => {
        if (isAdmin) {
            const c: Record<string, string> = { Person: '#6C5CE7', Skill: '#00B894', Project: '#FDCB6E', Document: '#FD79A8', Technology: '#74B9FF' };
            return c[node.type] || '#A29BFE';
        }
        const c: Record<string, string> = { User: '#6C5CE7', Connection: '#00B894', SecondDegree: '#FDCB6E' };
        return c[node.type] || '#A29BFE';
    };

    const getNodeSize = (node: GraphNode) => {
        if (node.type === 'User') return 12;
        if (node.type === 'Connection') return 7;
        return 5;
    };

    const getRequestStatus = (connectionId: string) => viewRequests.find(r => r.connection_id === connectionId);
    const handleZoomIn = () => { if (fgRef.current) fgRef.current.camera().position.z *= 0.8; };
    const handleZoomOut = () => { if (fgRef.current) fgRef.current.camera().position.z *= 1.2; };

    const pendingCount = viewRequests.filter(r => r.status === 'pending').length;
    const approvedCount = viewRequests.filter(r => r.status === 'approved').length;

    return (
        <Box sx={{ p: { xs: 1, md: 2 }, height: 'calc(100vh - 48px)' }}>
            <Grid container spacing={2} sx={{ height: '100%' }}>
                {/* Left Panel */}
                <Grid size={{ xs: 12, md: 3 }}>
                    <Card sx={{ height: '100%', overflow: 'auto' }}>
                        <CardContent sx={{ p: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                {isAdmin
                                    ? <AdminPanelSettingsIcon sx={{ color: '#FDCB6E' }} />
                                    : <HubIcon sx={{ color: '#6C5CE7' }} />}
                                <Typography variant="h6" fontWeight={700}>
                                    {isAdmin ? 'Full Graph Explorer' : 'My Network Graph'}
                                </Typography>
                            </Box>

                            {isAdmin && (
                                <Chip icon={<AdminPanelSettingsIcon />} label="Admin View — Full Access" size="small"
                                    color="warning" sx={{ mb: 2, fontWeight: 600 }} />
                            )}

                            {!isAdmin && (
                                <Alert severity="info" sx={{ mb: 2 }}>
                                    You can only see <strong>your direct connections</strong>. Request permission to view a connection's network.
                                </Alert>
                            )}

                            {isAdmin && (
                                <>
                                    <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Filter by Type</Typography>
                                    <ToggleButtonGroup value={nodeFilter} exclusive onChange={(_, v) => setNodeFilter(v || '')}
                                        sx={{ mb: 2, flexWrap: 'wrap' }} size="small">
                                        <ToggleButton value="">All</ToggleButton>
                                        <ToggleButton value="Person">Person</ToggleButton>
                                        <ToggleButton value="Skill">Skill</ToggleButton>
                                        <ToggleButton value="Project">Project</ToggleButton>
                                    </ToggleButtonGroup>
                                    <TextField fullWidth size="small" placeholder="Search node name..." value={searchQuery}
                                        onChange={(e: any) => setSearchQuery(e.target.value)} sx={{ mb: 2 }} />
                                </>
                            )}

                            {!isAdmin && (
                                <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
                                    <Chip icon={<GroupsIcon />} label={`${totalConnections} Connections`} size="small" color="success" />
                                    <Chip icon={<HourglassEmptyIcon />} label={`${pendingCount} Pending`} size="small" color="warning" />
                                    <Chip icon={<CheckCircleIcon />} label={`${approvedCount} Approved`} size="small" color="primary" />
                                </Box>
                            )}

                            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                <Button fullWidth variant="outlined" size="small" startIcon={<RefreshIcon />}
                                    onClick={isAdmin ? loadFullGraph : loadMyNetwork}
                                    sx={{ borderRadius: 2.5, textTransform: 'none' }}>Reload</Button>
                                <Button variant="outlined" size="small" onClick={handleZoomIn} sx={{ minWidth: 40, borderRadius: 2.5 }}>
                                    <ZoomInIcon fontSize="small" />
                                </Button>
                                <Button variant="outlined" size="small" onClick={handleZoomOut} sx={{ minWidth: 40, borderRadius: 2.5 }}>
                                    <ZoomOutIcon fontSize="small" />
                                </Button>
                            </Box>

                            <Divider sx={{ my: 2 }} />

                            {isAdmin && stats && (
                                <Box sx={{ mb: 2 }}>
                                    <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Graph Stats</Typography>
                                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                        {stats.nodes?.map((s: any) => (
                                            <Chip key={s.type} label={`${s.type}: ${s.count}`} size="small"
                                                sx={{ bgcolor: `${getNodeColor({ type: s.type } as GraphNode)}22` }} />
                                        ))}
                                    </Box>
                                </Box>
                            )}

                            {selectedNode && (
                                <Paper sx={{ p: 2, mb: 2, borderRadius: 1 }} variant="outlined">
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                                        <Avatar sx={{ bgcolor: getNodeColor(selectedNode), width: 40, height: 40, fontWeight: 600 }}>
                                            {selectedNode.label.charAt(0)}
                                        </Avatar>
                                        <Box>
                                            <Typography variant="body2" fontWeight={600}>{selectedNode.label}</Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                {selectedNode.properties?.role || selectedNode.type}
                                            </Typography>
                                        </Box>
                                    </Box>
                                    {selectedNode.properties?.department && (
                                        <Chip label={selectedNode.properties.department} size="small" sx={{ mb: 1, fontSize: '0.7rem' }} />
                                    )}

                                    {!isAdmin && selectedNode.type === 'Connection' && (() => {
                                        const req = getRequestStatus(selectedNode.id);
                                        if (req?.status === 'approved') {
                                            return <Chip icon={<LockOpenIcon />} label="Network visible" size="small" color="success" sx={{ mt: 1 }} />;
                                        }
                                        if (req?.status === 'pending') {
                                            return (
                                                <Box sx={{ mt: 1 }}>
                                                    <Chip icon={<HourglassEmptyIcon />} label="Request pending..." size="small" color="warning" sx={{ mb: 1 }} />
                                                    <Button fullWidth size="small" variant="outlined" color="success"
                                                        onClick={() => handleSimulateApproval(req.id)}>
                                                        Simulate Approval (Demo)
                                                    </Button>
                                                </Box>
                                            );
                                        }
                                        return (
                                            <Button fullWidth size="small" variant="contained" startIcon={<VisibilityIcon />}
                                                onClick={() => handleRequestView(selectedNode.id)}
                                                sx={{ mt: 1, borderRadius: 2.5, textTransform: 'none' }}>
                                                Request to view connections
                                            </Button>
                                        );
                                    })()}

                                    {!isAdmin && selectedNode.type === 'SecondDegree' && (
                                        <Chip icon={<LockOpenIcon />} label="2nd degree connection" size="small" color="warning" sx={{ mt: 1 }} />
                                    )}

                                    {isAdmin && (
                                        <Chip label={selectedNode.type} size="small" sx={{ mt: 1, bgcolor: `${getNodeColor(selectedNode)}22` }} />
                                    )}
                                </Paper>
                            )}

                            <Divider sx={{ my: 2 }} />

                            {!isAdmin && (
                                <>
                                    <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                        <SendIcon sx={{ fontSize: 16 }} /> View Requests
                                    </Typography>
                                    {viewRequests.length === 0 ? (
                                        <Typography variant="caption" color="text.secondary">
                                            No requests yet. Click a connection node to request access to their network.
                                        </Typography>
                                    ) : (
                                        <List dense sx={{ p: 0 }}>
                                            {viewRequests.map((req) => (
                                                <ListItem key={req.id} sx={{
                                                    px: 1, borderRadius: 1, mb: 0.5,
                                                    bgcolor: req.status === 'approved' ? 'success.light'
                                                        : req.status === 'pending' ? 'warning.light' : 'error.light',
                                                }}>
                                                    <ListItemAvatar sx={{ minWidth: 36 }}>
                                                        <Avatar sx={{
                                                            width: 28, height: 28, fontSize: '0.75rem',
                                                            bgcolor: req.status === 'approved' ? 'success.main' : req.status === 'pending' ? 'warning.main' : 'error.main',
                                                        }}>{req.connection_name.charAt(0)}</Avatar>
                                                    </ListItemAvatar>
                                                    <ListItemText primary={req.connection_name} secondary={req.status}
                                                        primaryTypographyProps={{ fontSize: '0.75rem', fontWeight: 600 }}
                                                        secondaryTypographyProps={{ fontSize: '0.65rem', textTransform: 'capitalize' }} />
                                                    {req.status === 'pending' && (
                                                        <ListItemSecondaryAction>
                                                            <Tooltip title="Simulate approval (demo)">
                                                                <IconButton size="small" onClick={() => handleSimulateApproval(req.id)}>
                                                                    <CheckCircleIcon sx={{ fontSize: 16, color: '#00B894' }} />
                                                                </IconButton>
                                                            </Tooltip>
                                                        </ListItemSecondaryAction>
                                                    )}
                                                    {req.status === 'approved' && <CheckCircleIcon sx={{ fontSize: 16, color: '#00B894' }} />}
                                                    {req.status === 'denied' && <CancelIcon sx={{ fontSize: 16, color: '#ef4444' }} />}
                                                </ListItem>
                                            ))}
                                        </List>
                                    )}
                                    <Divider sx={{ my: 2 }} />
                                </>
                            )}

                            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>Legend</Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                                {isAdmin ? (
                                    ['Person', 'Skill', 'Project', 'Document', 'Technology'].map((type) => (
                                        <Box key={type} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: getNodeColor({ type } as GraphNode) }} />
                                            <Typography variant="caption" color="text.secondary">{type}</Typography>
                                        </Box>
                                    ))
                                ) : (
                                    <>
                                        {[
                                            { color: '#6C5CE7', label: 'You' },
                                            { color: '#00B894', label: '1st Degree Connection' },
                                            { color: '#FDCB6E', label: '2nd Degree (Approved)' },
                                        ].map(({ color, label }) => (
                                            <Box key={label} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: color }} />
                                                <Typography variant="caption" color="text.secondary">{label}</Typography>
                                            </Box>
                                        ))}
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                                            <LockIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
                                            <Typography variant="caption" color="text.secondary">Locked = request needed</Typography>
                                        </Box>
                                    </>
                                )}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Graph View */}
                <Grid size={{ xs: 12, md: 9 }}>
                    <Card sx={{ height: '100%', position: 'relative', overflow: 'hidden' }}>
                        {loading ? (
                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 2 }}>
                                <CircularProgress size={50} sx={{ color: isAdmin ? '#FDCB6E' : '#6C5CE7' }} />
                                <Typography variant="body2" color="text.secondary">
                                    {isAdmin ? 'Loading full graph...' : 'Loading your network...'}
                                </Typography>
                            </Box>
                        ) : (
                            <ForceGraph3D
                                ref={fgRef}
                                graphData={graphData}
                                nodeLabel={(node: any) => {
                                    const n = node as GraphNode;
                                    const role = n.properties?.role ? ` — ${n.properties.role}` : '';
                                    const dept = n.properties?.department ? ` (${n.properties.department})` : '';
                                    return `${n.label}${role}${dept}`;
                                }}
                                nodeColor={(node: any) => getNodeColor(node as GraphNode)}
                                nodeRelSize={isAdmin ? 6 : 1}
                                nodeVal={isAdmin ? undefined : (node: any) => getNodeSize(node as GraphNode)}
                                linkColor={(link: any) => {
                                    if (isAdmin) return 'rgba(162,155,254,0.15)';
                                    const l = link as GraphLink;
                                    return l.type === 'KNOWS' ? 'rgba(253,203,110,0.3)' : 'rgba(0,184,148,0.4)';
                                }}
                                linkWidth={(link: any) => {
                                    if (isAdmin) return 1;
                                    const l = link as GraphLink;
                                    return l.type === 'KNOWS' ? 0.8 : 1.5;
                                }}
                                linkDirectionalParticles={isAdmin ? 0 : 2}
                                linkDirectionalParticleSpeed={0.005}
                                linkDirectionalParticleWidth={1.5}
                                linkDirectionalParticleColor={() => 'rgba(108,92,231,0.6)'}
                                backgroundColor="#0a0a0a"
                                onNodeClick={isAdmin ? handleAdminNodeClick : handleUserNodeClick}
                            />
                        )}

                        <Box sx={{
                            position: 'absolute', top: 16, right: 16,
                            bgcolor: 'background.paper', borderRadius: 1, px: 2, py: 1,
                            boxShadow: 1,
                        }}>
                            {isAdmin ? (
                                <Typography variant="caption" color="text.secondary">
                                    <AdminPanelSettingsIcon sx={{ fontSize: 14, verticalAlign: 'middle', mr: 0.5, color: '#FDCB6E' }} />
                                    Admin — <strong style={{ color: '#FDCB6E' }}>{graphData.nodes.length}</strong> nodes ·{' '}
                                    <strong style={{ color: '#FDCB6E' }}>{graphData.links.length}</strong> links
                                </Typography>
                            ) : (
                                <Typography variant="caption" color="text.secondary">
                                    <strong style={{ color: '#6C5CE7' }}>{graphData.nodes.length}</strong> nodes ·{' '}
                                    <strong style={{ color: '#00B894' }}>{graphData.links.length}</strong> connections
                                </Typography>
                            )}
                        </Box>
                    </Card>
                </Grid>
            </Grid>

            <Snackbar open={snackbar.open} autoHideDuration={4000}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
                <Alert onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                    severity={snackbar.severity} sx={{ borderRadius: 2.5, width: '100%' }}>
                    {snackbar.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default GraphVisualization;
