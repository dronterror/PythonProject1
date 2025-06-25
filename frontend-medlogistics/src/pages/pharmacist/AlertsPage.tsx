import React from 'react';
import {
  Box,
  Typography,
  Alert,
  AlertTitle,
  Grid,
  Card,
  CardContent,
  Chip,
  Button,
  IconButton,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  ShoppingCart as OrderIcon,
  Refresh as RefreshIcon,
  CheckCircle as ResolvedIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';

interface LowStockDrug {
  id: string;
  drugName: string;
  drugForm: string;
  drugStrength: string;
  currentStock: number;
  lowStockThreshold: number;
  maxStock: number;
  stockStatus: 'low-stock' | 'out-of-stock';
  daysSinceLastOrder?: number;
  expectedDelivery?: string;
  urgency: 'critical' | 'high' | 'medium';
}

interface StockAlert {
  id: string;
  type: 'low-stock' | 'out-of-stock' | 'expiring-soon';
  drugName: string;
  message: string;
  urgency: 'critical' | 'high' | 'medium';
  createdAt: string;
  isResolved: boolean;
}

const AlertsPage: React.FC = () => {
  const { wardId, wardName } = useActiveWard();

  // Fetch low stock drugs
  const {
    data: lowStockDrugs = [],
    isLoading: lowStockLoading,
    error: lowStockError,
    refetch: refetchLowStock,
  } = useQuery({
    queryKey: ['drugs', 'low-stock', wardId],
    queryFn: () => api.get<LowStockDrug[]>(`/drugs/low-stock?ward_id=${wardId}`),
    enabled: !!wardId,
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  // Fetch general alerts
  const {
    data: alerts = [],
    isLoading: alertsLoading,
    error: alertsError,
    refetch: refetchAlerts,
  } = useQuery({
    queryKey: ['alerts', wardId],
    queryFn: () => api.get<StockAlert[]>(`/alerts?ward_id=${wardId}&type=inventory`),
    enabled: !!wardId,
    refetchInterval: 300000, // Refetch every 5 minutes
  });

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStockPercentage = (current: number, _threshold: number, max: number) => {
    return Math.round((current / max) * 100);
  };

  const handleRefreshAll = () => {
    refetchLowStock();
    refetchAlerts();
  };

  if (!wardId) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please select a ward to view alerts.
        </Alert>
      </Box>
    );
  }

  if (lowStockError || alertsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load alerts. Please try again.
        </Alert>
      </Box>
    );
  }

  const criticalDrugs = lowStockDrugs.filter(drug => drug.urgency === 'critical');
  const highPriorityDrugs = lowStockDrugs.filter(drug => drug.urgency === 'high');
  const mediumPriorityDrugs = lowStockDrugs.filter(drug => drug.urgency === 'medium');

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Stock Alerts
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefreshAll}
          disabled={lowStockLoading || alertsLoading}
        >
          Refresh
        </Button>
      </Box>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Critical inventory alerts for {wardName}
      </Typography>

      {(lowStockLoading || alertsLoading) && (
        <Box sx={{ width: '100%', mb: 3 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Summary Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'error.light', color: 'error.contrastText' }}>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ErrorIcon sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">
                    {criticalDrugs.length}
                  </Typography>
                  <Typography variant="body2">
                    Critical Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'warning.light', color: 'warning.contrastText' }}>
            <CardContent>
              <Box display="flex" alignItems="center">
                <WarningIcon sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">
                    {highPriorityDrugs.length}
                  </Typography>
                  <Typography variant="body2">
                    High Priority
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card sx={{ bgcolor: 'info.light', color: 'info.contrastText' }}>
            <CardContent>
              <Box display="flex" alignItems="center">
                <WarningIcon sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">
                    {mediumPriorityDrugs.length}
                  </Typography>
                  <Typography variant="body2">
                    Medium Priority
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {lowStockDrugs.length === 0 ? (
        <Alert severity="success" sx={{ mb: 3 }}>
          <AlertTitle>All Good!</AlertTitle>
          No low stock alerts at this time. All medications are adequately stocked.
        </Alert>
      ) : (
        <>
          {/* Critical Alerts */}
          {criticalDrugs.length > 0 && (
            <Box mb={4}>
              <Typography variant="h5" gutterBottom color="error">
                🚨 Critical Alerts
              </Typography>
              <Grid container spacing={2}>
                {criticalDrugs.map((drug) => (
                  <Grid item xs={12} md={6} key={drug.id}>
                    <Alert severity="error" variant="filled">
                      <AlertTitle>
                        {drug.stockStatus === 'out-of-stock' ? 'OUT OF STOCK' : 'CRITICALLY LOW'}
                      </AlertTitle>
                      <Typography variant="body1" gutterBottom>
                        <strong>{drug.drugName}</strong> ({drug.drugStrength}, {drug.drugForm})
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        Current: {drug.currentStock} | Threshold: {drug.lowStockThreshold}
                      </Typography>
                      {drug.stockStatus !== 'out-of-stock' && (
                        <LinearProgress
                          variant="determinate"
                          value={getStockPercentage(drug.currentStock, drug.lowStockThreshold, drug.maxStock)}
                          sx={{ mt: 1, mb: 1, bgcolor: 'rgba(255,255,255,0.3)' }}
                        />
                      )}
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                        <Chip
                          label={drug.urgency.toUpperCase()}
                          color="error"
                          size="small"
                        />
                        <Button
                          variant="contained"
                          color="inherit"
                          size="small"
                          startIcon={<OrderIcon />}
                        >
                          Order Now
                        </Button>
                      </Box>
                    </Alert>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* High Priority Alerts */}
          {highPriorityDrugs.length > 0 && (
            <Box mb={4}>
              <Typography variant="h5" gutterBottom color="warning.main">
                ⚠️ High Priority
              </Typography>
              <Grid container spacing={2}>
                {highPriorityDrugs.map((drug) => (
                  <Grid item xs={12} md={6} key={drug.id}>
                    <Alert severity="warning" variant="outlined">
                      <AlertTitle>Low Stock Warning</AlertTitle>
                      <Typography variant="body1" gutterBottom>
                        <strong>{drug.drugName}</strong> ({drug.drugStrength}, {drug.drugForm})
                      </Typography>
                      <Typography variant="body2" gutterBottom>
                        Current: {drug.currentStock} | Threshold: {drug.lowStockThreshold}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={getStockPercentage(drug.currentStock, drug.lowStockThreshold, drug.maxStock)}
                        color="warning"
                        sx={{ mt: 1, mb: 1 }}
                      />
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                        <Chip
                          label={drug.urgency.toUpperCase()}
                          color="warning"
                          size="small"
                        />
                        <Button
                          variant="outlined"
                          color="warning"
                          size="small"
                          startIcon={<OrderIcon />}
                        >
                          Order Soon
                        </Button>
                      </Box>
                    </Alert>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Medium Priority Alerts */}
          {mediumPriorityDrugs.length > 0 && (
            <Box mb={4}>
              <Typography variant="h5" gutterBottom color="info.main">
                📋 Medium Priority
              </Typography>
              <List>
                {mediumPriorityDrugs.map((drug) => (
                  <ListItem key={drug.id} divider>
                    <ListItemText
                      primary={`${drug.drugName} (${drug.drugStrength}, ${drug.drugForm})`}
                      secondary={
                        <Box>
                          <Typography variant="body2" component="span">
                            Current Stock: {drug.currentStock} | Threshold: {drug.lowStockThreshold}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={getStockPercentage(drug.currentStock, drug.lowStockThreshold, drug.maxStock)}
                            color="info"
                            sx={{ mt: 1, width: '200px' }}
                          />
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={drug.urgency.toUpperCase()}
                        color="info"
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Button
                        variant="text"
                        color="info"
                        size="small"
                        startIcon={<OrderIcon />}
                      >
                        Order
                      </Button>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </>
      )}

      {/* General Alerts */}
      {alerts.length > 0 && (
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            📢 System Alerts
          </Typography>
          <Grid container spacing={2}>
            {alerts.filter(alert => !alert.isResolved).map((alert) => (
              <Grid item xs={12} key={alert.id}>
                <Alert 
                  severity={getUrgencyColor(alert.urgency) as any}
                  action={
                    <IconButton
                      color="inherit"
                      size="small"
                      onClick={() => {
                        // Mark as resolved logic would go here
                        console.log('Mark as resolved:', alert.id);
                      }}
                    >
                      <ResolvedIcon />
                    </IconButton>
                  }
                >
                  <AlertTitle>{alert.drugName}</AlertTitle>
                  {alert.message}
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    {new Date(alert.createdAt).toLocaleString()}
                  </Typography>
                </Alert>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Quick Actions */}
      <Box mt={4}>
        <Divider sx={{ mb: 3 }} />
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              startIcon={<OrderIcon />}
              size="large"
            >
              Bulk Order Critical Items
            </Button>
          </Grid>
          <Grid item>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={handleRefreshAll}
            >
              Refresh All Alerts
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default AlertsPage; 