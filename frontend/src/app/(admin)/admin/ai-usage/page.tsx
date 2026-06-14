'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminAIUsageLogs } from '@/hooks/useAdmin';

export default function AIUsagePage() {
  const [page, setPage] = useState(0);
  const [providerFilter, setProviderFilter] = useState<string | undefined>(undefined);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminAIUsageLogs(page * limit, limit, providerFilter);

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (isError) return <div>خطا در بارگذاری اطلاعات</div>;

  const logs = data?.items || [];
  const totalCost = logs.reduce((acc: number, log: any) => acc + log.cost, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مانیتورینگ مصرف هوش‌مصنوعی</h1>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.9rem', color: 'var(--muted)' }}>ارائه‌دهنده:</span>
          <input 
            type="text"
            placeholder="مثلا openai"
            value={providerFilter || ''} 
            onChange={(e) => setProviderFilter(e.target.value || undefined)}
            style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--background)' }}
            dir="ltr"
          />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <Card>
          <CardContent style={{ padding: '16px' }}>
            <div style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>مجموع رکوردها</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: '8px' }}>{data?.total || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent style={{ padding: '16px' }}>
            <div style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>هزینه کل نمایش داده شده (دلار)</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 600, marginTop: '8px', color: '#137333' }}>
              ${totalCost.toFixed(5)}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>ارائه‌دهنده / مدل</th>
                <th style={{ padding: '12px' }}>نوع درخواست</th>
                <th style={{ padding: '12px' }}>شناسه تیم / کاربر</th>
                <th style={{ padding: '12px' }}>توکن‌های ورودی</th>
                <th style={{ padding: '12px' }}>توکن‌های خروجی</th>
                <th style={{ padding: '12px' }}>هزینه ($)</th>
                <th style={{ padding: '12px' }}>تاریخ</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log: any) => (
                <tr key={log.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px' }} dir="ltr">
                    <span style={{ fontWeight: 600 }}>{log.provider}</span><br/>
                    <span style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{log.model}</span>
                  </td>
                  <td style={{ padding: '12px' }}>{log.request_type}</td>
                  <td style={{ padding: '12px', fontSize: '0.85rem' }}>
                    {log.team_id ? `تیم: ${log.team_id.substring(0, 8)}...` : (log.user_id ? `کاربر: ${log.user_id.substring(0, 8)}...` : '-')}
                  </td>
                  <td style={{ padding: '12px' }}>{log.prompt_tokens.toLocaleString('en-US')}</td>
                  <td style={{ padding: '12px' }}>{log.completion_tokens.toLocaleString('en-US')}</td>
                  <td style={{ padding: '12px', color: '#137333', fontWeight: 500 }}>
                    ${log.cost.toFixed(5)}
                  </td>
                  <td style={{ padding: '12px', fontSize: '0.85rem' }}>{new Date(log.created_at).toLocaleString('fa-IR')}</td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ لاگ مصرفی یافت نشد</td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
