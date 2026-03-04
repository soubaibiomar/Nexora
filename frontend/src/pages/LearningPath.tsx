import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    CardMedia,
    Grid,
    Button,
    CircularProgress,
    TextField,
    Chip,
    Stepper,
    Step,
    StepLabel,
    StepContent,
    Avatar,
    Paper,
    Autocomplete,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Tabs,
    Tab,
    Divider,
    InputAdornment,
    ToggleButtonGroup,
    ToggleButton,
    Alert,
} from '@mui/material';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import SearchIcon from '@mui/icons-material/Search';
import YouTubeIcon from '@mui/icons-material/YouTube';
import LanguageIcon from '@mui/icons-material/Language';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import StarIcon from '@mui/icons-material/Star';
import { learningService, learningResourcesService, documentService } from '../services/api';

// ── Types ───────────────────────────────────────────────────────

interface LearningStep {
    skill: string;
    level: string;
    estimated_hours: number;
    resources: Array<{ id: string; title: string; type: string; rating: number }>;
    mentors: Array<{ id: string; name: string; level: number; department: string }>;
    type?: string;
    description?: string;
    objectives?: string[];
    key_topics?: string[];
}

interface LearningPathData {
    target_skill: string;
    total_steps: number;
    estimated_total_hours: number;
    steps: LearningStep[];
    difficulty?: string;
    suggested_prerequisites?: string[];
}

interface VideoResource {
    id: string;
    title: string;
    channel: string;
    video_id: string;
    duration: string;
    level: string;
    views: string;
    skill: string;
    source: string;
    thumbnail: string;
    url: string;
    embed_url: string;
}

interface TutorialResource {
    id: string;
    title: string;
    url: string;
    topic: string;
    level: string;
    skill: string;
    source: string;
}

interface CourseResource {
    id: string;
    title: string;
    platform: string;
    url: string;
    instructor: string;
    level: string;
    price: string;
    rating: number;
    duration: string;
    source: string;
}

interface Recommendation {
    skill: string;
    reason: string;
    total_videos: number;
    total_tutorials: number;
    top_video: VideoResource | null;
    top_tutorial: TutorialResource | null;
}

// ── Tab Panel ───────────────────────────────────────────────────

function TabPanel({ children, value, index }: { children: React.ReactNode; value: number; index: number }) {
    return value === index ? <Box sx={{ pt: 3 }}>{children}</Box> : null;
}

// ── Main Component ──────────────────────────────────────────────

const LearningPathPage: React.FC = () => {
    const [tab, setTab] = useState(0);

    // Learning Path state
    const [currentSkills, setCurrentSkills] = useState<string[]>([]);
    const [targetSkill, setTargetSkill] = useState('');
    const [learningPath, setLearningPath] = useState<LearningPathData | null>(null);
    const [pathLoading, setPathLoading] = useState(false);
    const [recommendedSkills, setRecommendedSkills] = useState<any[]>([]);
    const [activeStep, setActiveStep] = useState(0);
    const [viewOpen, setViewOpen] = useState(false);
    const [viewLoading, setViewLoading] = useState(false);
    const [viewTitle, setViewTitle] = useState('');
    const [viewContent, setViewContent] = useState('');
    const [skillOptions, setSkillOptions] = useState<string[]>([]);

    // Resources state
    const [resourceSkills, setResourceSkills] = useState<string[]>([]);
    const [selectedSkill, setSelectedSkill] = useState('');
    const [videos, setVideos] = useState<VideoResource[]>([]);
    const [tutorials, setTutorials] = useState<TutorialResource[]>([]);
    const [courses, setCourses] = useState<CourseResource[]>([]);
    const [resourcesLoading, setResourcesLoading] = useState(false);
    const [levelFilter, setLevelFilter] = useState<string>('');
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [searchLoading, setSearchLoading] = useState(false);

    // AI Recommendations
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [recLoading, setRecLoading] = useState(false);

    // Video player dialog
    const [videoDialog, setVideoDialog] = useState(false);
    const [activeVideo, setActiveVideo] = useState<VideoResource | null>(null);

    // Skill-specific resources fetched with the generated path
    const [pathVideos, setPathVideos] = useState<VideoResource[]>([]);
    const [pathTutorials, setPathTutorials] = useState<TutorialResource[]>([]);
    const [pathCourses, setPathCourses] = useState<CourseResource[]>([]);

    useEffect(() => {
        loadSkills();
        loadResourceSkills();
    }, []);

    useEffect(() => {
        if (currentSkills.length > 0) {
            loadRecommendations();
            loadAIRecommendations();
        }
    }, [currentSkills]);

    // ── Data Loading ────────────────────────────────────────────

    const loadSkills = async () => {
        try {
            const response = await learningService.getSkills();
            setSkillOptions(response.data);
        } catch (error) {
            console.error('Error loading skills:', error);
        }
    };

    const loadResourceSkills = async () => {
        try {
            const response = await learningResourcesService.getSkills();
            setResourceSkills(response.data.skills);
            if (response.data.skills.length > 0 && !selectedSkill) {
                setSelectedSkill(response.data.skills[0]);
                loadResourcesForSkill(response.data.skills[0]);
            }
        } catch (error) {
            console.error('Error loading resource skills:', error);
        }
    };

    const loadResourcesForSkill = async (skill: string, level?: string) => {
        setResourcesLoading(true);
        try {
            const response = await learningResourcesService.getBySkill(skill, level || undefined);
            setVideos(response.data.videos);
            setTutorials(response.data.tutorials);
            setCourses(response.data.courses || []);
        } catch (error) {
            console.error('Error loading resources:', error);
        } finally {
            setResourcesLoading(false);
        }
    };

    const handleSkillSelect = (skill: string) => {
        setSelectedSkill(skill);
        loadResourcesForSkill(skill, levelFilter);
    };

    const handleLevelFilter = (level: string) => {
        setLevelFilter(level);
        if (selectedSkill) loadResourcesForSkill(selectedSkill, level);
    };

    const handleSearch = async () => {
        if (!searchQuery.trim()) return;
        setSearchLoading(true);
        try {
            const response = await learningResourcesService.search(searchQuery, levelFilter || undefined);
            setSearchResults(response.data.results);
        } catch (error) {
            console.error('Error searching:', error);
        } finally {
            setSearchLoading(false);
        }
    };

    const loadRecommendations = async () => {
        try {
            const response = await learningService.getRecommendedSkills(currentSkills, 5);
            setRecommendedSkills(response.data);
        } catch (error) {
            console.error('Error loading recommendations:', error);
        }
    };

    const loadAIRecommendations = async () => {
        setRecLoading(true);
        try {
            const response = await learningResourcesService.recommend(currentSkills, [], undefined, 8);
            setRecommendations(response.data.recommendations);
        } catch (error) {
            console.error('Error loading AI recommendations:', error);
        } finally {
            setRecLoading(false);
        }
    };

    const openResource = async (resource: { id: string; title: string }) => {
        setViewTitle(resource.title);
        setViewContent('');
        setViewOpen(true);
        setViewLoading(true);
        try {
            const res = await documentService.getById(resource.id);
            setViewContent(res.data?.content || '(No content)');
        } catch (error) {
            setViewContent('(Failed to load content)');
        } finally {
            setViewLoading(false);
        }
    };

    const generatePath = async () => {
        if (!targetSkill) return;
        setPathLoading(true);
        try {
            const [pathRes, resourcesRes] = await Promise.all([
                learningService.generatePath(currentSkills, targetSkill),
                learningResourcesService.getBySkill(targetSkill),
            ]);
            setLearningPath(pathRes.data);
            setActiveStep(0);
            // Store skill-specific videos & tutorials alongside the path
            setPathVideos(resourcesRes.data.videos || []);
            setPathTutorials(resourcesRes.data.tutorials || []);
            setPathCourses(resourcesRes.data.courses || []);
        } catch (error) {
            console.error('Error generating path:', error);
        } finally {
            setPathLoading(false);
        }
    };

    const getLevelColor = (level: string) => {
        const colors: { [key: string]: string } = {
            Beginner: '#00B894', Intermediate: '#FDCB6E', Advanced: '#FD79A8', Expert: '#6C5CE7',
        };
        return colors[level] || '#A29BFE';
    };

    const totalResources = learningPath?.steps?.reduce((acc, s) => acc + (s.resources?.length || 0), 0) || 0;
    const totalMentors = learningPath?.steps?.reduce((acc, s) => acc + (s.mentors?.length || 0), 0) || 0;

    // ── Render ──────────────────────────────────────────────────

    return (
        <Box sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                <SchoolIcon sx={{ fontSize: 36, color: 'primary.main' }} />
                <Typography variant="h4" fontWeight={700} color="primary">
                    Learning Center
                </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                YouTube tutorials, W3Schools guides, AI-recommended learning paths, and personalized skill development
            </Typography>

            {/* Tabs */}
            <Tabs value={tab} onChange={(_, v) => setTab(v)}
                variant="scrollable" scrollButtons="auto"
                sx={{
                    mb: 0,
                    '& .MuiTab-root': {
                        textTransform: 'none', fontWeight: 600, fontSize: '0.9rem',
                        minHeight: 48, borderRadius: '8px 8px 0 0',
                    },
                    '& .Mui-selected': { color: 'primary.main' },
                }}>
                <Tab icon={<PlayCircleOutlineIcon />} iconPosition="start" label="Video & Tutorials" />
                <Tab icon={<AutoAwesomeIcon />} iconPosition="start" label="AI Recommendations" />
                <Tab icon={<RocketLaunchIcon />} iconPosition="start" label="Learning Path Builder" />
            </Tabs>
            <Divider sx={{ mb: 0 }} />

            {/* ═══════════════════════════════════════════════════════
                TAB 0: Video & Tutorials
            ═══════════════════════════════════════════════════════ */}
            <TabPanel value={tab} index={0}>
                {/* Search Bar */}
                <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
                    <TextField
                        size="small"
                        placeholder="Search videos & tutorials..."
                        value={searchQuery}
                        onChange={(e: any) => setSearchQuery(e.target.value)}
                        onKeyDown={(e: any) => e.key === 'Enter' && handleSearch()}
                        InputProps={{
                            startAdornment: (
                                <InputAdornment position="start"><SearchIcon sx={{ color: 'text.secondary' }} /></InputAdornment>
                            ),
                        }}
                        sx={{ minWidth: 300 }}
                    />
                    <Button variant="contained" onClick={handleSearch} disabled={searchLoading}
                        sx={{ textTransform: 'none', borderRadius: 2.5 }}>
                        {searchLoading ? <CircularProgress size={20} /> : 'Search'}
                    </Button>
                    <ToggleButtonGroup
                        value={levelFilter}
                        exclusive
                        onChange={(_, v) => handleLevelFilter(v || '')}
                        size="small"
                    >
                        <ToggleButton value="">All</ToggleButton>
                        <ToggleButton value="Beginner">Beginner</ToggleButton>
                        <ToggleButton value="Intermediate">Intermediate</ToggleButton>
                        <ToggleButton value="Advanced">Advanced</ToggleButton>
                    </ToggleButtonGroup>
                </Box>

                {/* Search Results */}
                {searchResults.length > 0 && (
                    <Box sx={{ mb: 4 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Search Results ({searchResults.length})
                        </Typography>
                        <Grid container spacing={2}>
                            {searchResults.map((r: any) => (
                                <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={r.id}>
                                    {r.source === 'youtube' ? (
                                        <Card sx={{
                                            height: '100%', cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                        }}
                                            onClick={() => { setActiveVideo(r); setVideoDialog(true); }}>
                                            <CardMedia component="img" height="140" image={r.thumbnail} alt={r.title}
                                                sx={{ objectFit: 'cover' }} />
                                            <CardContent sx={{ p: 1.5 }}>
                                                <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5, lineClamp: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                    {r.title}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">{r.channel}</Typography>
                                                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, flexWrap: 'wrap' }}>
                                                    <Chip label={r.skill} size="small" sx={{ fontSize: '0.65rem', height: 20 }} />
                                                    <Chip label={r.level} size="small" sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(r.level)}22`, color: getLevelColor(r.level) }} />
                                                </Box>
                                            </CardContent>
                                        </Card>
                                    ) : (
                                        <Card sx={{
                                            height: '100%', cursor: 'pointer',
                                            '&:hover': { bgcolor: 'action.hover' },
                                        }}
                                            onClick={() => window.open(r.url, '_blank')}>
                                            <CardContent sx={{ p: 2 }}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                                    <LanguageIcon sx={{ color: '#04AA6D' }} />
                                                    <Typography variant="caption" color="#04AA6D" fontWeight={600}>W3Schools</Typography>
                                                </Box>
                                                <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{r.title}</Typography>
                                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                    <Chip label={r.skill} size="small" sx={{ fontSize: '0.65rem', height: 20 }} />
                                                    <Chip label={r.level} size="small" sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(r.level)}22`, color: getLevelColor(r.level) }} />
                                                </Box>
                                            </CardContent>
                                        </Card>
                                    )}
                                </Grid>
                            ))}
                        </Grid>
                        <Divider sx={{ my: 3 }} />
                    </Box>
                )}

                {/* Skill Chips */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>Browse by Skill</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {resourceSkills.map((skill) => (
                            <Chip key={skill} label={skill} clickable
                                onClick={() => handleSkillSelect(skill)}
                                sx={{
                                    borderRadius: 2, fontWeight: 600,
                                    bgcolor: selectedSkill === skill ? '#6C5CE7' : 'rgba(255,255,255,0.06)',
                                    color: selectedSkill === skill ? '#fff' : 'inherit',
                                    '&:hover': { bgcolor: selectedSkill === skill ? '#5A4BD1' : 'rgba(255,255,255,0.12)' },
                                }} />
                        ))}
                    </Box>
                </Box>

                {resourcesLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                        <CircularProgress sx={{ color: '#6C5CE7' }} />
                    </Box>
                ) : (
                    <>
                        {/* YouTube Videos Section */}
                        {videos.length > 0 && (
                            <Box sx={{ mb: 4 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                    <YouTubeIcon sx={{ color: '#FF0000', fontSize: 28 }} />
                                    <Typography variant="h6" fontWeight={700}>YouTube Videos</Typography>
                                    <Chip label={`${videos.length} videos`} size="small"
                                        sx={{ bgcolor: 'rgba(255,0,0,0.1)', color: '#FF4444' }} />
                                </Box>
                                <Grid container spacing={2}>
                                    {videos.map((video) => (
                                        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={video.id}>
                                            <Card sx={{
                                                height: '100%', cursor: 'pointer',
                                                '&:hover': { bgcolor: 'action.hover' },
                                            }}
                                                onClick={() => {
                                                    if (video.source === 'youtube_search' || !video.embed_url) {
                                                        window.open(video.url, '_blank');
                                                    } else {
                                                        setActiveVideo(video); setVideoDialog(true);
                                                    }
                                                }}>
                                                <Box sx={{ position: 'relative' }}>
                                                    {video.thumbnail ? (
                                                        <CardMedia component="img" height="160" image={video.thumbnail} alt={video.title}
                                                            sx={{ objectFit: 'cover' }} />
                                                    ) : (
                                                        <Box sx={{
                                                            height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                            bgcolor: 'error.main',
                                                        }}>
                                                            <YouTubeIcon sx={{ fontSize: 60, color: '#fff', opacity: 0.8 }} />
                                                        </Box>
                                                    )}
                                                    {video.duration && (
                                                        <Box sx={{
                                                            position: 'absolute', bottom: 8, right: 8,
                                                            bgcolor: 'rgba(0,0,0,0.8)', px: 1, py: 0.25, borderRadius: 1,
                                                        }}>
                                                            <Typography variant="caption" fontWeight={600}>{video.duration}</Typography>
                                                        </Box>
                                                    )}
                                                    <Box sx={{
                                                        position: 'absolute', inset: 0,
                                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                        bgcolor: 'rgba(0,0,0,0.15)', opacity: 0, transition: 'opacity 0.2s',
                                                        '&:hover': { opacity: 1 },
                                                    }}>
                                                        <PlayCircleOutlineIcon sx={{ fontSize: 60, color: '#fff' }} />
                                                    </Box>
                                                </Box>
                                                <CardContent sx={{ p: 1.5 }}>
                                                    <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5, lineClamp: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                        {video.title}
                                                    </Typography>
                                                    <Typography variant="caption" color="text.secondary" display="block">
                                                        {video.channel}
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, alignItems: 'center' }}>
                                                        <Chip label={video.level} size="small"
                                                            sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(video.level)}22`, color: getLevelColor(video.level) }} />
                                                        {video.views && (
                                                            <Typography variant="caption" color="text.secondary">{video.views} views</Typography>
                                                        )}
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2, gap: 2 }}>
                                    <Button variant="outlined" size="small"
                                        startIcon={<YouTubeIcon />}
                                        onClick={() => window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(selectedSkill)}+tutorial`, '_blank')}
                                        sx={{ borderColor: '#FF0000', color: '#FF4444', '&:hover': { borderColor: '#FF4444', bgcolor: 'rgba(255,0,0,0.08)' } }}>
                                        Browse More on YouTube
                                    </Button>
                                </Box>
                            </Box>
                        )}

                        {/* Online Courses & Certifications Section */}
                        {courses.length > 0 && (
                            <Box sx={{ mb: 4 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                    <SchoolIcon sx={{ color: '#f59e0b', fontSize: 28 }} />
                                    <Typography variant="h6" fontWeight={700}>Online Courses &amp; Certifications</Typography>
                                    <Chip label={`${courses.length} courses`} size="small"
                                        sx={{ bgcolor: 'rgba(245,158,11,0.1)', color: '#f59e0b' }} />
                                </Box>
                                <Grid container spacing={2}>
                                    {courses.map((course) => (
                                        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={course.id}>
                                            <Card sx={{
                                                height: '100%', cursor: 'pointer',
                                                '&:hover': { bgcolor: 'action.hover' },
                                            }}
                                                onClick={() => window.open(course.url, '_blank')}>
                                                <CardContent sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                                                        <Chip label={course.platform} size="small"
                                                            sx={{ fontWeight: 700, fontSize: '0.7rem', bgcolor: 'rgba(245,158,11,0.15)', color: '#fbbf24' }} />
                                                        <Chip label={course.price === 'Free' ? '🆓 Free' : `💰 ${course.price}`} size="small"
                                                            sx={{
                                                                fontWeight: 700, fontSize: '0.65rem', height: 22,
                                                                bgcolor: course.price === 'Free' ? 'rgba(34,197,94,0.15)' : 'rgba(245,158,11,0.15)',
                                                                color: course.price === 'Free' ? '#22c55e' : '#f59e0b',
                                                            }} />
                                                    </Box>
                                                    <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{course.title}</Typography>
                                                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                                                        {course.instructor}
                                                    </Typography>
                                                    <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', mb: 0.5 }}>
                                                        <StarIcon sx={{ fontSize: 14, color: '#f59e0b' }} />
                                                        <Typography variant="caption" fontWeight={600} color="#f59e0b">{course.rating}</Typography>
                                                        <Typography variant="caption" color="text.secondary">· {course.duration}</Typography>
                                                    </Box>
                                                    <Box sx={{ mt: 'auto' }}>
                                                        <Chip label={course.level} size="small"
                                                            sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(course.level)}22`, color: getLevelColor(course.level) }} />
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                            </Box>
                        )}

                        {/* Tutorials & Resources Section */}
                        {tutorials.length > 0 && (
                            <Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                    <LanguageIcon sx={{ color: '#04AA6D', fontSize: 28 }} />
                                    <Typography variant="h6" fontWeight={700}>Tutorials &amp; Resources</Typography>
                                    <Chip label={`${tutorials.length} resources`} size="small"
                                        sx={{ bgcolor: 'rgba(4,170,109,0.1)', color: '#04AA6D' }} />
                                </Box>
                                <Grid container spacing={2}>
                                    {tutorials.map((tut) => (
                                        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 3 }} key={tut.id}>
                                            <Card sx={{
                                                height: '100%', cursor: 'pointer',
                                                '&:hover': { bgcolor: 'action.hover' },
                                            }}
                                                onClick={() => window.open(tut.url, '_blank')}>
                                                <CardContent sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1.5 }}>
                                                        <Box sx={{
                                                            width: 44, height: 44, borderRadius: 2,
                                                            background: tut.source === 'web_search' ? '#4285F4' : '#04AA6D',
                                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                        }}>
                                                            <Typography variant="body2" fontWeight={900} color="#fff">
                                                                {tut.source === 'web_search' ? '🔍' : 'W3'}
                                                            </Typography>
                                                        </Box>
                                                        <OpenInNewIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                                                    </Box>
                                                    <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{tut.title}</Typography>
                                                    <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>{tut.topic}</Typography>
                                                    <Box sx={{ mt: 'auto' }}>
                                                        <Chip label={tut.level} size="small"
                                                            sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(tut.level)}22`, color: getLevelColor(tut.level) }} />
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        </Grid>
                                    ))}
                                </Grid>
                                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                                    <Button variant="outlined" size="small"
                                        startIcon={<LanguageIcon />}
                                        onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(selectedSkill)}+learning+resources+tutorial`, '_blank')}
                                        sx={{ borderColor: '#04AA6D', color: '#04AA6D', '&:hover': { borderColor: '#038654', bgcolor: 'rgba(4,170,109,0.08)' } }}>
                                        Browse More Resources
                                    </Button>
                                </Box>
                            </Box>
                        )}
                    </>
                )}
            </TabPanel>

            {/* ═══════════════════════════════════════════════════════
                TAB 1: AI Recommendations
            ═══════════════════════════════════════════════════════ */}
            <TabPanel value={tab} index={1}>
                <Alert severity="info" sx={{ mb: 3, borderRadius: 2 }}>
                    Select your <strong>current skills</strong> in the Learning Path Builder tab to get personalized AI recommendations.
                </Alert>

                {currentSkills.length === 0 ? (
                    <Card sx={{ p: 6, textAlign: 'center', border: '1px solid rgba(255,255,255,0.06)' }}>
                        <AutoAwesomeIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                            Go to "Learning Path Builder" tab and select your skills to get AI-powered recommendations
                        </Typography>
                    </Card>
                ) : recLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                        <CircularProgress sx={{ color: '#6C5CE7' }} />
                    </Box>
                ) : (
                    <Grid container spacing={3}>
                        {recommendations.map((rec) => (
                            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={rec.skill}>
                                <Card sx={{
                                    height: '100%',
                                    '&:hover': { bgcolor: 'action.hover' },
                                }}>
                                    <CardContent sx={{ p: 2.5 }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                                            <Box>
                                                <Typography variant="h6" fontWeight={700}>{rec.skill}</Typography>
                                                <Chip icon={<TrendingUpIcon />} label={rec.reason} size="small"
                                                    sx={{ mt: 0.5, bgcolor: 'rgba(108,92,231,0.12)', color: '#6C5CE7', fontSize: '0.7rem' }} />
                                            </Box>
                                            <AutoAwesomeIcon sx={{ color: '#00CEC9' }} />
                                        </Box>

                                        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                            <Chip icon={<YouTubeIcon />} label={`${rec.total_videos} videos`} size="small"
                                                sx={{ bgcolor: 'rgba(255,0,0,0.08)', color: '#FF4444', fontSize: '0.7rem' }} />
                                            <Chip icon={<LanguageIcon />} label={`${rec.total_tutorials} tutorials`} size="small"
                                                sx={{ bgcolor: 'rgba(4,170,109,0.08)', color: '#04AA6D', fontSize: '0.7rem' }} />
                                        </Box>

                                        {rec.top_video && (
                                            <Paper sx={{
                                                p: 1.5, mb: 1.5, cursor: 'pointer', borderRadius: 2,
                                                bgcolor: 'rgba(255,0,0,0.04)', border: '1px solid rgba(255,0,0,0.08)',
                                                '&:hover': { bgcolor: 'rgba(255,0,0,0.08)' },
                                            }}
                                                onClick={() => { setActiveVideo(rec.top_video as VideoResource); setVideoDialog(true); }}>
                                                <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                                                    <Box sx={{
                                                        width: 80, height: 45, borderRadius: 1, overflow: 'hidden', flexShrink: 0,
                                                        position: 'relative',
                                                    }}>
                                                        <img src={rec.top_video.thumbnail} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                        <PlayCircleOutlineIcon sx={{
                                                            position: 'absolute', top: '50%', left: '50%',
                                                            transform: 'translate(-50%,-50%)', fontSize: 24, color: '#fff',
                                                        }} />
                                                    </Box>
                                                    <Box sx={{ minWidth: 0 }}>
                                                        <Typography variant="caption" fontWeight={600} sx={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                                            {rec.top_video.title}
                                                        </Typography>
                                                        <Typography variant="caption" color="text.secondary" display="block">
                                                            {rec.top_video.channel}
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            </Paper>
                                        )}

                                        {rec.top_tutorial && (
                                            <Paper sx={{
                                                p: 1.5, cursor: 'pointer', borderRadius: 2,
                                                bgcolor: 'rgba(4,170,109,0.04)', border: '1px solid rgba(4,170,109,0.08)',
                                                '&:hover': { bgcolor: 'rgba(4,170,109,0.08)' },
                                            }}
                                                onClick={() => window.open(rec.top_tutorial!.url, '_blank')}>
                                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                                    <Box sx={{ width: 28, height: 28, borderRadius: 1, bgcolor: '#04AA6D', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                                        <Typography variant="caption" fontWeight={900} color="#fff" fontSize={10}>W3</Typography>
                                                    </Box>
                                                    <Box sx={{ minWidth: 0 }}>
                                                        <Typography variant="caption" fontWeight={600}>{rec.top_tutorial.title}</Typography>
                                                        <Typography variant="caption" color="text.secondary" display="block">Interactive tutorial</Typography>
                                                    </Box>
                                                    <OpenInNewIcon sx={{ fontSize: 14, color: 'text.secondary', ml: 'auto' }} />
                                                </Box>
                                            </Paper>
                                        )}

                                        <Button fullWidth variant="outlined" size="small"
                                            onClick={() => { setSelectedSkill(rec.skill); setTab(0); loadResourcesForSkill(rec.skill); }}
                                            sx={{ mt: 2, textTransform: 'none', borderRadius: 2 }}>
                                            View all {rec.skill} resources
                                        </Button>
                                    </CardContent>
                                </Card>
                            </Grid>
                        ))}
                    </Grid>
                )}
            </TabPanel>

            {/* ═══════════════════════════════════════════════════════
                TAB 2: Learning Path Builder (original)
            ═══════════════════════════════════════════════════════ */}
            <TabPanel value={tab} index={2}>
                <Grid container spacing={4}>
                    <Grid size={{ xs: 12, md: 4 }}>
                        <Card sx={{ height: '100%', border: '1px solid rgba(255,255,255,0.06)' }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
                                    <SchoolIcon color="primary" />
                                    <Typography variant="h6">Configure Your Path</Typography>
                                </Box>
                                <Typography variant="subtitle2" sx={{ mb: 1 }}>Your Current Skills</Typography>
                                <Autocomplete multiple options={skillOptions} value={currentSkills}
                                    onChange={(_, value) => setCurrentSkills(value)}
                                    renderTags={(value, getTagProps) =>
                                        value.map((option, index) => (
                                            <Chip label={option} {...getTagProps({ index })} sx={{ backgroundColor: 'rgba(99, 102, 241, 0.2)' }} />
                                        ))
                                    }
                                    renderInput={(params) => <TextField {...params} placeholder="Select your skills" />}
                                    sx={{ mb: 3 }}
                                />
                                <Typography variant="subtitle2" sx={{ mb: 1 }}>Target Skill</Typography>
                                <Autocomplete options={skillOptions} value={targetSkill}
                                    onChange={(_, value) => setTargetSkill(value || '')}
                                    renderInput={(params) => <TextField {...params} placeholder="What do you want to learn?" />}
                                    sx={{ mb: 3 }}
                                />
                                <Button fullWidth variant="contained" size="large" startIcon={<RocketLaunchIcon />}
                                    onClick={generatePath} disabled={!targetSkill || pathLoading} sx={{ mb: 3 }}>
                                    {pathLoading ? 'Generating...' : 'Generate Learning Path'}
                                </Button>
                                {recommendedSkills.length > 0 && (
                                    <Box>
                                        <Typography variant="subtitle2" sx={{ mb: 1 }}>Recommended Next Skills</Typography>
                                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                            {recommendedSkills.map((skill: any) => (
                                                <Chip key={skill.skill} label={skill.skill} onClick={() => setTargetSkill(skill.skill)}
                                                    sx={{ backgroundColor: 'rgba(0,206,201,0.2)', cursor: 'pointer', '&:hover': { backgroundColor: 'rgba(0,206,201,0.3)' } }} />
                                            ))}
                                        </Box>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid size={{ xs: 12, md: 8 }}>
                        {pathLoading ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress size={60} /></Box>
                        ) : learningPath ? (
                            <Card sx={{ border: '1px solid rgba(255,255,255,0.06)' }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 1 }}>
                                        <Typography variant="h5">
                                            Path to <span style={{ color: '#6C5CE7' }}>{learningPath.target_skill}</span>
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                            {learningPath.difficulty && (
                                                <Chip label={learningPath.difficulty} sx={{ backgroundColor: `${getLevelColor(learningPath.difficulty)}33`, color: getLevelColor(learningPath.difficulty) }} />
                                            )}
                                            <Chip icon={<AccessTimeIcon />} label={`${learningPath.estimated_total_hours}h total`} color="primary" />
                                            <Chip label={`${learningPath.total_steps} steps`} color="secondary" />
                                            {totalResources > 0 && <Chip icon={<MenuBookIcon />} label={`${totalResources} resources`} sx={{ backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#166534' }} />}
                                            {totalMentors > 0 && <Chip icon={<PersonIcon />} label={`${totalMentors} mentors`} sx={{ backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#3730a3' }} />}
                                        </Box>
                                    </Box>
                                    {learningPath.suggested_prerequisites && learningPath.suggested_prerequisites.length > 0 && (
                                        <Paper sx={{ p: 2, mb: 2, backgroundColor: 'rgba(34, 197, 94, 0.06)' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                                <SchoolIcon sx={{ fontSize: 18 }} />
                                                <Typography variant="subtitle2">Suggested Prerequisites</Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                                {learningPath.suggested_prerequisites.map((p) => (
                                                    <Chip key={p} label={p} sx={{ backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#166534' }} />
                                                ))}
                                            </Box>
                                        </Paper>
                                    )}
                                    <Stepper activeStep={activeStep} orientation="vertical">
                                        {learningPath.steps.map((step, index) => (
                                            <Step key={step.skill}>
                                                <StepLabel onClick={() => setActiveStep(index)} sx={{ cursor: 'pointer' }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                                        <Typography variant="subtitle1">{step.skill}</Typography>
                                                        <Chip label={step.level} size="small" sx={{ backgroundColor: `${getLevelColor(step.level)}33`, color: getLevelColor(step.level) }} />
                                                        {step.type && <Chip label={step.type === 'prerequisite' ? 'Prerequisite' : 'Target'} size="small" sx={{ backgroundColor: step.type === 'prerequisite' ? 'rgba(0,206,201,0.15)' : 'rgba(108,92,231,0.15)', color: step.type === 'prerequisite' ? '#00CEC9' : '#6C5CE7' }} />}
                                                        <Typography variant="caption" color="text.secondary">~{step.estimated_hours}h</Typography>
                                                    </Box>
                                                </StepLabel>
                                                <StepContent>
                                                    {/* Description */}
                                                    {step.description && (
                                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.7, pl: 0.5, borderLeft: '3px solid rgba(249,115,22,0.3)', ml: 0.5 }}>
                                                            {step.description}
                                                        </Typography>
                                                    )}

                                                    {/* Learning Objectives */}
                                                    {step.objectives && step.objectives.length > 0 && (
                                                        <Paper sx={{ p: 2, mb: 2, bgcolor: 'rgba(249,115,22,0.06)', border: '1px solid rgba(249,115,22,0.12)', borderRadius: 2 }}>
                                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                                <SchoolIcon sx={{ fontSize: 18, color: '#6C5CE7' }} />
                                                                <Typography variant="subtitle2" fontWeight={700}>Learning Objectives</Typography>
                                                            </Box>
                                                            {step.objectives.map((obj, oi) => (
                                                                <Box key={oi} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                                                                    <Box sx={{ width: 20, height: 20, borderRadius: '50%', bgcolor: 'rgba(249,115,22,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, mt: 0.2 }}>
                                                                        <Typography variant="caption" fontWeight={700} color="#6C5CE7" fontSize={10}>{oi + 1}</Typography>
                                                                    </Box>
                                                                    <Typography variant="body2" color="text.secondary">{obj}</Typography>
                                                                </Box>
                                                            ))}
                                                        </Paper>
                                                    )}

                                                    {/* Key Topics */}
                                                    {step.key_topics && step.key_topics.length > 0 && (
                                                        <Box sx={{ mb: 2 }}>
                                                            <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>Key Topics</Typography>
                                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
                                                                {step.key_topics.map((topic, ti) => (
                                                                    <Chip key={ti} label={topic} size="small" sx={{ bgcolor: 'rgba(253,203,110,0.15)', color: '#FDCB6E', fontWeight: 600, fontSize: '0.72rem' }} />
                                                                ))}
                                                            </Box>
                                                        </Box>
                                                    )}

                                                    {/* Resources & Mentors Grid */}
                                                    <Grid container spacing={2}>
                                                        {step.resources.length > 0 && (
                                                            <Grid size={{ xs: 12, md: 6 }}>
                                                                <Paper sx={{ p: 2, bgcolor: 'rgba(34,197,94,0.06)', border: '1px solid rgba(34,197,94,0.12)', borderRadius: 2 }}>
                                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                                        <MenuBookIcon sx={{ fontSize: 18, color: '#22c55e' }} />
                                                                        <Typography variant="subtitle2" fontWeight={700}>Resources</Typography>
                                                                        <Chip label={step.resources.length} size="small" sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(34,197,94,0.15)', color: '#22c55e' }} />
                                                                    </Box>
                                                                    {step.resources.map((resource) => (
                                                                        <Box key={resource.id} onClick={() => openResource(resource)}
                                                                            sx={{
                                                                                mb: 1, p: 1.5, borderRadius: 1.5, cursor: 'pointer',
                                                                                bgcolor: 'rgba(34,197,94,0.04)', border: '1px solid rgba(34,197,94,0.08)',
                                                                                transition: 'all 0.15s',
                                                                                '&:hover': { bgcolor: 'rgba(34,197,94,0.1)', transform: 'translateX(4px)' },
                                                                            }}>
                                                                            <Typography variant="body2" fontWeight={600}>{resource.title}</Typography>
                                                                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5, alignItems: 'center' }}>
                                                                                <Chip label={resource.type} size="small" sx={{ height: 18, fontSize: '0.6rem' }} />
                                                                                <Typography variant="caption" color="#f59e0b" fontWeight={600}>★ {resource.rating?.toFixed(1) || 'N/A'}</Typography>
                                                                            </Box>
                                                                        </Box>
                                                                    ))}
                                                                </Paper>
                                                            </Grid>
                                                        )}
                                                        {step.mentors.length > 0 && (
                                                            <Grid size={{ xs: 12, md: 6 }}>
                                                                <Paper sx={{ p: 2, bgcolor: 'rgba(249,115,22,0.06)', border: '1px solid rgba(249,115,22,0.12)', borderRadius: 2 }}>
                                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                                        <PersonIcon sx={{ fontSize: 18, color: '#6C5CE7' }} />
                                                                        <Typography variant="subtitle2" fontWeight={700}>Expert Mentors</Typography>
                                                                    </Box>
                                                                    {step.mentors.map((mentor) => (
                                                                        <Box key={mentor.id} sx={{
                                                                            display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5, p: 1.5,
                                                                            borderRadius: 1.5, bgcolor: 'rgba(249,115,22,0.04)', border: '1px solid rgba(249,115,22,0.08)',
                                                                            transition: 'all 0.15s',
                                                                            '&:hover': { bgcolor: 'rgba(249,115,22,0.1)' },
                                                                        }}>
                                                                            <Avatar sx={{ width: 36, height: 36, bgcolor: '#6C5CE7', fontSize: 14, fontWeight: 700 }}>{mentor.name?.charAt(0) || '?'}</Avatar>
                                                                            <Box>
                                                                                <Typography variant="body2" fontWeight={600}>{mentor.name}</Typography>
                                                                                <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
                                                                                    <Typography variant="caption" color="text.secondary">{mentor.department}</Typography>
                                                                                    <Typography variant="caption" color="#f59e0b">{'★'.repeat(mentor.level)}</Typography>
                                                                                </Box>
                                                                            </Box>
                                                                        </Box>
                                                                    ))}
                                                                </Paper>
                                                            </Grid>
                                                        )}
                                                    </Grid>

                                                    {/* Navigation Buttons */}
                                                    <Box sx={{ mt: 2.5, display: 'flex', gap: 1 }}>
                                                        {index < learningPath.steps.length - 1 && (
                                                            <Button variant="contained" size="small" onClick={() => setActiveStep(index + 1)}
                                                                sx={{ borderRadius: 2, textTransform: 'none', px: 3 }}>Next Step →</Button>
                                                        )}
                                                        {index > 0 && (
                                                            <Button variant="outlined" size="small" onClick={() => setActiveStep(index - 1)}
                                                                sx={{ borderRadius: 2, textTransform: 'none', px: 3 }}>← Previous</Button>
                                                        )}
                                                        <Button variant="outlined" size="small"
                                                            onClick={() => { setSelectedSkill(step.skill); setTab(0); loadResourcesForSkill(step.skill); }}
                                                            sx={{ borderRadius: 2, textTransform: 'none', px: 3, ml: 'auto' }}>Browse {step.skill} Videos</Button>
                                                    </Box>
                                                </StepContent>
                                            </Step>
                                        ))}
                                    </Stepper>

                                    {/* ── Skill-Specific Videos & Tutorials ──────────── */}
                                    {(pathVideos.length > 0 || pathTutorials.length > 0 || pathCourses.length > 0) && (
                                        <Box sx={{ mt: 4 }}>
                                            <Divider sx={{ mb: 3 }} />
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                                <PlayCircleOutlineIcon sx={{ color: '#6C5CE7', fontSize: 26 }} />
                                                <Typography variant="h6" fontWeight={700}>
                                                    All {learningPath.target_skill} Resources
                                                </Typography>
                                                <Chip label={`${pathVideos.length + pathTutorials.length + pathCourses.length} total`} size="small"
                                                    sx={{ bgcolor: 'rgba(108,92,231,0.12)', color: '#6C5CE7' }} />
                                            </Box>

                                            {/* Online Courses & Certifications */}
                                            {pathCourses.length > 0 && (
                                                <Box sx={{ mb: 3 }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                        <SchoolIcon sx={{ color: '#f59e0b', fontSize: 22 }} />
                                                        <Typography variant="subtitle1" fontWeight={600}>Online Courses & Certifications</Typography>
                                                        <Chip label={`${pathCourses.length}`} size="small"
                                                            sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(245,158,11,0.1)', color: '#f59e0b' }} />
                                                    </Box>
                                                    <Grid container spacing={2}>
                                                        {pathCourses.map((course) => (
                                                            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={course.id}>
                                                                <Card sx={{
                                                                    height: '100%', cursor: 'pointer',
                                                                    '&:hover': { bgcolor: 'action.hover' },
                                                                }}
                                                                    onClick={() => window.open(course.url, '_blank')}>
                                                                    <CardContent sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                                                                            <Chip label={course.platform} size="small"
                                                                                sx={{ fontWeight: 700, fontSize: '0.7rem', bgcolor: 'rgba(245,158,11,0.15)', color: '#fbbf24' }} />
                                                                            <Chip label={course.price === 'Free' ? '🆓 Free' : `💰 ${course.price}`} size="small"
                                                                                sx={{
                                                                                    fontWeight: 700, fontSize: '0.65rem', height: 22,
                                                                                    bgcolor: course.price === 'Free' ? 'rgba(34,197,94,0.15)' : 'rgba(245,158,11,0.15)',
                                                                                    color: course.price === 'Free' ? '#22c55e' : '#f59e0b',
                                                                                }} />
                                                                        </Box>
                                                                        <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{course.title}</Typography>
                                                                        <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                                                                            {course.instructor}
                                                                        </Typography>
                                                                        <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center', mb: 0.5 }}>
                                                                            <StarIcon sx={{ fontSize: 14, color: '#f59e0b' }} />
                                                                            <Typography variant="caption" fontWeight={600} color="#f59e0b">{course.rating}</Typography>
                                                                            <Typography variant="caption" color="text.secondary">· {course.duration}</Typography>
                                                                        </Box>
                                                                        <Box sx={{ mt: 'auto', display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                                                            <Chip label={course.level} size="small"
                                                                                sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(course.level)}22`, color: getLevelColor(course.level) }} />
                                                                        </Box>
                                                                    </CardContent>
                                                                </Card>
                                                            </Grid>
                                                        ))}
                                                    </Grid>
                                                </Box>
                                            )}

                                            {/* YouTube Videos */}
                                            {pathVideos.length > 0 && (
                                                <Box sx={{ mb: 3 }}>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                        <YouTubeIcon sx={{ color: '#FF0000', fontSize: 22 }} />
                                                        <Typography variant="subtitle1" fontWeight={600}>YouTube Videos</Typography>
                                                        <Chip label={`${pathVideos.length}`} size="small"
                                                            sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(255,0,0,0.1)', color: '#FF4444' }} />
                                                    </Box>
                                                    <Grid container spacing={2}>
                                                        {pathVideos.map((video) => (
                                                            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={video.id}>
                                                                <Card sx={{
                                                                    height: '100%', cursor: 'pointer',
                                                                    '&:hover': { bgcolor: 'action.hover' },
                                                                }}
                                                                    onClick={() => {
                                                                        if (video.embed_url) { setActiveVideo(video); setVideoDialog(true); }
                                                                        else { window.open(video.url, '_blank'); }
                                                                    }}>
                                                                    <Box sx={{ position: 'relative' }}>
                                                                        {video.thumbnail ? (
                                                                            <CardMedia component="img" height="140" image={video.thumbnail} alt={video.title}
                                                                                sx={{ objectFit: 'cover' }} />
                                                                        ) : (
                                                                            <Box sx={{
                                                                                height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                                bgcolor: 'error.main',
                                                                            }}>
                                                                                <YouTubeIcon sx={{ fontSize: 50, color: '#fff', opacity: 0.8 }} />
                                                                            </Box>
                                                                        )}
                                                                        {video.duration && (
                                                                            <Box sx={{
                                                                                position: 'absolute', bottom: 6, right: 6,
                                                                                bgcolor: 'rgba(0,0,0,0.85)', px: 0.8, py: 0.2, borderRadius: 1,
                                                                            }}>
                                                                                <Typography variant="caption" fontWeight={600} fontSize="0.7rem">{video.duration}</Typography>
                                                                            </Box>
                                                                        )}
                                                                    </Box>
                                                                    <CardContent sx={{ p: 1.5 }}>
                                                                        <Typography variant="body2" fontWeight={600} sx={{
                                                                            mb: 0.5, display: '-webkit-box', WebkitLineClamp: 2,
                                                                            WebkitBoxOrient: 'vertical', overflow: 'hidden',
                                                                        }}>
                                                                            {video.title}
                                                                        </Typography>
                                                                        <Typography variant="caption" color="text.secondary" display="block">{video.channel}</Typography>
                                                                        <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5, alignItems: 'center' }}>
                                                                            <Chip label={video.level} size="small"
                                                                                sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(video.level)}22`, color: getLevelColor(video.level) }} />
                                                                            {video.views && (
                                                                                <Typography variant="caption" color="text.secondary">{video.views} views</Typography>
                                                                            )}
                                                                        </Box>
                                                                    </CardContent>
                                                                </Card>
                                                            </Grid>
                                                        ))}
                                                    </Grid>
                                                </Box>
                                            )}

                                            {/* W3Schools Tutorials */}
                                            {pathTutorials.length > 0 && (
                                                <Box>
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                                                        <LanguageIcon sx={{ color: '#04AA6D', fontSize: 22 }} />
                                                        <Typography variant="subtitle1" fontWeight={600}>Tutorials & Guides</Typography>
                                                        <Chip label={`${pathTutorials.length}`} size="small"
                                                            sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(4,170,109,0.1)', color: '#04AA6D' }} />
                                                    </Box>
                                                    <Grid container spacing={2}>
                                                        {pathTutorials.map((tut) => (
                                                            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={tut.id}>
                                                                <Card sx={{
                                                                    height: '100%', cursor: 'pointer',
                                                                    '&:hover': { bgcolor: 'action.hover' },
                                                                }}
                                                                    onClick={() => window.open(tut.url, '_blank')}>
                                                                    <CardContent sx={{ p: 2, display: 'flex', flexDirection: 'column', height: '100%' }}>
                                                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1.5 }}>
                                                                            <Box sx={{
                                                                                width: 40, height: 40, borderRadius: 2,
                                                                                bgcolor: 'success.main',
                                                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                                            }}>
                                                                                <Typography variant="body2" fontWeight={900} color="#fff">W3</Typography>
                                                                            </Box>
                                                                            <OpenInNewIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                                                                        </Box>
                                                                        <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>{tut.title}</Typography>
                                                                        <Typography variant="caption" color="text.secondary" sx={{ mb: 1 }}>{tut.topic}</Typography>
                                                                        <Box sx={{ mt: 'auto' }}>
                                                                            <Chip label={tut.level} size="small"
                                                                                sx={{ fontSize: '0.65rem', height: 20, bgcolor: `${getLevelColor(tut.level)}22`, color: getLevelColor(tut.level) }} />
                                                                        </Box>
                                                                    </CardContent>
                                                                </Card>
                                                            </Grid>
                                                        ))}
                                                    </Grid>
                                                </Box>
                                            )}
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        ) : (
                            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.06)' }}>
                                <CardContent sx={{ textAlign: 'center' }}>
                                    <SchoolIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                                    <Typography variant="h6" color="text.secondary">Select a target skill to generate your learning path</Typography>
                                </CardContent>
                            </Card>
                        )}
                    </Grid>
                </Grid>
            </TabPanel>

            {/* ── Video Player Dialog ── */}
            <Dialog open={videoDialog} onClose={() => setVideoDialog(false)} maxWidth="md" fullWidth>
                {activeVideo && (
                    <>
                        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <YouTubeIcon sx={{ color: '#FF0000' }} />
                            {activeVideo.title}
                        </DialogTitle>
                        <DialogContent dividers sx={{ p: 0 }}>
                            <Box sx={{ position: 'relative', paddingTop: '56.25%', width: '100%' }}>
                                <iframe
                                    src={activeVideo.embed_url}
                                    title={activeVideo.title}
                                    style={{
                                        position: 'absolute', top: 0, left: 0,
                                        width: '100%', height: '100%', border: 'none',
                                    }}
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                />
                            </Box>
                            <Box sx={{ p: 2 }}>
                                <Typography variant="body2" fontWeight={600}>{activeVideo.channel}</Typography>
                                <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                                    <Chip label={activeVideo.level} size="small" sx={{ bgcolor: `${getLevelColor(activeVideo.level)}22`, color: getLevelColor(activeVideo.level) }} />
                                    <Chip label={activeVideo.duration} size="small" />
                                    <Chip label={`${activeVideo.views} views`} size="small" />
                                    <Chip label={activeVideo.skill} size="small" sx={{ bgcolor: 'rgba(245,158,11,0.15)', color: '#f59e0b' }} />
                                </Box>
                            </Box>
                        </DialogContent>
                        <DialogActions>
                            <Button onClick={() => window.open(activeVideo.url, '_blank')} startIcon={<OpenInNewIcon />}>
                                Open on YouTube
                            </Button>
                            <Button onClick={() => setVideoDialog(false)}>Close</Button>
                        </DialogActions>
                    </>
                )}
            </Dialog>

            {/* ── Document Viewer Dialog (from original) ── */}
            <Dialog open={viewOpen} onClose={() => setViewOpen(false)} maxWidth="md" fullWidth>
                <DialogTitle>{viewTitle}</DialogTitle>
                <DialogContent dividers>
                    {viewLoading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box>
                    ) : (
                        <Typography sx={{ whiteSpace: 'pre-wrap' }}>{viewContent || '(No content)'}</Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setViewOpen(false)}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default LearningPathPage;
