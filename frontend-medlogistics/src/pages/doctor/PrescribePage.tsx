import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Alert,
  Chip,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Cancel as OutOfStockIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';

interface Drug {
  id: string;
  name: string;
  form: string;
  strength: string;
  currentStock: number;
  lowStockThreshold: number;
  isAvailable: boolean;
  stockStatus: 'in-stock' | 'low-stock' | 'out-of-stock';
}

interface Patient {
  id: string;
  name: string;
  roomNumber: string;
  bedNumber: string;
  medicalRecordNumber: string;
}

interface PrescriptionForm {
  patientId: string;
  drugId: string;
  dosage: number;
  frequency: string;
  route: string;
  duration: number;
  durationType: 'days' | 'weeks' | 'months';
  instructions?: string;
  startDate: string;
}

const FREQUENCIES = [
  'Once daily (QD)',
  'Twice daily (BID)',
  'Three times daily (TID)',
  'Four times daily (QID)',
  'Every 4 hours',
  'Every 6 hours',
  'Every 8 hours',
  'Every 12 hours',
  'As needed (PRN)',
];

const ROUTES = [
  'Oral (PO)',
  'Intravenous (IV)',
  'Intramuscular (IM)',
  'Subcutaneous (SC)',
  'Topical',
  'Inhalation',
  'Sublingual',
  'Rectal',
];

const PrescribePage: React.FC = () => {
  const [form, setForm] = useState<PrescriptionForm>({
    patientId: '',
    drugId: '',
    dosage: 0,
    frequency: '',
    route: '',
    duration: 1,
    durationType: 'days',
    instructions: '',
    startDate: new Date().toISOString().split('T')[0],
  });

  const [selectedDrug, setSelectedDrug] = useState<Drug | null>(null);
  const { wardId } = useActiveWard();
  const queryClient = useQueryClient();

  // Fetch patients in the ward
  const { data: patients = [] } = useQuery({
    queryKey: ['patients', wardId],
    queryFn: () => api.get<Patient[]>(`/patients?ward_id=${wardId}`),
    enabled: !!wardId,
  });

  // Fetch formulary drugs
  const { data: formularyDrugs = [] } = useQuery({
    queryKey: ['formulary', wardId],
    queryFn: () => api.get<Drug[]>('/formulary'),
    enabled: !!wardId,
  });

  // Fetch inventory status
  const { data: inventoryStatus = [] } = useQuery({
    queryKey: ['inventory', 'status', wardId],
    queryFn: () => api.get<Drug[]>(`/inventory/status?ward_id=${wardId}`),
    enabled: !!wardId,
  });

  // Combine formulary and inventory data for smart suggestions
  const availableDrugs = formularyDrugs.map((drug) => {
    const inventoryItem = inventoryStatus.find((inv) => inv.id === drug.id);
    return {
      ...drug,
      currentStock: inventoryItem?.currentStock || 0,
      lowStockThreshold: inventoryItem?.lowStockThreshold || 0,
      isAvailable: inventoryItem ? inventoryItem.currentStock > 0 : false,
      stockStatus: inventoryItem
        ? inventoryItem.currentStock === 0
          ? 'out-of-stock'
          : inventoryItem.currentStock <= inventoryItem.lowStockThreshold
          ? 'low-stock'
          : 'in-stock'
        : 'out-of-stock',
    } as Drug;
  });

  // Create prescription mutation
  const createPrescriptionMutation = useMutation({
    mutationFn: (data: PrescriptionForm) => {
      const endDate = new Date(data.startDate);
      if (data.durationType === 'days') {
        endDate.setDate(endDate.getDate() + data.duration);
      } else if (data.durationType === 'weeks') {
        endDate.setDate(endDate.getDate() + data.duration * 7);
      } else if (data.durationType === 'months') {
        endDate.setMonth(endDate.getMonth() + data.duration);
      }

      return api.post('/orders', {
        ...data,
        endDate: endDate.toISOString().split('T')[0],
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      // Reset form
      setForm({
        patientId: '',
        drugId: '',
        dosage: 0,
        frequency: '',
        route: '',
        duration: 1,
        durationType: 'days',
        instructions: '',
        startDate: new Date().toISOString().split('T')[0],
      });
      setSelectedDrug(null);
    },
  });

  const handleDrugChange = (_event: any, value: Drug | null) => {
    setSelectedDrug(value);
    setForm({ ...form, drugId: value?.id || '' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.patientId || !form.drugId || !form.dosage || !form.frequency || !form.route) {
      return;
    }
    createPrescriptionMutation.mutate(form);
  };

  const getStockStatusIcon = (status: string) => {
    switch (status) {
      case 'in-stock':
        return <CheckIcon color="success" />;
      case 'low-stock':
        return <WarningIcon color="warning" />;
      case 'out-of-stock':
        return <OutOfStockIcon color="error" />;
      default:
        return null;
    }
  };

  const getStockStatusColor = (status: string) => {
    switch (status) {
      case 'in-stock':
        return 'success';
      case 'low-stock':
        return 'warning';
      case 'out-of-stock':
        return 'error';
      default:
        return 'default';
    }
  };

  if (!wardId) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please select a ward to prescribe medications.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" component="h1" gutterBottom>
        Prescribe Medication
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Create a new medication prescription for a patient in your ward
      </Typography>

      <Grid container spacing={3}>
        {/* Prescription Form */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Prescription Details
            </Typography>
            
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                {/* Patient Selection */}
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Patient</InputLabel>
                    <Select
                      value={form.patientId}
                      label="Patient"
                      onChange={(e) => setForm({ ...form, patientId: e.target.value })}
                    >
                      {patients.map((patient) => (
                        <MenuItem key={patient.id} value={patient.id}>
                          {patient.name} - Room {patient.roomNumber}, Bed {patient.bedNumber}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Drug Selection with Smart Autocomplete */}
                <Grid item xs={12}>
                  <Autocomplete
                    options={availableDrugs}
                    getOptionLabel={(option) => `${option.name} ${option.strength} (${option.form})`}
                    value={selectedDrug}
                    onChange={handleDrugChange}
                    getOptionDisabled={(option) => option.stockStatus === 'out-of-stock'}
                    renderOption={(props, option) => (
                      <Box component="li" {...props} key={option.id}>
                        <Box display="flex" alignItems="center" width="100%">
                          <Box flexGrow={1}>
                            <Typography variant="body1">
                              {option.name} {option.strength}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {option.form} • Stock: {option.currentStock}
                            </Typography>
                          </Box>
                          <Box display="flex" alignItems="center">
                            {getStockStatusIcon(option.stockStatus)}
                            <Chip
                              label={option.stockStatus.replace('-', ' ').toUpperCase()}
                              color={getStockStatusColor(option.stockStatus) as any}
                              size="small"
                              sx={{ ml: 1 }}
                            />
                          </Box>
                        </Box>
                      </Box>
                    )}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Drug *"
                        placeholder="Search for a medication..."
                        required
                      />
                    )}
                  />
                </Grid>

                {/* Dosage */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Dosage (mg)"
                    type="number"
                    required
                    value={form.dosage || ''}
                    onChange={(e) => setForm({ ...form, dosage: parseInt(e.target.value) || 0 })}
                    inputProps={{ min: 0, step: 0.25 }}
                  />
                </Grid>

                {/* Route */}
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Route</InputLabel>
                    <Select
                      value={form.route}
                      label="Route"
                      onChange={(e) => setForm({ ...form, route: e.target.value })}
                    >
                      {ROUTES.map((route) => (
                        <MenuItem key={route} value={route}>
                          {route}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Frequency */}
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Frequency</InputLabel>
                    <Select
                      value={form.frequency}
                      label="Frequency"
                      onChange={(e) => setForm({ ...form, frequency: e.target.value })}
                    >
                      {FREQUENCIES.map((frequency) => (
                        <MenuItem key={frequency} value={frequency}>
                          {frequency}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>

                {/* Duration */}
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Duration"
                    type="number"
                    required
                    value={form.duration}
                    onChange={(e) => setForm({ ...form, duration: parseInt(e.target.value) || 1 })}
                    inputProps={{ min: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Duration Type</InputLabel>
                    <Select
                      value={form.durationType}
                      label="Duration Type"
                      onChange={(e) => setForm({ ...form, durationType: e.target.value as any })}
                    >
                      <MenuItem value="days">Days</MenuItem>
                      <MenuItem value="weeks">Weeks</MenuItem>
                      <MenuItem value="months">Months</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>

                {/* Start Date */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Start Date"
                    type="date"
                    required
                    value={form.startDate}
                    onChange={(e) => setForm({ ...form, startDate: e.target.value })}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                {/* Instructions */}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Special Instructions"
                    multiline
                    rows={3}
                    value={form.instructions}
                    onChange={(e) => setForm({ ...form, instructions: e.target.value })}
                    placeholder="Additional instructions for nurses..."
                  />
                </Grid>

                {/* Submit Button */}
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={createPrescriptionMutation.isPending}
                    startIcon={
                      createPrescriptionMutation.isPending ? (
                        <CircularProgress size={20} />
                      ) : null
                    }
                  >
                    {createPrescriptionMutation.isPending ? 'Creating...' : 'Create Prescription'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </Paper>
        </Grid>

        {/* Drug Information Panel */}
        <Grid item xs={12} md={4}>
          {selectedDrug ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Drug Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box mb={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    {selectedDrug.name}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Strength: {selectedDrug.strength}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Form: {selectedDrug.form}
                  </Typography>
                </Box>

                <Divider sx={{ mb: 2 }} />

                <Box mb={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Inventory Status
                  </Typography>
                  <Box display="flex" alignItems="center" mb={1}>
                    {getStockStatusIcon(selectedDrug.stockStatus)}
                    <Chip
                      label={selectedDrug.stockStatus.replace('-', ' ').toUpperCase()}
                      color={getStockStatusColor(selectedDrug.stockStatus) as any}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Current Stock: {selectedDrug.currentStock}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Low Stock Threshold: {selectedDrug.lowStockThreshold}
                  </Typography>
                </Box>

                {selectedDrug.stockStatus === 'low-stock' && (
                  <Alert severity="warning" sx={{ mt: 2 }}>
                    This medication is running low in stock. Consider alternative options if available.
                  </Alert>
                )}
                
                {selectedDrug.stockStatus === 'out-of-stock' && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    This medication is currently out of stock and cannot be prescribed.
                  </Alert>
                )}
              </CardContent>
            </Card>
          ) : (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="textSecondary">
                Select a drug to view detailed information and stock status
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* Success/Error Messages */}
      {createPrescriptionMutation.isSuccess && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Prescription created successfully!
        </Alert>
      )}
      
      {createPrescriptionMutation.isError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to create prescription. Please try again.
        </Alert>
      )}
    </Box>
  );
};

export default PrescribePage; 