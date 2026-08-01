import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, MapPin, Grid, Layers, HardDrive, Plus, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

interface Bin {
  id: string;
  zone: string;
  rack: string;
  shelf: string;
  bin_code: string;
}

interface Warehouse {
  id: string;
  name: string;
  code: string;
  address: string | null;
  capacity_cubic_meters: number | null;
}

export function InventoryWarehouseDetails() {
  const { id } = useParams<{ id: string }>();
  const { addNotification } = useNotification();
  const [warehouse, setWarehouse] = useState<Warehouse | null>(null);
  const [bins, setBins] = useState<Bin[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const [warRes, binRes] = await Promise.all([
          apiClient.get(`/api/v1/inventory/warehouses/${id}`),
          apiClient.get(`/api/v1/inventory/warehouses/bins?warehouse_id=${id}`),
        ]);
        setWarehouse(warRes.data.data || null);
        setBins(binRes.data.data || []);
      } catch (err) {
        console.error("Failed to load warehouse details", err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!warehouse) {
    return (
      <div className="space-y-4">
        <Link to="/inventory/warehouses" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Warehouses
        </Link>
        <div className="p-8 border border-dashed rounded text-center text-muted-foreground text-sm">
          Warehouse facility profile not found.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/inventory/warehouses" className="flex items-center gap-1.5 text-xs text-primary hover:underline">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Warehouses
        </Link>
        <span className="font-mono text-xs uppercase text-muted-foreground">Facility ID: {warehouse.id}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Info Card */}
        <Card className="md:col-span-1">
          <CardContent className="pt-6 space-y-4">
            <div>
              <h2 className="text-lg font-bold text-foreground">{warehouse.name}</h2>
              <p className="text-xs text-muted-foreground font-mono uppercase">Code: {warehouse.code}</p>
            </div>
            
            <div className="border-t border-border pt-4 space-y-3 text-xs">
              <div className="flex items-center gap-2 text-muted-foreground">
                <MapPin className="h-3.5 w-3.5 shrink-0" />
                <span>Address: {warehouse.address || 'Malibu, CA'}</span>
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <HardDrive className="h-3.5 w-3.5 shrink-0" />
                <span>Capacity Space: {warehouse.capacity_cubic_meters || 'N/A'} m³</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Layout Bins Grid */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Storage Layout Bins</CardTitle>
            <CardDescription>Configure zones, racks, and shelving bin locations codes.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {bins.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">No bins logged for this warehouse. Seed enterprise data to verify.</p>
            ) : (
              bins.map((b) => (
                <div key={b.id} className="p-3 border border-border rounded bg-secondary/15 flex justify-between items-center text-xs">
                  <div>
                    <p className="font-semibold text-primary">Bin Code: {b.bin_code}</p>
                    <p className="text-[10px] text-muted-foreground">Zone {b.zone} • Rack {b.rack} • Shelf {b.shelf}</p>
                  </div>
                  <Grid className="h-4 w-4 text-muted-foreground" />
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
export default InventoryWarehouseDetails;
