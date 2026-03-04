import { createTheme } from '@mui/material/styles';
import type { Theme } from '@mui/material/styles';

const darkPalette = {
    mode: 'dark' as const,
    primary: {
        main: '#f97316',
        light: '#fb923c',
        dark: '#ea580c',
        contrastText: '#fff',
    },
    secondary: {
        main: '#f59e0b',
        light: '#fbbf24',
        dark: '#d97706',
    },
    error: {
        main: '#ef4444',
    },
    warning: {
        main: '#f59e0b',
    },
    info: {
        main: '#06b6d4',
    },
    success: {
        main: '#10b981',
    },
    background: {
        default: '#0f0f0f',
        paper: '#1a1a1a',
    },
    text: {
        primary: '#f5f5f5',
        secondary: '#a3a3a3',
    },
};

const lightPalette = {
    mode: 'light' as const,
    primary: {
        main: '#f97316',
        light: '#fb923c',
        dark: '#ea580c',
        contrastText: '#fff',
    },
    secondary: {
        main: '#f59e0b',
        light: '#fbbf24',
        dark: '#d97706',
    },
    background: {
        default: '#fafaf9',
        paper: '#ffffff',
    },
};

export const createAppTheme = (mode: 'dark' | 'light'): Theme => {
    return createTheme({
        palette: mode === 'dark' ? darkPalette : lightPalette,
        shape: {
            borderRadius: 12,
        },
        typography: {
            fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        },
    });
};

export default createAppTheme('dark');
