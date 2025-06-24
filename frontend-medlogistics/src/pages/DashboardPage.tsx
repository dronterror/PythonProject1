import React from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Medication as MedicationIcon,
} from '@mui/icons-material';
import { useActiveWard } from '@/stores/useAppStore';

const DashboardPage: React.FC = () => {
  const { wardName } = useActiveWard();

  // Mock data - this would come from React Query hooks
  const dashboardData = {
    pendingMedications: 12,
    completedToday: 28,
    overdueAdministrations: 3,
    totalPatients: 15,
    recentActivities: [
      { id: 1, patient: 'John Doe', medication: 'Aspirin 75mg', time: '10:30 AM', status: 'completed' },
      { id: 2, patient: 'Jane Smith', medication: 'Insulin 10u', time: '11:15 AM', status: 'pending' },
      { id: 3, patient: 'Bob Johnson', medication: 'Metformin 500mg', time: '12:00 PM', status: 'overdue' },
    ],
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'overdue':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      {/* Header */}
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="textSecondary">
          {wardName ? `${wardName} Ward` : 'Nurse Dashboard'}
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', pb: 1 }}>
              <MedicationIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6" component="div">
                {dashboardData.pendingMedications}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', pb: 1 }}>
              <CheckCircleIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6" component="div">
                {dashboardData.completedToday}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', pb: 1 }}>
              <WarningIcon color="error" sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6" component="div">
                {dashboardData.overdueAdministrations}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Overdue
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', pb: 1 }}>
              <AssignmentIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h6" component="div">
                {dashboardData.totalPatients}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Patients
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activities
          </Typography>
          <List>
            {dashboardData.recentActivities.map((activity, index) => (
              <React.Fragment key={activity.id}>
                <ListItem>
                  <ListItemIcon>
                    <ScheduleIcon color="action" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body1">
                          {activity.patient}
                        </Typography>
                        <Chip
                          label={activity.status}
                          size="small"
                          color={getStatusColor(activity.status) as any}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {activity.medication}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {activity.time}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
                {index < dashboardData.recentActivities.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
        <CardActions>
          <Button size="small" color="primary">
            View All Activities
          </Button>
        </CardActions>
      </Card>
    </Container>
  );
};

export default DashboardPage; 