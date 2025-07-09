import { useQuery } from '@tanstack/react-query';
import { api } from './api';

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

export const useDecisionTrees = () => {
  console.log("🌳 useDecisionTrees: Hook called");
  return useQuery({ 
    queryKey: ['decision-trees', 'v2'], // Added version to force cache refresh
    queryFn: async () => {
      try {
        console.log("🌳 useDecisionTrees: Making API call...");
        const response = await api.get('/research/decision-trees');
        const data = response.data;
        
        console.log("🌳 useDecisionTrees: Raw response data:", data);
        
        // Transform the nested tree structure to flat array format for frontend
        const flatTrees: any[] = [];
        
        // The API response has {status: 'success', data: {tracks...}}
        // We need to access data.data to get the actual tracks
        const tracksData = data?.data;
        
        if (tracksData && typeof tracksData === 'object') {
          Object.entries(tracksData).forEach(([trackName, trackData]: [string, any]) => {
            console.log(`🌳 useDecisionTrees: Processing track ${trackName}:`, trackData);
            if (trackData?.tree?.nodes) {
              // Convert nodes object to array and transform format
              const nodes = Object.values(trackData.tree.nodes).map((node: any) => ({
                ...node,
                title: node.content || node.id, // Use content as title
                parent: node.parent_id, // Map parent_id to parent
                timestamp: node.created_at || node.timestamp || new Date().toISOString(),
                track: trackName
              }));
              flatTrees.push(...nodes);
            }
          });
        }
        
        console.log("🌳 useDecisionTrees: Transformed data:", flatTrees.length, "nodes");
        console.log("🌳 useDecisionTrees: Sample nodes:", flatTrees.slice(0, 3));
        
        return flatTrees;
      } catch (error) {
        console.error("🌳 useDecisionTrees: Error in queryFn:", error);
        throw error;
      }
    }, 
    refetchInterval: 120000 
  });
};

export const useResearchTracks = () =>
  useQuery({ queryKey: ['research-tracks'], queryFn: () => api.get('/research/tracks').then(r => r.data), refetchInterval: 60000 }); 