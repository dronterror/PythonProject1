// Role interface for the roles array
interface Role {
  id: string;
  title: string;
  icon: string;
  description: string;
  gradient: string;
}

interface RoleSelectorProps {
  onRoleSelect: (roleId: string) => void;
}

const roles: Role[] = [
  {
    id: 'nurse',
    title: 'Nurse',
    icon: '👩‍⚕️',
    description: 'Medication administration and patient care',
    gradient: 'from-yellow-400 to-yellow-600',
  },
  {
    id: 'doctor',
    title: 'Doctor',
    icon: '🩺',
    description: 'Prescription management and patient orders',
    gradient: 'from-green-400 to-green-700',
  },
  {
    id: 'pharmacist',
    title: 'Pharmacist',
    icon: '💊',
    description: 'Inventory management and stock alerts',
    gradient: 'from-blue-500 to-blue-900',
  },
  {
    id: 'super_admin',
    title: 'Super Admin',
    icon: '⚙️',
    description: 'System administration and user management',
    gradient: 'from-red-500 to-red-700',
  },
];

const RoleSelector = ({ onRoleSelect }: RoleSelectorProps) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-400 to-purple-600 px-4 text-center">
      <div className="mb-12">
        <div className="text-5xl font-extrabold text-white mb-4 drop-shadow">🏥 MedLogistics</div>
        <h1 className="text-4xl font-extrabold text-white mb-2 drop-shadow">Select Your Role</h1>
        <p className="text-lg text-white/90 max-w-md mx-auto leading-relaxed">Choose your role to access the appropriate medication management interface</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl mb-12">
        {roles.map(role => (
          <button
            key={role.id}
            className={`relative bg-white/90 backdrop-blur rounded-3xl p-8 flex flex-col items-center justify-center min-h-[200px] shadow-lg cursor-pointer transition-all duration-200 hover:-translate-y-2 hover:shadow-2xl focus:outline-none group`}
            onClick={() => onRoleSelect(role.id)}
          >
            <div className={`absolute top-0 left-0 right-0 h-1.5 rounded-t-3xl bg-gradient-to-r ${role.gradient}`}></div>
            <div className="text-5xl mb-4">{role.icon}</div>
            <div className="text-2xl font-bold mb-1 text-gray-900">{role.title}</div>
            <div className="text-base text-gray-600 mb-4">{role.description}</div>
            <div className="text-xl font-bold text-blue-600 group-hover:translate-x-2 transition-transform">→</div>
          </button>
        ))}
      </div>
      <div className="text-white/80 text-sm">
        <p>ValMed Medication Logistics PWA</p>
        <p>Mobile-first medication management system</p>
      </div>
    </div>
  );
};

export default RoleSelector; 