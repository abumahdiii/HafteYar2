'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ApiClient } from '@/lib/api';
import styles from './Sidebar.module.css';

const MENU_ITEMS = [
  { title: 'داشبورد', path: '/admin', icon: '📊' },
  { title: 'تیم‌ها', path: '/admin/teams', icon: '👥' },
  { title: 'کاربران', path: '/admin/users', icon: '👤' },
  { title: 'اشتراک‌ها', path: '/admin/subscriptions', icon: '💳' },
  { title: 'مکالمات', path: '/admin/conversations', icon: '💬' },
  { title: 'تسک‌ها', path: '/admin/tasks', icon: '✅' },
  { title: 'مصرف هوش‌مصنوعی', path: '/admin/ai-usage', icon: '🧠' },
  { title: 'تنظیمات سیستم', path: '/admin/settings', icon: '⚙️' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const toggleCollapse = () => setCollapsed(!collapsed);

  return (
    <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
      <div className={styles.logoContainer}>
        {!collapsed && <span className={styles.logoText}>هفته‌یار | پشتیبانی</span>}
        <button className={styles.collapseBtn} onClick={toggleCollapse}>
          {collapsed ? '▶' : '◀'}
        </button>
      </div>

      <nav className={styles.nav}>
        {MENU_ITEMS.map((item) => {
          const isActive = pathname === item.path || (pathname.startsWith(item.path) && item.path !== '/admin');
          return (
            <Link 
              key={item.path} 
              href={item.path} 
              className={`${styles.navItem} ${isActive ? styles.active : ''}`}
              title={collapsed ? item.title : undefined}
            >
              <span className={styles.icon}>{item.icon}</span>
              {!collapsed && <span className={styles.label}>{item.title}</span>}
            </Link>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <button 
          className={styles.logoutBtn} 
          onClick={() => ApiClient.logout()}
          title={collapsed ? 'خروج' : undefined}
        >
          <span className={styles.icon}>🚪</span>
          {!collapsed && <span className={styles.label}>خروج</span>}
        </button>
      </div>
    </aside>
  );
}
