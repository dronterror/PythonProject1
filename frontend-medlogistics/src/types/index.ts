// User and Authentication Types
export interface UserProfile {
  sub: string;
  email: string;
  name: string;
  picture?: string;
  role: 'nurse' | 'doctor' | 'pharmacist' | 'admin';
  nurseId?: string;
  permissions?: string[];
}

// Ward Types
export interface Ward {
  id: string;
  name: string;
  description?: string;
  capacity: number;
  currentOccupancy: number;
  isActive: boolean;
}

// Patient Types
export interface Patient {
  id: string;
  name: string;
  dateOfBirth: string;
  gender: 'male' | 'female' | 'other';
  roomNumber: string;
  bedNumber: string;
  wardId: string;
  admissionDate: string;
  allergies?: string[];
  medicalRecordNumber: string;
}

// Medication Types
export interface Drug {
  id: string;
  name: string;
  form: string;
  strength: string;
  currentStock: number;
  lowStockThreshold: number;
}

// Order Types
export interface MedicationOrder {
  id: string;
  patientName: string;
  patientId: string;
  drugId: string;
  drug?: Drug;
  dosage: number;
  schedule: string;
  frequency: string;
  route: string;
  status: 'active' | 'completed' | 'cancelled' | 'on-hold';
  doctorId: string;
  createdAt: string;
  startDate: string;
  endDate?: string;
  instructions?: string;
  administrations?: Administration[];
}

// Administration Types
export interface Administration {
  id: string;
  orderId: string;
  nurseId: string;
  administrationTime: string;
  dosageGiven: number;
  notes?: string;
  status: 'completed' | 'missed' | 'refused';
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// App State Types
export interface AppState {
  userProfile: UserProfile | null;
  activeWardId: string | null;
  isLoading: boolean;
  error: string | null;
}

// Navigation Types
export interface NavigationItem {
  label: string;
  path: string;
  icon: React.ComponentType;
  badge?: number;
}

// Form Types
export interface AdministrationForm {
  orderId: string;
  dosageGiven: number;
  notes?: string;
  administrationTime: Date;
} 