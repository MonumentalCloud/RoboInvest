import { useQuery } from '@tanstack/react-query';
import { api } from './api';
import { useState, useEffect } from 'react';

export const useBudget = () =>
  useQuery({ queryKey: ['budget'], queryFn: () => api.get('/budget').then(r => r.data), refetchInterval: 10000 });

export const usePerformance = () =>
  useQuery({ queryKey: ['perf'], queryFn: () => api.get('/performance').then(r => r.data), refetchInterval: 10000 });

export const useTrades = (limit = 100) =>
  useQuery({ queryKey: ['trades', limit], queryFn: () => api.get(`/trades?limit=${limit}`).then(r => r.data), refetchInterval: 10000 });

export const usePositions = () =>
  useQuery({ queryKey: ['positions'], queryFn: () => api.get('/positions').then(r => r.data), refetchInterval: 10000 });

export const useLessons = () =>
  useQuery({ queryKey: ['lessons'], queryFn: () => api.get('/lessons').then(r => r.data), refetchInterval: 60000 });

// New research API hooks
export const useResearchStatus = () =>
  useQuery({ queryKey: ['research-status'], queryFn: () => api.get('/research/status').then(r => r.data), refetchInterval: 30000 });

export const useResearchInsights = (limit = 50) =>
  useQuery({ queryKey: ['research-insights', limit], queryFn: () => api.get(`/research/insights?limit=${limit}`).then(r => r.data), refetchInterval: 60000 });

export const useAlphaOpportunities = (minConfidence = 0.0) =>
  useQuery({ queryKey: ['alpha-opportunities', minConfidence], queryFn: () => api.get(`/research/alpha-opportunities?min_confidence=${minConfidence}`).then(r => r.data), refetchInterval: 60000 });

export function useDecisionTrees() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8081/api/research/decision-trees');
        const result = await response.json();
        
        if (result.status === 'success' && result.data) {
          const flatTrees: any[] = [];
          Object.entries(result.data).forEach(([trackName, trackData]: [string, any]) => {
            if (trackData?.tree?.nodes) {
              const nodes = Object.values(trackData.tree.nodes).map((node: any) => ({
                ...node,
                id: node.id || `node_${Date.now()}_${Math.random()}`,
                title: node.content || node.id || `Node ${node.id}`,
                parent: node.parent_id,
                timestamp: node.created_at || node.timestamp || new Date().toISOString()
              }));
              flatTrees.push(...nodes);
            }
          });
          
          setData(flatTrees);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch decision trees');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
}

export const useResearchTracks = () =>
  useQuery({ queryKey: ['research-tracks'], queryFn: () => api.get('/research/tracks').then(r => r.data), refetchInterval: 60000 }); 