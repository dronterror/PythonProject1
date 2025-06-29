import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/apiClient';
import { Box, Typography, Autocomplete, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { Drug, MedicationOrder } from '@/types';
import { useForm, Controller, FieldValues } from 'react-hook-form';

interface FormularyDrug extends Drug {
  inventoryStatus: 'in-stock' | 'low-stock' | 'out-of-stock';
}

interface PrescribeFormData {
  drug: FormularyDrug | null;
  patientId: string;
  dosage: string;
  schedule: string;
}

const PrescribePage: React.FC = () => {
  const queryClient = useQueryClient();
  const { control, handleSubmit, watch, formState: { errors } } = useForm<PrescribeFormData>({
    defaultValues: {
      drug: null,
      patientId: 'cde0f175-3752-4770-9add-281b6a48c08a', // Hardcoded patient for demo
      dosage: '',
      schedule: '',
    },
  });

  const selectedDrug = watch('drug');

  const { data: formulary, isLoading: isLoadingFormulary } = useQuery<FormularyDrug[], Error>({
    queryKey: ['formularyWithInventory'],
    queryFn: async () => {
      const drugsResponse = await apiClient.get<Drug[]>('/drugs/formulary');
      const inventoryStatusResponse = await apiClient.get<Record<string, { status: string }>>('/inventory/status');
      
      const drugs = drugsResponse.data;
      const inventoryStatus = inventoryStatusResponse.data;

      return drugs.map((drug: Drug) => ({
        ...drug,
        inventoryStatus: inventoryStatus[drug.id]?.status as FormularyDrug['inventoryStatus'] || 'out-of-stock',
      }));
    },
  });

  const mutation = useMutation<MedicationOrder, Error, Omit<PrescribeFormData, 'drug'> & { drugId: string }>({
    mutationFn: (newOrder) => apiClient.post('/orders', newOrder),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      // Reset form or show success message
    },
  });

  const onSubmit = (data: PrescribeFormData) => {
    if (!data.drug) return;
    mutation.mutate({
      drugId: data.drug.id,
      patientId: data.patientId,
      dosage: data.dosage,
      schedule: data.schedule,
    });
  };

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <Typography variant="h4" gutterBottom>
        Smart Prescribing
      </Typography>
      
      {isLoadingFormulary ? (
        <CircularProgress />
      ) : (
        <Controller
          name="drug"
          control={control}
          rules={{ required: 'Drug selection is required' }}
          render={({ field }: { field: FieldValues }) => (
            <Autocomplete
              {...field}
              options={formulary || []}
              getOptionLabel={(option: FormularyDrug) => `${option.name} (${option.strength})`}
              isOptionEqualToValue={(option: FormularyDrug, value: FormularyDrug) => option.id === value.id}
              onChange={(_event, value) => field.onChange(value)}
              value={field.value}
              renderOption={(props, option: FormularyDrug) => (
                <Box component="li" {...props} key={option.id} sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <Box>
                    <Typography>{option.name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {option.strength} - {option.form}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="caption" sx={{ mr: 1, color: `inventory.${option.inventoryStatus}.text` }}>
                      {option.inventoryStatus.replace('-', ' ')}
                    </Typography>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: `inventory.${option.inventoryStatus}.main`,
                      }}
                    />
                  </Box>
                </Box>
              )}
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  label="Select Drug" 
                  margin="normal"
                  error={!!errors.drug}
                  helperText={errors.drug?.message}
                />
              )}
            />
          )}
        />
      )}
      
      <Controller
        name="dosage"
        control={control}
        rules={{ required: 'Dosage is required' }}
        render={({ field }) => (
          <TextField 
            {...field}
            label="Dosage (e.g., '1 tablet')" 
            fullWidth 
            margin="normal"
            error={!!errors.dosage}
            helperText={errors.dosage?.message}
          />
        )}
      />
      
      <Controller
        name="schedule"
        control={control}
        rules={{ required: 'Schedule is required' }}
        render={({ field }) => (
          <TextField 
            {...field}
            label="Schedule (e.g., 'Twice a day')" 
            fullWidth 
            margin="normal"
            error={!!errors.schedule}
            helperText={errors.schedule?.message}
          />
        )}
      />
      
      <Button type="submit" variant="contained" sx={{ mt: 2 }} disabled={mutation.isPending || !selectedDrug}>
        {mutation.isPending ? <CircularProgress size={24} /> : 'Prescribe'}
      </Button>
      
      {mutation.isError && <Alert severity="error" sx={{ mt: 2 }}>{(mutation.error as Error).message}</Alert>}
      {mutation.isSuccess && <Alert severity="success" sx={{ mt: 2 }}>Order placed successfully!</Alert>}
    </Box>
  );
};

export default PrescribePage; 