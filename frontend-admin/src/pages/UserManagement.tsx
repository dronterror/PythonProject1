import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Snackbar,
  IconButton,
  Chip
} from '@mui/material';
import { DataGrid, GridToolbar, type GridColDef } from '@mui/x-data-grid';
import {
  Add,
  PersonAdd,
  Close,
  Email,
  Badge
} from '@mui/icons-material';

interface User {
  id: string;
  email: string;
  role: string;
  auth0_user_id: string;
  created_at: string;
}

interface Hospital {
  id: string;
  name: string;
}

interface Ward {
  id: string;
  name: string;
  hospital_id: string;
}

const UserManagement: React.FC = () => {
  const { getAccessTokenSilently } = useAuth0();
  const [users, setUsers] = useState<User[]>([]);
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [wards, setWards] = useState<Ward[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    role: '',
    hospital_id: '',
    ward_id: '',
    send_email: true
  });
  const [submitting, setSubmitting] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const userRoles = [
    { value: 'doctor', label: 'Doctor' },
    { value: 'nurse', label: 'Nurse' },
    { value: 'pharmacist', label: 'Pharmacist' },
    { value: 'super_admin', label: 'Super Admin' }
  ];

  const columns: GridColDef[] = [
    { 
      field: 'email', 
      headerName: 'Email', 
      width: 250,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          <Email sx={{ mr: 1, color: 'text.secondary', fontSize: 18 }} />
          {params.value}
        </Box>
      )
    },
    { 
      field: 'role', 
      headerName: 'Role', 
      width: 150,
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color="primary" 
          variant="outlined" 
          size="small"
        />
      )
    },
    { 
      field: 'auth0_user_id', 
      headerName: 'Auth0 ID', 
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      )
    },
    { 
      field: 'created_at', 
      headerName: 'Created', 
      width: 150,
      valueFormatter: (value: string) => new Date(value).toLocaleDateString()
    },
    { 
      field: 'id', 
      headerName: 'ID', 
      width: 200,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
          {params.value}
        </Typography>
      )
    }
  ];

  const fetchUsers = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(`${apiBaseUrl}/api/admin/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
    }
  };

  const fetchHospitals = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(`${apiBaseUrl}/api/admin/hospitals`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setHospitals(data);
    } catch (err) {
      console.error('Failed to fetch hospitals:', err);
    }
  };

  const fetchWards = async (hospitalId: string) => {
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(`${apiBaseUrl}/api/admin/hospitals/${hospitalId}/wards`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setWards(data);
    } catch (err) {
      console.error('Failed to fetch wards:', err);
      setWards([]);
    }
  };

  const handleSubmit = async () => {
    if (!formData.email.trim() || !formData.role || !formData.hospital_id || !formData.ward_id) {
      setSnackbar({ open: true, message: 'All fields are required', severity: 'error' });
      return;
    }

    setSubmitting(true);
    try {
      const token = await getAccessTokenSilently();
      const response = await fetch(`${apiBaseUrl}/api/admin/users/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          email: formData.email.trim(),
          role: formData.role,
          hospital_id: formData.hospital_id,
          ward_id: formData.ward_id,
          send_email: formData.send_email
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      await fetchUsers(); // Refresh the list
      setOpenDialog(false);
      setFormData({ email: '', role: '', hospital_id: '', ward_id: '', send_email: true });
      setWards([]);
      setSnackbar({ open: true, message: result.message, severity: 'success' });
    } catch (err) {
      setSnackbar({ 
        open: true, 
        message: err instanceof Error ? err.message : 'Failed to invite user', 
        severity: 'error' 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleHospitalChange = (hospitalId: string) => {
    setFormData({ ...formData, hospital_id: hospitalId, ward_id: '' });
    setWards([]);
    if (hospitalId) {
      fetchWards(hospitalId);
    }
  };

  useEffect(() => {
    const initializeData = async () => {
      setLoading(true);
      await Promise.all([fetchUsers(), fetchHospitals()]);
      setLoading(false);
    };
    initializeData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={50} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ m: 0 }}>
          User Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PersonAdd />}
          onClick={() => setOpenDialog(true)}
          size="large"
        >
          Invite User
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={users}
          columns={columns}
          initialState={{
            pagination: {
              paginationModel: { page: 0, pageSize: 10 },
            },
          }}
          pageSizeOptions={[5, 10, 20]}
          slots={{ toolbar: GridToolbar }}
          slotProps={{
            toolbar: {
              showQuickFilter: true,
              quickFilterProps: { debounceMs: 500 },
            },
          }}
          sx={{
            '& .MuiDataGrid-root': {
              border: 'none',
            },
            '& .MuiDataGrid-cell': {
              borderBottom: '1px solid #f0f0f0',
            },
            '& .MuiDataGrid-columnHeaders': {
              backgroundColor: '#f5f5f5',
              borderBottom: '2px solid #e0e0e0',
            },
          }}
        />
      </Box>

      {/* Invite User Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Invite New User
          <IconButton
            onClick={() => setOpenDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            sx={{ mb: 2 }}
            required
          />

          <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              label="Role"
            >
              {userRoles.map((role) => (
                <MenuItem key={role.value} value={role.value}>
                  <Box display="flex" alignItems="center">
                    <Badge sx={{ mr: 1 }} />
                    {role.label}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
            <InputLabel>Hospital</InputLabel>
            <Select
              value={formData.hospital_id}
              onChange={(e) => handleHospitalChange(e.target.value)}
              label="Hospital"
            >
              {hospitals.map((hospital) => (
                <MenuItem key={hospital.id} value={hospital.id}>
                  {hospital.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
            <InputLabel>Ward</InputLabel>
            <Select
              value={formData.ward_id}
              onChange={(e) => setFormData({ ...formData, ward_id: e.target.value })}
              label="Ward"
              disabled={!formData.hospital_id}
            >
              {wards.map((ward) => (
                <MenuItem key={ward.id} value={ward.id}>
                  {ward.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControlLabel
            control={
              <Switch
                checked={formData.send_email}
                onChange={(e) => setFormData({ ...formData, send_email: e.target.checked })}
                color="primary"
              />
            }
            label="Send invitation email to user"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenDialog(false)} disabled={submitting}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={submitting}
            startIcon={submitting ? <CircularProgress size={20} /> : <PersonAdd />}
          >
            {submitting ? 'Inviting...' : 'Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UserManagement; 