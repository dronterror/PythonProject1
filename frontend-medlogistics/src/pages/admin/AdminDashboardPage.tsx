
import { Box, Typography, Grid, Paper, Card, CardContent } from '@mui/material';
import { People, Business, Security, Assessment } from '@mui/icons-material';

function AdminDashboardPage() {
  const stats = [
    {
      title: 'Total Users',
      value: '--',
      icon: <People sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: 'Hospitals',
      value: '--',
      icon: <Business sx={{ fontSize: 40 }} />,
      color: '#388e3c',
    },
    {
      title: 'Active Permissions',
      value: '--',
      icon: <Security sx={{ fontSize: 40 }} />,
      color: '#f57c00',
    },
    {
      title: 'System Health',
      value: 'Online',
      icon: <Assessment sx={{ fontSize: 40 }} />,
      color: '#7b1fa2',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome to the MedLog Admin Panel. Manage users, hospitals, and system permissions.
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box sx={{ color: stat.color, mr: 2 }}>
                    {stat.icon}
                  </Box>
                  <Box>
                    <Typography variant="h4" component="div">
                      {stat.value}
                    </Typography>
                    <Typography color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Use the navigation menu to:
            </Typography>
            <Box component="ul" sx={{ mt: 1 }}>
              <li>Manage user accounts and permissions</li>
              <li>Create and organize hospitals and wards</li>
              <li>Invite new users with specific roles</li>
              <li>Monitor system activity and permissions</li>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Box>
              <Typography variant="body2" gutterBottom>
                ✅ API Server: Online
              </Typography>
              <Typography variant="body2" gutterBottom>
                ✅ Database: Connected
              </Typography>
              <Typography variant="body2" gutterBottom>
                ✅ Auth0: Active
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default AdminDashboardPage; 