'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import styles from './Header.module.css';

const getPageTitle = (pathname: string) => {
  if (pathname === '/admin') return 'داشبورد';
  if (pathname.includes('/teams')) return 'مدیریت تیم‌ها';
  if (pathname.includes('/users')) return 'مدیریت کاربران';
  if (pathname.includes('/subscriptions')) return 'اشتراک‌ها';
  if (pathname.includes('/conversations')) return 'مکالمات بات';
  if (pathname.includes('/tasks')) return 'تسک‌ها';
  if (pathname.includes('/ai-usage')) return 'مصرف هوش‌مصنوعی';
  if (pathname.includes('/settings')) return 'تنظیمات سیستم';
  return 'پنل مدیریت';
};

export function Header() {
  const pathname = usePathname();
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // Check initial theme from document or localStorage
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(isDark ? 'dark' : 'light');
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  };

  return (
    <header className={styles.header}>
      <h1 className={styles.title}>{getPageTitle(pathname)}</h1>
      <div className={styles.actions}>
        <button onClick={toggleTheme} className={styles.iconBtn} title="تغییر تم">
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        <div className={styles.profileBtn}>
          <span className={styles.avatar}>A</span>
          <span className={styles.profileName}>ادمین سیستم</span>
        </div>
      </div>
    </header>
  );
}
