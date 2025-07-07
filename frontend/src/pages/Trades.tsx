import { DataGrid } from '@mui/x-data-grid';
import type { GridColDef } from '@mui/x-data-grid';
import { useTrades } from '../hooks';
import { Box, Typography } from '@mui/material';

export default function Trades() {
  const { data } = useTrades(200);

  const columns: GridColDef[] = [
    { field: 'time', headerName: 'Time', flex: 1 },
    { field: 'symbol', headerName: 'Symbol', flex: 1 },
    { field: 'side', headerName: 'Side', flex: 1 },
    { field: 'qty', headerName: 'Qty', type: 'number', flex: 1 },
    { field: 'price', headerName: 'Price', type: 'number', flex: 1 },
    { field: 'pnl', headerName: 'PnL', type: 'number', flex: 1 },
  ];

  const rows = data ? data.map((t: any, idx: number) => ({ id: idx, ...t })) : [];

  return (
    <Box sx={{ p: 2, width: '100%' }}>
      <Typography variant="h5" gutterBottom>
        Trades
      </Typography>
      <DataGrid autoHeight rows={rows} columns={columns} disableRowSelectionOnClick />
    </Box>
  );
} 