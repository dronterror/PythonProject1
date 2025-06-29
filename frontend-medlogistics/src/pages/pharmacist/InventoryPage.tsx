import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';
import { Box, Typography, Card, CardContent, CircularProgress, Alert, Paper, Grid } from '@mui/material';
import { Drug } from '@/types';

const InventoryPage: React.FC = () => {
  const activeWard = useActiveWard();
  const { data: inventory, isLoading, error, isSuccess } = useQuery<Drug[], Error>({
    queryKey: ['inventory', activeWard?.id],
    queryFn: async () => {
      if (!activeWard?.id) return [];
      const response = await apiClient.get(`/inventory/ward/${activeWard.id}`);
      return response.data;
    },
    enabled: !!activeWard?.id,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}>
        <CircularProgress />
        <Typography ml={2}>Loading Inventory...</Typography>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error" sx={{ m: 2 }}>Error loading inventory: {error.message}</Alert>;
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Ward Inventory
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Ward: {activeWard?.name || 'N/A'}
      </Typography>

      {isSuccess && inventory?.length === 0 && (
        <Alert severity="info">No inventory data available for this ward.</Alert>
      )}

      <Grid container spacing={2} sx={{ mt: 2 }}>
        {isSuccess && inventory && inventory.map((drug) => (
          <Grid item xs={12} sm={6} md={4} key={drug.id}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" component="div">
                  {drug.name}
                </Typography>
                <Typography color="text.secondary">
                  {drug.strength}
                </Typography>
                <Typography variant="body2" sx={{ mt: 1.5 }}>
                  Current Stock: {drug.currentStock}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Paper>
  );
};

export default InventoryPage; 