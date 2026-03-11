import { createTheme } from '@mui/material/styles';
import type { Theme } from '@mui/material/styles';

const darkPalette = {
    mode: 'dark' as const,
    primary: {
        main: '#6C63FF',
        light: '#8B83FF',
        dark: '#5A52D5',
        contrastText: '#fff',
    },
    secondary: {
        main: '#00CEC9',
        light: '#55EFC4',
        dark: '#00B5B0',
    },
    error: {
        main: '#FF6B6B',
    },
    warning: {
        main: '#FDCB6E',
    },
    info: {
        main: '#74B9FF',
    },
    success: {
        main: '#00B894',
    },
    background: {
        default: '#0A0A1A',
        paper: '#141428',
    },
    text: {
        primary: '#E8E8F0',
        secondary: '#8E8EA0',
    },
};

const lightPalette = {
    mode: 'light' as const,
    primary: {
        main: '#6C63FF',
        light: '#8B83FF',
        dark: '#5A52D5',
        contrastText: '#fff',
    },
    secondary: {
        main: '#00CEC9',
        light: '#55EFC4',
        dark: '#00B5B0',
    },
    background: {
        default: '#F5F5FA',
        paper: '#FFFFFF',
    },
    text: {
        primary: '#1A1A2E',
        secondary: '#6B6B80',
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
