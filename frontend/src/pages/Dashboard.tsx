import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, CircularProgress, Chip, IconButton,
  Avatar, Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Select, MenuItem, FormControl, InputLabel, Alert, Snackbar, Tabs, Tab,
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import PeopleIcon from '@mui/icons-material/People';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import WorkIcon from '@mui/icons-material/Work';
import SchoolIcon from '@mui/icons-material/School';
import DescriptionIcon from '@mui/icons-material/Description';
import HubIcon from '@mui/icons-material/Hub';
import { useAuth } from '../contexts/AuthContext';
import { dashboardService } from '../services/api';
import { DeptBarChart, SkillPieChart, ProjectAreaChart, SkillRadarChart, CollaborationChart, SkillDistChart } from '../components/DashboardCharts';

// ══════════════════════════════════════════════════════════════════
//  ANALYTICS — Power BI style with interactive Recharts
// ══════════════════════════════════════════════════════════════════
const AnalyticsOverview: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [departments, setDepartments] = useState<any[]>([]);
  const [skills, setSkills] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [skillDist, setSkillDist] = useState<any[]>([]);
  const [collab, setCollab] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [s, d, sk, p, sd, co] = await Promise.all([
        dashboardService.getStats().then(r => r.data).catch(() => null),
        dashboardService.getDepartments().then(r => r.data).catch(() => []),
        dashboardService.getTopSkills(8).then(r => r.data).catch(() => []),
        dashboardService.getProjectStatus().then(r => r.data).catch(() => []),
        dashboardService.getSkillDistribution().then(r => r.data).catch(() => []),
        dashboardService.getCollaborationRate().then(r => r.data).catch(() => []),
      ]);
      setStats(s); setDepartments(d); setSkills(sk); setProjects(p); setSkillDist(sd); setCollab(co);
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress sx={{ color: '#6C63FF' }} /></Box>;

  const statCards = [
    { label: 'Experts', value: stats?.persons ?? 0, icon: <PeopleIcon />, color: '#6C63FF', bg: 'rgba(108,99,255,0.12)' },
    { label: 'Skills', value: stats?.skills ?? 0, icon: <SchoolIcon />, color: '#00CEC9', bg: 'rgba(0,206,201,0.12)' },
    { label: 'Projects', value: stats?.projects ?? 0, icon: <WorkIcon />, color: '#A78BFA', bg: 'rgba(167,139,250,0.12)' },
    { label: 'Documents', value: stats?.documents ?? 0, icon: <DescriptionIcon />, color: '#FDCB6E', bg: 'rgba(253,203,110,0.12)' },
    { label: 'Total Nodes', value: stats?.total_nodes ?? 0, icon: <HubIcon />, color: '#FF6B6B', bg: 'rgba(255,107,107,0.12)' },
    { label: 'Relationships', value: stats?.total_relationships ?? 0, icon: <TrendingUpIcon />, color: '#2ED573', bg: 'rgba(46,213,115,0.12)' },
  ];

  const cardSx = { transition: 'all 0.3s', '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 8px 30px rgba(108,99,255,0.15)' } };

  return (
    <Box>
      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {statCards.map(c => (
          <Grid size={{ xs: 6, sm: 4, md: 2 }} key={c.label}>
            <Card sx={cardSx}>
              <CardContent sx={{ textAlign: 'center', py: 2.5, px: 1.5 }}>
                <Box sx={{ width: 44, height: 44, mx: 'auto', mb: 1, borderRadius: 2.5, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: c.bg }}>
                  {React.cloneElement(c.icon, { sx: { color: c.color, fontSize: 22 } })}
                </Box>
                <Typography variant="h5" sx={{ color: c.color, fontWeight: 800 }}>{c.value.toLocaleString()}</Typography>
                <Typography variant="caption" color="text.secondary" fontWeight={500}>{c.label}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Row 1: Departments Bar + Skill Pie */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="h6" fontWeight={700} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PeopleIcon sx={{ color: '#6C63FF', fontSize: 20 }} /> Department Overview
                </Typography>
                <IconButton size="small" onClick={loadData}><RefreshIcon fontSize="small" /></IconButton>
              </Box>
              <DeptBarChart data={departments} />
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 5 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <SchoolIcon sx={{ color: '#00CEC9', fontSize: 20 }} /> Top Skills Distribution
              </Typography>
              <SkillPieChart data={skills} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Row 2: Projects Area + Skill Radar */}
      <Grid container spacing={2} sx={{ mb: 2 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <WorkIcon sx={{ color: '#A78BFA', fontSize: 20 }} /> Project Status & Budget
              </Typography>
              <ProjectAreaChart data={projects} />
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AnalyticsIcon sx={{ color: '#FF6B6B', fontSize: 20 }} /> Skill Demand vs Supply
              </Typography>
              <SkillRadarChart data={skills} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Row 3: Collaboration + Skill Categories */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <HubIcon sx={{ color: '#54A0FF', fontSize: 20 }} /> Cross-Dept Collaboration
              </Typography>
              <CollaborationChart data={collab} />
            </CardContent>
          </Card>
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={cardSx}>
            <CardContent>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUpIcon sx={{ color: '#FDCB6E', fontSize: 20 }} /> Skill Categories
              </Typography>
              <SkillDistChart data={skillDist} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// ══════════════════════════════════════════════════════════════════
//  ADMIN USER MANAGEMENT
// ══════════════════════════════════════════════════════════════════
interface UserRecord { id: string; username: string; email: string; full_name: string; role: string; is_active: boolean; created_at: string; }

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState({ username: '', email: '', password: '', full_name: '', headline: '', role: 'user' });
  const [editOpen, setEditOpen] = useState(false);
  const [editUser, setEditUser] = useState('');
  const [editForm, setEditForm] = useState({ email: '', full_name: '', headline: '', role: 'user', password: '' });
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteUser, setDeleteUser] = useState('');
  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try { const res = await fetch('http://localhost:8000/api/auth/users', { headers }); if (res.ok) setUsers(await res.json()); } catch {}
    setLoading(false);
  }, []);
  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleCreate = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/auth/users', { method: 'POST', headers, body: JSON.stringify(createForm) });
      if (res.ok) { setSnackbar({ open: true, message: 'User created', severity: 'success' }); setCreateOpen(false); setCreateForm({ username: '', email: '', password: '', full_name: '', headline: '', role: 'user' }); fetchUsers(); }
      else { const err = await res.json(); setSnackbar({ open: true, message: err.detail || 'Failed', severity: 'error' }); }
    } catch { setSnackbar({ open: true, message: 'Network error', severity: 'error' }); }
  };
  const handleEdit = async () => {
    try {
      const body: any = {}; if (editForm.email) body.email = editForm.email; if (editForm.full_name) body.full_name = editForm.full_name; if (editForm.role) body.role = editForm.role; if (editForm.password) body.password = editForm.password;
      const res = await fetch(`http://localhost:8000/api/auth/users/${editUser}`, { method: 'PUT', headers, body: JSON.stringify(body) });
      if (res.ok) { setSnackbar({ open: true, message: 'Updated', severity: 'success' }); setEditOpen(false); fetchUsers(); }
      else { const err = await res.json(); setSnackbar({ open: true, message: err.detail || 'Failed', severity: 'error' }); }
    } catch { setSnackbar({ open: true, message: 'Network error', severity: 'error' }); }
  };
  const handleDelete = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/auth/users/${deleteUser}`, { method: 'DELETE', headers });
      if (res.ok) { setSnackbar({ open: true, message: 'Deleted', severity: 'success' }); setDeleteOpen(false); fetchUsers(); }
      else { const err = await res.json(); setSnackbar({ open: true, message: err.detail || 'Failed', severity: 'error' }); }
    } catch { setSnackbar({ open: true, message: 'Network error', severity: 'error' }); }
  };
  const roleColor = (r: string) => r === 'admin' ? '#FF6B6B' : r === 'manager' ? '#A78BFA' : '#00CEC9';

  return (
    <Box>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[{ l: 'Total', v: users.length, c: '#6C63FF' }, { l: 'Admins', v: users.filter(u => u.role === 'admin').length, c: '#FF6B6B' }, { l: 'Managers', v: users.filter(u => u.role === 'manager').length, c: '#A78BFA' }, { l: 'Users', v: users.filter(u => u.role === 'user').length, c: '#00CEC9' }].map(s => (
          <Grid size={{ xs: 6, sm: 3 }} key={s.l}><Card><CardContent sx={{ textAlign: 'center', py: 2.5 }}><Typography variant="h4" sx={{ color: s.c, fontWeight: 800 }}>{s.v}</Typography><Typography variant="caption" color="text.secondary">{s.l}</Typography></CardContent></Card></Grid>
        ))}
      </Grid>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)} sx={{ borderRadius: 2.5, textTransform: 'none', fontWeight: 700, background: 'linear-gradient(135deg, #6C63FF, #5A52D5)' }}>Create User</Button>
        <IconButton onClick={fetchUsers} disabled={loading} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}><RefreshIcon fontSize="small" /></IconButton>
      </Box>
      {loading ? <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}><CircularProgress /></Box> : (
        <TableContainer component={Paper} sx={{ borderRadius: 3 }}><Table>
          <TableHead><TableRow><TableCell sx={{ fontWeight: 700 }}>User</TableCell><TableCell sx={{ fontWeight: 700 }}>Email</TableCell><TableCell sx={{ fontWeight: 700 }}>Role</TableCell><TableCell sx={{ fontWeight: 700 }}>Status</TableCell><TableCell sx={{ fontWeight: 700 }} align="right">Actions</TableCell></TableRow></TableHead>
          <TableBody>{users.map(u => (
            <TableRow key={u.id} hover>
              <TableCell><Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}><Avatar sx={{ width: 32, height: 32, background: `linear-gradient(135deg, ${roleColor(u.role)}, ${roleColor(u.role)}AA)`, fontSize: 14, fontWeight: 700 }}>{u.full_name.charAt(0)}</Avatar><Box><Typography variant="body2" fontWeight={600}>{u.full_name}</Typography><Typography variant="caption" color="text.secondary">@{u.username}</Typography></Box></Box></TableCell>
              <TableCell>{u.email}</TableCell>
              <TableCell><Chip label={u.role} size="small" sx={{ bgcolor: `${roleColor(u.role)}15`, color: roleColor(u.role), fontWeight: 700, textTransform: 'capitalize' }} /></TableCell>
              <TableCell><Chip label={u.is_active ? 'Active' : 'Inactive'} size="small" sx={{ bgcolor: u.is_active ? 'rgba(46,213,115,0.12)' : 'rgba(255,71,87,0.12)', color: u.is_active ? '#2ED573' : '#FF4757', fontWeight: 600 }} /></TableCell>
              <TableCell align="right">
                <IconButton size="small" onClick={() => { setEditUser(u.username); setEditForm({ email: u.email, full_name: u.full_name, headline: '', role: u.role, password: '' }); setEditOpen(true); }} sx={{ color: '#6C63FF' }}><EditIcon fontSize="small" /></IconButton>
                <IconButton size="small" onClick={() => { setDeleteUser(u.username); setDeleteOpen(true); }} sx={{ color: '#FF6B6B' }} disabled={u.username === 'admin'}><DeleteIcon fontSize="small" /></IconButton>
              </TableCell>
            </TableRow>
          ))}</TableBody>
        </Table></TableContainer>
      )}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>Create User</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          <TextField label="Full Name" fullWidth size="small" value={createForm.full_name} onChange={e => setCreateForm({ ...createForm, full_name: e.target.value })} />
          <TextField label="Username" fullWidth size="small" value={createForm.username} onChange={e => setCreateForm({ ...createForm, username: e.target.value })} />
          <TextField label="Email" fullWidth size="small" value={createForm.email} onChange={e => setCreateForm({ ...createForm, email: e.target.value })} />
          <TextField label="Password" fullWidth size="small" type="password" value={createForm.password} onChange={e => setCreateForm({ ...createForm, password: e.target.value })} />
          <FormControl fullWidth size="small"><InputLabel>Role</InputLabel><Select value={createForm.role} label="Role" onChange={e => setCreateForm({ ...createForm, role: e.target.value })}><MenuItem value="user">User</MenuItem><MenuItem value="manager">Manager</MenuItem><MenuItem value="admin">Admin</MenuItem></Select></FormControl>
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}><Button onClick={() => setCreateOpen(false)}>Cancel</Button><Button variant="contained" onClick={handleCreate} sx={{ background: 'linear-gradient(135deg, #6C63FF, #5A52D5)', borderRadius: 2 }}>Create</Button></DialogActions>
      </Dialog>
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>Edit @{editUser}</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          <TextField label="Full Name" fullWidth size="small" value={editForm.full_name} onChange={e => setEditForm({ ...editForm, full_name: e.target.value })} />
          <TextField label="Email" fullWidth size="small" value={editForm.email} onChange={e => setEditForm({ ...editForm, email: e.target.value })} />
          <TextField label="New Password" fullWidth size="small" type="password" value={editForm.password} onChange={e => setEditForm({ ...editForm, password: e.target.value })} />
          <FormControl fullWidth size="small"><InputLabel>Role</InputLabel><Select value={editForm.role} label="Role" onChange={e => setEditForm({ ...editForm, role: e.target.value })}><MenuItem value="user">User</MenuItem><MenuItem value="manager">Manager</MenuItem><MenuItem value="admin">Admin</MenuItem></Select></FormControl>
        </DialogContent>
        <DialogActions sx={{ p: 2.5 }}><Button onClick={() => setEditOpen(false)}>Cancel</Button><Button variant="contained" onClick={handleEdit} sx={{ background: 'linear-gradient(135deg, #6C63FF, #5A52D5)', borderRadius: 2 }}>Save</Button></DialogActions>
      </Dialog>
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} PaperProps={{ sx: { borderRadius: 3 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>Delete User</DialogTitle>
        <DialogContent><Alert severity="warning">Delete <strong>@{deleteUser}</strong>? This cannot be undone.</Alert></DialogContent>
        <DialogActions sx={{ p: 2.5 }}><Button onClick={() => setDeleteOpen(false)}>Cancel</Button><Button variant="contained" color="error" onClick={handleDelete} sx={{ borderRadius: 2 }}>Delete</Button></DialogActions>
      </Dialog>
      <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        <Alert severity={snackbar.severity} variant="filled">{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

// ══════════════════════════════════════════════════════════════════
//  MAIN DASHBOARD
// ══════════════════════════════════════════════════════════════════
const Dashboard: React.FC = () => {
  const { isAdmin, fullName, username, role } = useAuth();
  const [tab, setTab] = useState(0);

  return (
    <Box sx={{ p: { xs: 2, md: 4 } }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Avatar sx={{ width: 52, height: 52, background: 'linear-gradient(135deg, #6C63FF, #A78BFA)', fontSize: 22, fontWeight: 800 }}>{(fullName || 'U').charAt(0)}</Avatar>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h4" fontWeight={800} sx={{ background: 'linear-gradient(135deg, #E8E8F0, #A78BFA)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {isAdmin ? 'Admin Dashboard' : `Welcome, ${fullName?.split(' ')[0] || 'User'}`}
            </Typography>
            <Chip label={role} size="small" sx={{ bgcolor: isAdmin ? 'rgba(255,107,107,0.12)' : 'rgba(0,206,201,0.12)', color: isAdmin ? '#FF6B6B' : '#00CEC9', fontWeight: 700, fontSize: '0.65rem', height: 22, textTransform: 'capitalize' }} />
          </Box>
          <Typography variant="body2" color="text.secondary">@{username} · Interactive analytics dashboard</Typography>
        </Box>
      </Box>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3, '& .MuiTabs-indicator': { background: 'linear-gradient(90deg, #6C63FF, #A78BFA)', height: 2 }, '& .MuiTab-root': { textTransform: 'none', fontWeight: 600, '&.Mui-selected': { color: '#A78BFA' } } }}>
        <Tab icon={<AnalyticsIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="Analytics" />
        {isAdmin && <Tab icon={<PeopleIcon sx={{ fontSize: 18 }} />} iconPosition="start" label="User Management" />}
      </Tabs>

      {tab === 0 && <AnalyticsOverview />}
      {tab === 1 && isAdmin && <UserManagement />}
    </Box>
  );
};

export default Dashboard;
