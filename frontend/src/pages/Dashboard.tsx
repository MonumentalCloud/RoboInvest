import { Grid, Card, CardContent, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useBudget, usePerformance } from '../hooks';

export default function Dashboard() {
  const { data: perf } = usePerformance();
  const { data: budget } = useBudget();

  return (
    <Grid container spacing={2} sx={{ p: 2, width: '100%' }}>
      <Grid size={{ xs: 12, md: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total P&amp;L (last 10 trades)</Typography>
            <Typography variant="h3" color={perf?.total_pnl > 0 ? 'success.main' : 'error.main'}>
              {perf ? perf.total_pnl.toFixed(2) : '--'}$
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6">LLM Cost Today</Typography>
            <Typography variant="h3">${budget ? budget.cost_usd.toFixed(3) : '--'}</Typography>
            <Typography variant="body2">Budget: ${budget?.daily_budget}</Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid size={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Equity Curve
            </Typography>
            {perf?.equity_curve && (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={perf.equity_curve}>
                  <XAxis dataKey="t" hide />
                  <YAxis domain={['auto', 'auto']} />
                  <Tooltip />
                  <Line type="monotone" dataKey="equity" stroke="#00bfa5" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
} 