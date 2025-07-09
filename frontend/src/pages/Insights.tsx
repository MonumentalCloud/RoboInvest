import { useResearchInsights } from '../hooks';
import { Box, Typography, List, ListItem, ListItemText, CircularProgress, Alert, Chip } from '@mui/material';

export default function Insights() {
  const { data, isLoading, error } = useResearchInsights(50);

  if (isLoading) {
    return (
      <Box sx={{ p: 2, width: '100%', display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, width: '100%' }}>
        <Typography variant="h5" gutterBottom>
          AI Research Insights
        </Typography>
        <Alert severity="error">
          Failed to load research insights: {error.message || 'Unknown error'}
        </Alert>
      </Box>
    );
  }

  // Extract insights from the API response
  const apiData = data?.data || {};
  const insights = Array.isArray(apiData.insights) ? apiData.insights : [];
  const lastUpdated = apiData.last_updated;
  const totalAvailable = apiData.total_available || 0;

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        AI Research Insights
      </Typography>
      
      {/* Status info */}
      <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Chip 
          label={`${insights.length} insights`} 
          color="primary" 
          variant="outlined" 
        />
        <Chip 
          label={`${totalAvailable} total generated`} 
          color="secondary" 
          variant="outlined" 
        />
        {lastUpdated && (
          <Chip 
            label={`Updated: ${new Date(lastUpdated).toLocaleTimeString()}`} 
            variant="outlined" 
          />
        )}
      </Box>

      {insights.length === 0 ? (
        <Alert severity="info">
          No research insights available yet. The AI agents are working in the background to discover alpha opportunities.
        </Alert>
      ) : (
        <List>
          {insights.map((insight: any, idx: number) => {
            const confidence = insight.confidence || 0;
            const confidenceColor = confidence > 0.7 ? 'success' : confidence > 0.4 ? 'warning' : 'default';
            
            return (
              <ListItem key={idx} divider>
                <ListItemText 
                  primary={
                    <Box>
                      <Typography variant="body1" component="span">
                        {insight.insight || insight.text || 'No content'}
                      </Typography>
                      <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip 
                          label={insight.track || 'unknown'} 
                          size="small" 
                          color="primary" 
                        />
                        <Chip 
                          label={insight.specialization || 'general'} 
                          size="small" 
                          variant="outlined" 
                        />
                        <Chip 
                          label={`${(confidence * 100).toFixed(0)}% confidence`} 
                          size="small" 
                          color={confidenceColor}
                        />
                      </Box>
                      {insight.competitive_edge && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          Edge: {insight.competitive_edge}
                        </Typography>
                      )}
                    </Box>
                  }
                  secondary={
                    insight.timestamp 
                      ? new Date(insight.timestamp).toLocaleString() 
                      : new Date().toLocaleString()
                  }
                />
              </ListItem>
            );
          })}
        </List>
      )}
    </Box>
  );
} 