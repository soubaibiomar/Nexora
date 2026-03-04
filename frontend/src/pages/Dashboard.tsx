import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, CircularProgress, Chip, IconButton,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import CodeIcon from '@mui/icons-material/Code';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import DevicesIcon from '@mui/icons-material/Devices';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import RefreshIcon from '@mui/icons-material/Refresh';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import {
    BarChart, Bar, LabelList, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import { dashboardService } from '../services/api';

const COLORS = ['#1976d2', '#dc004e', '#388e3c', '#f57c00', '#7b1fa2', '#0097a7', '#ffb300', '#f44336'];

const SkillTick: React.FC<any> = ({ x, y, payload }) => {
    const label: string = payload?.value ?? '';
    const maxLen = 18;
    const display = label.length > maxLen ? `${label.slice(0, maxLen - 1)}…` : label;
    return (
        <text x={x} y={y} dy={4} textAnchor="end" fill="#a0a0b8" fontSize={11}>
            <title>{label}</title>
            {display}
        </text>
    );
};

const AnimatedNumber: React.FC<{ value?: number }> = ({ value = 0 }) => {
    const [display, setDisplay] = useState(0);
    useEffect(() => {
        let frame: number;
        const duration = 800;
        const start = performance.now();
        const animate = (now: number) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplay(Math.floor(value * eased));
            if (progress < 1) frame = requestAnimationFrame(animate);
        };
        frame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(frame);
    }, [value]);
    return <>{display.toLocaleString()}</>;
};

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<any>(null);
    const [topSkills, setTopSkills] = useState<any[]>([]);
    const [departments, setDepartments] = useState<any[]>([]);
    const [skillDistribution, setSkillDistribution] = useState<any[]>([]);
    const [projectStatus, setProjectStatus] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [selectedSkillCategory, setSelectedSkillCategory] = useState<string | 'all'>('all');

    useEffect(() => { loadDashboardData(); }, []);

    const loadDashboardData = async () => {
        setLoading(true);
        try {
            const [statsRes, topSkillsRes, deptsRes, distRes, projectRes] = await Promise.all([
                dashboardService.getStats(),
                dashboardService.getTopSkills(10),
                dashboardService.getDepartments(),
                dashboardService.getSkillDistribution(),
                dashboardService.getProjectStatus(),
            ]);
            setStats(statsRes.data); setTopSkills(topSkillsRes.data);
            setDepartments(deptsRes.data); setSkillDistribution(distRes.data);
            setProjectStatus(projectRes.data); setLastUpdated(new Date());
        } catch (error) { console.error('Error loading dashboard:', error); }
        finally { setLoading(false); }
    };

    const statCards = [
        { title: 'Total Experts', key: 'persons', icon: <PeopleIcon sx={{ fontSize: 28 }} />, color: '#1976d2' },
        { title: 'Skills', key: 'skills', icon: <CodeIcon sx={{ fontSize: 28 }} />, color: '#388e3c' },
        { title: 'Projects', key: 'projects', icon: <FolderIcon sx={{ fontSize: 28 }} />, color: '#f57c00' },
        { title: 'Documents', key: 'documents', icon: <DescriptionIcon sx={{ fontSize: 28 }} />, color: '#dc004e' },
        { title: 'Technologies', key: 'technologies', icon: <DevicesIcon sx={{ fontSize: 28 }} />, color: '#0097a7' },
    ];

    const uniqueSkillCategories = Array.from(new Set((topSkills || []).map((s: any) => s.category).filter(Boolean)));
    const filteredTopSkills = selectedSkillCategory === 'all' ? topSkills : topSkills.filter((s: any) => s.category === selectedSkillCategory);

    if (loading && !stats) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress size={50} sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: { xs: 2, md: 4 } }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                    <Box sx={{
                        width: 44, height: 44, borderRadius: 2.5, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        bgcolor: 'primary.light',
                    }}>
                        <AutoAwesomeIcon sx={{ color: 'primary.main', fontSize: 24 }} />
                    </Box>
                    <Box>
                        <Typography variant="h4" fontWeight={800} color="primary">
                            Analytics Dashboard
                        </Typography>
                    </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                        Organization knowledge metrics and skill intelligence
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {lastUpdated && (
                            <Typography variant="caption" color="text.secondary">Updated {lastUpdated.toLocaleTimeString()}</Typography>
                        )}
                        <IconButton size="small" onClick={loadDashboardData} disabled={loading}
                            sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, width: 32, height: 32 }}>
                            <RefreshIcon fontSize="small" sx={{ transition: 'transform 0.4s', transform: loading ? 'rotate(180deg)' : 'none' }} />
                        </IconButton>
                    </Box>
                </Box>
            </Box>

            {/* Stat Cards */}
            <Grid container spacing={2.5} sx={{ mb: 4 }}>
                {statCards.map((card) => (
                    <Grid size={{ xs: 12, sm: 6, md: 2.4 }} key={card.key}>
                        <Card sx={{
                            position: 'relative', overflow: 'hidden',
                        }}>
                            <CardContent sx={{ position: 'relative' }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Box>
                                        <Typography variant="caption" color="text.secondary" sx={{ mb: 0.5, display: 'block', fontWeight: 500 }}>
                                            {card.title}
                                        </Typography>
                                        <Typography variant="h4" sx={{ fontWeight: 800, color: card.color, lineHeight: 1 }}>
                                            <AnimatedNumber value={stats?.[card.key]} />
                                        </Typography>
                                    </Box>
                                    <Box sx={{
                                        width: 48, height: 48, borderRadius: 3, display: 'flex',
                                        alignItems: 'center', justifyContent: 'center',
                                        bgcolor: `${card.color}20`,
                                        color: card.color,
                                    }}>
                                        {card.icon}
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={2.5}>
                {/* Top Skills */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card sx={{ height: 420 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, mb: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <TrendingUpIcon sx={{ color: '#6C5CE7' }} />
                                    <Typography variant="h6" fontWeight={700}>Top Skills by Demand</Typography>
                                </Box>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    <Chip label="All" size="small"
                                        onClick={() => setSelectedSkillCategory('all')}
                                        color={selectedSkillCategory === 'all' ? 'primary' : 'default'}
                                        variant={selectedSkillCategory === 'all' ? 'filled' : 'outlined'} />
                                    {uniqueSkillCategories.slice(0, 3).map((category) => (
                                        <Chip key={category} label={category} size="small"
                                            onClick={() => setSelectedSkillCategory(category)}
                                            color={selectedSkillCategory === category ? 'primary' : 'default'}
                                            variant={selectedSkillCategory === category ? 'filled' : 'outlined'} />
                                    ))}
                                </Box>
                            </Box>
                            <ResponsiveContainer width="100%" height={320}>
                                <BarChart data={filteredTopSkills.slice(0, 8)} layout="vertical" margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                                    <XAxis type="number" stroke="#666" />
                                    <YAxis dataKey="name" type="category" width={160} tick={<SkillTick />} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 8 }} />
                                    <Bar dataKey="demand" radius={[0, 6, 6, 0]} isAnimationActive>
                                        {filteredTopSkills.slice(0, 8).map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                        <LabelList dataKey="demand" position="right" fill="#a0a0b8" fontSize={11} />
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Skill Distribution */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card sx={{ height: 420 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <CodeIcon sx={{ color: '#00CEC9' }} />
                                <Typography variant="h6" fontWeight={700}>Skills by Category</Typography>
                            </Box>
                            <ResponsiveContainer width="100%" height={320}>
                                <PieChart>
                                    <Pie data={skillDistribution} dataKey="skill_count" nameKey="category"
                                        cx="50%" cy="50%" outerRadius={110} innerRadius={55}
                                        label={({ name, percent = 0 }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                        labelLine={{ stroke: 'rgba(255,255,255,0.2)' }}>
                                        {skillDistribution.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 8 }} />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Department Stats */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card sx={{ height: 420 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <PeopleIcon sx={{ color: '#74B9FF' }} />
                                <Typography variant="h6" fontWeight={700}>Department Overview</Typography>
                            </Box>
                            <ResponsiveContainer width="100%" height={320}>
                                <BarChart data={departments.slice(0, 6)}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                                    <XAxis dataKey="department" stroke="#666" />
                                    <YAxis stroke="#666" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1a1a2e', border: '1px solid rgba(108,92,231,0.2)', borderRadius: 8 }} />
                                    <Legend />
                                    <Bar dataKey="person_count" name="Team Size" fill="#6C5CE7" radius={[6, 6, 0, 0]} />
                                    <Bar dataKey="avg_expertise" name="Avg Expertise" fill="#00CEC9" radius={[6, 6, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Project Status */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <FolderIcon sx={{ color: '#FDCB6E' }} />
                                <Typography variant="h6" fontWeight={700}>Project Status</Typography>
                            </Box>
                            <Grid container spacing={2}>
                                {projectStatus.map((status, index) => (
                                    <Grid size={{ xs: 6, sm: 3 }} key={status.status}>
                                        <Box sx={{
                                            p: 2.5, textAlign: 'center', borderRadius: 3,
                                            bgcolor: `${COLORS[index % COLORS.length]}10`,
                                            border: `1px solid ${COLORS[index % COLORS.length]}20`,
                                        }}>
                                            <Typography variant="h4" sx={{ color: COLORS[index % COLORS.length], fontWeight: 800 }}>
                                                {status.count}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize', fontWeight: 500 }}>
                                                {status.status}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Avg ${(status.avg_budget / 1000000).toFixed(1)}M
                                            </Typography>
                                        </Box>
                                    </Grid>
                                ))}
                            </Grid>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
};

export default Dashboard;
