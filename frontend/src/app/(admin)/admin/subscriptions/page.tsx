'use client';

import React from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminSubscriptions, useAdminSubscriptionPlans, useCreateSubscriptionPlan, useUpdateSubscriptionPlan } from '@/hooks/useAdmin';

export default function SubscriptionsPage() {
  const { data: plans, isLoading: isPlansLoading } = useAdminSubscriptionPlans();
  const { data: subscriptions, isLoading: isSubsLoading } = useAdminSubscriptions();
  
  const createPlanMutation = useCreateSubscriptionPlan();
  const updatePlanMutation = useUpdateSubscriptionPlan();

  const handleCreatePlan = () => {
    const name = prompt('نام پلن جدید:');
    if (!name) return;
    const priceStr = prompt('قیمت پلن (تومان):');
    if (!priceStr) return;
    const durationStr = prompt('مدت اعتبار (روز):');
    if (!durationStr) return;

    createPlanMutation.mutate({
      name,
      price: parseInt(priceStr, 10),
      duration_days: parseInt(durationStr, 10),
    });
  };

  const handleEditPlanPrice = (id: string, currentPrice: number) => {
    const priceStr = prompt('قیمت جدید (تومان):', currentPrice.toString());
    if (priceStr) {
      updatePlanMutation.mutate({ id, data: { price: parseInt(priceStr, 10) } });
    }
  };

  if (isPlansLoading || isSubsLoading) return <div>در حال بارگذاری...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>مدیریت اشتراک‌ها و پرداخت</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>پلن‌های اشتراکی تعریف‌شده</h2>
              <button 
                onClick={handleCreatePlan}
                style={{ padding: '6px 12px', background: 'var(--primary)', color: 'white', borderRadius: '6px', fontSize: '0.9rem' }}>
                ایجاد پلن جدید
              </button>
            </div>
            
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ padding: '12px' }}>نام پلن</th>
                  <th style={{ padding: '12px' }}>قیمت (تومان)</th>
                  <th style={{ padding: '12px' }}>مدت اعتبار (روز)</th>
                  <th style={{ padding: '12px' }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {(plans || []).map((plan: any) => (
                  <tr key={plan.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '12px', fontWeight: 600 }}>{plan.name}</td>
                    <td style={{ padding: '12px' }}>{plan.price.toLocaleString('fa-IR')}</td>
                    <td style={{ padding: '12px' }}>{plan.duration_days} روز</td>
                    <td style={{ padding: '12px' }}>
                      <button 
                        onClick={() => handleEditPlanPrice(plan.id, plan.price)}
                        style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                        ویرایش قیمت
                      </button>
                    </td>
                  </tr>
                ))}
                {(!plans || plans.length === 0) && (
                  <tr>
                    <td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ پلنی یافت نشد</td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              اشتراک‌های فعال کابران/تیم‌ها
            </h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ padding: '12px' }}>شناسه مالک</th>
                  <th style={{ padding: '12px' }}>نوع مالک</th>
                  <th style={{ padding: '12px' }}>پلن انتخابی</th>
                  <th style={{ padding: '12px' }}>تاریخ شروع</th>
                  <th style={{ padding: '12px' }}>تاریخ انقضا</th>
                  <th style={{ padding: '12px' }}>وضعیت</th>
                </tr>
              </thead>
              <tbody>
                {(subscriptions || []).map((sub: any) => {
                  const isExpired = sub.expires_at ? new Date(sub.expires_at).getTime() < Date.now() : false;
                  return (
                    <tr key={sub.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px', color: 'var(--muted)', fontSize: '0.85rem' }}>{sub.owner_id.substring(0, 8)}...</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ padding: '4px 8px', background: '#f1f5f9', borderRadius: '4px', fontSize: '0.85rem' }}>
                          {sub.owner_type === 'team' ? 'تیم' : 'کاربر شخصی'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>{plans?.find((p: any) => p.id === sub.plan_id)?.name || 'نامشخص'}</td>
                      <td style={{ padding: '12px' }}>{new Date(sub.starts_at).toLocaleDateString('fa-IR')}</td>
                      <td style={{ padding: '12px' }}>{sub.expires_at ? new Date(sub.expires_at).toLocaleDateString('fa-IR') : 'نامحدود'}</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ 
                          padding: '4px 8px', 
                          borderRadius: '4px', 
                          background: isExpired ? '#fce8e6' : '#e6f4ea',
                          color: isExpired ? '#c5221f' : '#137333',
                          fontSize: '0.85rem'
                        }}>
                          {isExpired ? 'منقضی شده' : 'فعال'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
                {(!subscriptions || subscriptions.length === 0) && (
                  <tr>
                    <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ اشتراکی یافت نشد</td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
