import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useData } from '../contexts/DataContext';
import { Users, Search, Trophy, Flag } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const DriversContainer = styled.div`
  padding: ${props => props.theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
`;

const PageHeader = styled.div`
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const PageTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  background: ${props => props.theme.colors.gradient};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: ${props => props.theme.spacing.md};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const SearchBar = styled.div`
  position: relative;
  max-width: 400px;
  margin-bottom: ${props => props.theme.spacing.xl};
`;

const SearchInput = styled.input`
  width: 100%;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.md} ${props => props.theme.spacing.md} 3rem;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.text};
  font-size: 1rem;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: ${props => props.theme.spacing.md};
  top: 50%;
  transform: translateY(-50%);
  color: ${props => props.theme.colors.textSecondary};
`;

const DriversGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const DriverCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const DriverHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const DriverNumber = styled.div`
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.gradient};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.125rem;
`;

const DriverInfo = styled.div`
  flex: 1;
`;

const DriverName = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const DriverCode = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const DriverStats = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${props => props.theme.spacing.md};
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const StatLabel = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const Drivers = () => {
  const { fetchDrivers, loading } = useData();
  const [drivers, setDrivers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDrivers, setFilteredDrivers] = useState([]);

  useEffect(() => {
    const loadDrivers = async () => {
      try {
        const data = await fetchDrivers({ limit: 50 });
        setDrivers(data.drivers || []);
        setFilteredDrivers(data.drivers || []);
      } catch (error) {
        console.error('Error loading drivers:', error);
      }
    };

    loadDrivers();
  }, []); // Empty dependency array to prevent infinite re-renders

  useEffect(() => {
    const filtered = drivers.filter(driver =>
      driver.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      driver.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      driver.nationality?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredDrivers(filtered);
  }, [searchQuery, drivers]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <DriversContainer>
      <PageHeader>
        <PageTitle>
          <Users />
          Drivers
        </PageTitle>
        <SearchBar>
          <SearchIcon>
            <Search size={20} />
          </SearchIcon>
          <SearchInput
            type="text"
            placeholder="Search drivers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchBar>
      </PageHeader>

      <DriversGrid>
        {filteredDrivers.map((driver) => (
          <DriverCard key={driver.driver_id}>
            <DriverHeader>
              <DriverNumber>
                {driver.permanent_number || '?'}
              </DriverNumber>
              <DriverInfo>
                <DriverName>{driver.full_name}</DriverName>
                <DriverCode>{driver.code}</DriverCode>
              </DriverInfo>
            </DriverHeader>
            
            <DriverStats>
              <StatItem>
                <StatValue>{driver.nationality}</StatValue>
                <StatLabel>Nationality</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{driver.date_of_birth ? new Date(driver.date_of_birth).getFullYear() : 'N/A'}</StatValue>
                <StatLabel>Born</StatLabel>
              </StatItem>
            </DriverStats>
          </DriverCard>
        ))}
      </DriversGrid>
    </DriversContainer>
  );
};

export default Drivers;
