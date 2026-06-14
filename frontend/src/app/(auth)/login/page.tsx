'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ApiClient } from '@/lib/api';
import { Button } from '@/components/shared/ui/Button';
import { Input } from '@/components/shared/ui/Input';
import { Card, CardContent } from '@/components/shared/ui/Card';
import styles from './page.module.css';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('لطفاً نام کاربری و رمز عبور را وارد کنید.');
      return;
    }

    setLoading(true);
    try {
      await ApiClient.adminLogin(username, password);
      router.push('/admin');
    } catch (err: any) {
      setError(err.message || 'خطا در ورود به سیستم');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Card className={styles.loginCard}>
        <CardContent>
          <div className={styles.header}>
            <h1 className={styles.title}>ورود مدیریت</h1>
            <p className={styles.subtitle}>جهت دسترسی به داشبورد اطلاعات خود را وارد کنید</p>
          </div>

          {error && <div className={styles.errorAlert}>{error}</div>}
          
          <form onSubmit={handleLogin} className={styles.form}>
            <Input
              label="نام کاربری"
              type="text"
              placeholder="admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              dir="ltr"
              disabled={loading}
              autoComplete="username"
            />
            <Input
              label="رمز عبور"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              dir="ltr"
              disabled={loading}
              autoComplete="current-password"
            />
            <Button type="submit" isLoading={loading} className={styles.submitBtn}>
              ورود به سیستم
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
