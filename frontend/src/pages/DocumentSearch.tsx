import React, { useState, useEffect } from 'react';
import {
    Box, Typography, TextField, Card, CardContent, Grid, Chip,
    InputAdornment, Select, MenuItem, FormControl, InputLabel, Button,
    CircularProgress, Rating, Fade, Dialog, DialogTitle, DialogContent,
    DialogActions, Stack, IconButton,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DescriptionIcon from '@mui/icons-material/Description';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import { documentService, authService } from '../services/api';

interface Document {
    id: string; title: string; type: string; topic: string;
    author: string; date: string; views: number; rating: number; content?: string;
}

const DocumentSearch: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [docType, setDocType] = useState('');
    const [types, setTypes] = useState<string[]>([]);
    const [minRating, setMinRating] = useState<number>(0);
    const [createOpen, setCreateOpen] = useState(false);
    const [creating, setCreating] = useState(false);
    const [newDoc, setNewDoc] = useState({
        title: '', type: '', topic: '', author: '', date: '',
        rating: 3.5 as number, views: 0 as number, content: '',
    });
    const [viewOpen, setViewOpen] = useState(false);
    const [viewDocTitle, setViewDocTitle] = useState('');
    const [viewContent, setViewContent] = useState('');
    const [viewLoading, setViewLoading] = useState(false);

    useEffect(() => { loadTypes(); }, []);
    useEffect(() => {
        const timer = setTimeout(() => { searchDocuments(); }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery, docType, minRating]);

    const loadTypes = async () => {
        try { const res = await documentService.getTypes(); setTypes(res.data); }
        catch (error) { console.error('Error loading types:', error); }
    };

    const searchDocuments = async () => {
        setLoading(true);
        try {
            const params: any = { limit: 100 };
            if (searchQuery) params.q = searchQuery;
            if (docType) params.type = docType;
            if (minRating > 0) params.min_rating = minRating;
            const response = await documentService.search(params);
            setDocuments(response.data);
        } catch (error) { console.error('Error searching documents:', error); }
        finally { setLoading(false); }
    };

    const handleCreate = async () => {
        if (!newDoc.title || !newDoc.type || !newDoc.topic || !newDoc.author) return;
        setCreating(true);
        try {
            await documentService.create({ ...newDoc, date: newDoc.date || null } as any);
            setCreateOpen(false);
            setNewDoc({ title: '', type: '', topic: '', author: '', date: '', rating: 3.5, views: 0, content: '' });
            await searchDocuments(); await loadTypes();
        } catch (error: any) {
            if (error.response?.status !== 401) {
                alert('Failed to create document: ' + (error.response?.data?.detail || error.message));
            }
        } finally { setCreating(false); }
    };

    const openView = async (doc: Document) => {
        setViewDocTitle(doc.title); setViewContent(doc.content || ''); setViewOpen(true);
        if (!doc.content) {
            setViewLoading(true);
            try { const res = await documentService.getById(doc.id); setViewContent(res.data?.content || '(No content)'); }
            catch { setViewContent('(Failed to load content)'); }
            finally { setViewLoading(false); }
        }
    };

    const closeView = () => setViewOpen(false);
    const handleSearch = (e: React.FormEvent) => { e.preventDefault(); searchDocuments(); };

    const handleDeleteDocument = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this document?')) {
            try { await documentService.delete(id); setDocuments(documents.filter(d => d.id !== id)); }
            catch { alert('Failed to delete document. Are you logged in?'); }
        }
    };

    const getTypeColor = (type: string) => {
        const colors: { [key: string]: string } = {
            'Guide': '#6C5CE7', 'Report': '#00B894', 'Tutorial': '#FDCB6E',
            'Article': '#FD79A8', 'Documentation': '#74B9FF',
        };
        return colors[type] || '#A29BFE';
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
                        <FolderOpenIcon sx={{ color: 'primary.main', fontSize: 24 }} />
                    </Box>
                    <Typography variant="h4" fontWeight={800} color="primary">Document Search</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ ml: 7.5 }}>
                    Discover knowledge resources, guides, and reports
                </Typography>
            </Box>

            {/* Search Form */}
            <Card sx={{ mb: 3 }}>
                <CardContent>
                    {authService.isAuthenticated() && (
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
                            <Button variant="outlined" onClick={() => setCreateOpen(true)} sx={{ borderRadius: 2.5 }}>Add Document</Button>
                        </Box>
                    )}
                    <form onSubmit={handleSearch}>
                        <Grid container spacing={2} alignItems="center">
                            <Grid size={{ xs: 12, md: 4 }}>
                                <TextField fullWidth placeholder="Search documents..." value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment> }} />
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <FormControl fullWidth>
                                    <InputLabel>Document Type</InputLabel>
                                    <Select value={docType} label="Document Type" onChange={(e) => setDocType(e.target.value)}>
                                        <MenuItem value="">All Types</MenuItem>
                                        {types.map((type) => <MenuItem key={type} value={type}>{type}</MenuItem>)}
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid size={{ xs: 12, md: 3 }}>
                                <Box>
                                    <Typography variant="caption" color="text.secondary" gutterBottom>Min Rating</Typography>
                                    <Rating value={minRating} onChange={(_, value) => setMinRating(value || 0)} precision={0.5} size="large" />
                                </Box>
                            </Grid>
                            <Grid size={{ xs: 12, md: 2 }}>
                                <Button fullWidth variant="contained" type="submit" size="large" sx={{ height: 56, borderRadius: 2.5 }}>Search</Button>
                            </Grid>
                        </Grid>
                    </form>
                </CardContent>
            </Card>

            {/* Create Dialog */}
            <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
                <DialogTitle>Add Document</DialogTitle>
                <DialogContent>
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        <TextField label="Title" value={newDoc.title} onChange={(e) => setNewDoc({ ...newDoc, title: e.target.value })} required fullWidth />
                        <FormControl fullWidth>
                            <InputLabel>Type</InputLabel>
                            <Select label="Type" value={newDoc.type} onChange={(e) => setNewDoc({ ...newDoc, type: String(e.target.value) })}>
                                {types.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                            </Select>
                        </FormControl>
                        <TextField label="Topic" value={newDoc.topic} onChange={(e) => setNewDoc({ ...newDoc, topic: e.target.value })} required fullWidth />
                        <TextField label="Author" value={newDoc.author} onChange={(e) => setNewDoc({ ...newDoc, author: e.target.value })} required fullWidth />
                        <TextField label="Date" type="date" InputLabelProps={{ shrink: true }} value={newDoc.date}
                            onChange={(e) => setNewDoc({ ...newDoc, date: e.target.value })} fullWidth />
                        <Box>
                            <Typography gutterBottom>Rating</Typography>
                            <Rating value={newDoc.rating} precision={0.5} onChange={(_, value) => setNewDoc({ ...newDoc, rating: value || 0 })} />
                        </Box>
                        <TextField label="Views" type="number" inputProps={{ min: 0 }} value={newDoc.views}
                            onChange={(e) => setNewDoc({ ...newDoc, views: Number(e.target.value) })} fullWidth />
                        <TextField label="Content" value={newDoc.content} onChange={(e) => setNewDoc({ ...newDoc, content: e.target.value })}
                            fullWidth multiline minRows={4} />
                    </Stack>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setCreateOpen(false)} disabled={creating}>Cancel</Button>
                    <Button onClick={handleCreate} variant="contained" sx={{ borderRadius: 2.5 }}
                        disabled={creating || !newDoc.title || !newDoc.type || !newDoc.topic || !newDoc.author}>
                        {creating ? 'Saving...' : 'Save'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* View Dialog */}
            <Dialog open={viewOpen} onClose={closeView} maxWidth="md" fullWidth>
                <DialogTitle>{viewDocTitle}</DialogTitle>
                <DialogContent dividers>
                    {viewLoading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress sx={{ color: '#6C5CE7' }} /></Box>
                    ) : (
                        <Typography sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{viewContent || '(No content)'}</Typography>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={closeView} sx={{ borderRadius: 2.5 }}>Close</Button>
                </DialogActions>
            </Dialog>

            {/* Results */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress size={50} sx={{ color: '#6C5CE7' }} />
                </Box>
            ) : (
                <Grid container spacing={2.5}>
                    {documents.map((doc, index) => (
                        <Grid size={{ xs: 12, md: 6 }} key={doc.id}>
                            <Fade in timeout={300 + index * 80}>
                                <Card onClick={() => openView(doc)}
                                    sx={{
                                        height: '100%', cursor: 'pointer',
                                        '&:hover': { bgcolor: 'action.hover' },
                                    }}>
                                    <CardContent>
                                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                                            <Box sx={{
                                                width: 48, height: 48, borderRadius: 2.5, mr: 2,
                                                bgcolor: 'action.selected',
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            }}>
                                                <DescriptionIcon sx={{ color: getTypeColor(doc.type) }} />
                                            </Box>
                                            <Box sx={{ flex: 1, minWidth: 0 }}>
                                                <Typography variant="body1" fontWeight={600} sx={{ mb: 0.3 }}>{doc.title}</Typography>
                                                <Typography variant="caption" color="text.secondary" noWrap display="block">{doc.topic}</Typography>
                                            </Box>
                                            {authService.isAuthenticated() && (
                                                <IconButton color="error" size="small"
                                                    onClick={(e) => { e.stopPropagation(); handleDeleteDocument(doc.id); }}>
                                                    <DeleteIcon fontSize="small" />
                                                </IconButton>
                                            )}
                                        </Box>
                                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1.5 }}>
                                            <Chip label={doc.type} size="small"
                                                sx={{ bgcolor: `${getTypeColor(doc.type)}18`, color: getTypeColor(doc.type), fontWeight: 600, fontSize: '0.7rem' }} />
                                            <Chip icon={<PersonIcon />} label={doc.author} size="small"
                                                sx={{ bgcolor: 'rgba(108,92,231,0.1)', fontSize: '0.7rem' }} />
                                        </Box>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <Rating value={doc.rating} precision={0.1} size="small" readOnly />
                                                <Typography variant="caption" color="text.secondary">({doc.rating.toFixed(1)})</Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                <VisibilityIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                                                <Typography variant="caption" color="text.secondary">{doc.views.toLocaleString()}</Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            </Fade>
                        </Grid>
                    ))}
                </Grid>
            )}

            {!loading && documents.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                    <Box sx={{
                        width: 80, height: 80, borderRadius: '50%', mx: 'auto', mb: 2,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        bgcolor: 'primary.light',
                    }}>
                        <FolderOpenIcon sx={{ fontSize: 36, color: 'primary.main' }} />
                    </Box>
                    <Typography variant="h6" color="text.secondary">No documents found. Try adjusting your search.</Typography>
                </Box>
            )}
        </Box>
    );
};

export default DocumentSearch;
