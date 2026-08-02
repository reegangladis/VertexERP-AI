import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Modal } from '@/components/Modal';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';
import { Calendar, Plus, Save, Clock, CalendarDays } from 'lucide-react';

interface BusinessCalendar {
  id: string;
  name: string;
  year: number;
  is_active: boolean;
}

interface WorkingDay {
  id: string;
  day_of_week: number;
  is_working: boolean;
  start_time: string;
  end_time: string;
}

interface Holiday {
  id: string;
  name: string;
  date: string;
  type: string;
  description: string | null;
}

export function OrgBusinessCalendar() {
  const { addNotification } = useNotification();
  const [calendars, setCalendars] = useState<BusinessCalendar[]>([]);
  const [selectedCalendar, setSelectedCalendar] = useState<BusinessCalendar | null>(null);
  const [workingDays, setWorkingDays] = useState<WorkingDay[]>([]);
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [newCalendarName, setNewCalendarName] = useState('');
  const [newCalendarYear, setNewCalendarYear] = useState(2026);

  // New Holiday form
  const [holidayName, setHolidayName] = useState('');
  const [holidayDate, setHolidayDate] = useState('');
  const [holidayType, setHolidayType] = useState('public');

  const fetchCalendars = async () => {
    try {
      const res = await apiClient.get('/api/v1/business-calendar');
      const data = res.data.data || [];
      setCalendars(data);
      if (data.length > 0 && !selectedCalendar) {
        // Auto-select active or first
        const active = data.find((c: BusinessCalendar) => c.is_active) || data[0];
        setSelectedCalendar(active);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchCalendarDetails = async (calendarId: string) => {
    try {
      const [daysRes, holRes] = await Promise.all([
        apiClient.get(`/api/v1/business-calendar/${calendarId}/working-days`),
        apiClient.get(`/api/v1/business-calendar/${calendarId}/holidays`),
      ]);
      setWorkingDays(daysRes.data.data || []);
      setHolidays(holRes.data.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchCalendars();
  }, []);

  useEffect(() => {
    if (selectedCalendar) {
      fetchCalendarDetails(selectedCalendar.id);
    }
  }, [selectedCalendar]);

  const handleCreateCalendar = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.post('/api/v1/business-calendar', {
        name: newCalendarName,
        year: newCalendarYear,
        is_active: true,
      });
      addNotification('Calendar created successfully', 'success');
      setModalOpen(false);
      setNewCalendarName('');
      setSelectedCalendar(res.data.data);
      fetchCalendars();
    } catch (err: any) {
      addNotification(err.message || 'Operation failed', 'error');
    }
  };

  const handleSaveWorkingDays = async () => {
    if (!selectedCalendar) return;
    try {
      // Map working days payload
      const payload = workingDays.map((d) => ({
        day_of_week: d.day_of_week,
        is_working: d.is_working,
        start_time: d.start_time,
        end_time: d.end_time,
      }));
      await apiClient.post(`/api/v1/business-calendar/${selectedCalendar.id}/working-days`, payload);
      addNotification('Working days settings saved', 'success');
    } catch (err: any) {
      addNotification(err.message || 'Save failed', 'error');
    }
  };

  const handleAddHoliday = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCalendar) return;
    try {
      const updatedHolidays = [...holidays, { name: holidayName, date: holidayDate, type: holidayType, description: '' }];
      const payload = updatedHolidays.map((h) => ({
        name: h.name,
        date: h.date,
        type: h.type,
      }));
      await apiClient.post(`/api/v1/business-calendar/${selectedCalendar.id}/holidays`, payload);
      addNotification('Holiday added successfully', 'success');
      setHolidayName('');
      setHolidayDate('');
      fetchCalendarDetails(selectedCalendar.id);
    } catch (err: any) {
      addNotification(err.message || 'Failed to add holiday', 'error');
    }
  };

  const handleWorkingDayChange = (index: number, key: string, value: any) => {
    const updated = [...workingDays];
    updated[index] = { ...updated[index], [key]: value };
    setWorkingDays(updated);
  };

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Business Calendars</h1>
          <p className="text-sm text-muted-foreground">Setup corporate working days, weekend exclusions, and company holidays.</p>
        </div>
        <div>
          <Button onClick={() => setModalOpen(true)} variant="primary" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create Calendar
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left List */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Calendar List</CardTitle>
            <CardDescription>Fiscal year calendars</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {calendars.length === 0 ? (
              <p className="text-xs text-muted-foreground">No calendars created.</p>
            ) : (
              calendars.map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedCalendar(c)}
                  className={`w-full text-left p-3 rounded border text-xs font-semibold flex items-center justify-between cursor-pointer transition-colors ${
                    selectedCalendar?.id === c.id
                      ? 'border-primary bg-primary/5 text-foreground'
                      : 'border-border bg-card hover:bg-secondary/40 text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-primary" />
                    {c.name}
                  </span>
                  {c.is_active && (
                    <span className="text-[8px] bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-1 py-0.5 rounded font-mono font-semibold uppercase">
                      Active
                    </span>
                  )}
                </button>
              ))
            )}
          </CardContent>
        </Card>

        {/* Right Details */}
        <div className="lg:col-span-3 space-y-6">
          {selectedCalendar ? (
            <>
              {/* Working Days */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5 text-primary" />
                      Weekly Shift Pattern
                    </CardTitle>
                    <CardDescription>Configure active working days and default shift start/end hours.</CardDescription>
                  </div>
                  <Button onClick={handleSaveWorkingDays} variant="primary" className="flex items-center gap-2">
                    <Save className="h-4 w-4" />
                    Save Shift Pattern
                  </Button>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {workingDays.map((day, idx) => (
                      <div
                        key={day.id}
                        className="flex items-center justify-between p-3 border border-border rounded bg-secondary/10"
                      >
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={day.is_working}
                            onChange={(e) => handleWorkingDayChange(idx, 'is_working', e.target.checked)}
                            className="rounded border-border text-primary focus:ring-ring h-4 w-4 cursor-pointer"
                          />
                          <span className="text-xs font-semibold">{dayNames[day.day_of_week]}</span>
                        </div>
                        {day.is_working && (
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={day.start_time}
                              onChange={(e) => handleWorkingDayChange(idx, 'start_time', e.target.value)}
                              className="h-8 w-16 border border-input rounded bg-background px-2 text-xs font-mono text-center focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                            <span className="text-xs text-muted-foreground">to</span>
                            <input
                              type="text"
                              value={day.end_time}
                              onChange={(e) => handleWorkingDayChange(idx, 'end_time', e.target.value)}
                              className="h-8 w-16 border border-input rounded bg-background px-2 text-xs font-mono text-center focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Holidays */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CalendarDays className="h-5 w-5 text-primary" />
                    Holiday Directory
                  </CardTitle>
                  <CardDescription>Configure public holidays, company days off, or leave calendar placeholders.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Add Holiday Form */}
                  <form onSubmit={handleAddHoliday} className="grid grid-cols-1 md:grid-cols-4 gap-3 bg-secondary/15 p-4 rounded border border-border">
                    <div className="flex flex-col space-y-1">
                      <label className="text-[10px] font-semibold uppercase text-muted-foreground">Holiday Name</label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. New Year's Day"
                        value={holidayName}
                        onChange={(e) => setHolidayName(e.target.value)}
                        className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>
                    <div className="flex flex-col space-y-1">
                      <label className="text-[10px] font-semibold uppercase text-muted-foreground">Holiday Date</label>
                      <input
                        type="date"
                        required
                        value={holidayDate}
                        onChange={(e) => setHolidayDate(e.target.value)}
                        className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                      />
                    </div>
                    <div className="flex flex-col space-y-1">
                      <label className="text-[10px] font-semibold uppercase text-muted-foreground">Type</label>
                      <select
                        value={holidayType}
                        onChange={(e) => setHolidayType(e.target.value)}
                        className="h-9 border border-input rounded bg-background px-3 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                      >
                        <option value="public">Public Holiday</option>
                        <option value="company">Company Holiday</option>
                        <option value="leave">Leave Calendar Placeholder</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <Button type="submit" variant="secondary" className="w-full h-9 flex items-center justify-center gap-1.5 text-xs font-semibold">
                        <Plus className="h-4 w-4" /> Add Holiday
                      </Button>
                    </div>
                  </form>

                  {/* Holidays List */}
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left border-collapse">
                      <thead>
                        <tr className="border-b border-border text-muted-foreground uppercase font-mono text-[10px]">
                          <th className="py-2.5 px-3">Date</th>
                          <th className="py-2.5 px-3">Holiday Name</th>
                          <th className="py-2.5 px-3">Type</th>
                        </tr>
                      </thead>
                      <tbody>
                        {holidays.length === 0 ? (
                          <tr>
                            <td colSpan={3} className="py-6 text-center text-muted-foreground">
                              No holidays registered yet.
                            </td>
                          </tr>
                        ) : (
                          holidays.map((h) => (
                            <tr key={h.id} className="border-b border-border hover:bg-secondary/5">
                              <td className="py-3 px-3 font-mono">{h.date}</td>
                              <td className="py-3 px-3 font-semibold">{h.name}</td>
                              <td className="py-3 px-3">
                                <span className={`inline-block px-2 py-0.5 rounded text-[9px] uppercase font-mono font-semibold ${
                                  h.type === 'public' ? 'bg-indigo-500/10 text-indigo-500' : 'bg-amber-500/10 text-amber-500'
                                }`}>
                                  {h.type}
                                </span>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </>
          ) : (
            <div className="flex justify-center items-center h-48 border border-dashed border-border rounded text-muted-foreground text-xs">
              Create or select a calendar of the corporate configuration.
            </div>
          )}
        </div>
      </div>

      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Create New Calendar">
        <form onSubmit={handleCreateCalendar} className="space-y-4">
          <Input
            label="Calendar Name"
            value={newCalendarName}
            onChange={(e) => setNewCalendarName(e.target.value)}
            required
          />
          <Input
            label="Year"
            type="number"
            value={newCalendarYear}
            onChange={(e) => setNewCalendarYear(parseInt(e.target.value))}
            required
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="submit" variant="primary">Create</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
export default OrgBusinessCalendar;
