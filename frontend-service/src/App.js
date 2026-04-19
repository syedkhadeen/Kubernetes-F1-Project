import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { AuthProvider } from './contexts/AuthContext';
import { DataProvider } from './contexts/DataContext';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Drivers from './pages/Drivers';
import Constructors from './pages/Constructors';
import Races from './pages/Races';
import Stats from './pages/Stats';
import Login from './pages/Login';
import Register from './pages/Register';
import LoadingSpinner from './components/LoadingSpinner';

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f8fafc;
    min-height: 100vh;
    overflow-x: hidden;
  }

  #root {
    min-height: 100vh;
  }
`;

const theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#0f172a',
    surface: '#1e293b',
    surfaceLight: '#334155',
    text: '#f8fafc',
    textSecondary: '#cbd5e1',
    border: '#475569',
    gradient: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
    gradientSecondary: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem',
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  },
};

const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  padding-top: 80px; /* Account for fixed navbar */
`;

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <GlobalStyle />
        <LoadingSpinner />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AuthProvider>
        <DataProvider>
          <Router>
            <AppContainer>
              <Navbar />
              <MainContent>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/drivers" element={<Drivers />} />
                  <Route path="/drivers/:id" element={<Drivers />} />
                  <Route path="/constructors" element={<Constructors />} />
                  <Route path="/constructors/:id" element={<Constructors />} />
                  <Route path="/races" element={<Races />} />
                  <Route path="/races/:season/:round" element={<Races />} />
                  <Route path="/stats" element={<Stats />} />
                </Routes>
              </MainContent>
            </AppContainer>
          </Router>
        </DataProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
