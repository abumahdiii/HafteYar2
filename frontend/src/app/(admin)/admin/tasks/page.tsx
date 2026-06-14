'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminTasks, useDeleteAdminTask } from '@/hooks/useAdmin';

export default function TasksPage() {
  const [page, setPage] = useState(0);
  const limit = 50;
  
  const { data, isLoading, isError } = useAdminTasks(page * limit, limit);
  const deleteMutation = useDeleteAdminTask();

  const handleDelete = (id: string) => {
    if (confirm('آیا از حذف این تسک مطمئن هستید؟ این عملیات غیرقابل بازگشت است.')) {
      deleteMutation.mutate(id);
    }
  };

  if (isLoading) return <div>در حال بارگذاری...</div>;
  if (isError) return <div>خطا در بارگذاری اطلاعات</div>;

  const tasks = data?.items || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مدیریت و نظارت بر تسک‌ها</h1>
      </div>

      <Card>
        <CardContent>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '12px' }}>شناسه</th>
                <th style={{ padding: '12px' }}>عنوان تسک</th>
                <th style={{ padding: '12px' }}>وضعیت</th>
                <th style={{ padding: '12px' }}>اولویت</th>
                <th style={{ padding: '12px' }}>تاریخ ایجاد</th>
                <th style={{ padding: '12px' }}>مهلت</th>
                <th style={{ padding: '12px' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task: any) => (
                <tr key={task.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '12px', color: 'var(--muted)', fontSize: '0.85rem' }}>{task.id.substring(0, 8)}...</td>
                  <td style={{ padding: '12px' }}>{task.title}</td>
                  <td style={{ padding: '12px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      background: task.status === 'DONE' ? '#e6f4ea' : (task.status === 'IN_PROGRESS' ? '#e8f0fe' : '#f1f3f4'),
                      color: task.status === 'DONE' ? '#137333' : (task.status === 'IN_PROGRESS' ? '#1967d2' : '#3c4043'),
                      fontSize: '0.85rem'
                    }}>
                      {task.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px' }}>
                    {task.priority === 0 ? 'معمولی' : (task.priority > 0 ? 'بالا' : 'پایین')}
                  </td>
                  <td style={{ padding: '12px' }}>{new Date(task.created_at).toLocaleDateString('fa-IR')}</td>
                  <td style={{ padding: '12px' }}>{task.due_date ? new Date(task.due_date).toLocaleDateString('fa-IR') : '-'}</td>
                  <td style={{ padding: '12px' }}>
                    <button 
                      onClick={() => handleDelete(task.id)}
                      style={{ padding: '4px 8px', background: '#fee2e2', color: '#991b1b', border: '1px solid #fecaca', borderRadius: '4px', fontSize: '0.85rem' }}>
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              {tasks.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ تسکی یافت نشد</td>
                </tr>
              )}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
