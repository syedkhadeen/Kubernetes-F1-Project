import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useData } from '../contexts/DataContext';
import { Trophy, Calendar, MapPin, Clock } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const RacesContainer = styled.div`
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

const RacesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const RaceCard = styled.div`
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

const RaceHeader = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const RaceName = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const RaceDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const CircuitInfo = styled.div`
  background: rgba(59, 130, 246, 0.1);
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.md};
`;

const CircuitName = styled.div`
  font-weight: 600;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const CircuitLocation = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const Races = () => {
  const { fetchRaces, loading } = useData();
  const [races, setRaces] = useState([]);

  useEffect(() => {
    const loadRaces = async () => {
      try {
        const data = await fetchRaces({ limit: 50 });
        console.log('Races Data:', data);
        setRaces(data.races || []);
      } catch (error) {
        console.error('Error loading races:', error);
      }
    };

    loadRaces();
  }, []); // Empty dependency array to prevent infinite re-renders

  if (loading) {
    return <LoadingSpinner />;
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'TBA';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <RacesContainer>
      <PageHeader>
        <PageTitle>
          <Trophy />
          Races
        </PageTitle>
      </PageHeader>

      <RacesGrid>
        {races.map((race) => (
          <RaceCard key={`${race.season}-${race.round}`}>
            <RaceHeader>
              <RaceName>{race.race_name}</RaceName>
              <RaceDetails>
                <DetailItem>
                  <Calendar size={16} />
                  Season {race.season} • Round {race.round}
                </DetailItem>
                <DetailItem>
                  <Clock size={16} />
                  {formatDate(race.date)}
                </DetailItem>
              </RaceDetails>
            </RaceHeader>
            
            {race.circuit && (
              <CircuitInfo>
                <CircuitName>{race.circuit.circuit_name}</CircuitName>
                <CircuitLocation>
                  <MapPin size={14} style={{ marginRight: '4px' }} />
                  {race.circuit.locality}, {race.circuit.country}
                </CircuitLocation>
              </CircuitInfo>
            )}
          </RaceCard>
        ))}
      </RacesGrid>
    </RacesContainer>
  );
};

export default Races;
