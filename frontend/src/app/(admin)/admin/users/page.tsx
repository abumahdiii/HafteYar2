'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminUsers, useCreateUser, useUpdateUser, useToggleUserSubscription } from '@/hooks/useAdmin';

export default function UsersPage() {
  const [page, setPage] = useState(0);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminUsers(page * limit, limit);
  const createMutation = useCreateUser();
  const updateMutation = useUpdateUser();
  const toggleMutation = useToggleUserSubscription();

  const handleCreate = () => {
    const phone = prompt('شماره موبایل کاربر جدید را وارد کنید:');
    if (phone) {
      createMutation.mutate({ phone });
    }
  };

  const handleToggleAdmin = (id: string, current: boolean) => {
    updateMutation.mutate({ id, data: { is_admin: !current } });
  };

  const handleToggleSubscription = (id: string, sub_type: string, is_active: boolean) => {
    let duration_days = 30;
    if (!is_active) {
      const days = prompt(`مدت اشتراک ${sub_type} (به روز) را وارد کنید:`, '30');
      if (!days) return; // Cancelled
      duration_days = parseInt(days, 10) || 30;
    } else {
      if (!confirm(`آیا مطمئن هستید که می‌خواهید اشتراک ${sub_type} را غیرفعال کنید؟`)) return;
    }
    toggleMutation.mutate({ id, data: { sub_type, duration_days } });
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
                <th style={{ padding: '12px' }}>شناسه / نام کاربری</th>
                <th style={{ padding: '12px' }}>موبایل</th>
                <th style={{ padding: '12px' }}>نقش</th>
                <th style={{ padding: '12px' }}>نوع اشتراک</th>
                <th style={{ padding: '12px' }}>پایان اشتراک</th>
                <th style={{ padding: '12px' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user: any) => {
                const hasBasic = user.subscription_type === 'BASIC';
                const hasPro = user.subscription_type === 'PRO';
                
                return (
                <tr key={user.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px' }}>
                    <div>{user.username || '-'}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--muted)' }}>{user.id.substring(0, 8)}...</div>
                  </td>
                  <td style={{ padding: '12px' }} dir="ltr">{user.phone || '-'}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      background: user.is_admin ? '#e8f0fe' : '#f1f3f4',
                      color: user.is_admin ? '#1967d2' : '#3c4043',
                      fontSize: '0.85rem'
                    }}>
                      {user.is_admin ? 'مدیر' : 'کاربر'}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    {user.subscription_type === 'PRO' ? (
                      <span style={{ padding: '4px 8px', background: '#fbbc04', color: 'black', borderRadius: '4px', fontSize: '0.85rem' }}>Pro</span>
                    ) : user.subscription_type === 'BASIC' ? (
                      <span style={{ padding: '4px 8px', background: '#34a853', color: 'white', borderRadius: '4px', fontSize: '0.85rem' }}>پایه</span>
                    ) : (
                      <span style={{ color: 'var(--muted)' }}>-</span>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    {user.subscription_end_date ? new Date(user.subscription_end_date).toLocaleDateString('fa-IR') : '-'}
                  </td>
                  <td style={{ padding: '12px', display: 'flex', gap: '4px', flexWrap: 'wrap', maxWidth: '300px' }}>
                    <button 
                      onClick={() => handleToggleAdmin(user.id, user.is_admin)}
                      style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.8rem' }}>
                      {user.is_admin ? 'لغو ادمین' : 'ارتقا به ادمین'}
                    </button>
                    <button 
                      onClick={() => handleToggleSubscription(user.id, 'BASIC', hasBasic)}
                      style={{ padding: '4px 8px', background: hasBasic ? '#ea4335' : '#34a853', color: 'white', border: 'none', borderRadius: '4px', fontSize: '0.8rem' }}>
                      {hasBasic ? 'لغو اشتراک پایه' : 'فعال‌سازی اشتراک پایه'}
                    </button>
                    <button 
                      onClick={() => handleToggleSubscription(user.id, 'PRO', hasPro)}
                      style={{ padding: '4px 8px', background: hasPro ? '#ea4335' : '#fbbc04', color: hasPro ? 'white' : 'black', border: 'none', borderRadius: '4px', fontSize: '0.8rem' }}>
                      {hasPro ? 'لغو اشتراک Pro' : 'فعال‌سازی اشتراک Pro'}
                    </button>
                  </td>
                </tr>
              )})}
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
