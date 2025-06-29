import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';
import { Box, Typography, Alert, CircularProgress, Paper } from '@mui/material';
import { Drug } from '@/types';

const AlertsPage: React.FC = () => {
  const activeWard = useActiveWard();

  const { data: lowStockDrugs, isLoading, error, isSuccess } = useQuery<Drug[], Error>({
    queryKey: ['lowStockDrugs', activeWard?.id],
    queryFn: async () => {
      const response = await apiClient.get(`/drugs/low-stock?ward_id=${activeWard?.id}`);
      return response.data;
    },
    enabled: !!activeWard?.id,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}>
        <CircularProgress />
        <Typography ml={2}>Loading Low Stock Alerts...</Typography>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error" sx={{ m: 2 }}>Error loading alerts: {error.message}</Alert>;
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Low Stock Alerts
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Ward: {activeWard?.name || 'N/A'}
      </Typography>
      
      {isSuccess && lowStockDrugs?.length === 0 && (
        <Alert severity="success">
          No low stock alerts for the selected ward. All items are well-stocked.
        </Alert>
      )}

      <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {isSuccess && lowStockDrugs && lowStockDrugs.map((drug) => (
          <Alert key={drug.id} severity="warning" variant="outlined">
            <Typography sx={{ fontWeight: 'bold' }}>
              {drug.name} ({drug.strength})
            </Typography>
            <Typography variant="body2">
              Current Stock: {drug.currentStock} units
            </Typography>
            <Typography variant="body2">
              Low Stock Threshold: {drug.lowStockThreshold} units
            </Typography>
          </Alert>
        ))}
      </Box>
    </Paper>
  );
};

export default AlertsPage; 