import React, { useState, useEffect, useRef } from 'react';
import {
  Box, Typography, Card, CardContent, TextField, Button,
  Tabs, Tab, Chip, CircularProgress, Alert, Paper,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  LinearProgress, Divider, Avatar, IconButton, InputAdornment,
  Autocomplete,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CategoryIcon from '@mui/icons-material/Category';
import PsychologyIcon from '@mui/icons-material/Psychology';

import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SpeedIcon from '@mui/icons-material/Speed';
import StorageIcon from '@mui/icons-material/Storage';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';
import { aiService, bigdataService, learningResourcesService } from '../services/api';
import SchoolIcon from '@mui/icons-material/School';
import YouTubeIcon from '@mui/icons-material/YouTube';
import LanguageIcon from '@mui/icons-material/Language';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';

const COLORS = ['#6C5CE7', '#FD79A8', '#00B894', '#FDCB6E', '#00CEC9', '#FF6B6B', '#A29BFE', '#FD79A8'];

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 24 }}>
      {value === index && children}
    </div>
  );
}

// ── Expert Recommender Tab ────────────────────────────────────────

function ExpertRecommender() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await aiService.recommendExperts(query);
      setResults(res.data.results || []);
    } catch (err) {
      console.error(err);
      setResults([]);
    }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <PsychologyIcon sx={{ color: '#6C5CE7' }} /> ML-Powered Expert Recommendation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Uses <strong>TF-IDF vectorization + cosine similarity</strong> to find experts matching your query.
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          fullWidth
          placeholder="e.g. 'python developer', 'machine learning expert', 'data scientist'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          InputProps={{
            startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              backgroundColor: 'rgba(255,255,255,0.05)',
              borderRadius: 2,
            },
          }}
        />
        <Button variant="contained" onClick={handleSearch} disabled={loading} sx={{ px: 4 }}>
          {loading ? <CircularProgress size={24} /> : 'Recommend'}
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2, borderRadius: 1 }} />}

      {searched && !loading && results.length === 0 && (
        <Alert severity="info">No experts found matching your query. Try different keywords.</Alert>
      )}

      {results.length > 0 && (
        <TableContainer component={Paper} sx={{ backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Rank</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Expert</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Role</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Department</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Similarity</TableCell>
                <TableCell sx={{ fontWeight: 700, color: '#6C5CE7' }}>Skills</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {results.map((expert, idx) => (
                <TableRow key={expert.id || idx} hover sx={{ '&:hover': { backgroundColor: 'rgba(108,92,231,0.08)' } }}>
                  <TableCell>
                    <Chip label={`#${idx + 1}`} size="small"
                      sx={{ fontWeight: 700, bgcolor: idx < 3 ? 'rgba(249,115,22,0.2)' : 'rgba(255,255,255,0.05)' }} />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: COLORS[idx % COLORS.length], fontSize: 14 }}>
                        {expert.name?.[0] || '?'}
                      </Avatar>
                      {expert.name}
                    </Box>
                  </TableCell>
                  <TableCell>{expert.role}</TableCell>
                  <TableCell>{expert.department}</TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={expert.similarity_score * 100}
                        sx={{
                          width: 60, height: 8, borderRadius: 4, bgcolor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': { bgcolor: '#00B894' }
                        }}
                      />
                      <Typography variant="body2" fontWeight={600}>
                        {(expert.similarity_score * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {(expert.skills || []).slice(0, 3).map((s: string) => (
                        <Chip key={s} label={s} size="small" variant="outlined"
                          sx={{ fontSize: '0.7rem', height: 24 }} />
                      ))}
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

// ── Document Classifier Tab ───────────────────────────────────────

function DocumentClassifier() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleClassify = async () => {
    if (!title.trim()) return;
    setLoading(true);
    try {
      const res = await aiService.classifyDocument(title, content);
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CategoryIcon sx={{ color: '#FD79A8' }} /> Document Auto-Classification
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Uses <strong>TF-IDF + Logistic Regression</strong> pipeline to predict a document's topic/category.
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
        <TextField
          fullWidth label="Document Title" value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Introduction to Machine Learning with Python"
          sx={{ '& .MuiOutlinedInput-root': { backgroundColor: 'rgba(255,255,255,0.05)' } }}
        />
        <TextField
          fullWidth label="Content (optional)" value={content}
          onChange={(e) => setContent(e.target.value)}
          multiline rows={3}
          placeholder="Paste document content for better accuracy..."
          sx={{ '& .MuiOutlinedInput-root': { backgroundColor: 'rgba(255,255,255,0.05)' } }}
        />
        <Button variant="contained" onClick={handleClassify} disabled={loading}
          sx={{ alignSelf: 'flex-start', px: 4 }}>
          {loading ? <CircularProgress size={24} /> : '🔮 Classify'}
        </Button>
      </Box>

      {result && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Predicted Topic: <Chip label={result.predicted_topic} color="secondary" sx={{ fontWeight: 700, fontSize: '1rem', ml: 1 }} />
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Confidence: <strong>{(result.confidence * 100).toFixed(1)}%</strong>
            </Typography>

            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>All Predictions:</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {(result.all_predictions || []).map((p: any, i: number) => (
                <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body2" sx={{ minWidth: 150 }}>{p.topic}</Typography>
                  <LinearProgress
                    variant="determinate"
                    value={p.confidence * 100}
                    sx={{
                      flexGrow: 1, height: 10, borderRadius: 5, bgcolor: 'rgba(255,255,255,0.05)',
                      '& .MuiLinearProgress-bar': { bgcolor: COLORS[i % COLORS.length], borderRadius: 5 }
                    }}
                  />
                  <Typography variant="body2" fontWeight={600} sx={{ minWidth: 50 }}>
                    {(p.confidence * 100).toFixed(1)}%
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

// ── Skill Gap Analysis Tab ────────────────────────────────────────

function SkillGapAnalysis() {
  const [expertId, setExpertId] = useState('');
  const [experts, setExperts] = useState<any[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Load experts for the dropdown
    const loadExperts = async () => {
      try {
        const res = await aiService.recommendExperts('developer engineer scientist', 30);
        setExperts(res.data.results || []);
      } catch { /* fallback empty */ }
    };
    loadExperts();
  }, []);

  const handleAnalyze = async () => {
    if (!expertId) return;
    setLoading(true);
    try {
      const res = await aiService.getSkillGaps(expertId);
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TrendingUpIcon sx={{ color: '#00B894' }} /> Skill Gap Prediction
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Uses <strong>collaborative filtering</strong> on the user-skill matrix to predict skills an expert should learn.
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Autocomplete
          fullWidth
          options={experts}
          getOptionLabel={(o) => `${o.name} - ${o.role}`}
          onChange={(_, val) => setExpertId(val?.id || '')}
          renderInput={(params) => <TextField {...params} label="Select Expert" placeholder="Search expert..." />}
        />
        <Button variant="contained" onClick={handleAnalyze} disabled={loading || !expertId}
          sx={{ px: 4 }}>
          {loading ? <CircularProgress size={24} /> : 'Analyze'}
        </Button>
      </Box>

      {result && (
        <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Card sx={{ flex: 1, minWidth: 300 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Current Skills ({result.current_skills?.length || 0})
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {(result.current_skills || []).map((s: string) => (
                  <Chip key={s} label={s} size="small" color="primary" variant="outlined" />
                ))}
              </Box>
            </CardContent>
          </Card>

          <Card sx={{ flex: 1.5, minWidth: 300 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                🎯 Recommended Skills to Learn
              </Typography>
              {(result.recommended_skills || []).map((s: any, i: number) => (
                <Box key={i} sx={{
                  display: 'flex', alignItems: 'center', gap: 2, mb: 1.5, p: 1,
                  borderRadius: 1, bgcolor: 'rgba(255,255,255,0.03)'
                }}>
                  <Chip label={`#${i + 1}`} size="small" sx={{ fontWeight: 700, bgcolor: 'rgba(34,197,94,0.2)' }} />
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" fontWeight={600}>{s.skill}</Typography>
                    <Typography variant="caption" color="text.secondary">{s.category} • {s.reason}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress variant="determinate" value={Math.min(s.relevance_score * 25, 100)}
                      sx={{
                        width: 50, height: 6, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.1)',
                        '& .MuiLinearProgress-bar': { bgcolor: '#00B894' }
                      }} />
                    <Typography variant="caption" fontWeight={600}>{s.relevance_score.toFixed(2)}</Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
}

// ── AI Chatbot Tab ────────────────────────────────────────────────

interface ChatMessage {
  role: 'user' | 'ai';
  content: string;
  data?: any;
  suggestions?: string[];
}

function AIChatbot() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'ai', content: '👋 Hello! I\'m Veda, your AI assistant. Ask me anything — experts, skills, documents, companies, or general knowledge!',
      suggestions: ['Who knows Python?', 'Show me top skills', 'How many experts?', 'Find documents about AI']
    },
  ]);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (msg?: string) => {
    const message = msg || input;
    if (!message.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setInput('');
    setLoading(true);

    try {
      const res = await aiService.chat(message);
      const data = res.data;
      setMessages((prev) => [...prev, {
        role: 'ai',
        content: data.message,
        data: data.data,
        suggestions: data.suggestions,
      }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'ai', content: '❌ Sorry, something went wrong. Please try again.' }]);
    }
    setLoading(false);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '60vh' }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SmartToyIcon sx={{ color: '#00CEC9' }} /> Veda — AI Knowledge Assistant
      </Typography>

      {/* Chat Messages */}
      <Box sx={{
        flexGrow: 1, overflow: 'auto', mb: 2, p: 2, borderRadius: 2,
        bgcolor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)'
      }}>
        {messages.map((msg, i) => (
          <Box key={i} sx={{
            display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start', mb: 2
          }}>
            <Box sx={{
              maxWidth: '80%', p: 2, borderRadius: 2,
              bgcolor: msg.role === 'user' ? 'rgba(108,92,231,0.2)' : 'rgba(255,255,255,0.05)',
              border: msg.role === 'user' ? '1px solid rgba(108,92,231,0.3)' : '1px solid rgba(255,255,255,0.08)',
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                {msg.role === 'ai' ? <SmartToyIcon sx={{ fontSize: 18, color: '#00CEC9' }} /> :
                  <PersonIcon sx={{ fontSize: 18, color: '#6C5CE7' }} />}
                <Typography variant="caption" fontWeight={600} color="text.secondary">
                  {msg.role === 'ai' ? 'Veda' : 'You'}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>{msg.content}</Typography>

              {/* Data display */}
              {msg.data && Array.isArray(msg.data) && msg.data.length > 0 && (
                <Box sx={{
                  mt: 1.5, maxHeight: 260, overflow: 'auto', borderRadius: 1,
                  bgcolor: 'rgba(255,255,255,0.03)', p: 1
                }}>
                  {msg.data.slice(0, 8).map((item: any, j: number) => (
                    <Box key={j} sx={{
                      display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, p: 0.5,
                      borderRadius: 1, '&:hover': { bgcolor: 'rgba(255,255,255,0.04)' }
                    }}>
                      <Chip label={j + 1} size="small" sx={{
                        minWidth: 28, fontWeight: 700,
                        bgcolor: 'rgba(108,92,231,0.15)', fontSize: '0.7rem'
                      }} />
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography variant="body2" fontWeight={600} noWrap>
                          {item.name || item.title || item.skill || item.department || '—'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" noWrap>
                          {[item.role, item.category, item.topic, item.level,
                          item.demand != null ? `Demand: ${item.demand}` : null,
                          item.experience_years ? `${item.experience_years} yrs exp` : null,
                          item.rating ? `★ ${item.rating}` : null,
                          item.member_count ? `${item.member_count} members` : null,
                          ].filter(Boolean).join(' • ')}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
              {/* Statistics data */}
              {msg.data && !Array.isArray(msg.data) && typeof msg.data === 'object' && (
                <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {Object.entries(msg.data).filter(([_, v]) => typeof v !== 'object').slice(0, 8).map(([k, v]: [string, any]) => (
                    <Chip key={k} label={`${k.replace(/_/g, ' ')}: ${v}`}
                      size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                  ))}
                </Box>
              )}

              {/* Suggestions */}
              {msg.suggestions && msg.suggestions.length > 0 && (
                <Box sx={{ mt: 1.5, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {msg.suggestions.map((s, j) => (
                    <Chip key={j} label={s} size="small" variant="outlined"
                      onClick={() => handleSend(s)}
                      sx={{
                        cursor: 'pointer', fontSize: '0.7rem',
                        '&:hover': { bgcolor: 'rgba(108,92,231,0.1)' }
                      }} />
                  ))}
                </Box>
              )}
            </Box>
          </Box>
        ))}
        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 2 }}>
            <CircularProgress size={16} /> <Typography variant="body2" color="text.secondary">Thinking...</Typography>
          </Box>
        )}
        <div ref={chatEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth placeholder="Ask about experts, skills, documents..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          sx={{ '& .MuiOutlinedInput-root': { backgroundColor: 'rgba(255,255,255,0.05)' } }}
        />
        <IconButton onClick={() => handleSend()} disabled={loading}
          sx={{ bgcolor: 'rgba(108,92,231,0.2)', '&:hover': { bgcolor: 'rgba(108,92,231,0.3)' } }}>
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}

// ── Big Data Analytics Tab ────────────────────────────────────────

function BigDataAnalytics() {
  const [skillData, setSkillData] = useState<any>(null);
  const [docData, setDocData] = useState<any>(null);
  const [rankData, setRankData] = useState<any>(null);
  const [pipelineStatus, setPipelineStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [skills, docs, ranks, status] = await Promise.all([
          bigdataService.getSkillAnalytics(),
          bigdataService.getDocumentStats(),
          bigdataService.getExpertRankings(),
          bigdataService.getPipelineStatus(),
        ]);
        setSkillData(skills.data?.data);
        setDocData(docs.data?.data);
        setRankData(ranks.data?.data);
        setPipelineStatus(status.data);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    };
    loadData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box>;

  const skillFreqData = (skillData?.skill_frequency || []).slice(0, 12);
  const topicData = (docData?.documents_by_topic || []).slice(0, 8);
  const rankings = (rankData?.rankings || []).slice(0, 10);
  const tierDist = rankData?.tier_distribution || [];

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <StorageIcon sx={{ color: '#FDCB6E' }} /> Big Data Analytics
        <Chip label="Apache Spark" size="small" sx={{ ml: 1, bgcolor: 'rgba(253,203,110,0.2)', color: '#FDCB6E' }} />
      </Typography>

      {/* Pipeline Status */}
      {pipelineStatus && (
        <Alert severity="info" sx={{
          mb: 3, bgcolor: 'rgba(0,206,201,0.1)', color: 'white',
          '& .MuiAlert-icon': { color: '#00CEC9' }
        }}>
          <strong>Pipeline:</strong> {pipelineStatus.pipeline} |
          {Object.entries(pipelineStatus.jobs || {}).map(([name, job]: [string, any]) => (
            <Chip key={name} label={`${name}: ${job.status}`} size="small" sx={{
              ml: 1, fontSize: '0.7rem',
              bgcolor: job.status === 'completed' ? 'rgba(34,197,94,0.2)' : 'rgba(245,158,11,0.2)'
            }} />
          ))}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
        {/* Skill Frequency Chart */}
        <Card sx={{ flex: 1, minWidth: 400 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>📊 Skill Frequency Analysis</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={skillFreqData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="skill_name" angle={-30} textAnchor="end" height={80} tick={{ fontSize: 11, fill: '#94a3b8' }} />
                <YAxis tick={{ fill: '#94a3b8' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                <Bar dataKey="expert_count" fill="#6C5CE7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Topic Distribution Pie */}
        <Card sx={{ flex: 1, minWidth: 350 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>📄 Document Topic Distribution</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={topicData} dataKey="count" nameKey="topic" cx="50%" cy="50%"
                  outerRadius={100} label={({ topic, count }: any) => `${topic}: ${count}`}>
                  {topicData.map((_: any, index: number) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Box>

      {/* Expert Rankings Table */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>🏆 Expert Influence Rankings (PageRank-like Algorithm)</Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            {tierDist.map((t: any, i: number) => (
              <Chip key={i} label={`${t.tier}: ${t.count}`} size="small"
                sx={{ bgcolor: 'rgba(255,255,255,0.05)', fontWeight: 600 }} />
            ))}
          </Box>
          <TableContainer sx={{ maxHeight: 400 }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  {['Rank', 'Expert', 'Department', 'Skills', 'Score', 'Tier'].map(h => (
                    <TableCell key={h} sx={{ fontWeight: 700, color: '#FDCB6E', bgcolor: '#1e293b' }}>{h}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {rankings.map((r: any, i: number) => (
                  <TableRow key={i} hover>
                    <TableCell><Chip label={`#${i + 1}`} size="small" sx={{ fontWeight: 700 }} /></TableCell>
                    <TableCell>{r.employee_name}</TableCell>
                    <TableCell>{r.department}</TableCell>
                    <TableCell>{r.num_skills}</TableCell>
                    <TableCell>
                      <Typography fontWeight={700} sx={{ color: '#00B894' }}>{r.influence_score}</Typography>
                    </TableCell>
                    <TableCell><Chip label={r.tier} size="small" sx={{ fontSize: '0.7rem' }} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}

// ── Model Stats Tab ───────────────────────────────────────────────

function ModelStats() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  const loadStats = async () => {
    try {
      const res = await aiService.getModelStats();
      setStats(res.data);
    } catch (err) { console.error(err); }
    setLoading(false);
  };

  useEffect(() => { loadStats(); }, []);

  const handleTrainAll = async () => {
    setTraining(true);
    try {
      await aiService.trainAll();
      await loadStats();
    } catch (err) { console.error(err); }
    setTraining(false);
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box>;

  const models = [
    { name: 'Expert Recommender', key: 'recommender', icon: '🎯', color: '#6C5CE7' },
    { name: 'Document Classifier', key: 'classifier', icon: '📄', color: '#FD79A8' },
    { name: 'Skill Predictor', key: 'skill_predictor', icon: '📈', color: '#00B894' },
    { name: 'Embedding Engine', key: 'embedding_engine', icon: '🔗', color: '#00CEC9' },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SpeedIcon sx={{ color: '#A29BFE' }} /> ML Model Dashboard
        </Typography>
        <Button variant="contained" onClick={handleTrainAll} disabled={training}>
          {training ? <><CircularProgress size={20} sx={{ mr: 1 }} /> Training...</> : '🚀 Train All Models'}
        </Button>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
        {models.map(m => {
          const data = stats?.[m.key] || {};
          return (
            <Card key={m.key} sx={{ flex: 1, minWidth: 250 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Typography variant="h5">{m.icon}</Typography>
                  <Typography variant="subtitle1" fontWeight={700}>{m.name}</Typography>
                </Box>
                <Chip label={data.is_trained ? '✅ Trained' : '⏳ Not Trained'} size="small"
                  sx={{ mb: 2, bgcolor: data.is_trained ? 'rgba(34,197,94,0.2)' : 'rgba(245,158,11,0.2)' }} />
                <Typography variant="body2" color="text.secondary">
                  Model: {data.model || 'N/A'}
                </Typography>
                {data.num_experts && <Typography variant="body2" color="text.secondary">Experts: {data.num_experts}</Typography>}
                {data.num_documents && <Typography variant="body2" color="text.secondary">Documents: {data.num_documents}</Typography>}
                {data.num_classes && <Typography variant="body2" color="text.secondary">Classes: {data.num_classes}</Typography>}
                {data.vocabulary_size > 0 && <Typography variant="body2" color="text.secondary">Vocabulary: {data.vocabulary_size}</Typography>}
                {data.cross_val_accuracy > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Accuracy: <strong style={{ color: '#00B894' }}>{(data.cross_val_accuracy * 100).toFixed(1)}%</strong>
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          );
        })}
      </Box>
    </Box>
  );
}

// ── Learning Recommender Tab ──────────────────────────────────────

function LearningRecommender() {
  const [skills, setSkills] = useState<string[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    learningResourcesService.getSkills().then(r => setSkills(r.data.skills)).catch(() => { });
  }, []);

  const handleRecommend = async () => {
    if (selectedSkills.length === 0) return;
    setLoading(true);
    try {
      const response = await learningResourcesService.recommend(selectedSkills, [], undefined, 8);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error loading recommendations:', error);
    } finally {
      setLoading(false);
    }
  };



  return (
    <Box>
      <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>AI Learning Recommender</Typography>
      <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
        Select your current skills and get <strong>personalized YouTube video & W3Schools tutorial</strong> recommendations.
      </Alert>
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <Autocomplete
          multiple size="small" options={skills} value={selectedSkills}
          onChange={(_, v) => setSelectedSkills(v)}
          renderInput={(params) => <TextField {...params} placeholder="Your current skills" sx={{ minWidth: 300 }} />}
          sx={{ flex: 1 }}
        />
        <Button variant="contained" onClick={handleRecommend} disabled={loading || selectedSkills.length === 0}
          sx={{ textTransform: 'none', borderRadius: 2 }}>
          {loading ? <CircularProgress size={20} /> : 'Get Recommendations'}
        </Button>
      </Box>
      {recommendations.length > 0 && (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {recommendations.map(rec => (
            <Card key={rec.skill} sx={{ border: '1px solid rgba(255,255,255,0.06)' }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1" fontWeight={700}>{rec.skill}</Typography>
                    <Chip label={rec.reason} size="small" sx={{ fontSize: '0.7rem', bgcolor: 'rgba(108,92,231,0.12)', color: '#6C5CE7' }} />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Chip icon={<YouTubeIcon />} label={`${rec.total_videos} videos`} size="small" sx={{ bgcolor: 'rgba(255,0,0,0.08)', color: '#FF4444', fontSize: '0.7rem' }} />
                    <Chip icon={<LanguageIcon />} label={`${rec.total_tutorials} tutorials`} size="small" sx={{ bgcolor: 'rgba(4,170,109,0.08)', color: '#04AA6D', fontSize: '0.7rem' }} />
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                  {rec.top_video && (
                    <Paper sx={{ p: 1.5, flex: 1, minWidth: 250, cursor: 'pointer', borderRadius: 2, bgcolor: 'rgba(255,0,0,0.04)', '&:hover': { bgcolor: 'rgba(255,0,0,0.08)' } }}
                      onClick={() => window.open(rec.top_video.url, '_blank')}>
                      <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                        <Box sx={{ width: 80, height: 45, borderRadius: 1, overflow: 'hidden', flexShrink: 0, position: 'relative' }}>
                          <img src={rec.top_video.thumbnail} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          <PlayCircleOutlineIcon sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', fontSize: 20, color: '#fff' }} />
                        </Box>
                        <Box sx={{ minWidth: 0 }}>
                          <Typography variant="caption" fontWeight={600}>{rec.top_video.title}</Typography>
                          <Typography variant="caption" color="text.secondary" display="block">{rec.top_video.channel} • {rec.top_video.duration}</Typography>
                        </Box>
                        <OpenInNewIcon sx={{ fontSize: 14, color: 'text.secondary', ml: 'auto' }} />
                      </Box>
                    </Paper>
                  )}
                  {rec.top_tutorial && (
                    <Paper sx={{ p: 1.5, flex: 1, minWidth: 250, cursor: 'pointer', borderRadius: 2, bgcolor: 'rgba(4,170,109,0.04)', '&:hover': { bgcolor: 'rgba(4,170,109,0.08)' } }}
                      onClick={() => window.open(rec.top_tutorial.url, '_blank')}>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Box sx={{ width: 28, height: 28, borderRadius: 1, bgcolor: '#04AA6D', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                          <Typography variant="caption" fontWeight={900} color="#fff" fontSize={10}>W3</Typography>
                        </Box>
                        <Box sx={{ minWidth: 0 }}>
                          <Typography variant="caption" fontWeight={600}>{rec.top_tutorial.title}</Typography>
                          <Typography variant="caption" color="text.secondary" display="block">Interactive tutorial • {rec.top_tutorial.topic}</Typography>
                        </Box>
                        <OpenInNewIcon sx={{ fontSize: 14, color: 'text.secondary', ml: 'auto' }} />
                      </Box>
                    </Paper>
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );
}

// ── Main Page Component ───────────────────────────────────────────

const AIInsights: React.FC = () => {
  const [tab, setTab] = useState(0);

  return (
    <Box sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
          <AutoAwesomeIcon sx={{ fontSize: 36, color: '#6C5CE7' }} />
          <Typography variant="h4" fontWeight={700}
            sx={{
              background: 'linear-gradient(135deg, #6C5CE7 0%, #FD79A8 50%, #00CEC9 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'
            }}>
            AI & Big Data Insights
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Machine Learning models and Apache Spark analytics for intelligent knowledge discovery
        </Typography>
      </Box>

      {/* Tabs */}
      <Tabs value={tab} onChange={(_, v) => setTab(v)}
        variant="scrollable" scrollButtons="auto"
        sx={{
          mb: 1,
          '& .MuiTab-root': {
            textTransform: 'none', fontWeight: 600, fontSize: '0.9rem',
            minHeight: 48, borderRadius: '8px 8px 0 0',
          },
          '& .Mui-selected': {
            color: '#6C5CE7 !important',
            background: 'rgba(108,92,231,0.08)',
          },
          '& .MuiTabs-indicator': {
            background: 'linear-gradient(90deg, #6C5CE7, #FD79A8)',
            height: 3, borderRadius: 3,
          },
        }}>
        <Tab icon={<PsychologyIcon />} iconPosition="start" label="Expert Recommender" />
        <Tab icon={<CategoryIcon />} iconPosition="start" label="Document Classifier" />
        <Tab icon={<TrendingUpIcon />} iconPosition="start" label="Skill Gaps" />
        <Tab icon={<SmartToyIcon />} iconPosition="start" label="AI Chatbot" />
        <Tab icon={<StorageIcon />} iconPosition="start" label="Big Data Analytics" />
        <Tab icon={<SpeedIcon />} iconPosition="start" label="Model Stats" />
        <Tab icon={<SchoolIcon />} iconPosition="start" label="Learning Recommender" />
      </Tabs>

      <Divider sx={{ mb: 0 }} />

      <TabPanel value={tab} index={0}><ExpertRecommender /></TabPanel>
      <TabPanel value={tab} index={1}><DocumentClassifier /></TabPanel>
      <TabPanel value={tab} index={2}><SkillGapAnalysis /></TabPanel>
      <TabPanel value={tab} index={3}><AIChatbot /></TabPanel>
      <TabPanel value={tab} index={4}><BigDataAnalytics /></TabPanel>
      <TabPanel value={tab} index={5}><ModelStats /></TabPanel>
      <TabPanel value={tab} index={6}><LearningRecommender /></TabPanel>
    </Box>
  );
};

export default AIInsights;
