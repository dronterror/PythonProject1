import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { DataGrid, GridColDef, GridRowParams } from '@mui/x-data-grid';
import {
  Edit as EditIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Cancel as OutOfStockIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';
import { useActiveWard } from '@/stores/useAppStore';

interface DrugStock {
  id: string;
  drugId: string;
  drugName: string;
  drugForm: string;
  drugStrength: string;
  currentStock: number;
  lowStockThreshold: number;
  maxStock: number;
  lastUpdated: string;
  updatedBy: string;
  stockStatus: 'in-stock' | 'low-stock' | 'out-of-stock';
}

interface UpdateStockForm {
  drugStockId: string;
  newStock: number;
  operation: 'set' | 'add' | 'subtract';
  notes?: string;
}

const InventoryPage: React.FC = () => {
  const [updateStockDialogOpen, setUpdateStockDialogOpen] = useState(false);
  const [selectedDrugStock, setSelectedDrugStock] = useState<DrugStock | null>(null);
  const [stockForm, setStockForm] = useState<UpdateStockForm>({
    drugStockId: '',
    newStock: 0,
    operation: 'set',
    notes: '',
  });

  const { wardId, wardName } = useActiveWard();
  const queryClient = useQueryClient();

  // Fetch drug stocks for the ward
  const {
    data: drugStocks = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['drug-stocks', wardId],
    queryFn: () => api.get<DrugStock[]>(`/drug-stocks?ward_id=${wardId}`),
    enabled: !!wardId,
  });

  // Update stock mutation
  const updateStockMutation = useMutation({
    mutationFn: (data: UpdateStockForm) => {
      let finalStock = data.newStock;
      if (data.operation === 'add') {
        finalStock = (selectedDrugStock?.currentStock || 0) + data.newStock;
      } else if (data.operation === 'subtract') {
        finalStock = Math.max(0, (selectedDrugStock?.currentStock || 0) - data.newStock);
      }
      
      return api.put(`/drug-stocks/${data.drugStockId}`, {
        currentStock: finalStock,
        notes: data.notes,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['drug-stocks', wardId] });
      setUpdateStockDialogOpen(false);
      setStockForm({
        drugStockId: '',
        newStock: 0,
        operation: 'set',
        notes: '',
      });
      setSelectedDrugStock(null);
    },
  });

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

  const calculateStockStatus = (current: number, threshold: number): DrugStock['stockStatus'] => {
    if (current === 0) return 'out-of-stock';
    if (current <= threshold) return 'low-stock';
    return 'in-stock';
  };

  const columns: GridColDef[] = [
    {
      field: 'drugName',
      headerName: 'Drug Name',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'drugStrength',
      headerName: 'Strength',
      width: 120,
    },
    {
      field: 'drugForm',
      headerName: 'Form',
      width: 100,
    },
    {
      field: 'currentStock',
      headerName: 'Current Stock',
      width: 120,
      renderCell: (params) => (
        <Box display="flex" alignItems="center">
          {getStockStatusIcon(calculateStockStatus(params.value, params.row.lowStockThreshold))}
          <Typography variant="body2" sx={{ ml: 1 }}>
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'lowStockThreshold',
      headerName: 'Low Threshold',
      width: 120,
    },
    {
      field: 'maxStock',
      headerName: 'Max Stock',
      width: 100,
    },
    {
      field: 'stockStatus',
      headerName: 'Status',
      width: 140,
      renderCell: (params) => {
        const status = calculateStockStatus(params.row.currentStock, params.row.lowStockThreshold);
        return (
          <Chip
            label={status.replace('-', ' ').toUpperCase()}
            color={getStockStatusColor(status) as any}
            size="small"
          />
        );
      },
    },
    {
      field: 'lastUpdated',
      headerName: 'Last Updated',
      width: 140,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Tooltip title="Update Stock">
          <IconButton
            size="small"
            onClick={() => handleUpdateStock(params.row)}
            color="primary"
          >
            <EditIcon />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  const handleUpdateStock = (drugStock: DrugStock) => {
    setSelectedDrugStock(drugStock);
    setStockForm({
      drugStockId: drugStock.id,
      newStock: drugStock.currentStock,
      operation: 'set',
      notes: '',
    });
    setUpdateStockDialogOpen(true);
  };

  const handleSubmitStockUpdate = () => {
    if (selectedDrugStock && stockForm.newStock >= 0) {
      updateStockMutation.mutate(stockForm);
    }
  };

  const getFinalStock = () => {
    if (!selectedDrugStock) return 0;
    
    switch (stockForm.operation) {
      case 'add':
        return selectedDrugStock.currentStock + stockForm.newStock;
      case 'subtract':
        return Math.max(0, selectedDrugStock.currentStock - stockForm.newStock);
      case 'set':
      default:
        return stockForm.newStock;
    }
  };

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load inventory data. Please try again.
        </Alert>
      </Box>
    );
  }

  if (!wardId) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please select a ward to view inventory.
        </Alert>
      </Box>
    );
  }

  const lowStockCount = drugStocks.filter(drug => 
    calculateStockStatus(drug.currentStock, drug.lowStockThreshold) === 'low-stock'
  ).length;
  
  const outOfStockCount = drugStocks.filter(drug => 
    calculateStockStatus(drug.currentStock, drug.lowStockThreshold) === 'out-of-stock'
  ).length;

  return (
    <Box p={3}>
      <Typography variant="h4" component="h1" gutterBottom>
        Inventory Management
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Manage drug inventory for {wardName}
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" color="success.main">
                    {drugStocks.filter(drug => 
                      calculateStockStatus(drug.currentStock, drug.lowStockThreshold) === 'in-stock'
                    ).length}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    In Stock
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <WarningIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {lowStockCount}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Low Stock
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <OutOfStockIcon color="error" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4" color="error.main">
                    {outOfStockCount}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Out of Stock
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Inventory Table */}
      <Paper>
        <DataGrid
          rows={drugStocks}
          columns={columns}
          loading={isLoading}
          autoHeight
          onRowClick={(params: GridRowParams) => handleUpdateStock(params.row)}
          sx={{
            '& .MuiDataGrid-row': {
              cursor: 'pointer',
            },
          }}
        />
      </Paper>

      {/* Update Stock Dialog */}
      <Dialog
        open={updateStockDialogOpen}
        onClose={() => setUpdateStockDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Update Stock - {selectedDrugStock?.drugName}
        </DialogTitle>
        <DialogContent>
          {selectedDrugStock && (
            <Box>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                {selectedDrugStock.drugStrength} • {selectedDrugStock.drugForm}
              </Typography>
              
              <Typography variant="body2" gutterBottom>
                Current Stock: <strong>{selectedDrugStock.currentStock}</strong>
              </Typography>
              
              <Box sx={{ mt: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      select
                      fullWidth
                      label="Operation"
                      value={stockForm.operation}
                      onChange={(e) => setStockForm({ ...stockForm, operation: e.target.value as any })}
                      SelectProps={{ native: true }}
                    >
                      <option value="set">Set to exact amount</option>
                      <option value="add">Add to current stock</option>
                      <option value="subtract">Remove from current stock</option>
                    </TextField>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label={stockForm.operation === 'set' ? 'New Stock Amount' : 'Quantity'}
                      type="number"
                      value={stockForm.newStock}
                      onChange={(e) => setStockForm({ ...stockForm, newStock: parseInt(e.target.value) || 0 })}
                      inputProps={{ min: 0 }}
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary">
                      Final stock will be: <strong>{getFinalStock()}</strong>
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Notes (optional)"
                      multiline
                      rows={2}
                      value={stockForm.notes}
                      onChange={(e) => setStockForm({ ...stockForm, notes: e.target.value })}
                      placeholder="Reason for stock update..."
                    />
                  </Grid>
                </Grid>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpdateStockDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmitStockUpdate}
            variant="contained"
            disabled={updateStockMutation.isPending}
          >
            {updateStockMutation.isPending ? 'Updating...' : 'Update Stock'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InventoryPage; 