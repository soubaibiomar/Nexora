import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, CircularProgress, Chip, IconButton,
    Avatar, LinearProgress, Button,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import CodeIcon from '@mui/icons-material/Code';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import DevicesIcon from '@mui/icons-material/Devices';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import RefreshIcon from '@mui/icons-material/Refresh';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import WorkIcon from '@mui/icons-material/Work';
import SchoolIcon from '@mui/icons-material/School';
import SearchIcon from '@mui/icons-material/Search';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import PersonIcon from '@mui/icons-material/Person';
import BarChartIcon from '@mui/icons-material/BarChart';
import GroupIcon from '@mui/icons-material/Group';
import {
    BarChart, Bar, LabelList, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import { dashboardService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

const COLORS = ['#6C63FF', '#A78BFA', '#00CEC9', '#FDCB6E', '#FF6B6B', '#74B9FF', '#55EFC4', '#FD79A8'];

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

// ══════════════════════════════════════════════════════════════════
//  ADMIN ANALYTICS DASHBOARD
// ══════════════════════════════════════════════════════════════════
const AdminDashboard: React.FC = () => {
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
        { title: 'Total Experts', key: 'persons', icon: <PeopleIcon sx={{ fontSize: 28 }} />, color: '#6C63FF' },
        { title: 'Skills', key: 'skills', icon: <CodeIcon sx={{ fontSize: 28 }} />, color: '#00CEC9' },
        { title: 'Projects', key: 'projects', icon: <FolderIcon sx={{ fontSize: 28 }} />, color: '#FDCB6E' },
        { title: 'Documents', key: 'documents', icon: <DescriptionIcon sx={{ fontSize: 28 }} />, color: '#FF6B6B' },
        { title: 'Technologies', key: 'technologies', icon: <DevicesIcon sx={{ fontSize: 28 }} />, color: '#74B9FF' },
    ];

    const uniqueSkillCategories = Array.from(new Set((topSkills || []).map((s: any) => s.category).filter(Boolean)));
    const filteredTopSkills = selectedSkillCategory === 'all' ? topSkills : topSkills.filter((s: any) => s.category === selectedSkillCategory);

    if (loading && !stats) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress size={50} sx={{ color: '#6C63FF' }} />
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
                        background: 'linear-gradient(135deg, rgba(108,99,255,0.15), rgba(167,139,250,0.15))',
                    }}>
                        <AdminPanelSettingsIcon sx={{ color: '#6C63FF', fontSize: 24 }} />
                    </Box>
                    <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="h4" fontWeight={800} sx={{
                                background: 'linear-gradient(135deg, #6C63FF, #A78BFA)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                            }}>
                                Admin Dashboard
                            </Typography>
                            <Chip label="Admin" size="small" sx={{
                                bgcolor: 'rgba(108,99,255,0.12)', color: '#A78BFA',
                                fontWeight: 700, fontSize: '0.65rem', height: 22,
                                border: '1px solid rgba(108,99,255,0.2)',
                            }} />
                        </Box>
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
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            '&:hover': { transform: 'translateY(-2px)', boxShadow: `0 8px 25px ${card.color}20` },
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
                                        bgcolor: `${card.color}15`,
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
                                    <TrendingUpIcon sx={{ color: '#6C63FF' }} />
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
                                    <Bar dataKey="person_count" name="Team Size" fill="#6C63FF" radius={[6, 6, 0, 0]} />
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
                                            transition: 'transform 0.2s',
                                            '&:hover': { transform: 'scale(1.02)' },
                                        }}>
                                            <Typography variant="h4" sx={{ color: COLORS[index % COLORS.length], fontWeight: 800 }}>
                                                {status.count}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize', fontWeight: 500 }}>
                                                {status.status}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary">
                                                Avg ${((status.avg_budget || 0) / 1000000).toFixed(1)}M
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


// ══════════════════════════════════════════════════════════════════
//  USER PERSONAL DASHBOARD
// ══════════════════════════════════════════════════════════════════
const UserDashboard: React.FC = () => {
    const { fullName, username } = useAuth();
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState<any>(null);
    const [topSkills, setTopSkills] = useState<any[]>([]);
    const [recentActivity] = useState([
        { type: 'skill', text: 'Added React to your profile', time: '2 hours ago', color: '#6C63FF' },
        { type: 'connection', text: 'Connected with Sarah Chen', time: '5 hours ago', color: '#00CEC9' },
        { type: 'document', text: 'Read "ML Best Practices"', time: '1 day ago', color: '#FDCB6E' },
        { type: 'job', text: 'Applied for Senior Developer', time: '2 days ago', color: '#FF6B6B' },
    ]);
    const [learningProgress] = useState([
        { skill: 'React', progress: 78, color: '#6C63FF' },
        { skill: 'TypeScript', progress: 65, color: '#A78BFA' },
        { skill: 'Python', progress: 90, color: '#00CEC9' },
        { skill: 'Docker', progress: 45, color: '#FDCB6E' },
    ]);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                const [statsRes, skillsRes] = await Promise.all([
                    dashboardService.getStats(),
                    dashboardService.getTopSkills(6),
                ]);
                setStats(statsRes.data);
                setTopSkills(skillsRes.data);
            } catch { /* ignore */ }
            finally { setLoading(false); }
        };
        loadData();
    }, []);

    if (loading && !stats) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
                <CircularProgress size={50} sx={{ color: '#6C63FF' }} />
            </Box>
        );
    }

    const quickActions = [
        { label: 'Find Experts', icon: <SearchIcon />, path: '/network', color: '#6C63FF' },
        { label: 'Browse Jobs', icon: <WorkIcon />, path: '/jobs', color: '#00CEC9' },
        { label: 'Start Learning', icon: <SchoolIcon />, path: '/learning', color: '#FDCB6E' },
        { label: 'Skill Map', icon: <BarChartIcon />, path: '/skill-map', color: '#A78BFA' },
    ];

    return (
        <Box sx={{ p: { xs: 2, md: 4 } }}>
            {/* Welcome Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                    <Avatar sx={{
                        width: 56, height: 56,
                        background: 'linear-gradient(135deg, #6C63FF, #A78BFA)',
                        fontSize: 24, fontWeight: 800,
                    }}>
                        {(fullName || 'U').charAt(0)}
                    </Avatar>
                    <Box>
                        <Typography variant="h4" fontWeight={800} sx={{
                            background: 'linear-gradient(135deg, #E8E8F0, #A78BFA)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                        }}>
                            Welcome back, {fullName?.split(' ')[0] || 'User'} 👋
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            @{username} • Here's your personal workspace overview
                        </Typography>
                    </Box>
                </Box>
            </Box>

            {/* Quick Actions */}
            <Grid container spacing={2} sx={{ mb: 4 }}>
                {quickActions.map((action) => (
                    <Grid size={{ xs: 6, sm: 3 }} key={action.label}>
                        <Card
                            component={Link}
                            to={action.path}
                            sx={{
                                textDecoration: 'none',
                                cursor: 'pointer',
                                transition: 'all 0.25s',
                                border: `1px solid ${action.color}15`,
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: `0 12px 30px ${action.color}20`,
                                    borderColor: `${action.color}30`,
                                },
                            }}
                        >
                            <CardContent sx={{ textAlign: 'center', py: 3 }}>
                                <Box sx={{
                                    width: 48, height: 48, borderRadius: 3, mx: 'auto', mb: 1.5,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    bgcolor: `${action.color}12`, color: action.color,
                                }}>
                                    {React.cloneElement(action.icon as React.ReactElement<any>, { sx: { fontSize: 24 } })}
                                </Box>
                                <Typography variant="body2" fontWeight={600} color="text.primary">
                                    {action.label}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Grid container spacing={2.5}>
                {/* Learning Progress */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                                <RocketLaunchIcon sx={{ color: '#6C63FF' }} />
                                <Typography variant="h6" fontWeight={700}>Learning Progress</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {learningProgress.map((item) => (
                                    <Box key={item.skill}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                            <Typography variant="body2" fontWeight={600}>{item.skill}</Typography>
                                            <Typography variant="caption" color="text.secondary">{item.progress}%</Typography>
                                        </Box>
                                        <LinearProgress
                                            variant="determinate"
                                            value={item.progress}
                                            sx={{
                                                height: 8, borderRadius: 4,
                                                bgcolor: `${item.color}15`,
                                                '& .MuiLinearProgress-bar': {
                                                    borderRadius: 4,
                                                    background: `linear-gradient(90deg, ${item.color}, ${item.color}AA)`,
                                                },
                                            }}
                                        />
                                    </Box>
                                ))}
                            </Box>
                            <Button
                                component={Link}
                                to="/learning"
                                fullWidth
                                variant="outlined"
                                size="small"
                                sx={{
                                    mt: 2.5, borderRadius: 2, textTransform: 'none', fontWeight: 600,
                                    borderColor: 'rgba(108,99,255,0.3)', color: '#A78BFA',
                                    '&:hover': { borderColor: '#6C63FF', bgcolor: 'rgba(108,99,255,0.05)' },
                                }}
                            >
                                View All Learning Paths →
                            </Button>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Recent Activity */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                                <EmojiEventsIcon sx={{ color: '#FDCB6E' }} />
                                <Typography variant="h6" fontWeight={700}>Recent Activity</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                                {recentActivity.map((item, idx) => (
                                    <Box key={idx} sx={{
                                        display: 'flex', alignItems: 'center', gap: 1.5,
                                        p: 1.5, borderRadius: 2,
                                        bgcolor: `${item.color}08`,
                                        border: `1px solid ${item.color}12`,
                                        transition: 'all 0.2s',
                                        '&:hover': { bgcolor: `${item.color}12` },
                                    }}>
                                        <Box sx={{
                                            width: 8, height: 8, borderRadius: '50%',
                                            bgcolor: item.color, flexShrink: 0,
                                        }} />
                                        <Box sx={{ flex: 1 }}>
                                            <Typography variant="body2" fontWeight={500}>{item.text}</Typography>
                                            <Typography variant="caption" color="text.secondary">{item.time}</Typography>
                                        </Box>
                                    </Box>
                                ))}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Trending Skills */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <TrendingUpIcon sx={{ color: '#00CEC9' }} />
                                <Typography variant="h6" fontWeight={700}>Trending Skills</Typography>
                            </Box>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {topSkills.slice(0, 10).map((skill: any, idx: number) => (
                                    <Chip
                                        key={skill.name || idx}
                                        label={`${skill.name} (${skill.demand || 0})`}
                                        size="small"
                                        sx={{
                                            bgcolor: `${COLORS[idx % COLORS.length]}12`,
                                            color: COLORS[idx % COLORS.length],
                                            border: `1px solid ${COLORS[idx % COLORS.length]}25`,
                                            fontWeight: 600, fontSize: '0.75rem',
                                        }}
                                    />
                                ))}
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                {/* Platform Stats Summary */}
                <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <GroupIcon sx={{ color: '#A78BFA' }} />
                                <Typography variant="h6" fontWeight={700}>Platform Overview</Typography>
                            </Box>
                            <Grid container spacing={2}>
                                {[
                                    { label: 'Experts', value: stats?.persons || 0, icon: <PersonIcon />, color: '#6C63FF' },
                                    { label: 'Skills', value: stats?.skills || 0, icon: <CodeIcon />, color: '#00CEC9' },
                                    { label: 'Projects', value: stats?.projects || 0, icon: <FolderIcon />, color: '#FDCB6E' },
                                    { label: 'Documents', value: stats?.documents || 0, icon: <DescriptionIcon />, color: '#FF6B6B' },
                                ].map((item) => (
                                    <Grid size={{ xs: 6 }} key={item.label}>
                                        <Box sx={{
                                            p: 2, borderRadius: 2.5, textAlign: 'center',
                                            bgcolor: `${item.color}08`,
                                            border: `1px solid ${item.color}12`,
                                        }}>
                                            <Typography variant="h5" sx={{ color: item.color, fontWeight: 800 }}>
                                                <AnimatedNumber value={item.value} />
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary" fontWeight={500}>
                                                {item.label}
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


// ══════════════════════════════════════════════════════════════════
//  MAIN DASHBOARD — route based on role
// ══════════════════════════════════════════════════════════════════
const Dashboard: React.FC = () => {
    const { isAdmin } = useAuth();
    return isAdmin ? <AdminDashboard /> : <UserDashboard />;
};

export default Dashboard;
