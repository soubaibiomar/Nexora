import { useState, useEffect } from 'react';
import {
    Box, Typography, Card, CardContent, Button, Chip, Grid,
    TextField, CircularProgress, Divider, InputAdornment,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import WorkIcon from '@mui/icons-material/Work';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BusinessIcon from '@mui/icons-material/Business';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { jobsService } from '../services/api';

function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const days = Math.floor(diff / 86400000);
    if (days < 1) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    return `${Math.floor(days / 30)} months ago`;
}

export default function Jobs() {
    const [jobs, setJobs] = useState<any[]>([]);
    const [recommended, setRecommended] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [locationFilter, setLocationFilter] = useState('');
    const [saved, setSaved] = useState<Set<string>>(new Set());
    const [applied, setApplied] = useState<Set<string>>(new Set());
    const [selectedJob, setSelectedJob] = useState<any>(null);

    useEffect(() => {
        const load = async () => {
            try {
                const [jobsRes, recRes] = await Promise.all([
                    jobsService.getJobs(), jobsService.getRecommended(),
                ]);
                setJobs(jobsRes.data.jobs || []);
                setRecommended(recRes.data.jobs || []);
                if (jobsRes.data.jobs?.length > 0) setSelectedJob(jobsRes.data.jobs[0]);
            } catch { /* ignore */ }
            setLoading(false);
        };
        load();
    }, []);

    const handleSearch = async () => {
        try {
            const res = await jobsService.getJobs({ q: search || undefined, location: locationFilter || undefined });
            setJobs(res.data.jobs || []);
            if (res.data.jobs?.length > 0) setSelectedJob(res.data.jobs[0]);
        } catch { /* ignore */ }
    };

    const handleApply = async (jobId: string) => {
        try { await jobsService.applyToJob(jobId); setApplied((prev) => new Set(prev).add(jobId)); } catch { /* ignore */ }
    };

    const toggleSave = (jobId: string) => {
        setSaved((prev) => { const copy = new Set(prev); if (copy.has(jobId)) copy.delete(jobId); else copy.add(jobId); return copy; });
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 1150, mx: 'auto', p: { xs: 2, md: 3 } }}>
            {/* Header */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h4" fontWeight={800} color="primary">
                    Jobs
                </Typography>
                <Typography variant="body2" color="text.secondary">AI-powered job recommendations tailored for you</Typography>
            </Box>

            {/* Search */}
            <Card sx={{ mb: 2.5 }}>
                <CardContent sx={{ display: 'flex', gap: 1.5, alignItems: 'center', py: '12px !important' }}>
                    <TextField size="small" placeholder="Search jobs by title, skill, or keyword..."
                        value={search} onChange={(e) => setSearch(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }}
                        sx={{ flex: 2 }} />
                    <TextField size="small" placeholder="Location"
                        value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}
                        InputProps={{ startAdornment: <InputAdornment position="start"><LocationOnIcon /></InputAdornment> }}
                        sx={{ flex: 1 }} />
                    <Button variant="contained" onClick={handleSearch} sx={{ borderRadius: 2.5, px: 3 }}>Search</Button>
                </CardContent>
            </Card>

            {/* Recommended */}
            {recommended.length > 0 && (
                <Box sx={{ mb: 2.5 }}>
                    <Typography variant="h6" fontWeight={700} sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AutoAwesomeIcon sx={{ color: '#A29BFE', fontSize: 22 }} /> AI Recommended for You
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1.5, overflowX: 'auto', pb: 1, '::-webkit-scrollbar': { height: 4 } }}>
                        {recommended.slice(0, 5).map((job: any) => (
                            <Card key={job.id} sx={{
                                minWidth: 240, cursor: 'pointer', transition: 'all 0.3s',
                            }} onClick={() => setSelectedJob(job)}>
                                <CardContent sx={{ pb: '12px !important' }}>
                                    <Chip icon={<AutoAwesomeIcon sx={{ fontSize: 12 }} />} label="AI Match" size="small"
                                        sx={{ mb: 1, fontSize: '0.65rem', height: 20, bgcolor: 'rgba(108,92,231,0.12)', color: '#A29BFE' }} />
                                    <Typography variant="body2" fontWeight={600} noWrap>{job.title}</Typography>
                                    <Typography variant="caption" color="text.secondary">{job.company}</Typography>
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        <LocationOnIcon sx={{ fontSize: 11, mr: 0.3 }} />{job.location}
                                    </Typography>
                                </CardContent>
                            </Card>
                        ))}
                    </Box>
                </Box>
            )}

            {/* Jobs List + Detail */}
            <Grid container spacing={2.5}>
                <Grid size={{ xs: 12, md: 5 }}>
                    <Card>
                        <CardContent sx={{ p: '0 !important', maxHeight: 'calc(100vh - 300px)', overflow: 'auto' }}>
                            {jobs.map((job: any, i: number) => (
                                <Box key={job.id}>
                                    <Box sx={{
                                        p: 2, cursor: 'pointer', transition: 'all 0.2s',
                                        bgcolor: selectedJob?.id === job.id ? 'action.selected' : 'transparent',
                                        borderLeft: selectedJob?.id === job.id ? '3px solid' : '3px solid transparent',
                                        borderColor: 'primary.main',
                                        '&:hover': { bgcolor: 'action.hover' },
                                    }} onClick={() => setSelectedJob(job)}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                            <Box sx={{ flex: 1, minWidth: 0 }}>
                                                <Typography variant="body2" fontWeight={600} color="primary" noWrap>{job.title}</Typography>
                                                <Typography variant="caption">{job.company}</Typography>
                                                <Typography variant="caption" color="text.secondary" display="block">
                                                    <LocationOnIcon sx={{ fontSize: 11, mr: 0.3 }} />{job.location}
                                                </Typography>
                                                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                                                    {job.easy_apply && <Chip label="Easy Apply" size="small" sx={{ fontSize: '0.6rem', height: 18, bgcolor: 'rgba(0,184,148,0.12)', color: '#00B894' }} />}
                                                    {job.is_promoted && <Chip label="Promoted" size="small" sx={{ fontSize: '0.6rem', height: 18 }} />}
                                                </Box>
                                                <Typography variant="caption" color="text.secondary">{timeAgo(job.posted_at)}</Typography>
                                            </Box>
                                            <Box onClick={(e) => e.stopPropagation()}>
                                                <Button size="small" onClick={() => toggleSave(job.id)} sx={{ minWidth: 0, p: 0.5 }}>
                                                    {saved.has(job.id) ? <BookmarkIcon color="primary" /> : <BookmarkBorderIcon />}
                                                </Button>
                                            </Box>
                                        </Box>
                                    </Box>
                                    {i < jobs.length - 1 && <Divider />}
                                </Box>
                            ))}
                        </CardContent>
                    </Card>
                </Grid>

                <Grid size={{ xs: 12, md: 7 }}>
                    {selectedJob && (
                        <Card sx={{ position: 'sticky', top: 16 }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                                    <Box>
                                        <Typography variant="h5" fontWeight={800} color="primary">{selectedJob.title}</Typography>
                                        <Typography variant="body1" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                                            <BusinessIcon sx={{ fontSize: 16 }} /> {selectedJob.company}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                            <LocationOnIcon sx={{ fontSize: 14 }} /> {selectedJob.location}
                                        </Typography>
                                    </Box>
                                    <Box onClick={(e) => e.stopPropagation()}>
                                        <Button onClick={() => toggleSave(selectedJob.id)} sx={{ minWidth: 0 }}>
                                            {saved.has(selectedJob.id) ? <BookmarkIcon color="primary" fontSize="large" /> : <BookmarkBorderIcon fontSize="large" />}
                                        </Button>
                                    </Box>
                                </Box>

                                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                                    <Chip icon={<WorkIcon />} label={selectedJob.type} size="small" />
                                    <Chip label={selectedJob.level} size="small" />
                                    <Chip label={selectedJob.salary_range} size="small" variant="outlined" />
                                    <Chip label={`${selectedJob.applicants} applicants`} size="small" variant="outlined" />
                                </Box>

                                <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                                    {applied.has(selectedJob.id) ? (
                                        <Button variant="contained" startIcon={<CheckCircleIcon />} disabled sx={{
                                            borderRadius: 2.5, px: 3, bgcolor: '#00B894 !important', color: 'white !important',
                                        }}>Applied</Button>
                                    ) : (
                                        <Button variant="contained" onClick={() => handleApply(selectedJob.id)} sx={{ borderRadius: 2.5, px: 3 }}>
                                            {selectedJob.easy_apply ? '⚡ Easy Apply' : 'Apply'}
                                        </Button>
                                    )}
                                    <Button variant="outlined" onClick={() => toggleSave(selectedJob.id)} sx={{ borderRadius: 2.5, px: 3 }}>
                                        {saved.has(selectedJob.id) ? 'Saved' : 'Save'}
                                    </Button>
                                </Box>

                                <Divider sx={{ mb: 2 }} />

                                <Typography variant="h6" fontWeight={700} gutterBottom>About the job</Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.7 }}>
                                    {selectedJob.description}
                                </Typography>

                                <Typography variant="h6" fontWeight={700} gutterBottom>Required Skills</Typography>
                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                    {selectedJob.required_skills?.map((skill: string, i: number) => (
                                        <Chip key={i} label={skill} size="small" variant="outlined" />
                                    ))}
                                </Box>
                            </CardContent>
                        </Card>
                    )}
                </Grid>
            </Grid>
        </Box>
    );
}
