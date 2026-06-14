'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminUsers, useCreateUser, useUpdateUser } from '@/hooks/useAdmin';

export default function UsersPage() {
  const [page, setPage] = useState(0);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminUsers(page * limit, limit);
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();

  const handleCreate = () => {
    const phone = prompt('شماره موبایل کاربر جدید را وارد کنید:');
    if (phone) {
      createMutation.mutate({ phone });
    }
  };

  const handleToggleAdmin = (id: string, current: boolean) => {
    updateMutation.mutate({ id, data: { is_admin: !current } });
  };

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (isError) return <div>خطا در بارگذاری اطلاعات</div>;

  const users = data?.items || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مدیریت کاربران</h1>
        <button 
          onClick={handleCreate}
          style={{ padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px' }}>
          کاربر جدید
        </button>
      </div>

      <Card>
        <CardContent>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>شناسه</th>
                <th style={{ padding: '12px' }}>نام کاربری</th>
                <th style={{ padding: '12px' }}>موبایل</th>
                <th style={{ padding: '12px' }}>نقش</th>
                <th style={{ padding: '12px' }}>تاریخ عضویت</th>
                <th style={{ padding: '12px' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user: any) => (
                <tr key={user.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px', color: 'var(--muted)' }}>{user.id.substring(0, 8)}...</td>
                  <td style={{ padding: '12px' }}>{user.username || '-'}</td>
                  <td style={{ padding: '12px' }} dir="ltr">{user.phone || '-'}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      background: user.is_admin ? '#e8f0fe' : '#f1f3f4',
                      color: user.is_admin ? '#1967d2' : '#3c4043',
                      fontSize: '0.85rem'
                    }}>
                      {user.is_admin ? 'مدیر سیستم' : 'کاربر عادی'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>{new Date(user.created_at).toLocaleDateString('fa-IR')}</td>
                  <td style={{ padding: '12px', display: 'flex', gap: '8px' }}>
                    <button 
                      onClick={() => handleToggleAdmin(user.id, user.is_admin)}
                      style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                      {user.is_admin ? 'لغو دسترسی ادمین' : 'ارتقا به ادمین'}
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ کاربری یافت نشد</td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
