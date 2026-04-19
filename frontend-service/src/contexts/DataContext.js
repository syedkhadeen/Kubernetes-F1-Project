import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const DataContext = createContext();

export const useData = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
};

export const DataProvider = ({ children }) => {
  const [drivers, setDrivers] = useState([]);
  const [constructors, setConstructors] = useState([]);
  const [races, setRaces] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5005';

  // API service functions
  const fetchDrivers = async (params = {}) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/drivers`, { params });
      setDrivers(response.data.drivers || []);
      return response.data;
    } catch (error) {
      setError('Failed to fetch drivers');
      console.error('Error fetching drivers:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const fetchConstructors = async (params = {}) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/constructors`, { params });
      setConstructors(response.data.constructors || []);
      return response.data;
    } catch (error) {
      setError('Failed to fetch constructors');
      console.error('Error fetching constructors:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const fetchRaces = async (params = {}) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/races`, { params });
      setRaces(response.data.races || []);
      return response.data;
    } catch (error) {
      setError('Failed to fetch races');
      console.error('Error fetching races:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const fetchDriverStats = async (driverId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drivers/${driverId}/stats`);
      return response.data;
    } catch (error) {
      console.error('Error fetching driver stats:', error);
      throw error;
    }
  };

  const fetchConstructorStats = async (constructorId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/constructors/${constructorId}/stats`);
      return response.data;
    } catch (error) {
      console.error('Error fetching constructor stats:', error);
      throw error;
    }
  };

  const fetchRaceResults = async (season, round) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/races/${season}/${round}/results`);
      return response.data;
    } catch (error) {
      console.error('Error fetching race results:', error);
      throw error;
    }
  };

  const fetchFastestLaps = async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats/fastest-lap`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching fastest laps:', error);
      throw error;
    }
  };

  const fetchPodiumFrequency = async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats/podium-frequency`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching podium frequency:', error);
      throw error;
    }
  };

  const fetchConstructorPerformance = async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/constructors/performance`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching constructor performance:', error);
      throw error;
    }
  };

  const fetchTopDrivers = async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drivers/top`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching top drivers:', error);
      throw error;
    }
  };

  const fetchConstructorRankings = async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/constructors/rankings`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching constructor rankings:', error);
      throw error;
    }
  };

  const fetchLatestRace = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/races/latest`);
      return response.data;
    } catch (error) {
      console.error('Error fetching latest race:', error);
      throw error;
    }
  };

  const fetchDriverForm = async (driverId, params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats/driver-form/${driverId}`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching driver form:', error);
      throw error;
    }
  };

  const fetchSeasonTrends = async (season) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats/season-trends/${season}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching season trends:', error);
      throw error;
    }
  };

  const searchDrivers = async (query) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drivers/search`, {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching drivers:', error);
      throw error;
    }
  };

  const searchConstructors = async (query) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/constructors/search`, {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      console.error('Error searching constructors:', error);
      throw error;
    }
  };

  const clearError = () => setError(null);

  const value = {
    // State
    drivers,
    constructors,
    races,
    stats,
    loading,
    error,
    
    // Actions
    fetchDrivers,
    fetchConstructors,
    fetchRaces,
    fetchDriverStats,
    fetchConstructorStats,
    fetchRaceResults,
    fetchFastestLaps,
    fetchPodiumFrequency,
    fetchConstructorPerformance,
    fetchTopDrivers,
    fetchConstructorRankings,
    fetchLatestRace,
    fetchDriverForm,
    fetchSeasonTrends,
    searchDrivers,
    searchConstructors,
    clearError,
  };

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  );
};
