'use client';

import React, { useState } from 'react';
import { Card, CardContent } from '@/components/shared/ui/Card';
import { 
  useAdminAIProviders, 
  useCreateAIProvider, 
  useUpdateAIProvider,
  useAdminAIModels,
  useCreateAIModel,
  useUpdateAIModel
} from '@/hooks/useAdmin';

export default function AISettingsPage() {
  const { data: providers, isLoading: isProvidersLoading } = useAdminAIProviders();
  const { data: models, isLoading: isModelsLoading } = useAdminAIModels();
  
  const createProviderMutation = useCreateAIProvider();
  const updateProviderMutation = useUpdateAIProvider();
  
  const createModelMutation = useCreateAIModel();
  const updateModelMutation = useUpdateAIModel();

  const handleCreateProvider = () => {
    const name = prompt('نام ارائه‌دهنده (مثل OpenAI یا OpenRouter):');
    if (!name) return;
    const apiKey = prompt('کلید API (API Key):');
    if (!apiKey) return;
    const baseUrl = prompt('آدرس Base URL (اختیاری):');

    createProviderMutation.mutate({ name, api_key: apiKey, base_url: baseUrl || null });
  };

  const handleToggleProvider = (id: string, current: boolean) => {
    updateProviderMutation.mutate({ id, data: { is_active: !current } });
  };

  const handleCreateModel = (providerId: string) => {
    const name = prompt('نام مدل (مثل gpt-4o):');
    if (!name) return;
    
    createModelMutation.mutate({
      provider_id: providerId,
      name,
      default_temperature: 0.7,
      max_tokens: 4096,
      is_active: true
    });
  };

  const handleToggleModel = (id: string, current: boolean) => {
    updateModelMutation.mutate({ id, data: { is_active: !current } });
  };

  if (isProvidersLoading || isModelsLoading) return <div>در حال بارگذاری...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '24px' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 600 }}>تنظیمات هوش‌مصنوعی (AI Providers & Models)</h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>مدیریت ارائه‌دهندگان (Providers)</h2>
              <button 
                onClick={handleCreateProvider}
                style={{ padding: '6px 12px', background: 'var(--primary)', color: 'white', borderRadius: '6px', fontSize: '0.9rem' }}>
                افزودن Provider جدید
              </button>
            </div>
            
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ padding: '12px' }}>نام</th>
                  <th style={{ padding: '12px' }}>آدرس Base URL</th>
                  <th style={{ padding: '12px' }}>وضعیت</th>
                  <th style={{ padding: '12px' }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {(providers || []).map((provider: any) => (
                  <tr key={provider.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '12px', fontWeight: 600 }} dir="ltr">{provider.name}</td>
                    <td style={{ padding: '12px' }} dir="ltr">{provider.base_url || 'پیش‌فرض'}</td>
                    <td style={{ padding: '12px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        background: provider.is_active ? '#e6f4ea' : '#fce8e6',
                        color: provider.is_active ? '#137333' : '#c5221f',
                        fontSize: '0.85rem'
                      }}>
                        {provider.is_active ? 'فعال' : 'غیرفعال'}
                      </span>
                    </td>
                    <td style={{ padding: '12px', display: 'flex', gap: '8px' }}>
                      <button 
                        onClick={() => handleToggleProvider(provider.id, provider.is_active)}
                        style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                        تغییر وضعیت
                      </button>
                      <button 
                        onClick={() => handleCreateModel(provider.id)}
                        style={{ padding: '4px 8px', background: '#e8f0fe', color: '#1967d2', border: '1px solid #d2e3fc', borderRadius: '4px', fontSize: '0.85rem' }}>
                        افزودن مدل به این ارائه‌دهنده
                      </button>
                    </td>
                  </tr>
                ))}
                {(!providers || providers.length === 0) && (
                  <tr>
                    <td colSpan={4} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ ارائه‌دهنده‌ای یافت نشد</td>
                  </tr>
                )}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 600, borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
              مدل‌های هوش‌مصنوعی
            </h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ padding: '12px' }}>ارائه‌دهنده</th>
                  <th style={{ padding: '12px' }}>نام مدل</th>
                  <th style={{ padding: '12px' }}>Temperature</th>
                  <th style={{ padding: '12px' }}>Max Tokens</th>
                  <th style={{ padding: '12px' }}>وضعیت</th>
                  <th style={{ padding: '12px' }}>عملیات</th>
                </tr>
              </thead>
              <tbody>
                {(models || []).map((model: any) => {
                  const provider = providers?.find((p: any) => p.id === model.provider_id);
                  return (
                    <tr key={model.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px', fontWeight: 600 }} dir="ltr">{provider?.name || 'نامشخص'}</td>
                      <td style={{ padding: '12px' }} dir="ltr">{model.name}</td>
                      <td style={{ padding: '12px' }}>{model.default_temperature}</td>
                      <td style={{ padding: '12px' }}>{model.max_tokens}</td>
                      <td style={{ padding: '12px' }}>
                        <span style={{ 
                          padding: '4px 8px', 
                          borderRadius: '4px', 
                          background: model.is_active ? '#e6f4ea' : '#fce8e6',
                          color: model.is_active ? '#137333' : '#c5221f',
                          fontSize: '0.85rem'
                        }}>
                          {model.is_active ? 'فعال' : 'غیرفعال'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <button 
                          onClick={() => handleToggleModel(model.id, model.is_active)}
                          style={{ padding: '4px 8px', border: '1px solid var(--border)', borderRadius: '4px', fontSize: '0.85rem' }}>
                          تغییر وضعیت
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {(!models || models.length === 0) && (
                  <tr>
                    <td colSpan={6} style={{ padding: '24px', textAlign: 'center', color: 'var(--muted)' }}>هیچ مدلی یافت نشد</td>
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
