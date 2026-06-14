'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminTeams, useCreateTeam, useUpdateTeam, useDeleteTeam } from '@/hooks/useAdmin';

export default function TeamsPage() {
  const [page, setPage] = useState(0);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminTeams(page * limit, limit);
  const createMutation = useCreateTeam();
  const updateMutation = useUpdateTeam();
  const deleteMutation = useDeleteTeam();

  const handleCreate = () => {
    const name = prompt('نام تیم جدید را وارد کنید:');
    if (name) {
      createMutation.mutate({ name });
    }
  };

  const handleToggleActive = (id: string, current: boolean) => {
    updateMutation.mutate({ id, data: { is_active: !current } });
  };

  const handleDelete = (id: string) => {
    if (confirm('آیا از حذف این تیم مطمئن هستید؟')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (isError) return <div>خطا در بارگذاری اطلاعات</div>;

  const teams = data?.items || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مدیریت تیم‌ها</h1>
        <button 
          onClick={handleCreate}
          style={{ padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px' }}>
          تیم جدید
        </button>
      </div>

      <Card>
        <CardContent>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>شناسه</th>
                <th style={{ padding: '12px' }}>نام</th>
                <th style={{ padding: '12px' }}>وضعیت</th>
                <th style={{ padding: '12px' }}>تاریخ ایجاد</th>
                <th style={{ padding: '12px' }}>انقضای اشتراک</th>
                <th style={{ padding: '12px' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((team: any) => (
                <tr key={team.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px', color: 'var(--muted)' }}>{team.id.substring(0, 8)}...</td>
                  <td style={{ padding: '12px' }}>{team.name}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      background: team.is_active ? '#e6f4ea' : '#fce8e6',
                      color: team.is_active ? '#137333' : '#c5221f',
                      fontSize: '0.85rem'
                    }}>
                      {team.is_active ? 'فعال' : 'غیرفعال'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>{new Date(team.created_at).toLocaleDateString('fa-IR')}</td>
                  <td style={{ padding: '12px' }}>{new Date(team.subscription_expiry).toLocaleDateString('fa-IR')}</td>
                  <td style={{ padding: '12px', display: 'flex', gap: '8px' }}>
                    <button 
                      onClick={() => handleToggleActive(team.id, team.is_active)}
                      style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                      {team.is_active ? 'غیرفعال‌سازی' : 'فعال‌سازی'}
                    </button>
                    <button 
                      onClick={() => handleDelete(team.id)}
                      style={{ padding: '4px 8px', background: '#fee2e2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: '4px', fontSize: '0.85rem' }}>
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              {teams.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ تیمی یافت نشد</td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
