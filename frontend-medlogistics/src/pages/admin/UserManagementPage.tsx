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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { 
  Add as AddIcon, 
  PersonAdd as PersonAddIcon, 
  Security as SecurityIcon,
  Delete as DeleteIcon 
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/apiClient';

interface User {
  id: string;
  email: string;
  name: string;
  isActive: boolean;
  createdAt: string;
  permissions?: UserPermission[];
}

interface UserPermission {
  id: string;
  userId: string;
  wardId: string;
  wardName: string;
  role: string;
}

interface Ward {
  id: string;
  name: string;
  hospitalName: string;
}

interface InviteUserForm {
  email: string;
  name: string;
  role: string;
}

interface AddPermissionForm {
  wardId: string;
  role: string;
}

const AVAILABLE_ROLES = [
  { value: 'doctor', label: 'Doctor' },
  { value: 'nurse', label: 'Nurse' },
  { value: 'pharmacist', label: 'Pharmacist' },
  { value: 'admin', label: 'Admin' },
];

const UserManagementPage: React.FC = () => {
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [permissionsDialogOpen, setPermissionsDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  
  const [inviteForm, setInviteForm] = useState<InviteUserForm>({
    email: '',
    name: '',
    role: 'nurse',
  });
  
  const [permissionForm, setPermissionForm] = useState<AddPermissionForm>({
    wardId: '',
    role: 'nurse',
  });

  const queryClient = useQueryClient();

  // Fetch users
  const {
    data: users = [],
    isLoading: usersLoading,
    error: usersError,
  } = useQuery({
    queryKey: ['users'],
    queryFn: () => api.get<User[]>('/users'),
  });

  // Fetch wards for permission assignment
  const {
    data: wards = [],
  } = useQuery({
    queryKey: ['wards-all'],
    queryFn: () => api.get<Ward[]>('/wards/all'),
  });

  // Fetch user permissions
  const {
    data: userPermissions = [],
    isLoading: permissionsLoading,
  } = useQuery({
    queryKey: ['users', selectedUser?.id, 'permissions'],
    queryFn: () => api.get<UserPermission[]>(`/users/${selectedUser?.id}/permissions`),
    enabled: !!selectedUser?.id,
  });

  // Invite user mutation
  const inviteUserMutation = useMutation({
    mutationFn: (data: InviteUserForm) => api.post('/users/invite', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setInviteDialogOpen(false);
      setInviteForm({ email: '', name: '', role: 'nurse' });
    },
  });

  // Add permission mutation
  const addPermissionMutation = useMutation({
    mutationFn: (data: AddPermissionForm) =>
      api.post(`/users/${selectedUser?.id}/permissions`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', selectedUser?.id, 'permissions'] });
      setPermissionForm({ wardId: '', role: 'nurse' });
    },
  });

  // Remove permission mutation
  const removePermissionMutation = useMutation({
    mutationFn: (permissionId: string) =>
      api.delete(`/users/${selectedUser?.id}/permissions/${permissionId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users', selectedUser?.id, 'permissions'] });
    },
  });

  // User columns
  const userColumns: GridColDef[] = [
    {
      field: 'name',
      headerName: 'Name',
      flex: 1,
      minWidth: 150,
    },
    {
      field: 'email',
      headerName: 'Email',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'isActive',
      headerName: 'Status',
      width: 120,
      renderCell: (params) => (
        <Chip
          label={params.value ? 'Active' : 'Inactive'}
          color={params.value ? 'success' : 'default'}
          size="small"
        />
      ),
    },
    {
      field: 'createdAt',
      headerName: 'Created',
      width: 120,
      renderCell: (params) => new Date(params.value).toLocaleDateString(),
    },
    {
      field: 'permissionsCount',
      headerName: 'Permissions',
      width: 100,
      renderCell: (params) => params.row.permissions?.length || 0,
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <Tooltip title="Manage Permissions">
            <IconButton
              size="small"
              onClick={() => handleManagePermissions(params.row)}
              color="primary"
            >
              <SecurityIcon />
            </IconButton>
          </Tooltip>
        </Box>
      ),
    },
  ];

  const handleManagePermissions = (user: User) => {
    setSelectedUser(user);
    setPermissionsDialogOpen(true);
  };

  const handleInviteUser = () => {
    inviteUserMutation.mutate(inviteForm);
  };

  const handleAddPermission = () => {
    if (selectedUser && permissionForm.wardId && permissionForm.role) {
      addPermissionMutation.mutate(permissionForm);
    }
  };

  const handleRemovePermission = (permissionId: string) => {
    removePermissionMutation.mutate(permissionId);
  };

  if (usersError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Failed to load users. Please try again.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          User Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<PersonAddIcon />}
          onClick={() => setInviteDialogOpen(true)}
        >
          Invite User
        </Button>
      </Box>

      {/* Users Grid */}
      <Paper>
        <DataGrid
          rows={users}
          columns={userColumns}
          loading={usersLoading}
          autoHeight
          disableRowSelectionOnClick
        />
      </Paper>

      {/* Invite User Dialog */}
      <Dialog
        open={inviteDialogOpen}
        onClose={() => setInviteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Invite New User</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                value={inviteForm.name}
                onChange={(e) =>
                  setInviteForm({ ...inviteForm, name: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={inviteForm.email}
                onChange={(e) =>
                  setInviteForm({ ...inviteForm, email: e.target.value })
                }
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Default Role</InputLabel>
                <Select
                  value={inviteForm.role}
                  label="Default Role"
                  onChange={(e) =>
                    setInviteForm({ ...inviteForm, role: e.target.value })
                  }
                >
                  {AVAILABLE_ROLES.map((role) => (
                    <MenuItem key={role.value} value={role.value}>
                      {role.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleInviteUser}
            variant="contained"
            disabled={inviteUserMutation.isPending}
          >
            Send Invitation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Permissions Management Dialog */}
      <Dialog
        open={permissionsDialogOpen}
        onClose={() => setPermissionsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Manage Permissions - {selectedUser?.name}
        </DialogTitle>
        <DialogContent>
          {/* Add Permission Form */}
          <Box mb={3}>
            <Typography variant="h6" gutterBottom>
              Grant New Permission
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Ward</InputLabel>
                  <Select
                    value={permissionForm.wardId}
                    label="Ward"
                    onChange={(e) =>
                      setPermissionForm({ ...permissionForm, wardId: e.target.value })
                    }
                  >
                    {wards.map((ward) => (
                      <MenuItem key={ward.id} value={ward.id}>
                        {ward.name} ({ward.hospitalName})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={4}>
                <FormControl fullWidth>
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={permissionForm.role}
                    label="Role"
                    onChange={(e) =>
                      setPermissionForm({ ...permissionForm, role: e.target.value })
                    }
                  >
                    {AVAILABLE_ROLES.map((role) => (
                      <MenuItem key={role.value} value={role.value}>
                        {role.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleAddPermission}
                  disabled={!permissionForm.wardId || addPermissionMutation.isPending}
                  sx={{ height: '56px' }}
                >
                  <AddIcon />
                </Button>
              </Grid>
            </Grid>
          </Box>

          <Divider />

          {/* Current Permissions List */}
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Current Permissions
            </Typography>
            {permissionsLoading ? (
              <Typography>Loading permissions...</Typography>
            ) : userPermissions.length === 0 ? (
              <Typography color="textSecondary">
                No permissions assigned yet.
              </Typography>
            ) : (
              <List>
                {userPermissions.map((permission) => (
                  <ListItem key={permission.id} divider>
                    <ListItemText
                      primary={`${permission.wardName}`}
                      secondary={`Role: ${permission.role.charAt(0).toUpperCase() + permission.role.slice(1)}`}
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        edge="end"
                        onClick={() => handleRemovePermission(permission.id)}
                        color="error"
                        disabled={removePermissionMutation.isPending}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPermissionsDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagementPage; 