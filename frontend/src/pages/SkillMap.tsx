import React, { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Grid, Chip, TextField,
    InputAdornment, CircularProgress, LinearProgress, Tooltip,
    ToggleButton, ToggleButtonGroup, Avatar, Fade,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';
import GroupIcon from '@mui/icons-material/Group';
import CategoryIcon from '@mui/icons-material/Category';
import StarIcon from '@mui/icons-material/Star';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import BarChartIcon from '@mui/icons-material/BarChart';
import api from '../services/api';

interface Skill {
    name: string;
    count: number;
    avgLevel: number;
    maxLevel: number;
    topDepartment: string;
    departments: Record<string, number>;
    expertCount: number;
    topExperts: Array<{ name: string; department: string; level: number }>;
    category: string;
}

interface SkillMapData {
    skills: Skill[];
    heatmap: any[];
    heatmapSkills: string[];
    departments: string[];
    categories: Array<{ name: string; count: number }>;
    totalExperts: number;
    totalSkills: number;
}

const CATEGORY_COLORS: Record<string, string> = {
    'Programming Languages': '#f97316',
    'Frameworks': '#f59e0b',
    'Cloud Platforms': '#06b6d4',
    'Data & AI': '#f59e0b',
    'DevOps & Tools': '#10b981',
    'Security': '#ef4444',
    'Other': '#64748b',
};

const getCatColor = (cat: string) => CATEGORY_COLORS[cat] || '#64748b';

const SkillMap: React.FC = () => {
    const [data, setData] = useState<SkillMapData | null>(null);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [view, setView] = useState<'bubble' | 'heatmap'>('bubble');
    const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
    const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await api.get('/skills/map');
                setData(res.data);
            } catch (err) {
                console.error('Failed to load skill map', err);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    const filteredSkills = data?.skills.filter(s => {
        const matchesSearch = s.name.toLowerCase().includes(search.toLowerCase());
        const matchesCat = !selectedCategory || s.category === selectedCategory;
        return matchesSearch && matchesCat;
    }) || [];

    const getLevelColor = (level: number) => {
        if (level >= 4) return '#10b981';
        if (level >= 3) return '#f97316';
        if (level >= 2) return '#f59e0b';
        return '#64748b';
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#f97316' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                    <BubbleChartIcon sx={{ fontSize: 32, color: '#f97316' }} />
                    <Typography variant="h4" sx={{ fontWeight: 700, background: 'linear-gradient(135deg, #f97316, #f59e0b, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        Skill Map
                    </Typography>
                </Box>
                <Typography color="text.secondary" sx={{ fontSize: '0.9rem' }}>
                    Interactive visualization of skills across the organization
                </Typography>
            </Box>

            {/* Stats Cards */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                {[
                    { label: 'Total Skills', value: data?.totalSkills || 0, icon: <CategoryIcon />, color: '#f97316' },
                    { label: 'Total Experts', value: data?.totalExperts || 0, icon: <GroupIcon />, color: '#f59e0b' },
                    { label: 'Categories', value: data?.categories.length || 0, icon: <ViewModuleIcon />, color: '#06b6d4' },
                    { label: 'Departments', value: data?.departments.length || 0, icon: <BarChartIcon />, color: '#10b981' },
                ].map((stat) => (
                    <Grid size={{ xs: 6, md: 3 }} key={stat.label}>
                        <Card sx={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Box sx={{ color: stat.color, opacity: 0.8 }}>{stat.icon}</Box>
                                    <Box>
                                        <Typography sx={{ fontSize: '1.4rem', fontWeight: 700, color: stat.color }}>{stat.value}</Typography>
                                        <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>{stat.label}</Typography>
                                    </Box>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Controls */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
                <TextField
                    size="small"
                    placeholder="Search skills..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    InputProps={{
                        startAdornment: <InputAdornment position="start"><SearchIcon sx={{ fontSize: 18, color: 'text.secondary' }} /></InputAdornment>,
                    }}
                    sx={{ width: 260, '& .MuiOutlinedInput-root': { borderRadius: 2.5, bgcolor: 'rgba(255,255,255,0.03)' } }}
                />
                <ToggleButtonGroup
                    size="small"
                    value={view}
                    exclusive
                    onChange={(_, v) => v && setView(v)}
                    sx={{ '& .MuiToggleButton-root': { px: 2, borderRadius: '8px !important', color: 'text.secondary', '&.Mui-selected': { color: '#f97316', bgcolor: 'rgba(249,115,22,0.1)' } } }}
                >
                    <ToggleButton value="bubble">Bubble</ToggleButton>
                    <ToggleButton value="heatmap">Heatmap</ToggleButton>
                </ToggleButtonGroup>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    <Chip
                        label="All"
                        size="small"
                        onClick={() => setSelectedCategory(null)}
                        sx={{
                            bgcolor: !selectedCategory ? 'rgba(249,115,22,0.15)' : 'rgba(255,255,255,0.04)',
                            color: !selectedCategory ? '#fb923c' : 'text.secondary',
                            border: '1px solid', borderColor: !selectedCategory ? 'rgba(249,115,22,0.3)' : 'rgba(255,255,255,0.06)',
                            fontWeight: 500, cursor: 'pointer',
                        }}
                    />
                    {data?.categories.map(cat => (
                        <Chip
                            key={cat.name}
                            label={`${cat.name} (${cat.count})`}
                            size="small"
                            onClick={() => setSelectedCategory(selectedCategory === cat.name ? null : cat.name)}
                            sx={{
                                bgcolor: selectedCategory === cat.name ? `${getCatColor(cat.name)}22` : 'rgba(255,255,255,0.04)',
                                color: selectedCategory === cat.name ? getCatColor(cat.name) : 'text.secondary',
                                border: '1px solid',
                                borderColor: selectedCategory === cat.name ? `${getCatColor(cat.name)}44` : 'rgba(255,255,255,0.06)',
                                fontWeight: 500, cursor: 'pointer', fontSize: '0.7rem',
                            }}
                        />
                    ))}
                </Box>
            </Box>

            {/* Main Content */}
            {view === 'bubble' ? (
                /* Bubble View */
                <Grid container spacing={1.5}>
                    {filteredSkills.map((skill, idx) => (
                        <Grid size={{ xs: 6, sm: 4, md: 3, lg: 2 }} key={skill.name}>
                            <Fade in timeout={200 + idx * 30}>
                                <Card
                                    onClick={() => setSelectedSkill(selectedSkill?.name === skill.name ? null : skill)}
                                    sx={{
                                        cursor: 'pointer',
                                        background: selectedSkill?.name === skill.name
                                            ? `linear-gradient(135deg, ${getCatColor(skill.category)}15, ${getCatColor(skill.category)}08)`
                                            : 'rgba(255,255,255,0.02)',
                                        border: '1px solid',
                                        borderColor: selectedSkill?.name === skill.name
                                            ? `${getCatColor(skill.category)}44`
                                            : 'rgba(255,255,255,0.04)',
                                        transition: 'all 0.2s', textAlign: 'center', p: 1.5,
                                        '&:hover': {
                                            borderColor: `${getCatColor(skill.category)}33`,
                                            transform: 'translateY(-2px)',
                                            boxShadow: `0 4px 20px ${getCatColor(skill.category)}15`,
                                        },
                                    }}
                                >
                                    <CardContent sx={{ p: '0 !important' }}>
                                        <Box sx={{
                                            width: Math.min(40 + skill.count * 3, 70),
                                            height: Math.min(40 + skill.count * 3, 70),
                                            borderRadius: '50%',
                                            background: `linear-gradient(135deg, ${getCatColor(skill.category)}25, ${getCatColor(skill.category)}10)`,
                                            border: `2px solid ${getCatColor(skill.category)}33`,
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            mx: 'auto', mb: 1,
                                        }}>
                                            <Typography sx={{ fontWeight: 700, fontSize: '1rem', color: getCatColor(skill.category) }}>
                                                {skill.count}
                                            </Typography>
                                        </Box>
                                        <Typography sx={{ fontWeight: 600, fontSize: '0.75rem', mb: 0.3, lineHeight: 1.2 }}>
                                            {skill.name}
                                        </Typography>
                                        <Typography sx={{ fontSize: '0.6rem', color: 'text.secondary' }}>
                                            Avg Level: {skill.avgLevel.toFixed(1)}
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Fade>
                        </Grid>
                    ))}
                </Grid>
            ) : (
                /* Heatmap View */
                <Card sx={{ overflow: 'auto', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)' }}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                            Department x Skill Heatmap
                        </Typography>
                        <Box sx={{ overflowX: 'auto' }}>
                            <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                                <thead>
                                    <tr>
                                        <th style={{ padding: '8px 12px', textAlign: 'left', borderBottom: '1px solid rgba(255,255,255,0.06)', fontSize: '0.7rem', color: 'rgba(255,255,255,0.5)' }}>
                                            Department
                                        </th>
                                        {data?.heatmapSkills.map(skill => (
                                            <th key={skill} style={{
                                                padding: '4px 6px', textAlign: 'center',
                                                borderBottom: '1px solid rgba(255,255,255,0.06)',
                                                fontSize: '0.55rem', color: 'rgba(255,255,255,0.5)',
                                                writingMode: 'vertical-lr', maxHeight: 100, whiteSpace: 'nowrap',
                                            }}>
                                                {skill}
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {data?.heatmap.map((row) => (
                                        <tr key={row.department}>
                                            <td style={{
                                                padding: '6px 12px', fontSize: '0.72rem', fontWeight: 500,
                                                borderBottom: '1px solid rgba(255,255,255,0.03)',
                                                whiteSpace: 'nowrap', color: 'rgba(255,255,255,0.8)',
                                            }}>
                                                {row.department}
                                            </td>
                                            {data?.heatmapSkills.map(skill => {
                                                const val = row[skill] || 0;
                                                const maxVal = 8;
                                                const intensity = Math.min(val / maxVal, 1);
                                                return (
                                                    <td key={skill} style={{
                                                        padding: '4px',
                                                        borderBottom: '1px solid rgba(255,255,255,0.03)',
                                                        textAlign: 'center',
                                                    }}>
                                                        <Tooltip title={`${row.department}: ${skill} - ${val} experts`} arrow>
                                                            <Box sx={{
                                                                width: 24, height: 24, borderRadius: 1,
                                                                mx: 'auto',
                                                                bgcolor: val > 0
                                                                    ? `rgba(249,115,22,${0.1 + intensity * 0.7})`
                                                                    : 'rgba(255,255,255,0.02)',
                                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                fontSize: '0.55rem', color: intensity > 0.3 ? '#fff' : 'transparent',
                                                                fontWeight: 600, cursor: 'default',
                                                            }}>
                                                                {val || ''}
                                                            </Box>
                                                        </Tooltip>
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </Box>
                    </CardContent>
                </Card>
            )}

            {/* Skill Detail Panel */}
            {selectedSkill && (
                <Fade in>
                    <Card sx={{
                        mt: 3, background: 'linear-gradient(135deg, rgba(249,115,22,0.06), rgba(245,158,11,0.03))',
                        border: '1px solid rgba(249,115,22,0.15)',
                    }}>
                        <CardContent sx={{ p: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                <Box>
                                    <Typography variant="h5" sx={{ fontWeight: 700 }}>{selectedSkill.name}</Typography>
                                    <Chip
                                        label={selectedSkill.category}
                                        size="small"
                                        sx={{ mt: 0.5, bgcolor: `${getCatColor(selectedSkill.category)}22`, color: getCatColor(selectedSkill.category), fontWeight: 600 }}
                                    />
                                </Box>
                                <Box sx={{ textAlign: 'right' }}>
                                    <Typography sx={{ fontSize: '2rem', fontWeight: 800, color: '#f97316' }}>
                                        {selectedSkill.count}
                                    </Typography>
                                    <Typography sx={{ fontSize: '0.7rem', color: 'text.secondary' }}>experts</Typography>
                                </Box>
                            </Box>

                            <Grid container spacing={3}>
                                <Grid size={{ xs: 12, md: 4 }}>
                                    <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', mb: 1, fontWeight: 600 }}>
                                        SKILL LEVEL
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                        <Typography sx={{ fontSize: '0.8rem' }}>Avg Level:</Typography>
                                        <Box sx={{ flex: 1 }}>
                                            <LinearProgress
                                                variant="determinate"
                                                value={selectedSkill.avgLevel * 20}
                                                sx={{
                                                    height: 6, borderRadius: 3,
                                                    bgcolor: 'rgba(255,255,255,0.05)',
                                                    '& .MuiLinearProgress-bar': {
                                                        bgcolor: getLevelColor(selectedSkill.avgLevel),
                                                        borderRadius: 3,
                                                    },
                                                }}
                                            />
                                        </Box>
                                        <Typography sx={{ fontWeight: 700, color: getLevelColor(selectedSkill.avgLevel), fontSize: '0.85rem' }}>
                                            {selectedSkill.avgLevel.toFixed(1)}/5
                                        </Typography>
                                    </Box>
                                </Grid>

                                <Grid size={{ xs: 12, md: 4 }}>
                                    <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', mb: 1, fontWeight: 600 }}>
                                        DEPARTMENT DISTRIBUTION
                                    </Typography>
                                    {Object.entries(selectedSkill.departments)
                                        .sort((a, b) => b[1] - a[1])
                                        .slice(0, 5)
                                        .map(([dept, count]) => (
                                            <Box key={dept} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.4 }}>
                                                <Typography sx={{ fontSize: '0.72rem', width: 120, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {dept}
                                                </Typography>
                                                <Box sx={{ flex: 1 }}>
                                                    <LinearProgress
                                                        variant="determinate"
                                                        value={(count / selectedSkill.count) * 100}
                                                        sx={{
                                                            height: 4, borderRadius: 2, bgcolor: 'rgba(255,255,255,0.05)',
                                                            '& .MuiLinearProgress-bar': { bgcolor: '#f59e0b', borderRadius: 2 },
                                                        }}
                                                    />
                                                </Box>
                                                <Typography sx={{ fontSize: '0.7rem', fontWeight: 600, minWidth: 20, textAlign: 'right' }}>{count}</Typography>
                                            </Box>
                                        ))}
                                </Grid>

                                <Grid size={{ xs: 12, md: 4 }}>
                                    <Typography sx={{ fontSize: '0.75rem', color: 'text.secondary', mb: 1, fontWeight: 600 }}>
                                        <StarIcon sx={{ fontSize: 14, verticalAlign: 'text-bottom', mr: 0.3 }} />
                                        TOP EXPERTS (Level 4+)
                                    </Typography>
                                    {selectedSkill.topExperts.length > 0 ? selectedSkill.topExperts.map((exp, i) => (
                                        <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                            <Avatar sx={{ width: 24, height: 24, fontSize: '0.6rem', bgcolor: '#f97316' }}>
                                                {exp.name.charAt(0)}
                                            </Avatar>
                                            <Box>
                                                <Typography sx={{ fontSize: '0.72rem', fontWeight: 600 }}>{exp.name}</Typography>
                                                <Typography sx={{ fontSize: '0.6rem', color: 'text.secondary' }}>{exp.department}</Typography>
                                            </Box>
                                            <Chip label={`Lv ${exp.level}`} size="small" sx={{ ml: 'auto', height: 18, fontSize: '0.55rem', bgcolor: 'rgba(16,185,129,0.15)', color: '#10b981' }} />
                                        </Box>
                                    )) : (
                                        <Typography sx={{ fontSize: '0.72rem', color: 'text.secondary', fontStyle: 'italic' }}>
                                            No experts at level 4+ yet
                                        </Typography>
                                    )}
                                </Grid>
                            </Grid>
                        </CardContent>
                    </Card>
                </Fade>
            )}
        </Box>
    );
};

export default SkillMap;
