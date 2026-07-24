import React, { useState } from 'react';
import {
  Users,
  Shield,
  Key,
  Plus,
  Search,
  SlidersHorizontal,
  Edit2,
  Trash2,
  Lock,
  Unlock,
  Check,
  X,
  Copy,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { Modal } from '@/components/Modal';
import { Alert } from '@/components/Alert';
import { PageHeader } from '@/components/PageHeader';
import { useNotification } from '@/hooks/useNotification';

// 1. USER MANAGEMENT DASHBOARD
export function UserManagement() {
  const { addNotification } = useNotification();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditRolesOpen, setIsEditRolesOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<any>(null);

  const [users, setUsers] = useState<any[]>([
    {
      id: '1',
      name: 'Reegangladis',
      email: 'admin@vertexerp.ai',
      roles: ['Super Admin', 'Organization Admin'],
      status: 'active',
      lastLogin: '2026-07-24 15:45 UTC',
    },
    {
      id: '2',
      name: 'Emma Stone',
      email: 'emma.stone@acme.com',
      roles: ['Manager'],
      status: 'active',
      lastLogin: '2026-07-23 09:20 UTC',
    },
    {
      id: '3',
      name: 'Dave Grohl',
      email: 'dave.grohl@acme.com',
      roles: ['Employee'],
      status: 'inactive',
      lastLogin: '2026-07-10 18:30 UTC',
    },
  ]);

  const [newUser, setNewUser] = useState({
    firstName: '',
    lastName: '',
    username: '',
    email: '',
    role: 'Employee',
  });

  const handleToggleStatus = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) => {
        if (u.id === userId) {
          const newStatus = u.status === 'active' ? 'suspended' : 'active';
          addNotification(`User ${u.name} has been ${newStatus === 'active' ? 'activated' : 'suspended'}`, 'info');
          return { ...u, status: newStatus };
        }
        return u;
      })
    );
  };

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    const created = {
      id: Math.random().toString(36).substring(2, 9),
      name: `${newUser.firstName} ${newUser.lastName}`,
      email: newUser.email,
      roles: [newUser.role],
      status: 'active',
      lastLogin: 'Never',
    };
    setUsers((prev) => [...prev, created]);
    setIsCreateOpen(false);
    addNotification(`User account created successfully`, 'success');
  };

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || user.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="User Administration"
        description="Configure identities, statuses, and role associations for user accounts."
        actions={
          <Button variant="primary" leftIcon={<Plus className="h-4 w-4" />} onClick={() => setIsCreateOpen(true)}>
            Add User
          </Button>
        }
      />

      {/* Filters Bar */}
      <div className="flex flex-col md:flex-row items-center gap-4 bg-secondary/20 p-4 rounded-lg border border-border">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <input
            placeholder="Search users name, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="h-10 w-full pl-9 border border-input rounded-md bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground shrink-0" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="h-10 border border-input rounded-md bg-background px-3 text-sm text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="suspended">Suspended</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Users table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>User Profile</TableHead>
            <TableHead>Assigned Roles</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Last Audited Access</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredUsers.map((user) => (
            <TableRow key={user.id}>
              <TableCell>
                <div className="flex flex-col">
                  <span className="font-semibold text-foreground">{user.name}</span>
                  <span className="text-xs text-muted-foreground">{user.email}</span>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {user.roles.map((r: string) => (
                    <span key={r} className="text-[10px] px-1.5 py-0.5 border border-border rounded bg-secondary font-mono">
                      {r}
                    </span>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <span
                  className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
                    user.status === 'active'
                      ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                      : 'bg-red-500/10 text-red-500 border border-red-500/20'
                  }`}
                >
                  {user.status}
                </span>
              </TableCell>
              <TableCell className="text-muted-foreground text-xs font-mono">{user.lastLogin}</TableCell>
              <TableCell className="text-right">
                <div className="inline-flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="p-1.5 h-auto w-auto rounded text-muted-foreground hover:text-foreground"
                    title="Edit Roles"
                    onClick={() => {
                      setSelectedUser(user);
                      setIsEditRolesOpen(true);
                    }}
                  >
                    <Edit2 className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className={`p-1.5 h-auto w-auto rounded ${
                      user.status === 'active' ? 'text-amber-500' : 'text-emerald-500'
                    }`}
                    title={user.status === 'active' ? 'Suspend User' : 'Activate User'}
                    onClick={() => handleToggleStatus(user.id)}
                  >
                    {user.status === 'active' ? <Lock className="h-3.5 w-3.5" /> : <Unlock className="h-3.5 w-3.5" />}
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* Modal - Create User */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Register User Account">
        <form onSubmit={handleCreateUser} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="First Name"
              required
              value={newUser.firstName}
              onChange={(e) => setNewUser((prev) => ({ ...prev, firstName: e.target.value }))}
            />
            <Input
              label="Last Name"
              required
              value={newUser.lastName}
              onChange={(e) => setNewUser((prev) => ({ ...prev, lastName: e.target.value }))}
            />
          </div>
          <Input
            label="Username"
            required
            value={newUser.username}
            onChange={(e) => setNewUser((prev) => ({ ...prev, username: e.target.value }))}
          />
          <Input
            label="Email Address"
            type="email"
            required
            value={newUser.email}
            onChange={(e) => setNewUser((prev) => ({ ...prev, email: e.target.value }))}
          />
          <div className="flex flex-col space-y-1.5">
            <label className="text-sm font-medium">Initial Role Mapping</label>
            <select
              value={newUser.role}
              onChange={(e) => setNewUser((prev) => ({ ...prev, role: e.target.value }))}
              className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="Employee">Employee</option>
              <option value="Manager">Manager</option>
              <option value="HR">HR</option>
              <option value="Finance">Finance</option>
            </select>
          </div>
          <div className="flex items-center justify-end gap-2 pt-4">
            <Button variant="outline" type="button" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Register User
            </Button>
          </div>
        </form>
      </Modal>

      {/* Modal - Edit Roles */}
      <Modal isOpen={isEditRolesOpen} onClose={() => setIsEditRolesOpen(false)} title={`Modify Roles: ${selectedUser?.name}`}>
        <div className="space-y-4">
          <p className="text-xs text-muted-foreground">Select system roles associated with this account:</p>
          <div className="grid grid-cols-2 gap-3 pt-2">
            {['Super Admin', 'Organization Admin', 'Manager', 'HR', 'Finance', 'Employee'].map((role) => (
              <label key={role} className="flex items-center gap-2 text-sm text-foreground cursor-pointer select-none">
                <input
                  type="checkbox"
                  defaultChecked={selectedUser?.roles.includes(role)}
                  className="rounded border-border text-primary focus:ring-ring h-4 w-4"
                />
                <span>{role}</span>
              </label>
            ))}
          </div>
          <div className="flex items-center justify-end gap-2 pt-6">
            <Button variant="outline" onClick={() => setIsEditRolesOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setIsEditRolesOpen(false);
                addNotification('Roles updated successfully', 'success');
              }}
            >
              Save Configuration
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

// 2. ROLE MANAGEMENT
export function RoleManagement() {
  const { addNotification } = () => ({ addNotification: (m: string, s: string) => {} }); // local ref
  const notification = useNotification();
  const [isCloneOpen, setIsCloneOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<any>(null);

  const [roles, setRoles] = useState<any[]>([
    { id: '1', name: 'Super Admin', desc: 'Root permissions override control.', type: 'default', priority: 10 },
    { id: '2', name: 'Organization Admin', desc: 'Manage users, settings, settings.', type: 'default', priority: 8 },
    { id: '3', name: 'Manager', desc: 'Operational dashboard reviewer.', type: 'default', priority: 5 },
    { id: '4', name: 'Employee', desc: 'Basic user portal.', type: 'default', priority: 2 },
  ]);

  const [cloneName, setCloneName] = useState('');

  const handleCloneRole = (e: React.FormEvent) => {
    e.preventDefault();
    const cloned = {
      id: Math.random().toString(36).substring(2, 9),
      name: cloneName,
      desc: `Cloned authorization permissions schema from ${selectedRole.name}`,
      type: 'custom',
      priority: selectedRole.priority,
    };
    setRoles((prev) => [...prev, cloned]);
    setIsCloneOpen(false);
    notification.addNotification(`Role cloned successfully as ${cloneName}`, 'success');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Role Mapping"
        description="Configure default, custom, and priority-mapped system roles."
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {roles.map((role) => (
          <Card key={role.id} hoverable>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="space-y-1">
                <CardTitle className="text-base flex items-center gap-2">
                  {role.name}
                  <span
                    className={`text-[9px] uppercase px-1 border rounded scale-90 ${
                      role.type === 'default'
                        ? 'bg-primary/10 text-primary border-primary/20'
                        : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                    }`}
                  >
                    {role.type}
                  </span>
                </CardTitle>
                <CardDescription className="text-xs">{role.desc}</CardDescription>
              </div>
              <Shield className="h-5 w-5 text-muted-foreground/60 shrink-0" />
            </CardHeader>
            <CardContent className="pt-2 flex items-center justify-between">
              <span className="text-[10px] text-muted-foreground font-mono">Priority Index: {role.priority}</span>
              <Button
                variant="outline"
                size="sm"
                className="h-8 px-2 text-xs"
                leftIcon={<Copy className="h-3 w-3" />}
                onClick={() => {
                  setSelectedRole(role);
                  setCloneName(`${role.name} (Copy)`);
                  setIsCloneOpen(true);
                }}
              >
                Clone Role
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modal - Clone Role */}
      <Modal isOpen={isCloneOpen} onClose={() => setIsCloneOpen(false)} title={`Clone Role: ${selectedRole?.name}`}>
        <form onSubmit={handleCloneRole} className="space-y-4">
          <Input
            label="Custom Role Name"
            required
            value={cloneName}
            onChange={(e) => setCloneName(e.target.value)}
          />
          <div className="flex items-center justify-end gap-2 pt-4">
            <Button variant="outline" type="button" onClick={() => setIsCloneOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Save custom Role
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

// 3. PERMISSION MATRIX
export function PermissionManagement() {
  const notification = useNotification();
  const [activeTab, setActiveTab] = useState('matrix');

  const categories = ['users', 'roles', 'hr', 'finance', 'inventory', 'admin'];
  const permissions = [
    { name: 'users.read', category: 'users' },
    { name: 'users.create', category: 'users' },
    { name: 'users.update', category: 'users' },
    { name: 'users.delete', category: 'users' },
    { name: 'roles.read', category: 'roles' },
    { name: 'roles.manage', category: 'roles' },
    { name: 'hr.read', category: 'hr' },
    { name: 'finance.update', category: 'finance' },
    { name: 'inventory.manage', category: 'inventory' },
    { name: 'admin.full', category: 'admin' },
  ];

  const rolesList = ['Super Admin', 'Organization Admin', 'Manager', 'Employee'];

  const matrix: Record<string, string[]> = {
    'Super Admin': permissions.map((p) => p.name),
    'Organization Admin': ['users.read', 'users.create', 'users.update', 'roles.read', 'hr.read'],
    'Manager': ['users.read', 'roles.read', 'hr.read'],
    'Employee': ['users.read'],
  };

  const [rolePermissionsMatrix, setRolePermissionsMatrix] = useState(matrix);

  const handleTogglePermission = (role: string, perm: string) => {
    setRolePermissionsMatrix((prev) => {
      const active = prev[role] || [];
      const updated = active.includes(perm) ? active.filter((p) => p !== perm) : [...active, perm];
      notification.addNotification(`Modified permission ${perm} for role ${role}`, 'info');
      return { ...prev, [role]: updated };
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Permission Matrix"
        description="Verify system authorization rules across organizational roles."
      />

      <div className="overflow-x-auto border border-border rounded-lg bg-card shadow-sm">
        <table className="w-full text-sm text-left border-collapse">
          <thead className="bg-muted/30 border-b border-border">
            <tr>
              <th className="p-4 font-semibold text-muted-foreground w-1/4">System Permissions</th>
              {rolesList.map((role) => (
                <th key={role} className="p-4 font-semibold text-foreground text-center">
                  {role}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {categories.map((category) => (
              <React.Fragment key={category}>
                {/* Category Header Row */}
                <tr className="bg-secondary/40 font-mono text-[10px] uppercase tracking-wider text-muted-foreground select-none">
                  <td colSpan={rolesList.length + 1} className="p-2 pl-4">
                    Category: {category}
                  </td>
                </tr>
                {permissions
                  .filter((p) => p.category === category)
                  .map((p) => (
                    <tr key={p.name} className="hover:bg-muted/10">
                      <td className="p-4">
                        <div className="flex flex-col">
                          <span className="font-medium text-foreground">{p.name}</span>
                          <span className="text-[10px] text-muted-foreground">Standard access scope</span>
                        </div>
                      </td>
                      {rolesList.map((role) => {
                        const isGranted = (rolePermissionsMatrix[role] || []).includes(p.name);
                        const isSuper = role === 'Super Admin';
                        return (
                          <td key={role} className="p-4 text-center">
                            <button
                              disabled={isSuper}
                              onClick={() => handleTogglePermission(role, p.name)}
                              className={`p-1.5 rounded-full border transition-all ${
                                isGranted
                                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500 hover:bg-emerald-500/25'
                                  : 'bg-secondary/40 border-border text-muted-foreground hover:bg-secondary'
                              } ${isSuper ? 'cursor-not-allowed opacity-80' : 'cursor-pointer'}`}
                            >
                              {isGranted ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
                            </button>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
