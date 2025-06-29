import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Alert,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import { DataGrid, GridColDef, GridRowParams } from '@mui/x-data-grid';
import { Add as AddIcon, Edit as EditIcon, Visibility as ViewIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';

interface Hospital {
  id: string;
  name: string;
  address: string;
  contactPhone: string;
  isActive: boolean;
  wardCount?: number;
}

interface Ward {
  id: string;
  name: string;
  description: string;
  capacity: number;
  currentOccupancy: number;
  isActive: boolean;
  hospitalId: string;
}

interface CreateHospitalForm {
  name: string;
  address: string;
  contactPhone: string;
}

interface CreateWardForm {
  name: string;
  description: string;
  capacity: number;
}

const HospitalManagementPage: React.FC = () => {
  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(null);
  const [hospitalDialogOpen, setHospitalDialogOpen] = useState(false);
  const [wardDialogOpen, setWardDialogOpen] = useState(false);
  const [hospitalForm, setHospitalForm] = useState<CreateHospitalForm>({
    name: '',
    address: '',
    contactPhone: '',
  });
  const [wardForm, setWardForm] = useState<CreateWardForm>({
    name: '',
    description: '',
    capacity: 20,
  });

  const queryClient = useQueryClient();

  // Fetch hospitals
  const {
    data: hospitals = [],
    isLoading: hospitalsLoading,
    error: hospitalsError,
  } = useQuery({
    queryKey: ['hospitals'],
    queryFn: async () => {
      const response = await apiClient.get<Hospital[]>('/hospitals');
      return response.data;
    },
  });

  // Fetch wards for selected hospital
  const {
    data: wards = [],
    isLoading: wardsLoading,
  } = useQuery({
    queryKey: ['hospitals', selectedHospital?.id, 'wards'],
    queryFn: async () => {
      if (!selectedHospital?.id) return [];
      const response = await apiClient.get<Ward[]>(`/hospitals/${selectedHospital.id}/wards`);
      return response.data;
    },
    enabled: !!selectedHospital?.id,
  });

  // Create hospital mutation
  const createHospitalMutation = useMutation({
    mutationFn: (data: CreateHospitalForm) => apiClient.post('/hospitals', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hospitals'] });
      setHospitalDialogOpen(false);
      setHospitalForm({ name: '', address: '', contactPhone: '' });
    },
  });

  // Create ward mutation
  const createWardMutation = useMutation({
    mutationFn: (data: CreateWardForm) =>
      apiClient.post(`/hospitals/${selectedHospital?.id}/wards`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hospitals', selectedHospital?.id, 'wards'] });
      setWardDialogOpen(false);
      setWardForm({ name: '', description: '', capacity: 20 });
    },
  });

  // Hospital columns
  const hospitalColumns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Hospital Name',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'address',
      headerName: 'Address',
      flex: 1,
      minWidth: 250,
    },
    {
      field: 'contactPhone',
      headerName: 'Phone',
      width: 150,
    },
    {
      field: 'isActive',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'wardCount',
      headerName: 'Wards',
      width: 80,
      renderCell: (params) => params.row.wardCount || 0,
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Tooltip title="View Wards">
            <IconButton
              size="small"
              onClick={() => handleViewHospital(params.row)}
              color="primary"
            >
              <ViewIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Edit Hospital">
            <IconButton size="small" color="secondary">
              <EditIcon />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  // Ward columns
  const wardColumns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Ward Name',
      flex: 1,
      minWidth: 150,
    },
    {
      field: 'description',
      headerName: 'Description',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'capacity',
      headerName: 'Capacity',
      width: 100,
    },
    {
      field: 'currentOccupancy',
      headerName: 'Occupied',
      width: 100,
    },
    {
      field: 'occupancyRate',
      headerName: 'Occupancy %',
      width: 120,
      renderCell: (params) => {
        const rate = Math.round((params.row.currentOccupancy / params.row.capacity) * 100);
        return (
          <Chip
            label={`${rate}%`}
            color={rate > 90 ? 'error' : rate > 75 ? 'warning' : 'success'}
            size="small"
          />
        );
      },
    },
    {
      field: 'isActive',
      headerName: 'Status',
      width: 100,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    },
  ];

  const handleViewHospital = (hospital: Hospital) => {
    setSelectedHospital(hospital);
  };

  const handleCreateHospital = () => {
    createHospitalMutation.mutate(hospitalForm);
  };

  const handleCreateWard = () => {
    if (selectedHospital) {
      createWardMutation.mutate(wardForm);
    }
  };

  if (hospitalsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load hospitals. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Hospital Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setHospitalDialogOpen(true)}
        >
          Create Hospital
        </Button>
      </Box>

      {/* Hospitals Grid */}
      <Paper sx={{ mb: 3 }}>
        <DataGrid
          rows={hospitals}
          columns={hospitalColumns}
          loading={hospitalsLoading}
          autoHeight
          onRowClick={(params: GridRowParams) => handleViewHospital(params.row)}
          sx={{
            '& .MuiDataGrid-row': {
              cursor: 'pointer',
            },
          }}
        />
      </Paper>

      {/* Wards Section */}
      {selectedHospital && (
        <Paper sx={{ p: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Wards - {selectedHospital.name}
            </Typography>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={() => setWardDialogOpen(true)}
            >
              Add Ward
            </Button>
          </Box>
          <DataGrid
            rows={wards}
            columns={wardColumns}
            loading={wardsLoading}
            autoHeight
          />
        </Paper>
      )}

      {/* Create Hospital Dialog */}
      <Dialog
        open={hospitalDialogOpen}
        onClose={() => setHospitalDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Hospital</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Hospital Name"
                value={hospitalForm.name}
                onChange={(e) =>
                  setHospitalForm({ ...hospitalForm, name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                value={hospitalForm.address}
                onChange={(e) =>
                  setHospitalForm({ ...hospitalForm, address: e.target.value })
                }
                multiline
                rows={3}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Contact Phone"
                value={hospitalForm.contactPhone}
                onChange={(e) =>
                  setHospitalForm({ ...hospitalForm, contactPhone: e.target.value })
                }
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHospitalDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateHospital}
            variant="contained"
            disabled={createHospitalMutation.isPending}
          >
            Create Hospital
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Ward Dialog */}
      <Dialog
        open={wardDialogOpen}
        onClose={() => setWardDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Ward to {selectedHospital?.name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Ward Name"
                value={wardForm.name}
                onChange={(e) =>
                  setWardForm({ ...wardForm, name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={wardForm.description}
                onChange={(e) =>
                  setWardForm({ ...wardForm, description: e.target.value })
                }
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Capacity"
                type="number"
                value={wardForm.capacity}
                onChange={(e) =>
                  setWardForm({ ...wardForm, capacity: parseInt(e.target.value) || 20 })
                }
                required
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWardDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateWard}
            variant="contained"
            disabled={createWardMutation.isPending}
          >
            Add Ward
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default HospitalManagementPage; 