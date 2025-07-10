import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Badge,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  ExpandMore,
  Refresh,
  Add,
  Visibility,
  Timeline,
  Assessment
} from '@mui/icons-material';
import { api } from '../api';

interface Play {
  play_id: string;
  order_id: string;
  symbol: string;
  status: string;
  title: string;
  side: string;
  timeframe: string;
  priority: number;
  tags: string[];
  created_at: string;
  performance?: {
    pnl_pct: number;
    max_profit: number;
    max_drawdown: number;
    time_in_play: number;
  };
  interventions: number;
  adaptations: number;
}

interface PlayDetails {
  play_id: string;
  natural_language_description: string;
  parsed_play: any;
  execution_plan: any;
  monitoring_conditions: any;
  interventions: any[];
  adaptations: any[];
  performance_history: any[];
}

interface PlayStatistics {
  total_plays: number;
  active_plays: number;
  completed_plays: number;
  intervened_plays: number;
  profitable_plays: number;
  losing_plays: number;
  avg_profit: number;
  avg_loss: number;
  total_interventions: number;
  total_adaptations: number;
  success_rate: number;
}

const PlayExecutor: React.FC = () => {
  const [plays, setPlays] = useState<Play[]>([]);
  const [statistics, setStatistics] = useState<PlayStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedPlay, setSelectedPlay] = useState<PlayDetails | null>(null);
  
  // Create play form
  const [playDescription, setPlayDescription] = useState('');
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [confidence, setConfidence] = useState(0.7);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadPlays();
    loadStatistics();
  }, []);

  const loadPlays = async () => {
    try {
      setLoading(true);
      const response = await api.get('/plays');
      if (response.data.status === 'success') {
        const allPlays = [
          ...response.data.data.active_plays,
          ...response.data.data.historical_plays
        ].filter(Boolean);
        setPlays(allPlays);
      }
    } catch (error) {
      console.error('Error loading plays:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await api.get('/plays/statistics');
      if (response.data.status === 'success') {
        setStatistics(response.data.data);
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const loadPlayDetails = async (playId: string) => {
    try {
      const response = await api.get(`/plays/reporting/${playId}/details`);
      if (response.data.status === 'success') {
        setSelectedPlay(response.data.data);
        setDetailsDialogOpen(true);
      }
    } catch (error) {
      console.error('Error loading play details:', error);
    }
  };

  const createPlay = async () => {
    try {
      setCreating(true);
      const response = await api.post('/plays/create', {
        play_description: playDescription,
        symbol: symbol.toUpperCase(),
        initial_quantity: quantity,
        confidence_score: confidence
      });
      
      if (response.data.status === 'success') {
        setCreateDialogOpen(false);
        setPlayDescription('');
        setSymbol('');
        setQuantity(1);
        setConfidence(0.7);
        loadPlays();
        loadStatistics();
      }
    } catch (error) {
      console.error('Error creating play:', error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'intervened': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <PlayArrow />;
      case 'completed': return <CheckCircle />;
      case 'intervened': return <Warning />;
      case 'failed': return <Error />;
      default: return <PlayArrow />;
    }
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatTime = (hours: number) => {
    if (hours < 1) return `${(hours * 60).toFixed(0)}m`;
    if (hours < 24) return `${hours.toFixed(1)}h`;
    return `${(hours / 24).toFixed(1)}d`;
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            🎭 Play Executor
          </Typography>
          <Box>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadPlays}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateDialogOpen(true)}
            >
              Create Play
            </Button>
          </Box>
        </Box>

        {/* Statistics Cards */}
        {statistics && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Plays
                  </Typography>
                  <Typography variant="h4">
                    {statistics.total_plays}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Plays
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {statistics.active_plays}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Success Rate
                  </Typography>
                  <Typography variant="h4" color="info.main">
                    {formatPercentage(statistics.success_rate)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Interventions
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {statistics.total_interventions}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Plays Table */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              All Plays
            </Typography>
            
            {loading ? (
              <LinearProgress />
            ) : (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>Symbol</TableCell>
                      <TableCell>Title</TableCell>
                      <TableCell>Side</TableCell>
                      <TableCell>P&L</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Interventions</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {plays.map((play) => (
                      <TableRow key={play.play_id}>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(play.status)}
                            label={play.status}
                            color={getStatusColor(play.status) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {play.symbol}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {play.title}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {play.timeframe} • Priority {play.priority}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={play.side.toUpperCase()}
                            color={play.side === 'buy' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {play.performance && (
                            <Typography
                              variant="body2"
                              color={play.performance.pnl_pct >= 0 ? 'success.main' : 'error.main'}
                              fontWeight="bold"
                            >
                              {formatPercentage(play.performance.pnl_pct)}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          {play.performance && (
                            <Typography variant="body2">
                              {formatTime(play.performance.time_in_play)}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            {play.interventions > 0 && (
                              <Badge badgeContent={play.interventions} color="warning">
                                <Warning fontSize="small" />
                              </Badge>
                            )}
                            {play.adaptations > 0 && (
                              <Badge badgeContent={play.adaptations} color="info">
                                <TrendingUp fontSize="small" />
                              </Badge>
                            )}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              onClick={() => loadPlayDetails(play.play_id)}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Create Play Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Trading Play</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Symbol"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="e.g., NVDA, AAPL, SPY"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={4}
              label="Natural Language Play Description"
              value={playDescription}
              onChange={(e) => setPlayDescription(e.target.value)}
              placeholder="Describe your trading play in natural language. Include entry strategy, exit strategy, catalysts, risks, etc."
              sx={{ mb: 2 }}
            />
            <Grid container spacing={2}>
              <Grid size={{ xs: 6 }}>
                <TextField
                  fullWidth
                  type="number"
                  label="Quantity"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                  inputProps={{ min: 1 }}
                />
              </Grid>
              <Grid size={{ xs: 6 }}>
                <TextField
                  fullWidth
                  type="number"
                  label="Confidence Score"
                  value={confidence}
                  onChange={(e) => setConfidence(parseFloat(e.target.value) || 0.7)}
                  inputProps={{ min: 0, max: 1, step: 0.1 }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={createPlay}
            variant="contained"
            disabled={creating || !symbol || !playDescription}
          >
            {creating ? 'Creating...' : 'Create Play'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Play Details Dialog */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          Play Details: {selectedPlay?.parsed_play?.title}
        </DialogTitle>
        <DialogContent>
          {selectedPlay && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12 }}>
                  <Typography variant="h6" gutterBottom>
                    Natural Language Description
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {selectedPlay.natural_language_description}
                  </Typography>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="h6" gutterBottom>
                    Parsed Play
                  </Typography>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2">
                        <strong>Side:</strong> {selectedPlay.parsed_play?.side}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Timeframe:</strong> {selectedPlay.parsed_play?.timeframe}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Priority:</strong> {selectedPlay.parsed_play?.priority}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Tags:</strong> {selectedPlay.parsed_play?.tags?.join(', ')}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="h6" gutterBottom>
                    Execution Plan
                  </Typography>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Typography>Phases</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      {selectedPlay.execution_plan?.phases?.map((phase: any, index: number) => (
                        <Box key={index} sx={{ mb: 1 }}>
                          <Typography variant="subtitle2">
                            {phase.phase}: {phase.description}
                          </Typography>
                        </Box>
                      ))}
                    </AccordionDetails>
                  </Accordion>
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <Typography variant="h6" gutterBottom>
                    Interventions ({selectedPlay.interventions?.length || 0})
                  </Typography>
                  {selectedPlay.interventions?.map((intervention: any, index: number) => (
                    <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                      <Typography variant="subtitle2">
                        {intervention.intervention_type}: {intervention.reason}
                      </Typography>
                      <Typography variant="caption">
                        {new Date(intervention.timestamp).toLocaleString()}
                      </Typography>
                    </Alert>
                  ))}
                </Grid>

                <Grid size={{ xs: 12 }}>
                  <Typography variant="h6" gutterBottom>
                    Adaptations ({selectedPlay.adaptations?.length || 0})
                  </Typography>
                  {selectedPlay.adaptations?.map((adaptation: any, index: number) => (
                    <Alert key={index} severity="info" sx={{ mb: 1 }}>
                      <Typography variant="subtitle2">
                        {adaptation.adaptation_type}: {adaptation.reason}
                      </Typography>
                      <Typography variant="caption">
                        {new Date(adaptation.timestamp).toLocaleString()}
                      </Typography>
                    </Alert>
                  ))}
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PlayExecutor; 