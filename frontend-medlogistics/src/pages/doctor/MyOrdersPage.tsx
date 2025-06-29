import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { Box, Typography, Card, CardContent, CircularProgress, Alert, Paper } from '@mui/material';
import { MedicationOrder } from '@/types';
import { useUser } from '@/stores/useAppStore';

const MyOrdersPage: React.FC = () => {
  const user = useUser();
  const { data: orders, isLoading, error, isSuccess } = useQuery<MedicationOrder[], Error>({
    queryKey: ['myOrders', user?.sub],
    queryFn: async () => {
      const response = await apiClient.get(`/orders/doctor/${user?.sub}`);
      return response.data;
    },
    enabled: !!user?.sub,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}>
        <CircularProgress />
        <Typography ml={2}>Loading My Orders...</Typography>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error" sx={{ m: 2 }}>Error loading orders: {error.message}</Alert>;
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Orders
      </Typography>

      {isSuccess && orders?.length === 0 && (
        <Alert severity="info">You have not created any orders yet.</Alert>
      )}

      <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {isSuccess && orders && orders.map((order) => (
          <Card key={order.id} variant="outlined">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Patient: {order.patientName}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary">
                Drug: {order.drug?.name || 'N/A'}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2"><strong>Dosage:</strong> {order.dosage}</Typography>
                <Typography variant="body2"><strong>Schedule:</strong> {order.schedule}</Typography>
                <Typography variant="body2"><strong>Status:</strong> {order.status}</Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Paper>
  );
};

export default MyOrdersPage; 