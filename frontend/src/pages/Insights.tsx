import { useLessons } from '../hooks';
import { Box, Typography, List, ListItem, ListItemText } from '@mui/material';

export default function Insights() {
  const { data } = useLessons();

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        Insights & Lessons
      </Typography>
      <List>
        {data?.map((lesson: any, idx: number) => (
          <ListItem key={idx} divider>
            <ListItemText primary={lesson.text || lesson.lesson} secondary={lesson.time || lesson.t || ''} />
          </ListItem>
        ))}
      </List>
    </Box>
  );
} 