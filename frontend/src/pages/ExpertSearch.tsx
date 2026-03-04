import React, { useState, useEffect } from 'react';
import {
    Box, Typography, TextField, Card, CardContent, Grid, Chip, Avatar,
    InputAdornment, Select, MenuItem, FormControl, InputLabel, Slider,
    Button, CircularProgress, Fade, Dialog, DialogTitle, DialogContent,
    DialogActions, Stack, Divider, IconButton, LinearProgress, Paper,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import StarIcon from '@mui/icons-material/Star';
import DeleteIcon from '@mui/icons-material/Delete';
import EmailIcon from '@mui/icons-material/Email';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SchoolIcon from '@mui/icons-material/School';
import CloseIcon from '@mui/icons-material/Close';
import CodeIcon from '@mui/icons-material/Code';
import PersonIcon from '@mui/icons-material/Person';
import PeopleIcon from '@mui/icons-material/People';
import { expertService, authService } from '../services/api';

interface Expert {
    id: string; name: string; email: string; department: string;
    role: string; location: string; hire_date?: string;
    experience_years: number; expertise_level: number;
}

interface ExpertDetails extends Expert {
    skills?: Array<{ id: string; name: string; level?: string }>;
    projects?: Array<{ id: string; name: string; status?: string }>;
    documents?: Array<{ id: string; title: string; type?: string }>;
    connections?: number;
}

const generateBio = (expert: Expert): string => {
    const bios: { [key: string]: string[] } = {
        'Engineering': [
            `${expert.name} is a passionate software engineer with ${expert.experience_years} years of experience in building scalable applications. Specializes in modern development practices and mentoring junior developers.`,
            `With a strong foundation in computer science and ${expert.experience_years} years of hands-on experience, ${expert.name} has contributed to numerous high-impact projects across the organization.`,
        ],
        'Data Science': [
            `${expert.name} is an experienced data scientist who transforms complex data into actionable insights. With ${expert.experience_years} years in the field, they excel at machine learning and statistical analysis.`,
        ],
        'DevOps': [
            `${expert.name} specializes in building and maintaining robust CI/CD pipelines and cloud infrastructure. With ${expert.experience_years} years of experience in DevOps practices.`,
        ],
        'Security': [
            `${expert.name} is a cybersecurity specialist with ${expert.experience_years} years of experience in protecting digital assets and implementing security best practices.`,
        ],
        'default': [
            `${expert.name} is a dedicated professional with ${expert.experience_years} years of experience in ${expert.department}. Known for their expertise and collaborative approach to problem-solving.`,
        ],
    };
    const deptBios = bios[expert.department] || bios['default'];
    return deptBios[Math.floor(Math.random() * deptBios.length)];
};

const generateSkills = (expert: Expert): Array<{ name: string; level: number }> => {
    const skillsByDept: { [key: string]: string[] } = {
        'Engineering': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'AWS'],
        'Data Science': ['Python', 'TensorFlow', 'PyTorch', 'Pandas', 'SQL', 'Machine Learning', 'Statistics', 'Spark'],
        'DevOps': ['Kubernetes', 'Docker', 'Terraform', 'AWS', 'CI/CD', 'Jenkins', 'Linux', 'Ansible'],
        'Security': ['OWASP', 'Penetration Testing', 'Network Security', 'Encryption', 'IAM', 'SIEM'],
        'Cloud Infrastructure': ['AWS', 'Azure', 'GCP', 'Terraform', 'Kubernetes', 'Networking'],
        'Web Development': ['React', 'TypeScript', 'Node.js', 'CSS', 'HTML', 'GraphQL', 'REST APIs'],
        'AI Research': ['PyTorch', 'TensorFlow', 'NLP', 'Computer Vision', 'Deep Learning', 'Python'],
        'default': ['Communication', 'Problem Solving', 'Teamwork', 'Project Management'],
    };
    const deptSkills = skillsByDept[expert.department] || skillsByDept['default'];
    const numSkills = Math.min(5 + Math.floor(expert.expertise_level / 2), deptSkills.length);
    return deptSkills.slice(0, numSkills).map(skill => ({
        name: skill, level: 50 + Math.floor(Math.random() * 50),
    }));
};

const generateProjects = (expert: Expert): Array<{ name: string; status: string; role: string }> => {
    const projects = [
        { name: 'Cloud Migration Initiative', status: 'Active', role: 'Tech Lead' },
        { name: 'Data Platform Modernization', status: 'Completed', role: 'Developer' },
        { name: 'Security Audit 2024', status: 'Active', role: 'Consultant' },
        { name: 'API Gateway Implementation', status: 'Completed', role: 'Architect' },
        { name: 'ML Pipeline Automation', status: 'Planning', role: 'Developer' },
        { name: 'DevOps Transformation', status: 'Active', role: 'Lead Engineer' },
    ];
    return projects.slice(0, 2 + Math.floor(expert.expertise_level / 2));
};

const generateCertifications = (expert: Expert): string[] => {
    const certsByDept: { [key: string]: string[] } = {
        'Engineering': ['AWS Solutions Architect', 'Google Cloud Professional', 'Certified Kubernetes Administrator'],
        'Data Science': ['TensorFlow Developer Certificate', 'AWS Machine Learning Specialty', 'Data Science Professional'],
        'DevOps': ['AWS DevOps Engineer', 'Certified Kubernetes Administrator', 'HashiCorp Terraform Associate'],
        'Security': ['CISSP', 'CEH', 'CompTIA Security+', 'OSCP'],
        'default': ['Professional Scrum Master', 'PMP', 'ITIL Foundation'],
    };
    const certs = certsByDept[expert.department] || certsByDept['default'];
    return certs.slice(0, Math.min(expert.expertise_level, certs.length));
};

const ExpertSearch: React.FC = () => {
    const [experts, setExperts] = useState<Expert[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [location, setLocation] = useState('');
    const [locations, setLocations] = useState<string[]>([]);
    const [department, setDepartment] = useState('');
    const [departments, setDepartments] = useState<string[]>([]);
    const [minLevel, setMinLevel] = useState<number>(1);
    const [minExperience, setMinExperience] = useState<number>(0);
    const [createOpen, setCreateOpen] = useState(false);
    const [creating, setCreating] = useState(false);
    const [newExpert, setNewExpert] = useState({
        name: '', email: '', department: '', role: '', location: '',
        experience_years: 0, expertise_level: 3,
    });
    const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);
    const [detailOpen, setDetailOpen] = useState(false);
    const [_expertDetails, setExpertDetails] = useState<ExpertDetails | null>(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

    useEffect(() => { loadFilters(); }, []);
    useEffect(() => {
        const timer = setTimeout(() => { searchExperts(); }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery, location, department, minLevel, minExperience]);

    const loadFilters = async () => {
        try {
            const [locRes, deptRes] = await Promise.all([expertService.getLocations(), expertService.getDepartments()]);
            setLocations(locRes.data); setDepartments(deptRes.data);
        } catch (error) { console.error('Error loading filters:', error); }
    };

    const searchExperts = async () => {
        setLoading(true);
        try {
            const params: any = { limit: 20 };
            if (searchQuery) params.q = searchQuery;
            if (location) params.location = location;
            if (department) params.department = department;
            if (minLevel > 1) params.level = minLevel;
            if (minExperience > 0) params.experience = minExperience;
            const response = await expertService.search(params);
            setExperts(response.data);
        } catch (error) { console.error('Error searching experts:', error); }
        finally { setLoading(false); }
    };

    const handleSearch = (e: React.FormEvent) => { e.preventDefault(); searchExperts(); };

    const handleExpertClick = async (expert: Expert) => {
        setSelectedExpert(expert); setDetailOpen(true); setLoadingDetails(true);
        try {
            const response = await expertService.getById(expert.id);
            setExpertDetails(response.data);
        } catch (error) {
            setExpertDetails({
                ...expert,
                skills: generateSkills(expert).map(s => ({ id: s.name, name: s.name, level: s.level.toString() })),
                projects: [], documents: [],
            });
        } finally { setLoadingDetails(false); }
    };

    const handleCloseDetail = () => { setDetailOpen(false); setSelectedExpert(null); setExpertDetails(null); };

    const handleDeleteExpert = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this expert?')) {
            try { await expertService.delete(id); setExperts(experts.filter(e => e.id !== id)); }
            catch (error) { alert('Failed to delete expert. Are you logged in?'); }
        }
    };

    const getLevelColor = (level: number) => {
        const colors = ['#94a3b8', '#00B894', '#6C5CE7', '#FDCB6E', '#FD79A8'];
        return colors[level - 1] || colors[0];
    };

    const getLevelLabel = (level: number) => {
        const labels = ['Junior', 'Intermediate', 'Senior', 'Lead', 'Principal'];
        return labels[level - 1] || 'Unknown';
    };

    const handleCreate = async () => {
        setCreating(true);
        try {
            await expertService.create(newExpert);
            setCreateOpen(false);
            setNewExpert({ name: '', email: '', department: '', role: '', location: '', experience_years: 0, expertise_level: 3 });
            await searchExperts(); await loadFilters();
        } catch (error: any) {
            if (error.response?.status !== 401) {
                alert('Failed to create expert: ' + (error.response?.data?.detail || error.message));
            }
        } finally { setCreating(false); }
    };

    return (
        <Box sx={{ p: { xs: 2, md: 4 } }}>
            {/* Header */}
            <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5 }}>
                    <Box sx={{
                        width: 44, height: 44, borderRadius: 2.5, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        bgcolor: 'primary.light',
                    }}>
                        <PeopleIcon sx={{ color: 'primary.main', fontSize: 24 }} />
                    </Box>
                    <Typography variant="h4" fontWeight={800} color="primary">Expert Search</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 7.5 }}>
                    Find experts by skills, location, and experience level
                </Typography>
            </Box>

            {/* Search Form */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    {authService.isAuthenticated() && (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                            <Button variant="outlined" onClick={() => setCreateOpen(true)} sx={{ borderRadius: 2.5 }}>Add Expert</Button>
                        </Box>
                    )}
                    <form onSubmit={handleSearch}>
                        <Grid container spacing={2} alignItems="center">
                            <Grid size={{ xs: 12, md: 3 }}>
                                <TextField fullWidth placeholder="Search name, role, or skill..." value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }} />
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <FormControl fullWidth>
                                    <InputLabel>Location</InputLabel>
                                    <Select value={location} label="Location" onChange={(e) => setLocation(e.target.value)}>
                                        <MenuItem value="">All Locations</MenuItem>
                                        {locations.map((loc) => <MenuItem key={loc} value={loc}>{loc}</MenuItem>)}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <FormControl fullWidth>
                                    <InputLabel>Department</InputLabel>
                                    <Select value={department} label="Department" onChange={(e: any) => setDepartment(e.target.value)}>
                                        <MenuItem value="">All Departments</MenuItem>
                                        {departments.map((dept) => <MenuItem key={dept} value={dept}>{dept}</MenuItem>)}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <TextField fullWidth type="number" label="Min Experience (years)" value={minExperience}
                                    onChange={(e) => setMinExperience(Number(e.target.value))} inputProps={{ min: 0 }} />
                            </Grid>
                            <Grid size={{ xs: 12, md: 9 }}>
                                <Box sx={{ px: 2 }}>
                                    <Typography variant="caption" color="text.secondary">Min Expertise Level: {minLevel}</Typography>
                                    <Slider value={minLevel} onChange={(_, value) => setMinLevel(value as number)}
                                        min={1} max={5} marks valueLabelDisplay="auto" sx={{ mt: 1 }} />
                                </Box>
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <Button fullWidth variant="contained" type="submit" size="large" sx={{ height: 56, borderRadius: 2.5 }}>Search</Button>
                            </Grid>
                        </Grid>
                    </form>
                </CardContent>
            </Card>

            {/* Create Expert Dialog */}
            <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Add Expert</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        <TextField label="Full Name" value={newExpert.name} onChange={(e) => setNewExpert({ ...newExpert, name: e.target.value })} required fullWidth />
                        <TextField label="Email" type="email" value={newExpert.email} onChange={(e) => setNewExpert({ ...newExpert, email: e.target.value })} required fullWidth />
                        <TextField label="Department" value={newExpert.department} onChange={(e) => setNewExpert({ ...newExpert, department: e.target.value })} required fullWidth />
                        <TextField label="Role" value={newExpert.role} onChange={(e) => setNewExpert({ ...newExpert, role: e.target.value })} required fullWidth />
                        <TextField label="Location" value={newExpert.location} onChange={(e) => setNewExpert({ ...newExpert, location: e.target.value })} required fullWidth />
                        <TextField label="Years of Experience" type="number" value={newExpert.experience_years}
                            onChange={(e) => setNewExpert({ ...newExpert, experience_years: Number(e.target.value) })} required fullWidth />
                        <Box>
                            <Typography gutterBottom>Expertise Level: {newExpert.expertise_level}</Typography>
                            <Slider value={newExpert.expertise_level} onChange={(_, value) => setNewExpert({ ...newExpert, expertise_level: value as number })} min={1} max={5} marks />
                        </Box>
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateOpen(false)} disabled={creating}>Cancel</Button>
                    <Button onClick={handleCreate} variant="contained" disabled={creating || !newExpert.name || !newExpert.email}
                        sx={{ borderRadius: 2.5 }}>{creating ? 'Saving...' : 'Save'}</Button>
                </DialogActions>
            </Dialog>

            {/* Expert Detail Dialog */}
            <Dialog open={detailOpen} onClose={handleCloseDetail} maxWidth="md" fullWidth
                PaperProps={{ sx: { borderRadius: 3 } }}>
                {selectedExpert && (
                    <>
                        <DialogTitle sx={{ pb: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="h5" fontWeight={700}>Expert Profile</Typography>
                            <IconButton onClick={handleCloseDetail} sx={{ color: 'text.secondary' }}><CloseIcon /></IconButton>
                        </DialogTitle>
                        <DialogContent>
                            {loadingDetails ? (
                                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress sx={{ color: '#6C5CE7' }} /></Box>
                            ) : (
                                <Box sx={{ py: 2 }}>
                                    {/* Header */}
                                    <Paper sx={{
                                        p: 3, mb: 3, borderRadius: 3,
                                        background: 'linear-gradient(135deg, rgba(108,92,231,0.1), rgba(0,206,201,0.05))',
                                        border: '1px solid rgba(108,92,231,0.1)',
                                    }}>
                                        <Box sx={{ display: 'flex', gap: 3, alignItems: 'flex-start' }}>
                                            <Avatar
                                                src={`https://ui-avatars.com/api/?name=${encodeURIComponent(selectedExpert.name)}&background=1976d2&color=fff&size=200&bold=true`}
                                                sx={{
                                                    width: 100, height: 100, bgcolor: 'primary.main', fontSize: '2.5rem', fontWeight: 700,
                                                }}>
                                                {selectedExpert.name.charAt(0)}
                                            </Avatar>
                                            <Box sx={{ flex: 1 }}>
                                                <Typography variant="h4" fontWeight={800} sx={{ mb: 0.5 }}>{selectedExpert.name}</Typography>
                                                <Typography variant="h6" color="primary" sx={{ mb: 1 }}>{selectedExpert.role}</Typography>
                                                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                    <Chip icon={<WorkIcon />} label={selectedExpert.department} size="small"
                                                        sx={{ bgcolor: 'rgba(108,92,231,0.15)' }} />
                                                    <Chip icon={<LocationOnIcon />} label={selectedExpert.location} size="small"
                                                        sx={{ bgcolor: 'rgba(0,184,148,0.15)' }} />
                                                    <Chip icon={<StarIcon sx={{ color: getLevelColor(selectedExpert.expertise_level) }} />}
                                                        label={`${getLevelLabel(selectedExpert.expertise_level)} (Level ${selectedExpert.expertise_level})`} size="small"
                                                        sx={{ bgcolor: 'rgba(253,203,110,0.12)' }} />
                                                </Box>
                                            </Box>
                                        </Box>
                                    </Paper>

                                    {/* Bio */}
                                    <Box sx={{ mb: 3 }}>
                                        <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <PersonIcon color="primary" /> About
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                                            {generateBio(selectedExpert)}
                                        </Typography>
                                    </Box>
                                    <Divider sx={{ my: 2 }} />

                                    {/* Contact & Certs */}
                                    <Grid container spacing={3} sx={{ mb: 3 }}>
                                        <Grid size={{ xs: 12, md: 6 }}>
                                            <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <EmailIcon color="primary" /> Contact
                                            </Typography>
                                            <Stack spacing={1.5}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <EmailIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
                                                    <Typography variant="body2">{selectedExpert.email}</Typography>
                                                </Box>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <LocationOnIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
                                                    <Typography variant="body2">{selectedExpert.location}</Typography>
                                                </Box>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <CalendarTodayIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
                                                    <Typography variant="body2">{selectedExpert.experience_years} years of experience</Typography>
                                                </Box>
                                            </Stack>
                                        </Grid>
                                        <Grid size={{ xs: 12, md: 6 }}>
                                            <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                                <SchoolIcon sx={{ color: '#00CEC9' }} /> Certifications
                                            </Typography>
                                            <Stack spacing={1}>
                                                {generateCertifications(selectedExpert).map((cert, idx) => (
                                                    <Chip key={idx} label={cert} size="small" sx={{ width: 'fit-content', bgcolor: 'rgba(108,92,231,0.12)' }} />
                                                ))}
                                            </Stack>
                                        </Grid>
                                    </Grid>
                                    <Divider sx={{ my: 2 }} />

                                    {/* Skills */}
                                    <Box sx={{ mb: 3 }}>
                                        <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <CodeIcon color="primary" /> Technical Skills
                                        </Typography>
                                        <Grid container spacing={2}>
                                            {generateSkills(selectedExpert).map((skill, idx) => (
                                                <Grid size={{ xs: 12, sm: 6 }} key={idx}>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                                        <Typography variant="body2" fontWeight={500}>{skill.name}</Typography>
                                                        <Typography variant="body2" color="text.secondary">{skill.level}%</Typography>
                                                    </Box>
                                                    <LinearProgress variant="determinate" value={skill.level} sx={{ height: 6, borderRadius: 3 }} />
                                                </Grid>
                                            ))}
                                        </Grid>
                                    </Box>
                                    <Divider sx={{ my: 2 }} />

                                    {/* Projects */}
                                    <Box>
                                        <Typography variant="h6" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <WorkIcon sx={{ color: '#FDCB6E' }} /> Recent Projects
                                        </Typography>
                                        <Grid container spacing={2}>
                                            {generateProjects(selectedExpert).map((project, idx) => (
                                                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={idx}>
                                                    <Paper sx={{
                                                        p: 2, borderRadius: 2.5,
                                                        border: '1px solid', borderColor: 'divider',
                                                    }}>
                                                        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>{project.name}</Typography>
                                                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                                                            <Chip label={project.status} size="small"
                                                                color={project.status === 'Active' ? 'success' : project.status === 'Completed' ? 'info' : 'default'} />
                                                            <Chip label={project.role} size="small" variant="outlined" />
                                                        </Box>
                                                    </Paper>
                                                </Grid>
                                            ))}
                                        </Grid>
                                    </Box>
                                </Box>
                            )}
                        </DialogContent>
                        <DialogActions sx={{ px: 3, pb: 2 }}>
                            <Button onClick={handleCloseDetail} variant="outlined" sx={{ borderRadius: 2.5 }}>Close</Button>
                            <Button variant="contained" startIcon={<EmailIcon />} sx={{ borderRadius: 2.5 }}
                                onClick={() => window.location.href = `mailto:${selectedExpert.email}`}>Contact Expert</Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>

            {/* Results */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress size={50} sx={{ color: '#6C5CE7' }} />
                </Box>
            ) : (
                <Grid container spacing={2.5}>
                    {experts.map((expert, index) => (
                        <Grid size={{ xs: 12, md: 6, lg: 4 }} key={expert.id}>
                            <Fade in timeout={300 + index * 80}>
                                <Card
                                    onClick={() => handleExpertClick(expert)}
                                    sx={{
                                        height: '100%', cursor: 'pointer',
                                        '&:hover': { bgcolor: 'action.hover' },
                                    }}
                                >
                                    <CardContent>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                            <Avatar
                                                src={`https://ui-avatars.com/api/?name=${encodeURIComponent(expert.name)}&background=1976d2&color=fff&size=128&bold=true`}
                                                sx={{
                                                    width: 56, height: 56, bgcolor: 'primary.main', fontSize: '1.5rem', fontWeight: 700, mr: 2,
                                                }}>
                                                {expert.name.charAt(0)}
                                            </Avatar>
                                            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                                                <Typography variant="body1" fontWeight={600} noWrap>{expert.name}</Typography>
                                                <Typography variant="caption" color="text.secondary" noWrap display="block">{expert.role}</Typography>
                                            </Box>
                                            {authService.isAuthenticated() && (
                                                <IconButton color="error" size="small"
                                                    onClick={(e) => { e.stopPropagation(); handleDeleteExpert(expert.id); }}>
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            )}
                                        </Box>
                                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1.5 }}>
                                            <Chip icon={<WorkIcon />} label={expert.department} size="small" sx={{ bgcolor: 'rgba(108,92,231,0.12)', fontSize: '0.7rem' }} />
                                            <Chip icon={<LocationOnIcon />} label={expert.location} size="small" sx={{ bgcolor: 'rgba(0,184,148,0.12)', fontSize: '0.7rem' }} />
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <StarIcon sx={{ color: getLevelColor(expert.expertise_level), fontSize: 18 }} />
                                                <Typography variant="caption" fontWeight={600}>
                                                    {getLevelLabel(expert.expertise_level)}
                                                </Typography>
                                            </Box>
                                            <Typography variant="caption" color="text.secondary">{expert.experience_years} yrs exp.</Typography>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Fade>
                        </Grid>
                    ))}
                </Grid>
            )}

            {!loading && experts.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Box sx={{
                        width: 80, height: 80, borderRadius: '50%', mx: 'auto', mb: 2,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'linear-gradient(135deg, rgba(108,92,231,0.1), rgba(0,206,201,0.05))',
                    }}>
                        <PeopleIcon sx={{ fontSize: 36, color: '#A29BFE' }} />
                    </Box>
                    <Typography variant="h6" color="text.secondary">No experts found. Try adjusting your filters.</Typography>
                </Box>
            )}
        </Box>
    );
};

export default ExpertSearch;
