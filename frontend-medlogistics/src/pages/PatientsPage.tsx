import React from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Avatar,
} from '@mui/material';
import {
  Person as PersonIcon,
} from '@mui/icons-material';
import { useActiveWard } from '@/stores/useAppStore';

const PatientsPage: React.FC = () => {
  const { wardName } = useActiveWard();

  // Mock patient data
  const patients = [
    { id: 1, name: 'John Doe', room: '101A', condition: 'Stable', age: 45 },
    { id: 2, name: 'Jane Smith', room: '102B', condition: 'Critical', age: 67 },
    { id: 3, name: 'Bob Johnson', room: '103A', condition: 'Recovering', age: 32 },
  ];

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case 'Stable':
        return 'success';
      case 'Critical':
        return 'error';
      case 'Recovering':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      <Box mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Patients
        </Typography>
        <Typography variant="body1" color="textSecondary">
          {wardName ? `${wardName} Ward Patients` : 'Patient List'}
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <List>
            {patients.map((patient) => (
              <ListItem key={patient.id}>
                <ListItemIcon>
                  <Avatar>
                    <PersonIcon />
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body1">
                        {patient.name}
                      </Typography>
                      <Chip
                        label={patient.condition}
                        size="small"
                        color={getConditionColor(patient.condition) as any}
                      />
                    </Box>
                  }
                  secondary={`Room ${patient.room} • Age ${patient.age}`}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Container>
  );
};

export default PatientsPage; 