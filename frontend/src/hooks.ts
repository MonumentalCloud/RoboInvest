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