import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, Chip, TextField,
    Button, CircularProgress, Avatar, LinearProgress, Fade,
    IconButton, Select, MenuItem, FormControl, InputLabel, Paper,
    Autocomplete,
} from '@mui/material';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import AddIcon from '@mui/icons-material/Add';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import TuneIcon from '@mui/icons-material/Tune';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import StarIcon from '@mui/icons-material/Star';
import SwapHorizIcon from '@mui/icons-material/SwapHoriz';
import BalanceIcon from '@mui/icons-material/Balance';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import api from '../services/api';

interface TeamMember {
    id: string;
    name: string;
    role: string;
    department: string;
    experienceYears: number;
    expertiseLevel: number;
    matchedSkills: Array<{ skill: string; level: number; match: string }>;
    coveragePercent: number;
    score: number;
    allSkills: string[];
}

interface TeamResult {
    projectName: string;
    team: TeamMember[];
    alternates: TeamMember[];
    stats: {
        teamSize: number;
        skillCoverage: number;
        avgExperience: number;
        skillGaps: string[];
        coveredSkills: string[];
    };
}

const TeamBuilder: React.FC = () => {
    const [availableSkills, setAvailableSkills] = useState<string[]>([]);
    const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
    const [projectName, setProjectName] = useState('');
    const [teamSize, setTeamSize] = useState(5);
    const [priority, setPriority] = useState('balanced');
    const [result, setResult] = useState<TeamResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [loadingSkills, setLoadingSkills] = useState(true);

    useEffect(() => {
        const loadSkills = async () => {
            try {
                const res = await api.get('/skills/available');
                setAvailableSkills(res.data.skills || []);
            } catch (err) {
                console.error('Failed to load skills', err);
            } finally {
                setLoadingSkills(false);
            }
        };
        loadSkills();
    }, []);

    const buildTeam = async () => {
        if (selectedSkills.length === 0) return;
        setLoading(true);
        try {
            const res = await api.post('/skills/team-builder', {
                skills: selectedSkills,
                teamSize,
                projectName: projectName || 'New Project',
                priority,
            });
            setResult(res.data);
        } catch (err) {
            console.error('Failed to build team', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                    <GroupWorkIcon sx={{ fontSize: 32, color: '#f59e0b' }} />
                    <Typography variant="h4" sx={{
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #f59e0b, #f97316, #06b6d4)',
                        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                    }}>
                        Team Builder
                    </Typography>
                </Box>
                <Typography color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                    AI-powered team assembly - find the perfect team for any project
                </Typography>
            </Box>

            {/* Configuration */}
            <Card sx={{
                mb: 3, background: 'linear-gradient(135deg, rgba(245,158,11,0.06), rgba(249,115,22,0.03))',
                border: '1px solid rgba(245,158,11,0.12)',
            }}>
                <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2.5 }}>
                        <TuneIcon sx={{ color: '#f59e0b', fontSize: 20 }} />
                        <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>Configure Your Team</Typography>
                    </Box>

                    <Grid container spacing={2.5}>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <TextField
                                fullWidth
                                size="small"
                                label="Project Name"
                                placeholder="e.g. Cloud Migration, AI Chatbot..."
                                value={projectName}
                                onChange={(e) => setProjectName(e.target.value)}
                                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                            />
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <FormControl fullWidth size="small">
                                <InputLabel>Team Size</InputLabel>
                                <Select
                                    value={teamSize}
                                    label="Team Size"
                                    onChange={(e) => setTeamSize(Number(e.target.value))}
                                    sx={{ borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' }}
                                >
                                    {[3, 4, 5, 6, 7, 8, 10].map(n => (
                                        <MenuItem key={n} value={n}>{n} members</MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Grid>
                        <Grid size={{ xs: 6, md: 3 }}>
                            <FormControl fullWidth size="small">
                                <InputLabel>Priority</InputLabel>
                                <Select
                                    value={priority}
                                    label="Priority"
                                    onChange={(e) => setPriority(e.target.value)}
                                    sx={{ borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' }}
                                >
                                    <MenuItem value="balanced">
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <BalanceIcon sx={{ fontSize: 16, color: '#f59e0b' }} /> Balanced
                                        </Box>
                                    </MenuItem>
                                    <MenuItem value="skill_coverage">
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <TrackChangesIcon sx={{ fontSize: 16, color: '#10b981' }} /> Skill Coverage
                                        </Box>
                                    </MenuItem>
                                    <MenuItem value="experience">
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <TrendingUpIcon sx={{ fontSize: 16, color: '#f59e0b' }} /> Experience
                                        </Box>
                                    </MenuItem>
                                </Select>
                            </FormControl>
                        </Grid>

                        <Grid size={12}>
                            <Autocomplete
                                multiple
                                freeSolo
                                options={availableSkills.filter(s => !selectedSkills.includes(s))}
                                value={selectedSkills}
                                onChange={(_, val) => setSelectedSkills(val as string[])}
                                loading={loadingSkills}
                                slotProps={{
                                    popper: { sx: { minWidth: 300 } },
                                }}
                                renderTags={(value, getTagProps) =>
                                    value.map((option, index) => (
                                        <Chip
                                            label={option}
                                            size="small"
                                            {...getTagProps({ index })}
                                            sx={{
                                                bgcolor: 'rgba(249,115,22,0.12)',
                                                color: '#fb923c',
                                                border: '1px solid rgba(249,115,22,0.2)',
                                                fontWeight: 500,
                                            }}
                                        />
                                    ))
                                }
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        size="small"
                                        label="Required Skills"
                                        placeholder="Type or select skills..."
                                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(0,0,0,0.2)' } }}
                                    />
                                )}
                            />
                        </Grid>

                        <Grid size={12}>
                            <Button
                                variant="contained"
                                onClick={buildTeam}
                                disabled={selectedSkills.length === 0 || loading}
                                startIcon={loading ? <CircularProgress size={18} sx={{ color: 'white' }} /> : <RocketLaunchIcon />}
                                sx={{
                                    px: 4, py: 1.2, fontWeight: 600, fontSize: '0.9rem',
                                    background: 'linear-gradient(135deg, #f59e0b, #f97316)',
                                    boxShadow: '0 4px 16px rgba(245,158,11,0.3)',
                                    '&:hover': {
                                        background: 'linear-gradient(135deg, #fbbf24, #fb923c)',
                                        transform: 'translateY(-1px)',
                                    },
                                }}
                            >
                                {loading ? 'Building Team...' : 'Build Optimal Team'}
                            </Button>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>

            {/* Results */}
            {result && (
                <Fade in>
                    <Box>
                        {/* Stats Row */}
                        <Grid container spacing={2} sx={{ mb: 3 }}>
                            {[
                                { label: 'Team Size', value: result.stats.teamSize, icon: <GroupWorkIcon sx={{ fontSize: 18 }} />, color: '#f97316' },
                                { label: 'Skill Coverage', value: `${result.stats.skillCoverage}%`, icon: result.stats.skillCoverage === 100 ? <CheckCircleIcon sx={{ fontSize: 18 }} /> : <WarningIcon sx={{ fontSize: 18 }} />, color: result.stats.skillCoverage === 100 ? '#10b981' : '#f59e0b' },
                                { label: 'Avg Experience', value: `${result.stats.avgExperience} yrs`, icon: <TrendingUpIcon sx={{ fontSize: 18 }} />, color: '#f59e0b' },
                                { label: 'Skill Gaps', value: result.stats.skillGaps.length, icon: result.stats.skillGaps.length === 0 ? <TrackChangesIcon sx={{ fontSize: 18 }} /> : <WarningIcon sx={{ fontSize: 18 }} />, color: result.stats.skillGaps.length === 0 ? '#10b981' : '#ef4444' },
                            ].map((stat) => (
                                <Grid size={{ xs: 6, md: 3 }} key={stat.label}>
                                    <Card sx={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                                        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                            <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary', mb: 0.3 }}>{stat.label}</Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8 }}>
                                                <Box sx={{ color: stat.color, display: 'flex' }}>{stat.icon}</Box>
                                                <Typography sx={{ fontSize: '1.3rem', fontWeight: 700, color: stat.color }}>{stat.value}</Typography>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>

                        {/* Skill Gaps Warning */}
                        {result.stats.skillGaps.length > 0 && (
                            <Card sx={{ mb: 3, background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.15)' }}>
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <WarningIcon sx={{ color: '#ef4444', fontSize: 20 }} />
                                        <Typography sx={{ fontWeight: 600, fontSize: '0.85rem', color: '#ef4444' }}>Skill Gaps</Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', gap: 0.5, mt: 1, flexWrap: 'wrap' }}>
                                        {result.stats.skillGaps.map(gap => (
                                            <Chip key={gap} label={gap} size="small" sx={{ bgcolor: 'rgba(239,68,68,0.1)', color: '#fca5a5', border: '1px solid rgba(239,68,68,0.2)', fontSize: '0.7rem' }} />
                                        ))}
                                    </Box>
                                </CardContent>
                            </Card>
                        )}

                        {/* Team Members */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                            <StarIcon sx={{ color: '#f59e0b', fontSize: 22 }} />
                            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                Recommended Team for "{result.projectName}"
                            </Typography>
                        </Box>
                        <Grid container spacing={2}>
                            {result.team.map((member, idx) => (
                                <Grid size={{ xs: 12, md: 6 }} key={member.id}>
                                    <Fade in timeout={300 + idx * 100}>
                                        <Card sx={{
                                            background: 'rgba(255,255,255,0.02)',
                                            border: '1px solid rgba(255,255,255,0.06)',
                                            transition: 'all 0.2s',
                                            '&:hover': { borderColor: 'rgba(249,115,22,0.2)', transform: 'translateY(-2px)' },
                                        }}>
                                            <CardContent sx={{ p: 2.5 }}>
                                                <Box sx={{ display: 'flex', gap: 2 }}>
                                                    <Box sx={{ position: 'relative' }}>
                                                        <Avatar sx={{
                                                            width: 48, height: 48, fontSize: '1rem',
                                                            background: 'linear-gradient(135deg, #f97316, #f59e0b)',
                                                        }}>
                                                            {member.name.split(' ').map(n => n[0]).join('')}
                                                        </Avatar>
                                                        <Box sx={{
                                                            position: 'absolute', top: -4, left: -4,
                                                            width: 20, height: 20, borderRadius: '50%',
                                                            bgcolor: '#18181b', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                            border: '2px solid #f97316', fontSize: '0.55rem', fontWeight: 700, color: '#f97316',
                                                        }}>
                                                            #{idx + 1}
                                                        </Box>
                                                    </Box>
                                                    <Box sx={{ flex: 1 }}>
                                                        <Typography sx={{ fontWeight: 700, fontSize: '0.95rem' }}>{member.name}</Typography>
                                                        <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                                                            {member.role} | {member.department}
                                                        </Typography>
                                                        <Box sx={{ display: 'flex', gap: 2, mt: 0.5 }}>
                                                            <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
                                                                {member.experienceYears} yrs exp
                                                            </Typography>
                                                            <Typography sx={{ fontSize: '0.65rem', color: 'text.secondary' }}>
                                                                {member.coveragePercent}% match
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                    <Box sx={{ textAlign: 'right' }}>
                                                        <Typography sx={{ fontWeight: 700, fontSize: '1.1rem', color: '#f97316' }}>
                                                            {member.score.toFixed(1)}
                                                        </Typography>
                                                        <Typography sx={{ fontSize: '0.55rem', color: 'text.secondary' }}>score</Typography>
                                                    </Box>
                                                </Box>

                                                {/* Matched Skills */}
                                                <Box sx={{ mt: 1.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                    {member.matchedSkills.map((ms) => (
                                                        <Chip
                                                            key={ms.skill}
                                                            label={`${ms.skill} (Lv${ms.level})`}
                                                            size="small"
                                                            icon={<CheckCircleIcon sx={{ fontSize: '14px !important' }} />}
                                                            sx={{
                                                                height: 22, fontSize: '0.6rem',
                                                                bgcolor: ms.match === 'exact' ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)',
                                                                color: ms.match === 'exact' ? '#34d399' : '#fbbf24',
                                                                border: `1px solid ${ms.match === 'exact' ? 'rgba(16,185,129,0.2)' : 'rgba(245,158,11,0.2)'}`,
                                                                '& .MuiChip-icon': { color: 'inherit' },
                                                            }}
                                                        />
                                                    ))}
                                                </Box>
                                            </CardContent>
                                        </Card>
                                    </Fade>
                                </Grid>
                            ))}
                        </Grid>

                        {/* Alternates */}
                        {result.alternates.length > 0 && (
                            <Box sx={{ mt: 3 }}>
                                <Typography sx={{ fontWeight: 600, fontSize: '0.85rem', mb: 1.5, color: 'text.secondary' }}>
                                    <SwapHorizIcon sx={{ fontSize: 16, verticalAlign: 'text-bottom', mr: 0.5 }} />
                                    Alternate Candidates
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                    {result.alternates.map(alt => (
                                        <Chip
                                            key={alt.id}
                                            avatar={<Avatar sx={{ bgcolor: '#ea580c', width: 24, height: 24, fontSize: '0.6rem' }}>{alt.name.charAt(0)}</Avatar>}
                                            label={`${alt.name} | ${alt.department} | ${alt.coveragePercent}% match`}
                                            sx={{
                                                bgcolor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                                                color: 'text.secondary', fontSize: '0.7rem',
                                            }}
                                        />
                                    ))}
                                </Box>
                            </Box>
                        )}
                    </Box>
                </Fade>
            )}
        </Box>
    );
};

export default TeamBuilder;
