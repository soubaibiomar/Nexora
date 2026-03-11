import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, Chip, CircularProgress,
    LinearProgress, Avatar, Fade, ToggleButton, ToggleButtonGroup,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import TimelineIcon from '@mui/icons-material/Timeline';
import GroupsIcon from '@mui/icons-material/Groups';
import { aiService } from '../services/api';

interface EmergingSkill {
    skill: string;
    recent_adoption_rate: number;
    older_adoption_rate: number;
    growth_rate: number;
    status: string;
}

interface FutureSkill {
    skill: string;
    current_supply: number;
    current_project_demand: number;
    predicted_demand: number;
    predicted_gap: number;
    growth_rate: number;
    urgency: string;
}

interface CrossDeptSuggestion {
    department_1: string;
    department_2: string;
    shared_skills: string[];
    unique_to_dept_1: string[];
    unique_to_dept_2: string[];
    collaboration_potential: number;
    rationale: string;
}

const SkillEvolution: React.FC = () => {
    const [emerging, setEmerging] = useState<EmergingSkill[]>([]);
    const [declining, setDeclining] = useState<EmergingSkill[]>([]);
    const [futureSkills, setFutureSkills] = useState<FutureSkill[]>([]);
    const [crossDept, setCrossDept] = useState<CrossDeptSuggestion[]>([]);
    const [loading, setLoading] = useState(true);
    const [forecastMonths, setForecastMonths] = useState<number>(12);
    const [activeTab, setActiveTab] = useState<string>('emerging');

    useEffect(() => {
        loadData();
    }, []);

    useEffect(() => {
        loadForecast();
    }, [forecastMonths]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [emergingRes, futureRes, crossRes] = await Promise.all([
                aiService.getEmergingSkills(),
                aiService.getFutureSkills(forecastMonths),
                aiService.getCrossDepartmentSuggestions(),
            ]);
            setEmerging(emergingRes.data.emerging_skills || []);
            setDeclining(emergingRes.data.declining_skills || []);
            setFutureSkills(futureRes.data.predictions || []);
            setCrossDept(crossRes.data.suggestions || []);
        } catch (err) {
            console.error('Failed to load skill evolution data:', err);
        }
        setLoading(false);
    };

    const loadForecast = async () => {
        try {
            const res = await aiService.getFutureSkills(forecastMonths);
            setFutureSkills(res.data.predictions || []);
        } catch (err) {
            console.error('Failed to load forecast:', err);
        }
    };

    const getUrgencyColor = (urgency: string) => {
        switch (urgency) {
            case 'critical': return '#ef4444';
            case 'high': return '#f97316';
            case 'medium': return '#eab308';
            default: return '#22c55e';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'rising': return '#22c55e';
            case 'stable': return '#3b82f6';
            default: return '#ef4444';
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#f97316' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ p: 3, maxWidth: 1400, mx: 'auto' }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" sx={{
                    fontWeight: 800, mb: 1,
                    background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>
                    <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 36, color: '#f97316' }} />
                    Skill Evolution
                </Typography>
                <Typography color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                    Track how skills evolve, predict future demands, and discover collaboration opportunities
                </Typography>
            </Box>

            {/* Tab Toggle */}
            <ToggleButtonGroup
                value={activeTab}
                exclusive
                onChange={(_, v) => v && setActiveTab(v)}
                sx={{ mb: 3 }}
            >
                <ToggleButton value="emerging" sx={{ px: 3 }}>
                    <TrendingUpIcon sx={{ mr: 1, fontSize: 18 }} /> Emerging Skills
                </ToggleButton>
                <ToggleButton value="forecast" sx={{ px: 3 }}>
                    <AutoGraphIcon sx={{ mr: 1, fontSize: 18 }} /> Demand Forecast
                </ToggleButton>
                <ToggleButton value="collaboration" sx={{ px: 3 }}>
                    <GroupsIcon sx={{ mr: 1, fontSize: 18 }} /> Cross-Dept Collaboration
                </ToggleButton>
            </ToggleButtonGroup>

            {/* ── Emerging Skills Tab ────────────────────────────────── */}
            {activeTab === 'emerging' && (
                <Fade in>
                    <Box>
                        <Grid container spacing={3}>
                            {/* Rising Skills */}
                            <Grid size={{ xs: 12, md: 7 }}>
                                <Card sx={{
                                    background: 'linear-gradient(145deg, rgba(34,197,94,0.05), rgba(30,30,30,0.95))',
                                    border: '1px solid rgba(34,197,94,0.15)', borderRadius: 3,
                                }}>
                                    <CardContent>
                                        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <TrendingUpIcon sx={{ color: '#22c55e' }} /> Rising Skills
                                        </Typography>
                                        {emerging.map((skill, i) => (
                                            <Fade in key={skill.skill} timeout={300 + i * 100}>
                                                <Box sx={{
                                                    display: 'flex', alignItems: 'center', gap: 2,
                                                    p: 1.5, mb: 1, borderRadius: 2,
                                                    bgcolor: 'rgba(255,255,255,0.02)',
                                                    '&:hover': { bgcolor: 'rgba(34,197,94,0.08)' },
                                                    transition: 'all 0.2s',
                                                }}>
                                                    <Avatar sx={{
                                                        width: 36, height: 36, fontSize: '0.8rem',
                                                        bgcolor: `${getStatusColor(skill.status)}22`,
                                                        color: getStatusColor(skill.status),
                                                        fontWeight: 700,
                                                    }}>
                                                        #{i + 1}
                                                    </Avatar>
                                                    <Box sx={{ flex: 1 }}>
                                                        <Typography sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                                                            {skill.skill}
                                                        </Typography>
                                                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                                                            <Chip label={`+${(skill.growth_rate * 100).toFixed(0)}% growth`}
                                                                size="small"
                                                                sx={{
                                                                    fontSize: '0.7rem', fontWeight: 600, height: 22,
                                                                    bgcolor: `${getStatusColor(skill.status)}22`,
                                                                    color: getStatusColor(skill.status),
                                                                }} />
                                                            <Chip label={`${(skill.recent_adoption_rate * 100).toFixed(1)}% adoption`}
                                                                size="small" variant="outlined"
                                                                sx={{ fontSize: '0.7rem', height: 22 }} />
                                                        </Box>
                                                    </Box>
                                                    <Box sx={{ width: 100 }}>
                                                        <LinearProgress variant="determinate"
                                                            value={Math.min(100, skill.growth_rate * 50)}
                                                            sx={{
                                                                height: 6, borderRadius: 3,
                                                                bgcolor: 'rgba(255,255,255,0.05)',
                                                                '& .MuiLinearProgress-bar': {
                                                                    bgcolor: getStatusColor(skill.status),
                                                                    borderRadius: 3,
                                                                },
                                                            }} />
                                                    </Box>
                                                </Box>
                                            </Fade>
                                        ))}
                                    </CardContent>
                                </Card>
                            </Grid>

                            {/* Declining Skills */}
                            <Grid size={{ xs: 12, md: 5 }}>
                                <Card sx={{
                                    background: 'linear-gradient(145deg, rgba(239,68,68,0.05), rgba(30,30,30,0.95))',
                                    border: '1px solid rgba(239,68,68,0.15)', borderRadius: 3,
                                }}>
                                    <CardContent>
                                        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <TrendingDownIcon sx={{ color: '#ef4444' }} /> Declining Skills
                                        </Typography>
                                        {declining.length === 0 ? (
                                            <Typography color="text.secondary" sx={{ fontSize: '0.85rem', py: 2 }}>
                                                No declining skills detected in the current analysis period.
                                            </Typography>
                                        ) : declining.map((skill) => (
                                            <Box key={skill.skill} sx={{
                                                display: 'flex', alignItems: 'center', gap: 2,
                                                p: 1.5, mb: 1, borderRadius: 2,
                                                bgcolor: 'rgba(255,255,255,0.02)',
                                            }}>
                                                <Typography sx={{ fontWeight: 600, fontSize: '0.85rem', flex: 1 }}>
                                                    {skill.skill}
                                                </Typography>
                                                <Chip label={`${(skill.growth_rate * 100).toFixed(0)}%`}
                                                    size="small"
                                                    sx={{
                                                        fontSize: '0.7rem', fontWeight: 600, height: 22,
                                                        bgcolor: 'rgba(239,68,68,0.15)', color: '#ef4444',
                                                    }} />
                                            </Box>
                                        ))}
                                    </CardContent>
                                </Card>

                                {/* Insight Card */}
                                <Card sx={{
                                    mt: 2,
                                    background: 'linear-gradient(145deg, rgba(249,115,22,0.08), rgba(30,30,30,0.95))',
                                    border: '1px solid rgba(249,115,22,0.2)', borderRadius: 3,
                                }}>
                                    <CardContent>
                                        <Typography sx={{ fontWeight: 700, fontSize: '0.85rem', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <LightbulbIcon sx={{ color: '#f97316', fontSize: 20 }} /> AI Insight
                                        </Typography>
                                        <Typography color="text.secondary" sx={{ fontSize: '0.8rem', lineHeight: 1.6 }}>
                                            {emerging.length > 0
                                                ? `${emerging[0]?.skill} and ${emerging[1]?.skill || 'related skills'} show the strongest growth. Consider investing in training programs for these technologies.`
                                                : 'Analyzing skill trends across the organization...'}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>
                        </Grid>
                    </Box>
                </Fade>
            )}

            {/* ── Demand Forecast Tab ───────────────────────────────── */}
            {activeTab === 'forecast' && (
                <Fade in>
                    <Box>
                        {/* Forecast Horizon Selector */}
                        <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                            {[6, 12, 18, 24].map(m => (
                                <Chip key={m} label={`${m} months`}
                                    onClick={() => setForecastMonths(m)}
                                    sx={{
                                        fontWeight: 600,
                                        bgcolor: forecastMonths === m ? 'rgba(249,115,22,0.2)' : 'rgba(255,255,255,0.05)',
                                        color: forecastMonths === m ? '#f97316' : 'text.secondary',
                                        border: forecastMonths === m ? '1px solid rgba(249,115,22,0.4)' : '1px solid transparent',
                                        cursor: 'pointer',
                                        '&:hover': { bgcolor: 'rgba(249,115,22,0.1)' },
                                    }} />
                            ))}
                        </Box>

                        <TableContainer component={Card} sx={{
                            background: 'linear-gradient(145deg, rgba(249,115,22,0.03), rgba(30,30,30,0.95))',
                            border: '1px solid rgba(249,115,22,0.1)', borderRadius: 3,
                        }}>
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell sx={{ fontWeight: 700, color: '#f97316' }}>Skill</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Supply</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Current Demand</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Predicted Demand</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Gap</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Growth</TableCell>
                                        <TableCell align="center" sx={{ fontWeight: 700 }}>Urgency</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {futureSkills.map((skill) => (
                                        <TableRow key={skill.skill} sx={{
                                            '&:hover': { bgcolor: 'rgba(249,115,22,0.05)' },
                                        }}>
                                            <TableCell>
                                                <Typography sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
                                                    {skill.skill}
                                                </Typography>
                                            </TableCell>
                                            <TableCell align="center">{skill.current_supply}</TableCell>
                                            <TableCell align="center">{skill.current_project_demand}</TableCell>
                                            <TableCell align="center" sx={{ fontWeight: 600 }}>
                                                {skill.predicted_demand}
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip label={skill.predicted_gap}
                                                    size="small"
                                                    sx={{
                                                        fontWeight: 700, height: 24, minWidth: 40,
                                                        bgcolor: `${getUrgencyColor(skill.urgency)}22`,
                                                        color: getUrgencyColor(skill.urgency),
                                                    }} />
                                            </TableCell>
                                            <TableCell align="center">
                                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                                                    {skill.growth_rate > 0
                                                        ? <TrendingUpIcon sx={{ fontSize: 16, color: '#22c55e' }} />
                                                        : <TrendingDownIcon sx={{ fontSize: 16, color: '#ef4444' }} />}
                                                    <Typography sx={{ fontSize: '0.8rem', fontWeight: 600 }}>
                                                        {(skill.growth_rate * 100).toFixed(0)}%
                                                    </Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell align="center">
                                                <Chip label={skill.urgency}
                                                    size="small"
                                                    sx={{
                                                        fontWeight: 700, fontSize: '0.7rem', height: 22,
                                                        bgcolor: `${getUrgencyColor(skill.urgency)}22`,
                                                        color: getUrgencyColor(skill.urgency),
                                                        textTransform: 'capitalize',
                                                    }} />
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>

                        {/* Warning Cards for Critical Gaps */}
                        {futureSkills.filter(s => s.urgency === 'critical').length > 0 && (
                            <Card sx={{
                                mt: 2,
                                background: 'linear-gradient(145deg, rgba(239,68,68,0.08), rgba(30,30,30,0.95))',
                                border: '1px solid rgba(239,68,68,0.2)', borderRadius: 3,
                            }}>
                                <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                    <WarningAmberIcon sx={{ color: '#ef4444', fontSize: 28 }} />
                                    <Box>
                                        <Typography sx={{ fontWeight: 700, fontSize: '0.9rem', color: '#ef4444' }}>
                                            {futureSkills.filter(s => s.urgency === 'critical').length} Critical Skill Gap{futureSkills.filter(s => s.urgency === 'critical').length > 1 ? 's' : ''} Detected
                                        </Typography>
                                        <Typography color="text.secondary" sx={{ fontSize: '0.8rem' }}>
                                            Immediate action recommended: launch training programs or consider external hiring for{' '}
                                            {futureSkills.filter(s => s.urgency === 'critical').slice(0, 3).map(s => s.skill).join(', ')}.
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        )}
                    </Box>
                </Fade>
            )}

            {/* ── Cross-Dept Collaboration Tab ──────────────────────── */}
            {activeTab === 'collaboration' && (
                <Fade in>
                    <Grid container spacing={2}>
                        {crossDept.map((sug, i) => (
                            <Grid size={{ xs: 12, md: 6 }} key={i}>
                                <Card sx={{
                                    background: 'linear-gradient(145deg, rgba(59,130,246,0.05), rgba(30,30,30,0.95))',
                                    border: '1px solid rgba(59,130,246,0.15)', borderRadius: 3,
                                    transition: 'all 0.2s',
                                    '&:hover': { border: '1px solid rgba(59,130,246,0.3)', transform: 'translateY(-2px)' },
                                }}>
                                    <CardContent>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <Chip label={sug.department_1} size="small"
                                                    sx={{ fontWeight: 600, bgcolor: 'rgba(249,115,22,0.15)', color: '#f97316' }} />
                                                <Typography sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>×</Typography>
                                                <Chip label={sug.department_2} size="small"
                                                    sx={{ fontWeight: 600, bgcolor: 'rgba(59,130,246,0.15)', color: '#3b82f6' }} />
                                            </Box>
                                            <Chip label={`${sug.collaboration_potential}%`}
                                                size="small"
                                                sx={{
                                                    fontWeight: 700, fontSize: '0.75rem',
                                                    bgcolor: sug.collaboration_potential > 50 ? 'rgba(34,197,94,0.15)' : 'rgba(249,115,22,0.15)',
                                                    color: sug.collaboration_potential > 50 ? '#22c55e' : '#f97316',
                                                }} />
                                        </Box>

                                        <Typography color="text.secondary" sx={{ fontSize: '0.8rem', mb: 1.5, lineHeight: 1.5 }}>
                                            {sug.rationale}
                                        </Typography>

                                        <Box sx={{ display: 'flex', gap: 2 }}>
                                            <Box sx={{ flex: 1 }}>
                                                <Typography sx={{ fontSize: '0.7rem', fontWeight: 600, color: 'text.secondary', mb: 0.5 }}>
                                                    Shared Skills
                                                </Typography>
                                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                    {sug.shared_skills.map(s => (
                                                        <Chip key={s} label={s} size="small" variant="outlined"
                                                            sx={{ fontSize: '0.65rem', height: 20 }} />
                                                    ))}
                                                </Box>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                </Fade>
            )}
        </Box>
    );
};

export default SkillEvolution;
