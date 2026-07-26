import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Building2, Save } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

const orgSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address').optional().or(z.literal('')),
  phone: z.string().optional(),
  country: z.string().optional(),
  timezone: z.string().min(1, 'Timezone is required'),
});

type OrgFormValues = z.infer<typeof orgSchema>;

export function OrgProfile() {
  const { addNotification } = useNotification();
  const [loading, setLoading] = useState(false);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(orgSchema),
    defaultValues: {
      name: '',
      email: '',
      phone: '',
      country: '',
      timezone: 'UTC',
    },
  });

  useEffect(() => {
    const fetchOrg = async () => {
      try {
        const response = await apiClient.get('/api/v1/organizations/me');
        const data = response.data.data;
        if (data) {
          setValue('name', data.name || '');
          setValue('email', data.email || '');
          setValue('phone', data.phone || '');
          setValue('country', data.country || '');
          setValue('timezone', data.timezone || 'UTC');
          setLogoUrl(data.logo || null);
        }
      } catch (err) {
        console.error('Failed to load organization profile', err);
      }
    };
    fetchOrg();
  }, [setValue]);

  const onSubmit = async (values: OrgFormValues) => {
    setLoading(true);
    try {
      await apiClient.put('/api/v1/organizations/me', values);
      addNotification('Organization profile updated successfully', 'success');
    } catch (err: any) {
      addNotification(err.message || 'Failed to update organization profile', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Organization Profile</h1>
        <p className="text-sm text-muted-foreground">Manage corporate metadata, address registries, and timezone specifications.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-primary" />
              General Details
            </CardTitle>
            <CardDescription>Setup metadata profiles, contact lines, and active timezones.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Company Name"
                  {...register('name')}
                  error={errors.name?.message as string}
                />
                <Input
                  label="Support Email Address"
                  type="email"
                  {...register('email')}
                  error={errors.email?.message as string}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Contact Phone"
                  {...register('phone')}
                  error={errors.phone?.message as string}
                />
                <Input
                  label="Headquarters Country"
                  {...register('country')}
                  error={errors.country?.message as string}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Primary Timezone"
                  {...register('timezone')}
                  error={errors.timezone?.message as string}
                />
              </div>

              <Button type="submit" disabled={loading} variant="primary" className="flex items-center gap-2">
                <Save className="h-4 w-4" />
                {loading ? 'Saving...' : 'Save Profile Details'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Branding & Logo</CardTitle>
            <CardDescription>Upload corporate brand logo assets</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center p-6 space-y-4">
            <div className="h-32 w-32 rounded border border-border flex items-center justify-center bg-secondary/20 overflow-hidden relative group">
              {logoUrl ? (
                <img src={logoUrl} alt="Logo" className="object-cover h-full w-full" />
              ) : (
                <Building2 className="h-12 w-12 text-muted-foreground" />
              )}
            </div>
            <div className="text-center text-xs text-muted-foreground">
              <p>Supports PNG, JPG assets up to 2MB.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default OrgProfile;
