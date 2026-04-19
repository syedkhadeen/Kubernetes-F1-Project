import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useData } from '../contexts/DataContext';
import { Car, Search, Trophy, Flag } from 'lucide-react';
import LoadingSpinner from '../components/LoadingSpinner';

const ConstructorsContainer = styled.div`
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

const ConstructorsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${props => props.theme.spacing.lg};
`;

const ConstructorCard = styled.div`
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

const ConstructorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const ConstructorLogo = styled.div`
  width: 50px;
  height: 50px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: ${props => props.theme.colors.gradient};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.5rem;
`;

const ConstructorInfo = styled.div`
  flex: 1;
`;

const ConstructorName = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ConstructorNationality = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
`;

const ConstructorStats = styled.div`
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

const Constructors = () => {
  const { fetchConstructors, loading } = useData();
  const [constructors, setConstructors] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredConstructors, setFilteredConstructors] = useState([]);

  useEffect(() => {
    const loadConstructors = async () => {
      try {
        const data = await fetchConstructors({ limit: 50 });
        console.log('Constructors Data:', data);
        setConstructors(data.constructors || []);
        setFilteredConstructors(data.constructors || []);
      } catch (error) {
        console.error('Error loading constructors:', error);
      }
    };

    loadConstructors();
  }, []); // Empty dependency array to prevent infinite re-renders

  useEffect(() => {
    const filtered = constructors.filter(constructor =>
      constructor.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      constructor.nationality?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredConstructors(filtered);
  }, [searchQuery, constructors]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <ConstructorsContainer>
      <PageHeader>
        <PageTitle>
          <Car />
          Constructors
        </PageTitle>
        <SearchBar>
          <SearchIcon>
            <Search size={20} />
          </SearchIcon>
          <SearchInput
            type="text"
            placeholder="Search constructors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchBar>
      </PageHeader>

      <ConstructorsGrid>
        {filteredConstructors.map((constructor) => (
          <ConstructorCard key={constructor.constructor_id}>
            <ConstructorHeader>
              <ConstructorLogo>
                <Car />
              </ConstructorLogo>
              <ConstructorInfo>
                <ConstructorName>{constructor.name}</ConstructorName>
                <ConstructorNationality>
                  <Flag size={14} />
                  {constructor.nationality}
                </ConstructorNationality>
              </ConstructorInfo>
            </ConstructorHeader>
            
            <ConstructorStats>
              <StatItem>
                <StatValue>{constructor.nationality}</StatValue>
                <StatLabel>Country</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>Active</StatValue>
                <StatLabel>Status</StatLabel>
              </StatItem>
            </ConstructorStats>
          </ConstructorCard>
        ))}
      </ConstructorsGrid>
    </ConstructorsContainer>
  );
};

export default Constructors;
