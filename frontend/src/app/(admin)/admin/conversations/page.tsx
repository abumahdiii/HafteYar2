'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminConversations, useUpdateConversation } from '@/hooks/useAdmin';

export default function ConversationsPage() {
  const [page, setPage] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminConversations(page * limit, limit, statusFilter);
  const updateMutation = useUpdateConversation();

  const handleStatusChange = (id: string, newStatus: string) => {
    updateMutation.mutate({ id, data: { status: newStatus } });
  };

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (isError) return <div>خطا در بارگذاری اطلاعات</div>;

  const conversations = data?.items || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مرکز پشتیبانی (تیکت‌ها / مکالمات)</h1>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>فیلتر وضعیت:</span>
          <select 
            value={statusFilter || ''} 
            onChange={(e) => setStatusFilter(e.target.value || undefined)}
            style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)' }}
          >
            <option value="">همه</option>
            <option value="OPEN">باز (OPEN)</option>
            <option value="PENDING">در حال بررسی (PENDING)</option>
            <option value="CLOSED">بسته شده (CLOSED)</option>
          </select>
        </div>
      </div>

      <Card>
        <CardContent>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>شناسه مکالمه</th>
                <th style={{ padding: '12px' }}>شناسه کاربر</th>
                <th style={{ padding: '12px' }}>کانال</th>
                <th style={{ padding: '12px' }}>تگ‌ها</th>
                <th style={{ padding: '12px' }}>تاریخ آخرین پیام</th>
                <th style={{ padding: '12px' }}>وضعیت پشتیبانی</th>
              </tr>
            </thead>
            <tbody>
              {conversations.map((conv: any) => (
                <tr key={conv.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px', color: 'var(--muted)', fontSize: '0.85rem' }}>{conv.id.substring(0, 8)}...</td>
                  <td style={{ padding: '12px', fontSize: '0.85rem' }}>{conv.user_id.substring(0, 8)}...</td>
                  <td style={{ padding: '12px' }}>{conv.channel}</td>
                  <td style={{ padding: '12px' }}>
                    {conv.tags ? conv.tags.join(', ') : '-'}
                  </td>
                  <td style={{ padding: '12px' }}>{new Date(conv.last_message_at).toLocaleString('fa-IR')}</td>
                  <td style={{ padding: '12px' }}>
                    <select
                      value={conv.status}
                      onChange={(e) => handleStatusChange(conv.id, e.target.value)}
                      style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        border: '1px solid var(--border)',
                        background: conv.status === 'OPEN' ? '#fff3e0' : (conv.status === 'CLOSED' ? '#e6f4ea' : '#e8f0fe'),
                        color: conv.status === 'OPEN' ? '#e65100' : (conv.status === 'CLOSED' ? '#137333' : '#1967d2'),
                        fontSize: '0.85rem'
                      }}
                    >
                      <option value="OPEN">باز (OPEN)</option>
                      <option value="PENDING">در انتظار (PENDING)</option>
                      <option value="CLOSED">بسته (CLOSED)</option>
                    </select>
                  </td>
                </tr>
              ))}
              {conversations.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ مکالمه‌ای یافت نشد</td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
