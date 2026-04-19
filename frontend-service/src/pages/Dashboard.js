import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useData } from '../contexts/DataContext';
import { useAuth } from '../contexts/AuthContext';
import { BarChart3, Trophy, Users, Car, TrendingUp, Calendar } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';

const DashboardContainer = styled.div`
  padding: ${props => props.theme.spacing.xl};
  max-width: 1400px;
  margin: 0 auto;
`;

const WelcomeSection = styled.div`
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const WelcomeTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  background: ${props => props.theme.colors.gradient};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: ${props => props.theme.spacing.md};
`;

const WelcomeSubtitle = styled.p`
  font-size: 1.125rem;
  color: ${props => props.theme.colors.textSecondary};
  max-width: 600px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const StatCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.lg};
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.lg};
    border-color: ${props => props.theme.colors.primary};
  }
`;

const StatIcon = styled.div`
  width: 60px;
  height: 60px;
  border-radius: ${props => props.theme.borderRadius.lg};
  background: ${props => props.theme.colors.gradient};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 2rem;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const StatLabel = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xxl};
`;

const ChartCard = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
`;

const ChartTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ChartContainer = styled.div`
  height: 300px;
  width: 100%;
`;

const RecentActivity = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
`;

const ActivityTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  padding: ${props => props.theme.spacing.md};
  border-radius: ${props => props.theme.borderRadius.md};
  margin-bottom: ${props => props.theme.spacing.sm};
  transition: all 0.2s ease;

  &:hover {
    background: rgba(59, 130, 246, 0.1);
  }

  &:last-child {
    margin-bottom: 0;
  }
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: ${props => props.theme.borderRadius.md};
  background: rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.theme.colors.primary};
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityText = styled.div`
  color: ${props => props.theme.colors.text};
  font-weight: 500;
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const ActivityTime = styled.div`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

const Dashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const { 
    fetchDrivers, 
    fetchConstructors, 
    fetchRaces, 
    loading, 
    setLoading 
  } = useData();
  
  const [dashboardData, setDashboardData] = useState({
    drivers: [],
    constructors: [],
    races: []
  });

  const [counts, setCounts] = useState({
    driversCount: 0,
    constructorsCount: 0,
    racesCount: 0
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [driversData, constructorsData, racesData] = await Promise.all([
          fetchDrivers({ limit: 50 }),
          fetchConstructors({ limit: 50 }),
          fetchRaces({ limit: 50 })
        ]);

        setDashboardData({
          drivers: driversData.drivers || [],
          constructors: constructorsData.constructors || [],
          races: racesData.races || []
        });

        setCounts({
          driversCount: driversData.drivers.length || 0,
          constructorsCount: constructorsData.constructors.length || 0,
          racesCount: racesData.races.length || 0
        });
      } catch (error) {
        console.error('Error loading dashboard data:', error);
      }
    };

    loadDashboardData();
  }, []); // Empty dependency array to prevent infinite re-renders

  if (loading) {
    return <LoadingSpinner />;
  }

  const currentYear = new Date().getFullYear();

  return (
    <DashboardContainer>
      <WelcomeSection>
        <WelcomeTitle>
          Welcome{isAuthenticated && user ? `, ${user.username}` : ''} to RaceMetrics
        </WelcomeTitle>
        <WelcomeSubtitle>
          Your comprehensive Formula 1 data analytics platform. Explore driver statistics, 
          constructor performance, race results, and advanced analytics.
        </WelcomeSubtitle>
      </WelcomeSection>

      <StatsGrid>
        <StatCard>
          <StatIcon>
            <Trophy />
          </StatIcon>
          <StatContent>
            <StatValue>{20}</StatValue>
            <StatLabel>Active Drivers</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>
            <Car />
          </StatIcon>
          <StatContent>
            <StatValue>{10}</StatValue>
            <StatLabel>Constructors</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>
            <Calendar />
          </StatIcon>
          <StatContent>
            <StatValue>{currentYear}</StatValue>
            <StatLabel>Current Season</StatLabel>
          </StatContent>
        </StatCard>

        <StatCard>
          <StatIcon>
            <TrendingUp />
          </StatIcon>
          <StatContent>
            <StatValue>{11}</StatValue>
            <StatLabel>Fastest Laps</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>
            <Trophy />
            Top Drivers by Points
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dashboardData.drivers.slice(0, 10).map(driver => ({
                name: driver.givenName || driver.fullName || 'Unknown',
                value: 1
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis 
                  dataKey="name" 
                  stroke="#cbd5e1"
                  fontSize={12}
                />
                <YAxis stroke="#cbd5e1" fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#f8fafc'
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <Car />
            Constructor Performance
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={dashboardData.constructors.slice(0, 5).map(constructor => ({
                    name: constructor.name || 'Unknown',
                    value: 1
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name }) => name}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {dashboardData.constructors.slice(0, 5).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#f8fafc'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <TrendingUp />
            Podium Frequency
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dashboardData.races.slice(0, 8).map(race => ({
                name: race.sessionName || race.raceName || 'Unknown',
                value: 1
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis 
                  dataKey="name" 
                  stroke="#cbd5e1"
                  fontSize={10}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#cbd5e1" fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: '8px',
                    color: '#f8fafc'
                  }}
                />
                <Bar dataKey="value" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>
      </ChartsGrid>

      <RecentActivity>
        <ActivityTitle>
          <BarChart3 />
          Recent Activity
        </ActivityTitle>
        
        {dashboardData.races.slice(0, 1).map((race, index) => (
          <ActivityItem key={race._id || index}>
            <ActivityIcon>
              <Trophy />
            </ActivityIcon>
            <ActivityContent>
              <ActivityText>
                Latest Session: {race.sessionName || race.raceName || 'Unknown'}
              </ActivityText>
              <ActivityTime>
                {race.location || 'Location TBD'} • {race.year || currentYear}
              </ActivityTime>
            </ActivityContent>
          </ActivityItem>
        ))}

        {dashboardData.drivers.slice(0, 3).map((driver, index) => (
          <ActivityItem key={driver._id || index}>
            <ActivityIcon>
              <Users />
            </ActivityIcon>
            <ActivityContent>
              <ActivityText>
                {driver.fullName || `${driver.givenName} ${driver.familyName}`} - {driver.teamName || 'Team TBD'}
              </ActivityText>
              <ActivityTime>
                Driver #{driver.driver_number || 'N/A'} • {driver.nationality || 'Nationality TBD'}
              </ActivityTime>
            </ActivityContent>
          </ActivityItem>
        ))}
      </RecentActivity>
    </DashboardContainer>
  );
};

export default Dashboard;
