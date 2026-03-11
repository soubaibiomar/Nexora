import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  Box, Typography, Avatar, Badge, InputBase, Menu, MenuItem,
  Divider, ListItemIcon, ListItemText, Button, Popover,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import PeopleIcon from '@mui/icons-material/People';
import WorkIcon from '@mui/icons-material/Work';
import ChatIcon from '@mui/icons-material/Chat';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import TimelineIcon from '@mui/icons-material/Timeline';
import MapIcon from '@mui/icons-material/Map';
import BubbleChartIcon from '@mui/icons-material/BubbleChart';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import SchoolIcon from '@mui/icons-material/School';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import LoginIcon from '@mui/icons-material/Login';
import AppsIcon from '@mui/icons-material/Apps';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import { createAppTheme } from './theme/theme';

// Pages
import Feed from './pages/Feed';
import Profile from './pages/Profile';
import MyNetwork from './pages/MyNetwork';
import Jobs from './pages/Jobs';
import Messaging from './pages/Messaging';
import Notifications from './pages/Notifications';
import SkillMap from './pages/SkillMap';
import TeamBuilder from './pages/TeamBuilder';
import GraphVisualization from './pages/GraphVisualization';
import LearningPath from './pages/LearningPath';
import Dashboard from './pages/Dashboard';
import AIInsights from './pages/AIInsights';
import Login from './pages/Login';
import Register from './pages/Register';
import TeamWorkspace from './pages/TeamWorkspace';
import SkillEvolution from './pages/SkillEvolution';
import AIChatbot from './components/AIChatbot';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// ── Theme Mode Context ─────────────────────────────────────────────
type ThemeMode = 'dark' | 'light';
const ThemeModeContext = createContext<{
  mode: ThemeMode;
  toggleMode: () => void;
}>({ mode: 'dark', toggleMode: () => { } });

export const useThemeMode = () => useContext(ThemeModeContext);

// Auth helper — now provided by AuthContext (see contexts/AuthContext.tsx)

const NAVBAR_HEIGHT = 56;

// ── Top Navigation Bar ─────────────────────────────────────────────
function TopNavBar() {
  const { isAuthenticated, username, fullName, logout } = useAuth();
  const location = useLocation();
  const { mode, toggleMode } = useThemeMode();
  const [profileMenu, setProfileMenu] = useState<null | HTMLElement>(null);
  const [moreMenu, setMoreMenu] = useState<null | HTMLElement>(null);
  const [badges, setBadges] = useState<{ messaging: number; notifications: number }>({
    messaging: 0,
    notifications: 0,
  });

  useEffect(() => {
    const fetchBadges = async () => {
      try {
        const [msgRes, notifRes] = await Promise.all([
          fetch('http://localhost:8000/api/messaging/conversations').then((r) => r.json()),
          fetch('http://localhost:8000/api/notifications?unread_only=true').then((r) => r.json()),
        ]);
        const msgUnread = (msgRes.conversations || []).reduce(
          (sum: number, c: any) => sum + (c.unread || 0),
          0
        );
        const notifs = notifRes.notifications || [];
        const notifUnread = notifRes.unread_count ?? notifs.filter((n: any) => !n.read).length;
        setBadges({ messaging: msgUnread, notifications: notifUnread });
      } catch {
        /* ignore */
      }
    };
    fetchBadges();
    const interval = setInterval(fetchBadges, 30000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { label: 'Home', icon: <HomeIcon />, path: '/' },
    { label: 'My Network', icon: <PeopleIcon />, path: '/network' },
    { label: 'Jobs', icon: <WorkIcon />, path: '/jobs' },
    { label: 'Messaging', icon: <ChatIcon />, path: '/messaging', badgeKey: 'messaging' },
    { label: 'Notifications', icon: <NotificationsIcon />, path: '/notifications', badgeKey: 'notifications' },
  ];

  const moreItems = [
    { label: 'Skill Map', icon: <MapIcon />, path: '/skill-map' },
    { label: 'Team Builder', icon: <GroupWorkIcon />, path: '/team-builder' },
    { label: 'Graph Explorer', icon: <BubbleChartIcon />, path: '/graph' },
    { label: 'Learning Paths', icon: <SchoolIcon />, path: '/learning' },
    { label: 'AI Insights', icon: <AutoAwesomeIcon />, path: '/ai-insights' },
    { label: 'Skill Evolution', icon: <TimelineIcon />, path: '/skill-evolution' },
    { label: 'Workspaces', icon: <GroupWorkIcon />, path: '/workspaces' },
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  ];

  const isMoreActive = moreItems.some((item) => location.pathname === item.path);

  const NavIcon = ({ item }: { item: { label: string; icon: React.ReactElement; path: string; badgeKey?: string } }) => {
    const isActive = location.pathname === item.path;
    const badgeCount = item.badgeKey ? badges[item.badgeKey as keyof typeof badges] : 0;

    return (
      <Box
        component={Link}
        to={item.path}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textDecoration: 'none',
          px: { xs: 1, md: 2 },
          height: NAVBAR_HEIGHT,
          position: 'relative',
          color: isActive ? 'primary.main' : 'text.secondary',
          transition: 'color 0.2s',
          '&:hover': {
            color: isActive ? 'primary.main' : 'text.primary',
          },
          '&::after': isActive ? {
            content: '""',
            position: 'absolute',
            bottom: 0,
            left: '15%',
            right: '15%',
            height: 2,
            borderRadius: '2px 2px 0 0',
            background: 'linear-gradient(90deg, #6C63FF, #8B83FF)',
          } : {},
        }}
      >
        <Badge
          badgeContent={badgeCount}
          color="error"
          sx={{
            '& .MuiBadge-badge': {
              fontSize: '0.55rem',
              minWidth: 15,
              height: 15,
              top: 2,
              right: -2,
              background: '#FF4757',
              border: '2px solid',
              borderColor: mode === 'dark' ? '#141428' : '#fff',
            },
          }}
        >
          {React.cloneElement(item.icon as React.ReactElement<any>, {
            sx: { fontSize: 21 },
          })}
        </Badge>
        <Typography
          variant="caption"
          sx={{
            fontSize: '0.58rem',
            fontWeight: isActive ? 600 : 400,
            mt: 0.3,
            whiteSpace: 'nowrap',
            letterSpacing: '0.01em',
          }}
        >
          {item.label}
        </Typography>
      </Box>
    );
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1200,
        height: NAVBAR_HEIGHT,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: { xs: 1.5, md: 3 },
        background: mode === 'dark'
          ? 'linear-gradient(180deg, rgba(20,20,40,0.97) 0%, rgba(20,20,40,0.92) 100%)'
          : 'linear-gradient(180deg, rgba(255,255,255,0.97) 0%, rgba(255,255,255,0.92) 100%)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid',
        borderColor: mode === 'dark' ? 'rgba(108,99,255,0.08)' : 'rgba(0,0,0,0.06)',
        boxShadow: mode === 'dark'
          ? '0 4px 30px rgba(0,0,0,0.3)'
          : '0 1px 8px rgba(0,0,0,0.06)',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          maxWidth: 1200,
        }}
      >
        {/* ── Logo + Search ── */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mr: 'auto' }}>
          <Box
            component={Link}
            to="/"
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              textDecoration: 'none',
              flexShrink: 0,
            }}
          >
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 14px rgba(108,99,255,0.35)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 6px 20px rgba(108,99,255,0.45)',
                },
              }}
            >
              <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: '1.15rem', lineHeight: 1 }}>N</Typography>
            </Box>
            <Typography
              sx={{
                color: 'text.primary',
                fontWeight: 700,
                fontSize: '1.15rem',
                display: { xs: 'none', md: 'block' },
                letterSpacing: '-0.03em',
                background: 'linear-gradient(135deg, #E8E8F0, #A78BFA)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Nexora
            </Typography>
          </Box>

          {/* Search */}
          <Box
            sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              borderRadius: 2,
              bgcolor: mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
              border: '1px solid',
              borderColor: mode === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
              px: 1.5,
              py: 0.6,
              minWidth: 220,
              transition: 'all 0.2s',
              '&:focus-within': {
                borderColor: 'primary.main',
                bgcolor: mode === 'dark' ? 'rgba(108,99,255,0.06)' : 'rgba(108,99,255,0.04)',
                boxShadow: '0 0 0 3px rgba(108,99,255,0.1)',
              },
            }}
          >
            <SearchIcon sx={{ fontSize: 18, color: 'text.secondary', mr: 1 }} />
            <InputBase
              placeholder="Search..."
              sx={{
                fontSize: '0.82rem',
                color: 'text.primary',
                flex: 1,
                '& input::placeholder': { color: 'text.secondary', opacity: 0.8 },
              }}
            />
          </Box>
        </Box>

        {/* ── Nav Icons ── */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {navItems.map((item) => (
            <NavIcon key={item.path} item={item} />
          ))}

          {/* More dropdown */}
          <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1.5, opacity: 0.3 }} />
          <Box
            onClick={(e: React.MouseEvent<HTMLElement>) => setMoreMenu(e.currentTarget)}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              px: { xs: 1, md: 1.5 },
              height: NAVBAR_HEIGHT,
              cursor: 'pointer',
              color: isMoreActive ? 'primary.main' : 'text.secondary',
              position: 'relative',
              transition: 'color 0.2s',
              '&:hover': { color: isMoreActive ? 'primary.main' : 'text.primary' },
              '&::after': isMoreActive ? {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: '15%',
                right: '15%',
                height: 2,
                borderRadius: '2px 2px 0 0',
                background: 'linear-gradient(90deg, #6C63FF, #8B83FF)',
              } : {},
            }}
          >
            <AppsIcon sx={{ fontSize: 21 }} />
            <Typography variant="caption" sx={{ fontSize: '0.58rem', mt: 0.3 }}>
              More
            </Typography>
          </Box>
          <Popover
            anchorEl={moreMenu}
            open={Boolean(moreMenu)}
            onClose={() => setMoreMenu(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
            transformOrigin={{ vertical: 'top', horizontal: 'center' }}
            slotProps={{
              paper: {
                sx: {
                  mt: 1,
                  borderRadius: 3,
                  minWidth: 220,
                  bgcolor: mode === 'dark' ? '#1C1C36' : '#fff',
                  border: '1px solid',
                  borderColor: mode === 'dark' ? 'rgba(108,99,255,0.12)' : 'rgba(0,0,0,0.08)',
                  boxShadow: mode === 'dark'
                    ? '0 12px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(108,99,255,0.08)'
                    : '0 8px 30px rgba(0,0,0,0.1)',
                  overflow: 'hidden',
                },
              },
            }}
          >
            <Box sx={{ p: 1 }}>
              <Typography variant="caption" sx={{ px: 1.5, py: 0.5, display: 'block', color: 'text.secondary', fontWeight: 600, fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Explore
              </Typography>
              {moreItems.map((item) => {
                const isActive = location.pathname === item.path;
                return (
                  <MenuItem
                    key={item.path}
                    component={Link}
                    to={item.path}
                    onClick={() => setMoreMenu(null)}
                    sx={{
                      gap: 1.5,
                      py: 1,
                      px: 1.5,
                      borderRadius: 2,
                      mb: 0.3,
                      color: isActive ? 'primary.main' : 'text.primary',
                      bgcolor: isActive
                        ? (mode === 'dark' ? 'rgba(108,99,255,0.1)' : 'rgba(108,99,255,0.06)')
                        : 'transparent',
                      '&:hover': {
                        bgcolor: mode === 'dark' ? 'rgba(108,99,255,0.08)' : 'rgba(108,99,255,0.04)',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 'unset', color: isActive ? 'primary.main' : 'text.secondary' }}>
                      {React.cloneElement(item.icon as React.ReactElement<any>, { sx: { fontSize: 20 } })}
                    </ListItemIcon>
                    <ListItemText primaryTypographyProps={{ fontSize: '0.85rem', fontWeight: isActive ? 600 : 400 }}>
                      {item.label}
                    </ListItemText>
                  </MenuItem>
                );
              })}
            </Box>
          </Popover>

          {/* ── Me (profile) ── */}
          <Box
            onClick={(e: React.MouseEvent<HTMLElement>) => setProfileMenu(e.currentTarget)}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              px: { xs: 1, md: 1.5 },
              height: NAVBAR_HEIGHT,
              cursor: 'pointer',
              color: profileMenu ? 'text.primary' : 'text.secondary',
              transition: 'color 0.2s',
              '&:hover': { color: 'text.primary' },
            }}
          >
            <Avatar
              sx={{
                width: 26,
                height: 26,
                bgcolor: 'transparent',
                background: 'linear-gradient(135deg, #6C63FF, #A78BFA)',
                fontSize: 12,
                fontWeight: 700,
                border: '2px solid',
                borderColor: profileMenu ? '#A78BFA' : 'transparent',
                transition: 'border-color 0.2s',
              }}
            >
              {(fullName || 'U').charAt(0)}
            </Avatar>
            <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.1 }}>
              <Typography variant="caption" sx={{ fontSize: '0.58rem' }}>
                Me
              </Typography>
              <ArrowDropDownIcon sx={{ fontSize: 14, ml: -0.3 }} />
            </Box>
          </Box>
          <Menu
            anchorEl={profileMenu}
            open={Boolean(profileMenu)}
            onClose={() => setProfileMenu(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            slotProps={{
              paper: {
                sx: {
                  mt: 1,
                  borderRadius: 3,
                  minWidth: 260,
                  bgcolor: mode === 'dark' ? '#1C1C36' : '#fff',
                  border: '1px solid',
                  borderColor: mode === 'dark' ? 'rgba(108,99,255,0.12)' : 'rgba(0,0,0,0.08)',
                  boxShadow: mode === 'dark'
                    ? '0 12px 40px rgba(0,0,0,0.5)'
                    : '0 8px 30px rgba(0,0,0,0.1)',
                  overflow: 'hidden',
                },
              },
            }}
          >
            <Box sx={{ px: 2.5, py: 2, display: 'flex', gap: 1.5, alignItems: 'center' }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  background: 'linear-gradient(135deg, #6C63FF, #A78BFA)',
                  fontSize: 20,
                  fontWeight: 700,
                }}
              >
                {(fullName || 'U').charAt(0)}
              </Avatar>
              <Box>
                <Typography variant="body2" fontWeight={600}>
                  {fullName || 'User'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  @{username || 'user'}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ px: 2, pb: 1.5 }}>
              <Button
                component={Link}
                to="/profile"
                fullWidth
                variant="outlined"
                size="small"
                onClick={() => setProfileMenu(null)}
                sx={{
                  borderRadius: 6,
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  textTransform: 'none',
                  borderColor: 'primary.main',
                  color: 'primary.main',
                  py: 0.5,
                  '&:hover': {
                    bgcolor: 'rgba(108,99,255,0.08)',
                    borderColor: '#8B83FF',
                  },
                }}
              >
                View Profile
              </Button>
            </Box>
            <Divider sx={{ opacity: 0.15 }} />
            <Box sx={{ p: 1 }}>
              <MenuItem onClick={() => { toggleMode(); setProfileMenu(null); }}
                sx={{ borderRadius: 2, gap: 1.5, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 'unset' }}>
                  {mode === 'dark' ? <LightModeIcon fontSize="small" sx={{ color: '#FDCB6E' }} /> : <DarkModeIcon fontSize="small" />}
                </ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>
                  {mode === 'dark' ? 'Light Mode' : 'Dark Mode'}
                </ListItemText>
              </MenuItem>
              <MenuItem component={Link} to="/profile" onClick={() => setProfileMenu(null)}
                sx={{ borderRadius: 2, gap: 1.5, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 'unset' }}><PersonIcon fontSize="small" /></ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>My Profile</ListItemText>
              </MenuItem>
              <MenuItem component={Link} to="/dashboard" onClick={() => setProfileMenu(null)}
                sx={{ borderRadius: 2, gap: 1.5, py: 1 }}>
                <ListItemIcon sx={{ minWidth: 'unset' }}><DashboardIcon fontSize="small" /></ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>Analytics</ListItemText>
              </MenuItem>
            </Box>
            <Divider sx={{ opacity: 0.15 }} />
            <Box sx={{ p: 1 }}>
              {isAuthenticated ? (
                <MenuItem onClick={() => { logout(); window.location.reload(); }}
                  sx={{ borderRadius: 2, gap: 1.5, py: 1 }}>
                  <ListItemIcon sx={{ minWidth: 'unset' }}><LogoutIcon fontSize="small" sx={{ color: '#FF4757' }} /></ListItemIcon>
                  <ListItemText primaryTypographyProps={{ fontSize: '0.85rem', color: '#FF4757' }}>
                    Sign Out
                  </ListItemText>
                </MenuItem>
              ) : (
                <MenuItem component={Link} to="/login" onClick={() => setProfileMenu(null)}
                  sx={{ borderRadius: 2, gap: 1.5, py: 1 }}>
                  <ListItemIcon sx={{ minWidth: 'unset' }}><LoginIcon fontSize="small" /></ListItemIcon>
                  <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>Sign In</ListItemText>
                </MenuItem>
              )}
            </Box>
          </Menu>
        </Box>
      </Box>
    </Box>
  );
}

// ── App Content (needs AuthContext) ────────────────────────────────
const AppContent: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      {isAuthenticated ? (
        <Box sx={{ minHeight: '100vh' }}>
          <TopNavBar />
          <Box
            component="main"
            sx={{
              mt: `${NAVBAR_HEIGHT}px`,
              minHeight: `calc(100vh - ${NAVBAR_HEIGHT}px)`,
              bgcolor: 'background.default',
            }}
          >
            <Routes>
              <Route path="/" element={<Feed />} />
              <Route path="/network" element={<MyNetwork />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/messaging" element={<Messaging />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/skill-map" element={<SkillMap />} />
              <Route path="/team-builder" element={<TeamBuilder />} />
              <Route path="/graph" element={<GraphVisualization />} />
              <Route path="/learning" element={<LearningPath />} />
              <Route path="/ai-insights" element={<AIInsights />} />
              <Route path="/skill-evolution" element={<SkillEvolution />} />
              <Route path="/workspaces" element={<TeamWorkspace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/login" element={<Navigate to="/" replace />} />
              <Route path="/register" element={<Navigate to="/" replace />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Box>
          <AIChatbot />
        </Box>
      ) : (
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      )}
    </BrowserRouter>
  );
};

// ── App Component ──────────────────────────────────────────────────
const App: React.FC = () => {
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    return (localStorage.getItem('nexora-theme') as ThemeMode) || 'dark';
  });

  const theme = useMemo(() => createAppTheme(themeMode), [themeMode]);

  const toggleMode = () => {
    setThemeMode((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('nexora-theme', next);
      return next;
    });
  };

  return (
    <AuthProvider>
      <ThemeModeContext.Provider value={{ mode: themeMode, toggleMode }}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AppContent />
        </ThemeProvider>
      </ThemeModeContext.Provider>
    </AuthProvider>
  );
};

export default App;

