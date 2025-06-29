import React from 'react';
import { useUser } from '@/stores/useAppStore';
import DoctorLayout from '@/components/layout/DoctorLayout';
import PharmacistLayout from '@/components/layout/PharmacistLayout';
import NurseLayout from '@/components/layout/NurseLayout';
import { Box, CircularProgress, Typography } from '@mui/material';

const AppDispatcher: React.FC = () => {
  const user = useUser();

  if (!user) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
        <Typography ml={2}>Loading user profile...</Typography>
      </Box>
    );
  }

  const { roles } = user;

  if (roles.includes('doctor')) {
    return <DoctorLayout />;
  }
  if (roles.includes('pharmacist')) {
    return <PharmacistLayout />;
  }
  if (roles.includes('nurse')) {
    return <NurseLayout />;
  }

  // Default fallback or error for users with no recognized role
  return (
    <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
      <Typography color="error">
        No valid role found for this user.
      </Typography>
    </Box>
  );
};

export default AppDispatcher; 