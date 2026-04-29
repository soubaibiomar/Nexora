import { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Avatar, Button, Divider,
    Grid, IconButton, CircularProgress, Chip, LinearProgress,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import LinkIcon from '@mui/icons-material/Link';
import PeopleIcon from '@mui/icons-material/People';
import VisibilityIcon from '@mui/icons-material/Visibility';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import VerifiedIcon from '@mui/icons-material/Verified';
import SchoolIcon from '@mui/icons-material/School';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import EmailIcon from '@mui/icons-material/Email';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { networkService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

export default function Profile() {
    const { fullName, username, email, role } = useAuth();
    const [profile, setProfile] = useState<any>(null);
    const [netStats, setNetStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                // Fetch the authenticated user's own profile from /api/auth/me
                const meRes = await api.get('/auth/me');
                setProfile(meRes.data);
            } catch {
                // Fallback: use data from AuthContext
                setProfile({
                    full_name: fullName,
                    username,
                    email,
                    role,
                    headline: '',
                });
            }
            try {
                const statsRes = await networkService.getStats();
                setNetStats(statsRes.data);
            } catch { /* use fallback */ }
            setLoading(false);
        };
        load();
    }, [fullName, username, email, role]);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    // Map auth profile fields to the template's expected shape
    const user = profile ? {
        name: profile.full_name || profile.name || fullName,
        role: profile.headline || profile.role || role,
        department: profile.department || '',
        location: profile.location || '',
        experience_years: profile.experience_years || 2,
        skills: profile.skills || ['React', 'TypeScript', 'Python', 'Node.js', 'Docker', 'FastAPI', 'Neo4j', 'AWS'],
        email: profile.email || email,
        username: profile.username || username,
    } : {
        name: fullName || 'User',
        role: role || 'user',
        department: '',
        location: '',
        experience_years: 2,
        skills: ['React', 'TypeScript', 'Node.js', 'Python', 'FastAPI', 'Docker', 'Neo4j', 'PostgreSQL'],
        email,
        username,
    };

    const skills = user.skills || ['React', 'TypeScript', 'Python', 'Node.js', 'Docker', 'FastAPI', 'Neo4j', 'AWS'];
    const endorsements = [52, 45, 42, 38, 35, 28, 22, 18];
    const stats = netStats || { total_connections: 127, profile_views: 284, search_appearances: 430, pending_requests: 3 };

    const experiences = [
        { title: user.role, company: 'Nexora', type: 'Full-time', startYear: 2024 - (user.experience_years || 3), endYear: 'Present', years: user.experience_years || 3, location: user.location || 'Remote', logo: 'N', color: '#6C5CE7', description: 'Building scalable knowledge cartography platform. Leading development of expert discovery, learning paths, and AI-powered recommendations.' },
        { title: 'Software Engineer Intern', company: 'TechCorp', type: 'Internship', startYear: 2024 - (user.experience_years || 3) - 1, endYear: 2024 - (user.experience_years || 3), years: 1, location: user.location || 'Remote', logo: 'T', color: '#00CEC9', description: 'Developed RESTful APIs and contributed to microservices architecture. Built data processing pipelines using Python.' },
    ];

    const education = { school: 'University of Engineering', degree: 'Master\'s degree, Computer Science', years: `${2024 - (user.experience_years || 3) - 2} – ${2024 - (user.experience_years || 3)}` };

    return (
        <Box sx={{ maxWidth: 950, mx: 'auto', p: { xs: 2, md: 3 } }}>
            {/* Banner + Profile */}
            <Card sx={{ mb: 2.5, overflow: 'visible' }}>
                <Box sx={{
                    height: 200,
                    bgcolor: 'primary.dark',
                    borderRadius: '12px 12px 0 0', position: 'relative',
                }}>
                    <IconButton sx={{ position: 'absolute', top: 12, right: 12, color: 'white', bgcolor: 'rgba(0,0,0,0.35)', '&:hover': { bgcolor: 'rgba(0,0,0,0.5)' } }}>
                        <PhotoCameraIcon fontSize="small" />
                    </IconButton>
                </Box>

                <CardContent sx={{ pt: 0, position: 'relative' }}>
                    <Avatar
                        src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user.name || '')}&background=1976d2&color=fff&size=256&bold=true`}
                        sx={{
                            width: 150, height: 150, fontSize: '3.5rem', fontWeight: 700,
                            bgcolor: 'primary.main', border: '5px solid', borderColor: 'background.paper',
                            position: 'absolute', top: -75, left: 24,
                        }}
                    >{user.name?.charAt(0)}</Avatar>

                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                        <IconButton sx={{ color: 'text.secondary' }}><EditIcon /></IconButton>
                    </Box>

                    <Box sx={{ ml: { xs: 0, md: '190px' }, mb: 2, mt: { xs: 10, md: 0 } }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="h4" fontWeight={800}>{user.name}</Typography>
                            <VerifiedIcon sx={{ color: '#6C5CE7', fontSize: 22 }} />
                        </Box>
                        <Typography variant="body1" color="text.secondary" sx={{ mt: 0.3 }}>
                            {user.role} at Nexora
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2.5, mt: 0.8, flexWrap: 'wrap' }}>
                            {[
                                { icon: <LocationOnIcon sx={{ fontSize: 15, color: 'primary.main' }} />, text: user.location || 'Remote' },
                                { icon: <WorkIcon sx={{ fontSize: 15, color: 'primary.main' }} />, text: user.department },
                                { icon: <EmailIcon sx={{ fontSize: 15, color: 'primary.main' }} />, text: 'Contact info' },
                            ].map((item, i) => (
                                <Typography key={i} variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    {item.icon} {item.text}
                                </Typography>
                            ))}
                        </Box>
                        <Typography variant="body2" color="primary" sx={{ mt: 1, cursor: 'pointer', fontWeight: 600, '&:hover': { textDecoration: 'underline' } }}>
                            {stats.total_connections}+ connections
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 1, ml: { xs: 0, md: '190px' }, flexWrap: 'wrap' }}>
                        <Button variant="contained" size="small" sx={{ borderRadius: 2.5, px: 3, fontWeight: 600 }}>Open to</Button>
                        <Button variant="outlined" size="small" sx={{ borderRadius: 2.5, px: 3, fontWeight: 600 }}>Add section</Button>
                        <Button variant="outlined" size="small" sx={{ borderRadius: 2.5, px: 2, minWidth: 0 }}>More</Button>
                    </Box>
                </CardContent>
            </Card>

            <Grid container spacing={2.5}>
                {/* Left Column */}
                <Grid size={{ xs: 12, md: 8 }}>
                    {/* AI Insights Card */}
                    <Card sx={{
                        mb: 2.5, bgcolor: 'action.hover',
                    }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                <AutoAwesomeIcon sx={{ color: 'primary.main', fontSize: 20 }} />
                                <Typography variant="subtitle2" fontWeight={700} color="primary">AI Profile Insights</Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                                Your profile strength is <strong style={{ color: '#00B894' }}>85%</strong>.
                                Adding 2 more skills and a project description can increase your visibility by <strong style={{ color: '#6C5CE7' }}>23%</strong>.
                            </Typography>
                            <LinearProgress variant="determinate" value={85} sx={{ mt: 1.5, height: 6, borderRadius: 3, bgcolor: 'rgba(108,92,231,0.1)' }} />
                        </CardContent>
                    </Card>

                    {/* Analytics */}
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                                <Typography variant="h6" fontWeight={700}>Analytics</Typography>
                                <Chip icon={<VisibilityIcon sx={{ fontSize: 14 }} />} label="Private to you" size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                            </Box>
                            <Grid container spacing={2}>
                                {[
                                    { icon: <PeopleIcon />, value: stats.profile_views, label: 'Profile views', change: '+12% this week', color: '#6C5CE7' },
                                    { icon: <TrendingUpIcon />, value: stats.search_appearances, label: 'Search appearances', change: '+8% this week', color: '#00CEC9' },
                                    { icon: <PeopleIcon />, value: stats.total_connections, label: 'Connections', change: `+${stats.pending_requests || 3} pending`, color: '#FD79A8' },
                                ].map((stat, idx) => (
                                    <Grid key={idx} size={{ xs: 12, sm: 4 }}>
                                        <Box sx={{
                                            textAlign: 'center', p: 2, borderRadius: 3,
                                            bgcolor: 'action.hover',
                                            border: `1px solid divider`,
                                        }}>
                                            <Box sx={{ color: stat.color, mb: 0.5 }}>{stat.icon}</Box>
                                            <Typography variant="h4" fontWeight={800} sx={{ color: stat.color }}>{stat.value}</Typography>
                                            <Typography variant="caption" color="text.secondary" display="block">{stat.label}</Typography>
                                            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 600, fontSize: '0.65rem' }}>{stat.change}</Typography>
                                        </Box>
                                    </Grid>
                                ))}
                            </Grid>
                        </CardContent>
                    </Card>

                    {/* About */}
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="h6" fontWeight={700}>About</Typography>
                                <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                            </Box>
                            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                                Passionate {user.role} with {user.experience_years || 3}+ years in {user.department}. Skilled in building scalable applications and driving technical excellence. Focused on knowledge graph technologies, AI-powered recommendations, and modern web architectures.
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8, mt: 1 }}>
                                Always learning, always building. Open to exciting opportunities and collaborations. 🚀
                            </Typography>
                        </CardContent>
                    </Card>

                    {/* Experience */}
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="h6" fontWeight={700}>Experience</Typography>
                                <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                            </Box>
                            {experiences.map((exp, i) => (
                                <Box key={i}>
                                    <Box sx={{ display: 'flex', gap: 2, py: 1.5 }}>
                                        <Avatar variant="rounded" sx={{
                                            bgcolor: exp.color, width: 52, height: 52, fontWeight: 700, fontSize: '1.2rem',
                                            boxShadow: `0 2px 8px ${exp.color}30`,
                                        }}>{exp.logo}</Avatar>
                                        <Box sx={{ flex: 1 }}>
                                            <Typography variant="body1" fontWeight={600}>{exp.title}</Typography>
                                            <Typography variant="body2">{exp.company} • {exp.type}</Typography>
                                            <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <CalendarTodayIcon sx={{ fontSize: 12 }} /> {exp.startYear} – {exp.endYear} • {exp.years} yr{exp.years > 1 ? 's' : ''}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <LocationOnIcon sx={{ fontSize: 12 }} />{exp.location}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.8, lineHeight: 1.6, fontSize: '0.82rem' }}>
                                                {exp.description}
                                            </Typography>
                                        </Box>
                                    </Box>
                                    {i < experiences.length - 1 && <Divider sx={{ my: 0.5 }} />}
                                </Box>
                            ))}
                        </CardContent>
                    </Card>

                    {/* Education */}
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="h6" fontWeight={700}>Education</Typography>
                                <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 2 }}>
                                <Avatar variant="rounded" sx={{ bgcolor: '#00CEC9', width: 52, height: 52, boxShadow: '0 2px 8px rgba(0,206,201,0.3)' }}>
                                    <SchoolIcon />
                                </Avatar>
                                <Box>
                                    <Typography variant="body1" fontWeight={600}>{education.school}</Typography>
                                    <Typography variant="body2">{education.degree}</Typography>
                                    <Typography variant="caption" color="text.secondary">{education.years}</Typography>
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>

                    {/* Skills */}
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                                <Typography variant="h6" fontWeight={700}>Skills</Typography>
                                <IconButton size="small"><EditIcon fontSize="small" /></IconButton>
                            </Box>
                            {skills.slice(0, 6).map((skill: string, i: number) => (
                                <Box key={i}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 1.5 }}>
                                        <Box sx={{ flex: 1, mr: 2 }}>
                                            <Typography variant="body2" fontWeight={600}>{skill}</Typography>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                                                <LinearProgress variant="determinate" value={Math.min(100, (endorsements[i] || 0) * 2)}
                                                    sx={{ flex: 1, maxWidth: 120, height: 5, borderRadius: 3, bgcolor: 'rgba(108,92,231,0.08)' }} />
                                                <Typography variant="caption" color="text.secondary">{endorsements[i] || 0} endorsements</Typography>
                                            </Box>
                                        </Box>
                                        <Button size="small" variant="outlined" sx={{ borderRadius: 2.5, minWidth: 90, fontWeight: 600, fontSize: '0.75rem' }}>
                                            Endorse
                                        </Button>
                                    </Box>
                                    {i < Math.min(skills.length, 6) - 1 && <Divider />}
                                </Box>
                            ))}
                            {skills.length > 6 && (
                                <Button fullWidth sx={{ mt: 1, borderRadius: 2.5, color: 'text.secondary' }}>
                                    Show all {skills.length} skills →
                                </Button>
                            )}
                        </CardContent>
                    </Card>
                </Grid>

                {/* Right Sidebar */}
                <Grid size={{ xs: 12, md: 4 }}>
                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="subtitle2" fontWeight={700}>Profile language</Typography>
                                <IconButton size="small"><EditIcon sx={{ fontSize: 16 }} /></IconButton>
                            </Box>
                            <Typography variant="body2" color="text.secondary">English</Typography>
                        </CardContent>
                    </Card>

                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="subtitle2" fontWeight={700}>Public profile & URL</Typography>
                                <IconButton size="small"><EditIcon sx={{ fontSize: 16 }} /></IconButton>
                            </Box>
                            <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                <LinkIcon sx={{ fontSize: 16, color: '#6C5CE7' }} /> nexora.io/in/{user.username || user.name?.toLowerCase().replace(/\s+/g, '-')}
                            </Typography>
                        </CardContent>
                    </Card>

                    <Card sx={{ mb: 2.5 }}>
                        <CardContent>
                            <Typography variant="subtitle2" fontWeight={700} gutterBottom>Activity</Typography>
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
                                {stats.total_connections} followers
                            </Typography>
                            {[
                                { text: 'Shared a post about knowledge graphs and expert discovery systems.', time: '2d' },
                                { text: 'Published an article on building AI-powered recommendation engines.', time: '1w' },
                            ].map((activity, idx) => (
                                <Box key={idx} sx={{ py: 1, borderBottom: idx === 0 ? '1px solid' : 'none', borderColor: 'divider' }}>
                                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.82rem', lineHeight: 1.5 }}>
                                        {activity.text}
                                    </Typography>
                                    <Typography variant="caption" color="text.disabled">{activity.time}</Typography>
                                </Box>
                            ))}
                            <Button fullWidth size="small" sx={{ mt: 1, borderRadius: 2.5, color: 'text.secondary' }}>
                                Show all activity →
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent>
                            <Typography variant="subtitle2" fontWeight={700} gutterBottom>People also viewed</Typography>
                            {[
                                { name: 'Alex Chen', role: 'Data Scientist', dept: 'AI/ML' },
                                { name: 'Sarah Kim', role: 'Backend Engineer', dept: 'Engineering' },
                                { name: 'James Wilson', role: 'DevOps Lead', dept: 'Infrastructure' },
                                { name: 'Maria Garcia', role: 'Product Manager', dept: 'Product' },
                            ].map((person, i) => (
                                <Box key={i} sx={{
                                    display: 'flex', gap: 1.5, alignItems: 'center', py: 1,
                                    borderBottom: i < 3 ? '1px solid' : 'none', borderColor: 'divider',
                                }}>
                                    <Avatar
                                        src={`https://ui-avatars.com/api/?name=${encodeURIComponent(person.name)}&background=6C5CE7&color=fff&size=128&bold=true`}
                                        sx={{ width: 40, height: 40, bgcolor: '#6C5CE7', fontSize: '0.9rem' }}>{person.name.charAt(0)}</Avatar>
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                        <Typography variant="body2" fontWeight={600} noWrap>{person.name}</Typography>
                                        <Typography variant="caption" color="text.secondary" noWrap>{person.role} • {person.dept}</Typography>
                                    </Box>
                                    <Button size="small" variant="outlined" sx={{ borderRadius: 2.5, fontSize: '0.7rem', minWidth: 0, px: 1.5 }}>
                                        Connect
                                    </Button>
                                </Box>
                            ))}
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Box>
    );
}
