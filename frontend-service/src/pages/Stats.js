import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useData } from '../contexts/DataContext';
import { BarChart3, TrendingUp, Award, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import LoadingSpinner from '../components/LoadingSpinner';

const StatsContainer = styled.div`
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

const ChartsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
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
  height: 400px;
  width: 100%;
`;

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

const Stats = () => {
  const { 
    fetchFastestLaps, 
    fetchPodiumFrequency, 
    fetchConstructorPerformance,
    loading 
  } = useData();
  
  const [statsData, setStatsData] = useState({
    fastestLaps: [],
    podiumFrequency: [],
    constructorPerformance: []
  });

  useEffect(() => {
    const loadStatsData = async () => {
      try {
        const [fastestLapsData, podiumFrequencyData, constructorPerformanceData] = await Promise.all([
          fetchFastestLaps({ limit: 15 }),
          fetchPodiumFrequency({ limit: 15 }),
          fetchConstructorPerformance({ limit: 10 })
        ]);

        setStatsData({
          fastestLaps: fastestLapsData.fastest_laps || [],
          podiumFrequency: podiumFrequencyData.podium_frequency || [],
          constructorPerformance: constructorPerformanceData.constructor_performance || []
        });
      } catch (error) {
        console.error('Error loading stats data:', error);
      }
    };

    loadStatsData();
  }, [fetchFastestLaps, fetchPodiumFrequency, fetchConstructorPerformance]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <StatsContainer>
      <PageHeader>
        <PageTitle>
          <BarChart3 />
          Statistics
        </PageTitle>
      </PageHeader>

      <ChartsGrid>
        <ChartCard>
          <ChartTitle>
            <Zap />
            Fastest Laps
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statsData.fastestLaps.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis 
                  dataKey="driver.driver_id" 
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
                <Bar dataKey="fastest_lap.average_speed" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <Award />
            Podium Frequency
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statsData.podiumFrequency.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis 
                  dataKey="driver_name" 
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
                <Bar dataKey="podiums" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>

        <ChartCard>
          <ChartTitle>
            <TrendingUp />
            Constructor Performance
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statsData.constructorPerformance.slice(0, 8)}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ constructor_name, points }) => `${constructor_name}: ${points}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="points"
                >
                  {statsData.constructorPerformance.slice(0, 8).map((entry, index) => (
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
            <BarChart3 />
            Wins Distribution
          </ChartTitle>
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statsData.podiumFrequency.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                <XAxis 
                  dataKey="driver_name" 
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
                <Bar dataKey="wins" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        </ChartCard>
      </ChartsGrid>
    </StatsContainer>
  );
};

export default Stats;
