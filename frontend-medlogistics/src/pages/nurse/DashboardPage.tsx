import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { Box, Typography, Card, CardContent, CircularProgress, Alert } from '@mui/material';
import { Patient, MedicationOrder } from '@/types';

interface MarDashboardData {
  patient: Patient;
  orders: MedicationOrder[];
}

const NurseDashboardPage: React.FC = () => {
  const { data, isLoading, error } = useQuery<MarDashboardData[], Error>({
    queryKey: ['marDashboard'],
    queryFn: () => apiClient.get('/mar-dashboard'),
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
        <Typography ml={2}>Loading MAR Dashboard...</Typography>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">Error loading dashboard: {error.message}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        MAR Dashboard
      </Typography>
      {data?.map((item) => (
        <Card key={item.patient.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{item.patient.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              Room: {item.patient.roomNumber} - Bed: {item.patient.bedNumber}
            </Typography>
            {item.orders.map((order) => (
              <Box key={order.id} mt={2} pl={2} borderLeft="2px solid" borderColor="divider">
                <Typography variant="subtitle1">{order.drug?.name}</Typography>
                <Typography variant="body2">Dosage: {order.dosage}</Typography>
                <Typography variant="body2">Schedule: {order.schedule}</Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default NurseDashboardPage; 