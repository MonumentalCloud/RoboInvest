import React from 'react';
import Box from '@mui/material/Box';
import ResearchTreeFlow from '../components/ResearchTreeFlow';

const AlphaStream: React.FC = () => {
  return (
    <Box sx={{ height: '100vh', width: '100%' }}>
      <ResearchTreeFlow maxNodes={100} />
    </Box>
  );
};

export default AlphaStream; 