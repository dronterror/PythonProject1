import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  LinearProgress,
  useTheme,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Assignment as OrderIcon,
  Person as PatientIcon,
  LocalHospital as DrugIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CompletedIcon,
  Cancel as CancelledIcon,
  Pause as OnHoldIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';

interface MedicationOrder {
  id: string;
  patientName: string;
  patientId: string;
  drugName: string;
  drugId: string;
  dosage: number;
  schedule: string;
  frequency: string;
  route: string;
  status: 'active' | 'completed' | 'cancelled' | 'on-hold';
  createdAt: string;
  startDate: string;
  endDate?: string;
  instructions?: string;
  administrations?: Administration[];
  totalDoses?: number;
  completedDoses?: number;
}

interface Administration {
  id: string;
  orderId: string;
  nurseId: string;
  nurseName: string;
  administrationTime: string;
  dosageGiven: number;
  notes?: string;
  status: 'completed' | 'missed' | 'refused';
}

const MyOrdersPage: React.FC = () => {
  const [selectedOrder, setSelectedOrder] = useState<MedicationOrder | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  
  const theme = useTheme();
  const { wardId } = useActiveWard();

  // Fetch doctor's orders
  const {
    data: orders = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['orders', 'my-orders', wardId],
    queryFn: () => api.get<MedicationOrder[]>('/orders/my-orders'),
    enabled: !!wardId,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'primary';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      case 'on-hold':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <OrderIcon />;
      case 'completed':
        return <CompletedIcon />;
      case 'cancelled':
        return <CancelledIcon />;
      case 'on-hold':
        return <OnHoldIcon />;
      default:
        return <OrderIcon />;
    }
  };

  const getCompletionPercentage = (order: MedicationOrder) => {
    if (!order.totalDoses || order.totalDoses === 0) return 0;
    return Math.round((order.completedDoses || 0) / order.totalDoses * 100);
  };

  const handleViewOrder = (order: MedicationOrder) => {
    setSelectedOrder(order);
    setDetailsDialogOpen(true);
  };

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load your orders. Please try again.
        </Alert>
      </Box>
    );
  }

  if (!wardId) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please select a ward to view your orders.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" component="h1" gutterBottom>
        My Orders
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Track your medication prescriptions and their administration status
      </Typography>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <LinearProgress sx={{ width: '100%', maxWidth: 400 }} />
        </Box>
      ) : orders.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <OrderIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            No Orders Found
          </Typography>
          <Typography variant="body2" color="textSecondary">
            You haven't prescribed any medications in this ward yet.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {orders.map((order) => (
            <Grid item xs={12} md={6} lg={4} key={order.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  '&:hover': {
                    boxShadow: theme.shadows[4],
                    transform: 'translateY(-2px)',
                    transition: 'all 0.2s ease-in-out',
                  },
                }}
                onClick={() => handleViewOrder(order)}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Header */}
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Chip
                      icon={getStatusIcon(order.status)}
                      label={order.status.replace('-', ' ').toUpperCase()}
                      color={getStatusColor(order.status) as any}
                      size="small"
                    />
                    <Tooltip title="View Details">
                      <IconButton size="small" color="primary">
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Patient & Drug Info */}
                  <Box mb={2}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <PatientIcon sx={{ mr: 1, fontSize: 18, color: 'text.secondary' }} />
                      <Typography variant="h6" noWrap>
                        {order.patientName}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" mb={1}>
                      <DrugIcon sx={{ mr: 1, fontSize: 18, color: 'text.secondary' }} />
                      <Typography variant="body1" noWrap>
                        {order.drugName}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center">
                      <ScheduleIcon sx={{ mr: 1, fontSize: 18, color: 'text.secondary' }} />
                      <Typography variant="body2" color="textSecondary">
                        {order.dosage}mg • {order.frequency} • {order.route}
                      </Typography>
                    </Box>
                  </Box>

                  {/* Progress */}
                  {order.status === 'active' && (
                    <Box mb={2}>
                      <Box display="flex" justifyContent="space-between" mb={1}>
                        <Typography variant="body2" color="textSecondary">
                          Progress
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {order.completedDoses || 0} / {order.totalDoses || 0} doses
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={getCompletionPercentage(order)}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  )}

                  {/* Dates */}
                  <Typography variant="caption" color="textSecondary">
                    Started: {new Date(order.startDate).toLocaleDateString()}
                    {order.endDate && (
                      <> • Ends: {new Date(order.endDate).toLocaleDateString()}</>
                    )}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Order Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedOrder && (
          <>
            <DialogTitle>
              Order Details - {selectedOrder.patientName}
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                {/* Order Information */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Medication Information
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Drug"
                        secondary={selectedOrder.drugName}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Dosage"
                        secondary={`${selectedOrder.dosage}mg`}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Route"
                        secondary={selectedOrder.route}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Frequency"
                        secondary={selectedOrder.frequency}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Schedule"
                        secondary={selectedOrder.schedule}
                      />
                    </ListItem>
                    {selectedOrder.instructions && (
                      <ListItem>
                        <ListItemText
                          primary="Instructions"
                          secondary={selectedOrder.instructions}
                        />
                      </ListItem>
                    )}
                  </List>
                </Grid>

                {/* Administration History */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Administration History
                  </Typography>
                  {selectedOrder.administrations && selectedOrder.administrations.length > 0 ? (
                                         <List dense>
                       {selectedOrder.administrations.map((admin) => (
                         <ListItem key={admin.id}>
                           <ListItemText
                             primary={new Date(admin.administrationTime).toLocaleString()}
                             secondary={
                               <Box>
                                 <Typography variant="body2" component="span">
                                   By: {admin.nurseName} • {admin.dosageGiven}mg
                                 </Typography>
                                 {admin.notes && (
                                   <Typography variant="caption" display="block">
                                     Notes: {admin.notes}
                                   </Typography>
                                 )}
                               </Box>
                             }
                           />
                           <ListItemSecondaryAction>
                             <Chip
                               label={admin.status}
                               color={admin.status === 'completed' ? 'success' : 'warning'}
                               size="small"
                             />
                           </ListItemSecondaryAction>
                         </ListItem>
                       ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="textSecondary" style={{ fontStyle: 'italic' }}>
                      No administrations recorded yet
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailsDialogOpen(false)}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default MyOrdersPage; 