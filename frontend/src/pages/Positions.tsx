import { usePositions } from '../hooks';
import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { Box, Typography } from '@mui/material';

export default function Positions() {
  const { data } = usePositions();

  const columns: GridColDef[] = [
    { field: 'symbol', headerName: 'Symbol', flex: 1 },
    { field: 'qty', headerName: 'Qty', type: 'number', flex: 1 },
    { field: 'avg_price', headerName: 'Avg Price', type: 'number', flex: 1 },
    { field: 'market_value', headerName: 'Market Value', type: 'number', flex: 1 },
    { field: 'unrealized_pnl', headerName: 'Unrealized PnL', type: 'number', flex: 1 },
  ];

  const rows = data ? data.map((p: any, idx: number) => ({ id: idx, ...p })) : [];

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        Positions
      </Typography>
      <DataGrid autoHeight rows={rows} columns={columns} disableRowSelectionOnClick />
    </Box>
  );
} 