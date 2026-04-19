import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import { Menu, X, User, LogOut, BarChart3, Users, Car, Trophy } from 'lucide-react';

const NavbarContainer = styled.nav`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: 0 ${props => props.theme.spacing.lg};
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  text-decoration: none;
  color: ${props => props.theme.colors.text};
  font-size: 1.5rem;
  font-weight: 700;
  
  &:hover {
    color: ${props => props.theme.colors.primary};
  }
`;

const NavLinks = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xl};

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  text-decoration: none;
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  font-weight: 500;
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  transition: all 0.2s ease;

  &:hover {
    color: ${props => props.theme.colors.primary};
    background: rgba(59, 130, 246, 0.1);
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;

  @media (max-width: 768px) {
    display: none;
  }
`;

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  background: none;
  border: 1px solid ${props => props.theme.colors.border};
  color: ${props => props.theme.colors.textSecondary};
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;

  &:hover {
    color: ${props => props.theme.colors.error};
    border-color: ${props => props.theme.colors.error};
    background: rgba(239, 68, 68, 0.1);
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: ${props => props.theme.colors.text};
  cursor: pointer;
  padding: ${props => props.theme.spacing.sm};

  @media (max-width: 768px) {
    display: block;
  }
`;

const MobileMenu = styled.div`
  position: fixed;
  top: 80px;
  left: 0;
  right: 0;
  background: ${props => props.theme.colors.surface};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: ${props => props.theme.spacing.lg};
  transform: ${props => props.isOpen ? 'translateY(0)' : 'translateY(-100%)'};
  transition: transform 0.3s ease;
  z-index: 999;

  @media (min-width: 769px) {
    display: none;
  }
`;

const MobileNavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  text-decoration: none;
  color: ${props => props.active ? props.theme.colors.primary : props.theme.colors.textSecondary};
  font-weight: 500;
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.sm};
  transition: all 0.2s ease;

  &:hover {
    color: ${props => props.theme.colors.primary};
    background: rgba(59, 130, 246, 0.1);
  }

  &:last-child {
    margin-bottom: 0;
  }
`;

const AuthButtons = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const AuthButton = styled(Link)`
  padding: ${props => props.theme.spacing.sm} ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.md};
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  
  ${props => props.primary ? `
    background: ${props.theme.colors.gradient};
    color: white;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: ${props.theme.shadows.lg};
    }
  ` : `
    border: 1px solid ${props.theme.colors.border};
    color: ${props.theme.colors.text};
    
    &:hover {
      background: rgba(59, 130, 246, 0.1);
      border-color: ${props.theme.colors.primary};
      color: ${props.theme.colors.primary};
    }
  `}
`;

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: BarChart3 },
    { path: '/drivers', label: 'Drivers', icon: Users },
    { path: '/constructors', label: 'Constructors', icon: Car },
    { path: '/races', label: 'Races', icon: Trophy },
    { path: '/stats', label: 'Statistics', icon: BarChart3 },
  ];

  return (
    <>
      <NavbarContainer>
        <Logo to="/">
          🏎️ RaceMetrics
        </Logo>

        <NavLinks>
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              active={location.pathname === path}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </NavLinks>

        <UserSection>
          {isAuthenticated ? (
            <>
              <UserInfo>
                <User size={16} />
                {user?.username}
              </UserInfo>
              <LogoutButton onClick={handleLogout}>
                <LogOut size={16} />
                Logout
              </LogoutButton>
            </>
          ) : (
            <AuthButtons>
              <AuthButton to="/login">Login</AuthButton>
              <AuthButton to="/register" primary>Sign Up</AuthButton>
            </AuthButtons>
          )}

          <MobileMenuButton onClick={toggleMobileMenu}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </MobileMenuButton>
        </UserSection>
      </NavbarContainer>

      <MobileMenu isOpen={mobileMenuOpen}>
        {navItems.map(({ path, label, icon: Icon }) => (
          <MobileNavLink
            key={path}
            to={path}
            active={location.pathname === path}
            onClick={() => setMobileMenuOpen(false)}
          >
            <Icon size={18} />
            {label}
          </MobileNavLink>
        ))}
        
        {isAuthenticated ? (
          <MobileNavLink onClick={handleLogout} as="button" style={{ background: 'none', border: 'none', width: '100%', textAlign: 'left' }}>
            <LogOut size={18} />
            Logout
          </MobileNavLink>
        ) : (
          <>
            <MobileNavLink to="/login" onClick={() => setMobileMenuOpen(false)}>
              Login
            </MobileNavLink>
            <MobileNavLink to="/register" onClick={() => setMobileMenuOpen(false)}>
              Sign Up
            </MobileNavLink>
          </>
        )}
      </MobileMenu>
    </>
  );
};

export default Navbar;
