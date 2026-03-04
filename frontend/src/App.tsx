import React, { useState, useEffect, useMemo, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  Box, Typography, IconButton, Avatar, Badge, InputBase, Menu, MenuItem,
  Divider, ListItemIcon, ListItemText, Tooltip, Button, Popover,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HomeIcon from '@mui/icons-material/Home';
import PeopleIcon from '@mui/icons-material/People';
import WorkIcon from '@mui/icons-material/Work';
import ChatIcon from '@mui/icons-material/Chat';
import NotificationsIcon from '@mui/icons-material/Notifications';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
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
import AIChatbot from './components/AIChatbot';

// ── Theme Mode Context ─────────────────────────────────────────────
type ThemeMode = 'dark' | 'light';
const ThemeModeContext = createContext<{
  mode: ThemeMode;
  toggleMode: () => void;
}>({ mode: 'dark', toggleMode: () => { } });

export const useThemeMode = () => useContext(ThemeModeContext);

// Auth helper
const authService = {
  isAuthenticated: () => !!localStorage.getItem('token'),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('fullName');
    localStorage.removeItem('email');
  },
  getUsername: () => localStorage.getItem('username') || 'User',
  getFullName: () => localStorage.getItem('fullName') || 'Current User',
};

const NAVBAR_HEIGHT = 52;

// ── Top Navigation Bar ─────────────────────────────────────────────
function TopNavBar() {
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
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  ];

  const NavIcon = ({ item }: { item: { label: string; icon: React.ReactElement; path: string; badgeKey?: string } }) => {
    const isActive = location.pathname === item.path;
    const badgeCount = item.badgeKey ? badges[item.badgeKey as keyof typeof badges] : 0;

    return (
      <Tooltip title={item.label} arrow>
        <Box
          component={Link}
          to={item.path}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textDecoration: 'none',
            px: 1.5,
            py: 0.5,
            minWidth: 60,
            color: isActive ? 'text.primary' : 'text.secondary',
            borderBottom: isActive ? '2px solid' : '2px solid transparent',
            borderColor: isActive ? 'text.primary' : 'transparent',
            transition: 'all 0.15s',
            '&:hover': {
              color: 'text.primary',
            },
          }}
        >
          <Badge
            badgeContent={badgeCount}
            color="error"
            sx={{
              '& .MuiBadge-badge': {
                fontSize: '0.6rem',
                minWidth: 16,
                height: 16,
                background: 'linear-gradient(135deg, #FF6B6B, #EE5A5A)',
              },
            }}
          >
            {React.cloneElement(item.icon as React.ReactElement<any>, {
              sx: { fontSize: 22 },
            })}
          </Badge>
          <Typography
            variant="caption"
            sx={{
              fontSize: '0.62rem',
              fontWeight: isActive ? 600 : 400,
              mt: 0.2,
              whiteSpace: 'nowrap',
            }}
          >
            {item.label}
          </Typography>
        </Box>
      </Tooltip>
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
        px: 2,
        background: mode === 'dark'
          ? 'rgba(26,26,26,0.95)'
          : 'rgba(255,255,255,0.95)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid',
        borderColor: mode === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          maxWidth: 1128,
          gap: 1,
        }}
      >
        {/* Logo + Search */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mr: 'auto' }}>
          {/* LinkedIn-style "in" logo */}
          <Box
            component={Link}
            to="/"
            sx={{
              width: 34,
              height: 34,
              borderRadius: 1,
              background: '#0A66C2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              textDecoration: 'none',
              flexShrink: 0,
            }}
          >
            <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: '1.2rem', lineHeight: 1 }}>in</Typography>
          </Box>

          {/* Search */}
          <Box
            sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              borderRadius: 1,
              bgcolor: mode === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
              px: 1.5,
              py: 0.5,
              minWidth: 200,
            }}
          >
            <SearchIcon sx={{ fontSize: 18, color: 'text.secondary', mr: 1 }} />
            <InputBase
              placeholder="Search"
              sx={{
                fontSize: '0.82rem',
                color: 'text.primary',
                flex: 1,
                '& input::placeholder': { color: 'text.secondary', opacity: 1 },
              }}
            />
          </Box>
        </Box>

        {/* Nav Icons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0 }}>
          {navItems.map((item) => (
            <NavIcon key={item.path} item={item} />
          ))}

          {/* More dropdown */}
          <Box
            onClick={(e: React.MouseEvent<HTMLElement>) => setMoreMenu(e.currentTarget)}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              px: 1.5,
              py: 0.5,
              minWidth: 60,
              cursor: 'pointer',
              color: moreMenu ? 'text.primary' : 'text.secondary',
              borderBottom: '2px solid transparent',
              transition: 'all 0.15s',
              '&:hover': { color: 'text.primary' },
            }}
          >
            <AppsIcon sx={{ fontSize: 22 }} />
            <Typography variant="caption" sx={{ fontSize: '0.62rem', mt: 0.2 }}>
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
                  mt: 0.5,
                  borderRadius: 2,
                  minWidth: 200,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                },
              },
            }}
          >
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
                    py: 1.2,
                    color: isActive ? 'primary.main' : 'text.primary',
                    fontWeight: isActive ? 600 : 400,
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 'unset', color: isActive ? 'primary.main' : 'text.secondary' }}>
                    {React.cloneElement(item.icon as React.ReactElement<any>, { sx: { fontSize: 20 } })}
                  </ListItemIcon>
                  <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>
                    {item.label}
                  </ListItemText>
                </MenuItem>
              );
            })}
          </Popover>

          <Divider orientation="vertical" flexItem sx={{ mx: 0.5, my: 1 }} />

          {/* Me (profile avatar) */}
          <Box
            onClick={(e: React.MouseEvent<HTMLElement>) => setProfileMenu(e.currentTarget)}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              px: 1.5,
              py: 0.5,
              minWidth: 60,
              cursor: 'pointer',
              color: profileMenu ? 'text.primary' : 'text.secondary',
              borderBottom: '2px solid transparent',
              transition: 'all 0.15s',
              '&:hover': { color: 'text.primary' },
            }}
          >
            <Avatar
              sx={{
                width: 24,
                height: 24,
                bgcolor: 'primary.main',
                fontSize: 12,
                fontWeight: 700,
              }}
            >
              {authService.getFullName().charAt(0)}
            </Avatar>
            <Typography variant="caption" sx={{ fontSize: '0.62rem', mt: 0.2 }}>
              Me ▾
            </Typography>
          </Box>
          <Menu
            anchorEl={profileMenu}
            open={Boolean(profileMenu)}
            onClose={() => setProfileMenu(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <Box sx={{ px: 2, py: 1.5, display: 'flex', gap: 1.5, alignItems: 'center' }}>
              <Avatar sx={{ width: 48, height: 48, bgcolor: 'primary.main' }}>
                {authService.getFullName().charAt(0)}
              </Avatar>
              <Box>
                <Typography variant="body2" fontWeight={600}>
                  {authService.getFullName()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  @{authService.getUsername()}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ px: 2, pb: 1 }}>
              <Button
                component={Link}
                to="/profile"
                fullWidth
                variant="outlined"
                size="small"
                onClick={() => setProfileMenu(null)}
                sx={{ borderRadius: 5, fontSize: '0.75rem' }}
              >
                View Profile
              </Button>
            </Box>
            <Divider />
            <MenuItem onClick={toggleMode}>
              <ListItemIcon>
                {mode === 'dark' ? <LightModeIcon fontSize="small" /> : <DarkModeIcon fontSize="small" />}
              </ListItemIcon>
              <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>
                {mode === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </ListItemText>
            </MenuItem>
            <MenuItem component={Link} to="/profile" onClick={() => setProfileMenu(null)}>
              <ListItemIcon><PersonIcon fontSize="small" /></ListItemIcon>
              <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>My Profile</ListItemText>
            </MenuItem>
            <MenuItem component={Link} to="/dashboard" onClick={() => setProfileMenu(null)}>
              <ListItemIcon><DashboardIcon fontSize="small" /></ListItemIcon>
              <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>Analytics</ListItemText>
            </MenuItem>
            <Divider />
            {authService.isAuthenticated() ? (
              <MenuItem onClick={() => { authService.logout(); window.location.reload(); }}>
                <ListItemIcon><LogoutIcon fontSize="small" sx={{ color: '#FF6B6B' }} /></ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: '0.85rem', color: '#FF6B6B' }}>
                  Sign Out
                </ListItemText>
              </MenuItem>
            ) : (
              <MenuItem component={Link} to="/login" onClick={() => setProfileMenu(null)}>
                <ListItemIcon><LoginIcon fontSize="small" /></ListItemIcon>
                <ListItemText primaryTypographyProps={{ fontSize: '0.85rem' }}>Sign In</ListItemText>
              </MenuItem>
            )}
          </Menu>
        </Box>
      </Box>
    </Box>
  );
}

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

  const isAuthenticated = authService.isAuthenticated();

  return (
    <ThemeModeContext.Provider value={{ mode: themeMode, toggleMode }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
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
      </ThemeProvider>
    </ThemeModeContext.Provider>
  );
};

export default App;
