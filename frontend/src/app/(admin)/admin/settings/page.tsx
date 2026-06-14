'use client';

import React from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { useAdminSystemSettings, useUpdateSystemSetting, useAdminFeatureFlags, useUpdateFeatureFlag } from '@/hooks/useAdmin';

export default function SettingsPage() {
  const { data: settings, isLoading: isSettingsLoading } = useAdminSystemSettings();
  const { data: featureFlags, isLoading: isFlagsLoading } = useAdminFeatureFlags();
  
  const updateSettingMutation = useUpdateSystemSetting();
  const updateFlagMutation = useUpdateFeatureFlag();

  const handleUpdateSetting = (key: string, currentValue: string) => {
    const value = prompt(`مقدار جدید برای ${key} را وارد کنید:`, currentValue);
    if (value !== null) {
      updateSettingMutation.mutate({ key, data: { value } });
    }
  };

  const handleToggleFlag = (key: string, current: boolean) => {
    updateFlagMutation.mutate({ key, data: { is_enabled: !current } });
  };

  if (isSettingsLoading || isFlagsLoading) return <div>در حال بارگذاری...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>تنظیمات سیستم</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              تنظیمات عمومی (System Settings)
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {(settings || []).map((setting: any) => (
                <div key={setting.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--background)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }} dir="ltr">{setting.key}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{setting.description}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <code style={{ background: '#f1f5f9', padding: '4px 8px', borderRadius: '4px' }}>{setting.value}</code>
                    <button 
                      onClick={() => handleUpdateSetting(setting.key, setting.value)}
                      style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                      ویرایش
                    </button>
                  </div>
                </div>
              ))}
              {(!settings || settings.length === 0) && (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ تنظیمی یافت نشد.</div>
              )}
            </div>
            <button 
              onClick={() => handleUpdateSetting('new_setting', '')}
              style={{ marginTop: '16px', alignSelf: 'flex-start', padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px' }}>
              افزودن تنظیم جدید
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              مدیریت فیچرها (Feature Flags)
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {(featureFlags || []).map((flag: any) => (
                <div key={flag.key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'var(--background)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                  <div>
                    <div style={{ fontWeight: 600 }} dir="ltr">{flag.key}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--muted)' }}>{flag.description}</div>
                  </div>
                  <button 
                    onClick={() => handleToggleFlag(flag.key, flag.is_enabled)}
                    style={{ 
                      padding: '4px 8px', 
                      background: flag.is_enabled ? '#e6f4ea' : '#f1f3f4',
                      color: flag.is_enabled ? '#137333' : '#3c4043',
                      border: 'none', 
                      borderRadius: '4px', 
                      fontSize: '0.85rem' 
                    }}>
                    {flag.is_enabled ? 'روشن' : 'خاموش'}
                  </button>
                </div>
              ))}
              {(!featureFlags || featureFlags.length === 0) && (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ فیچری یافت نشد.</div>
              )}
            </div>
            <button 
              onClick={() => {
                const key = prompt('نام کلید فیچر جدید را وارد کنید (مثلا ENABLE_AI_CHAT):');
                if (key) updateFlagMutation.mutate({ key, data: { is_enabled: false } });
              }}
              style={{ marginTop: '16px', alignSelf: 'flex-start', padding: '8px 16px', background: 'var(--primary)', color: 'white', borderRadius: '8px' }}>
              افزودن فیچر جدید
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
