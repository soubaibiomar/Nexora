import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    Box, Typography, Card, CardContent, Avatar, TextField, Button, IconButton,
    Chip, Divider, CircularProgress, LinearProgress,
} from '@mui/material';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbUpOutlinedIcon from '@mui/icons-material/ThumbUpOutlined';
import ChatBubbleOutlineIcon from '@mui/icons-material/ChatBubbleOutline';
import ShareIcon from '@mui/icons-material/Share';
import SendIcon from '@mui/icons-material/Send';
import ImageIcon from '@mui/icons-material/Image';
import VideocamIcon from '@mui/icons-material/Videocam';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CloseIcon from '@mui/icons-material/Close';
import ArticleIcon from '@mui/icons-material/Article';
import CelebrationIcon from '@mui/icons-material/Celebration';
import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import PublicIcon from '@mui/icons-material/Public';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import PlayCircleFilledIcon from '@mui/icons-material/PlayCircleFilled';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import GroupIcon from '@mui/icons-material/Group';
import { feedService, networkService, dashboardService } from '../services/api';

const API_BASE = 'http://localhost:8000';

interface MediaItem { id: string; filename: string; url: string; content_type: string; media_type: 'image' | 'video' | 'file'; size: number; }
interface Post { id: string; author_name: string; author_role: string; author_department: string; author_avatar?: string; content: string; post_type: string; created_at: string; likes: number; comments_count: number; shares: number; liked_by: string[]; media?: MediaItem[]; }

function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d`;
    return `${Math.floor(days / 7)}w`;
}

function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fileIcon(filename: string) {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    if (ext === 'pdf') return <PictureAsPdfIcon sx={{ color: '#FF6B6B' }} />;
    if (['doc', 'docx'].includes(ext)) return <InsertDriveFileIcon sx={{ color: '#74B9FF' }} />;
    if (['xls', 'xlsx', 'csv'].includes(ext)) return <InsertDriveFileIcon sx={{ color: '#00B894' }} />;
    if (['ppt', 'pptx'].includes(ext)) return <InsertDriveFileIcon sx={{ color: '#FDCB6E' }} />;
    return <InsertDriveFileIcon sx={{ color: '#A29BFE' }} />;
}

export default function Feed() {
    const [posts, setPosts] = useState<Post[]>([]);
    const [loading, setLoading] = useState(true);
    const [newPost, setNewPost] = useState('');
    const [commenting, setCommenting] = useState<string | null>(null);
    const [commentText, setCommentText] = useState('');
    const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [filePreviews, setFilePreviews] = useState<{ file: File; url: string; type: string }[]>([]);
    const [uploading, setUploading] = useState(false);
    const [stats, setStats] = useState<any>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const videoInputRef = useRef<HTMLInputElement>(null);
    const docInputRef = useRef<HTMLInputElement>(null);

    const loadFeed = useCallback(async () => {
        try {
            const res = await feedService.getFeed(0, 15);
            setPosts(res.data.posts || []);
        } catch { /* ignore */ }
        setLoading(false);
    }, []);

    useEffect(() => { loadFeed(); }, [loadFeed]);

    useEffect(() => {
        const loadStats = async () => {
            try {
                const [netRes, dashRes] = await Promise.all([
                    networkService.getStats().catch(() => ({ data: {} })),
                    dashboardService.getStats().catch(() => ({ data: {} })),
                ]);
                setStats({ ...netRes.data, ...dashRes.data });
            } catch { /* ignore */ }
        };
        loadStats();
    }, []);

    useEffect(() => {
        return () => { filePreviews.forEach((fp) => URL.revokeObjectURL(fp.url)); };
    }, [filePreviews]);

    const addFiles = (newFiles: FileList | null) => {
        if (!newFiles) return;
        const arr = Array.from(newFiles);
        const total = [...selectedFiles, ...arr];
        if (total.length > 10) { alert('Maximum 10 files per post'); return; }
        setSelectedFiles(total);
        const previews = arr.map((f) => ({
            file: f,
            url: f.type.startsWith('image/') || f.type.startsWith('video/') ? URL.createObjectURL(f) : '',
            type: f.type.startsWith('image/') ? 'image' : f.type.startsWith('video/') ? 'video' : 'file',
        }));
        setFilePreviews((prev) => [...prev, ...previews]);
    };

    const removeFile = (index: number) => {
        const fp = filePreviews[index];
        if (fp?.url) URL.revokeObjectURL(fp.url);
        setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
        setFilePreviews((prev) => prev.filter((_, i) => i !== index));
    };

    const handlePost = async () => {
        if (!newPost.trim() && selectedFiles.length === 0) return;
        setUploading(true);
        try {
            let res;
            if (selectedFiles.length > 0) { res = await feedService.createPostWithMedia(newPost, selectedFiles); }
            else { res = await feedService.createPost(newPost); }
            setPosts((prev) => [res.data, ...prev]);
            setNewPost('');
            setSelectedFiles([]);
            filePreviews.forEach((fp) => fp.url && URL.revokeObjectURL(fp.url));
            setFilePreviews([]);
        } catch { /* ignore */ }
        setUploading(false);
    };

    const handleLike = async (postId: string) => {
        try {
            await feedService.likePost(postId);
            setLikedPosts((prev) => { const copy = new Set(prev); if (copy.has(postId)) copy.delete(postId); else copy.add(postId); return copy; });
            setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, likes: likedPosts.has(postId) ? p.likes - 1 : p.likes + 1 } : p));
        } catch { /* ignore */ }
    };

    const handleComment = async (postId: string) => {
        if (!commentText.trim()) return;
        try {
            await feedService.commentPost(postId, commentText);
            setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, comments_count: p.comments_count + 1 } : p));
            setCommentText('');
            setCommenting(null);
        } catch { /* ignore */ }
    };

    const postTypeIcon = (type: string) => {
        switch (type) {
            case 'article': return <ArticleIcon sx={{ fontSize: 14, color: '#6C5CE7' }} />;
            case 'celebration': return <CelebrationIcon sx={{ fontSize: 14, color: '#FDCB6E' }} />;
            case 'photo': return <ImageIcon sx={{ fontSize: 14, color: '#74B9FF' }} />;
            case 'video': return <VideocamIcon sx={{ fontSize: 14, color: '#FDCB6E' }} />;
            case 'document': return <AttachFileIcon sx={{ fontSize: 14, color: '#00CEC9' }} />;
            default: return null;
        }
    };

    const renderPostMedia = (media: MediaItem[]) => {
        if (!media || media.length === 0) return null;
        const images = media.filter((m) => m.media_type === 'image');
        const videos = media.filter((m) => m.media_type === 'video');
        const files = media.filter((m) => m.media_type === 'file');
        const mediaUrl = (url: string) => url.startsWith('http') ? url : `${API_BASE}${url}`;
        return (
            <Box sx={{ mt: 1.5, mb: 0.5 }}>
                {images.length > 0 && (
                    <Box sx={{
                        display: 'grid',
                        gridTemplateColumns: images.length === 1 ? '1fr' : images.length === 2 ? '1fr 1fr' : 'repeat(3, 1fr)',
                        gap: 0.5, borderRadius: 3, overflow: 'hidden',
                        mb: videos.length > 0 || files.length > 0 ? 1 : 0,
                    }}>
                        {images.map((img, idx) => (
                            <Box key={img.id} component="img" src={mediaUrl(img.url)} alt={img.filename}
                                sx={{
                                    width: '100%', height: images.length === 1 ? 400 : 220, objectFit: 'cover',
                                    cursor: 'pointer', transition: 'all 0.3s',
                                    '&:hover': { opacity: 0.9, transform: 'scale(1.01)' },
                                    ...(images.length === 3 && idx === 0 ? { gridRow: '1 / 3' } : {}),
                                }}
                                onClick={() => window.open(mediaUrl(img.url), '_blank')}
                            />
                        ))}
                    </Box>
                )}
                {videos.map((vid) => (
                    <Box key={vid.id} sx={{ borderRadius: 3, overflow: 'hidden', mb: files.length > 0 ? 1 : 0 }}>
                        <video src={mediaUrl(vid.url)} controls style={{ width: '100%', maxHeight: 450, borderRadius: 12, backgroundColor: '#000' }} />
                    </Box>
                ))}
                {files.length > 0 && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        {files.map((f) => (
                            <Box key={f.id}
                                sx={{
                                    p: 1.5, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 1.5,
                                    borderRadius: 2.5, border: '1px solid', borderColor: 'divider',
                                    transition: 'all 0.2s',
                                    '&:hover': { bgcolor: 'rgba(108,92,231,0.05)', borderColor: 'rgba(108,92,231,0.2)' },
                                }}
                                onClick={() => window.open(mediaUrl(f.url), '_blank')}
                            >
                                {fileIcon(f.filename)}
                                <Box sx={{ flex: 1, minWidth: 0 }}>
                                    <Typography variant="body2" fontWeight={600} noWrap>{f.filename}</Typography>
                                    <Typography variant="caption" color="text.secondary">{formatFileSize(f.size)}</Typography>
                                </Box>
                                <Chip label="Download" size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                            </Box>
                        ))}
                    </Box>
                )}
            </Box>
        );
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
                <CircularProgress sx={{ color: '#6C5CE7' }} />
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: 900, mx: 'auto', p: { xs: 2, md: 3 }, display: 'flex', gap: 3 }}>
            {/* Hidden file inputs */}
            <input type="file" ref={fileInputRef} hidden multiple accept="image/*" onChange={(e) => addFiles(e.target.files)} />
            <input type="file" ref={videoInputRef} hidden multiple accept="video/*" onChange={(e) => addFiles(e.target.files)} />
            <input type="file" ref={docInputRef} hidden multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.csv,.txt" onChange={(e) => addFiles(e.target.files)} />

            {/* Main Feed */}
            <Box sx={{ flex: 1, minWidth: 0 }}>
                {/* Page header */}
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h4" fontWeight={800} color="primary">
                        Your Feed
                    </Typography>
                    <Typography variant="body2" color="text.secondary">Stay updated with your network</Typography>
                </Box>

                {/* Create Post */}
                <Card sx={{ mb: 2.5 }}>
                    <CardContent sx={{ pb: '12px !important' }}>
                        <Box sx={{ display: 'flex', gap: 1.5, mb: 1.5 }}>
                            <Avatar sx={{
                                bgcolor: 'primary.main', width: 48, height: 48,
                            }}>Y</Avatar>
                            <TextField
                                fullWidth multiline minRows={1} maxRows={6}
                                placeholder="Share your thoughts, insights, or achievements..."
                                value={newPost} onChange={(e) => setNewPost(e.target.value)} variant="outlined"
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        borderRadius: 3,
                                        bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(108,92,231,0.02)',
                                    },
                                }}
                            />
                        </Box>

                        {/* File Previews */}
                        {filePreviews.length > 0 && (
                            <Box sx={{
                                display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1.5, p: 1.5,
                                borderRadius: 3, bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
                                border: '1px solid', borderColor: 'divider',
                            }}>
                                {filePreviews.map((fp, idx) => (
                                    <Box key={idx} sx={{ position: 'relative' }}>
                                        {fp.type === 'image' ? (
                                            <Box component="img" src={fp.url} alt={fp.file.name}
                                                sx={{ width: 100, height: 100, borderRadius: 2.5, objectFit: 'cover' }} />
                                        ) : fp.type === 'video' ? (
                                            <Box sx={{
                                                width: 100, height: 100, borderRadius: 2.5,
                                                bgcolor: '#1a1a2e', display: 'flex', alignItems: 'center',
                                                justifyContent: 'center', position: 'relative', overflow: 'hidden',
                                            }}>
                                                <video src={fp.url} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                                <PlayCircleFilledIcon sx={{ position: 'absolute', fontSize: 36, color: '#fff', opacity: 0.9 }} />
                                            </Box>
                                        ) : (
                                            <Box sx={{
                                                width: 100, height: 100, borderRadius: 2.5,
                                                bgcolor: 'rgba(108,92,231,0.06)', display: 'flex',
                                                flexDirection: 'column', alignItems: 'center', justifyContent: 'center', px: 0.5,
                                            }}>
                                                {fileIcon(fp.file.name)}
                                                <Typography variant="caption" noWrap sx={{ mt: 0.5, maxWidth: 90, textAlign: 'center' }}>
                                                    {fp.file.name}
                                                </Typography>
                                            </Box>
                                        )}
                                        <IconButton size="small" onClick={() => removeFile(idx)} sx={{
                                            position: 'absolute', top: -6, right: -6,
                                            bgcolor: 'rgba(0,0,0,0.7)', color: '#fff', width: 22, height: 22,
                                            '&:hover': { bgcolor: '#FF6B6B' },
                                        }}>
                                            <CloseIcon sx={{ fontSize: 14 }} />
                                        </IconButton>
                                    </Box>
                                ))}
                            </Box>
                        )}

                        {uploading && <LinearProgress sx={{ mb: 1, borderRadius: 1 }} />}

                        <Divider sx={{ mb: 1 }} />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box sx={{ display: 'flex', gap: 0.5 }}>
                                <Button startIcon={<ImageIcon />} size="small" onClick={() => fileInputRef.current?.click()}
                                    sx={{ color: '#74B9FF', '&:hover': { bgcolor: 'rgba(116,185,255,0.08)' } }}>Photo</Button>
                                <Button startIcon={<VideocamIcon />} size="small" onClick={() => videoInputRef.current?.click()}
                                    sx={{ color: '#FDCB6E', '&:hover': { bgcolor: 'rgba(253,203,110,0.08)' } }}>Video</Button>
                                <Button startIcon={<AttachFileIcon />} size="small" onClick={() => docInputRef.current?.click()}
                                    sx={{ color: '#00CEC9', '&:hover': { bgcolor: 'rgba(0,206,201,0.08)' } }}>File</Button>
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {selectedFiles.length > 0 && (
                                    <Chip label={`${selectedFiles.length} file${selectedFiles.length > 1 ? 's' : ''}`}
                                        size="small" onDelete={() => {
                                            filePreviews.forEach((fp) => fp.url && URL.revokeObjectURL(fp.url));
                                            setSelectedFiles([]); setFilePreviews([]);
                                        }} />
                                )}
                                <Button variant="contained" size="small"
                                    disabled={(!newPost.trim() && selectedFiles.length === 0) || uploading}
                                    onClick={handlePost} sx={{ borderRadius: 2.5, px: 3 }}>
                                    {uploading ? 'Posting...' : 'Post'}
                                </Button>
                            </Box>
                        </Box>
                    </CardContent>
                </Card>

                {/* Posts */}
                <Box>
                    {posts.map((post) => (
                        <Card key={post.id} sx={{ mb: 2, '&:hover': { borderColor: 'rgba(108,92,231,0.15)' } }}>
                            <CardContent sx={{ pb: '8px !important' }}>
                                {/* Author */}
                                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5, mb: 1.5 }}>
                                    <Avatar src={post.author_avatar}
                                        sx={{ bgcolor: 'primary.main', width: 44, height: 44, fontSize: '1rem' }}>
                                        {post.author_name?.charAt(0)}
                                    </Avatar>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="body2" fontWeight={600}>{post.author_name}</Typography>
                                        <Typography variant="caption" color="text.secondary">{post.author_role} • {post.author_department}</Typography>
                                        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                            {timeAgo(post.created_at)} • <PublicIcon sx={{ fontSize: 12 }} /> {postTypeIcon(post.post_type)}
                                        </Typography>
                                    </Box>
                                    <IconButton size="small"><MoreHorizIcon /></IconButton>
                                </Box>

                                {/* Content */}
                                {post.content && (
                                    <Typography variant="body2" sx={{ mb: 1, whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                                        {post.content}
                                    </Typography>
                                )}

                                {/* Media */}
                                {renderPostMedia(post.media || [])}

                                {/* Stats */}
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5, px: 0.5 }}>
                                    <Typography variant="caption" color="text.secondary">
                                        👍 {post.likes} {post.likes > 1 ? 'likes' : 'like'}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                        {post.comments_count > 0 && `${post.comments_count} comments • `}
                                        {post.shares > 0 && `${post.shares} shares`}
                                    </Typography>
                                </Box>

                                <Divider sx={{ mb: 0.5 }} />

                                {/* Actions */}
                                <Box sx={{ display: 'flex', justifyContent: 'space-around' }}>
                                    <Button startIcon={likedPosts.has(post.id) ? <ThumbUpIcon /> : <ThumbUpOutlinedIcon />}
                                        onClick={() => handleLike(post.id)} size="small"
                                        sx={{
                                            flex: 1,
                                            color: likedPosts.has(post.id) ? 'primary.main' : 'text.secondary',
                                            fontWeight: likedPosts.has(post.id) ? 600 : 400,
                                            '&:hover': { bgcolor: 'rgba(108,92,231,0.06)' },
                                        }}>Like</Button>
                                    <Button startIcon={<ChatBubbleOutlineIcon />}
                                        onClick={() => setCommenting(commenting === post.id ? null : post.id)}
                                        size="small" sx={{ flex: 1, color: 'text.secondary', '&:hover': { bgcolor: 'rgba(108,92,231,0.06)' } }}>
                                        Comment
                                    </Button>
                                    <Button startIcon={<ShareIcon />} size="small"
                                        sx={{ flex: 1, color: 'text.secondary', '&:hover': { bgcolor: 'rgba(108,92,231,0.06)' } }}>
                                        Share
                                    </Button>
                                </Box>

                                {/* Comment Input */}
                                {commenting === post.id && (
                                    <Box sx={{ display: 'flex', gap: 1, mt: 1.5, alignItems: 'center' }}>
                                        <Avatar sx={{ width: 28, height: 28, bgcolor: '#6C5CE7', fontSize: '0.75rem' }}>Y</Avatar>
                                        <TextField fullWidth size="small" placeholder="Add a comment..."
                                            value={commentText} onChange={(e) => setCommentText(e.target.value)}
                                            onKeyDown={(e) => e.key === 'Enter' && handleComment(post.id)}
                                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2.5 } }} />
                                        <IconButton size="small" color="primary"
                                            onClick={() => handleComment(post.id)} disabled={!commentText.trim()}>
                                            <SendIcon fontSize="small" />
                                        </IconButton>
                                    </Box>
                                )}
                            </CardContent>
                        </Card>
                    ))}
                </Box>
            </Box>

            {/* Right Sidebar */}
            <Box sx={{ width: 280, flexShrink: 0, display: { xs: 'none', lg: 'block' } }}>
                {/* Quick Stats */}
                <Card sx={{ mb: 2, overflow: 'visible' }}>
                    <CardContent>
                        <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <AutoAwesomeIcon sx={{ fontSize: 18, color: '#A29BFE' }} /> Quick Insights
                        </Typography>
                        {[
                            { label: 'Connections', value: stats?.total_connections || 127, icon: <GroupIcon />, color: '#6C5CE7' },
                            { label: 'Profile Views', value: stats?.profile_views || 284, icon: <TrendingUpIcon />, color: '#00CEC9' },
                        ].map((item, i) => (
                            <Box key={i} sx={{
                                display: 'flex', alignItems: 'center', gap: 1.5, py: 1.2,
                                borderBottom: i === 0 ? '1px solid' : 'none', borderColor: 'divider',
                            }}>
                                <Box sx={{
                                    width: 36, height: 36, borderRadius: 2, display: 'flex',
                                    alignItems: 'center', justifyContent: 'center',
                                    background: `linear-gradient(135deg, ${item.color}20, ${item.color}10)`,
                                    color: item.color,
                                }}>
                                    {React.cloneElement(item.icon, { sx: { fontSize: 18 } })}
                                </Box>
                                <Box>
                                    <Typography variant="h6" fontWeight={700} sx={{ lineHeight: 1.2 }}>{item.value}</Typography>
                                    <Typography variant="caption" color="text.secondary">{item.label}</Typography>
                                </Box>
                            </Box>
                        ))}
                    </CardContent>
                </Card>

                {/* Trending */}
                <Card>
                    <CardContent>
                        <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1.5 }}>
                            🔥 Trending Topics
                        </Typography>
                        {['AI & Machine Learning', 'Remote Work', 'GraphQL', 'Web3', 'Data Engineering'].map((topic, i) => (
                            <Box key={i} sx={{
                                py: 1, cursor: 'pointer', transition: 'all 0.2s',
                                '&:hover': { color: '#6C5CE7' },
                                borderBottom: i < 4 ? '1px solid' : 'none', borderColor: 'divider',
                            }}>
                                <Typography variant="body2" fontWeight={500}>{topic}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {Math.floor(Math.random() * 500 + 100)} posts this week
                                </Typography>
                            </Box>
                        ))}
                    </CardContent>
                </Card>
            </Box>
        </Box>
    );
}
