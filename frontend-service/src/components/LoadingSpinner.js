import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const LoadingContainer = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
`;

const Spinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const Logo = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.md};
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingText = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 1rem;
  animation: ${pulse} 2s ease-in-out infinite;
`;

const LoadingSpinner = () => {
  return (
    <LoadingContainer>
      <Logo>🏎️ RaceMetrics</Logo>
      <Spinner />
      <LoadingText>Loading F1 Analytics...</LoadingText>
    </LoadingContainer>
  );
};

export default LoadingSpinner;
