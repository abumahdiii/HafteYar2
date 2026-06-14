import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/shared/ui/Card';
import { Badge } from '@/components/shared/ui/Badge';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/shared/ui/Table';
import styles from './page.module.css';

export default function AdminDashboard() {
  return (
    <div className={styles.dashboard}>
      <div className={styles.statsGrid}>
        <Card>
          <CardContent className={styles.statContent}>
            <div className={styles.statLabel}>کل کاربران</div>
            <div className={styles.statValue}>۱,۲۳۴</div>
            <Badge variant="success" className={styles.statBadge}>+۱۲٪ در ماه</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className={styles.statContent}>
            <div className={styles.statLabel}>تیم‌های فعال</div>
            <div className={styles.statValue}>۵۶</div>
            <Badge variant="info" className={styles.statBadge}>۵ تیم جدید</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardContent className={styles.statContent}>
            <div className={styles.statLabel}>درآمد ماهانه</div>
            <div className={styles.statValue}>۱۲.۵M</div>
            <Badge variant="warning" className={styles.statBadge}>نیازمند بررسی</Badge>
          </CardContent>
        </Card>
      </div>
      
      <div className={styles.recentActivity}>
        <h2 className={styles.sectionTitle}>کاربران جدید</h2>
        <Card>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>نام کاربر</TableHead>
                <TableHead>شماره تماس</TableHead>
                <TableHead>تیم</TableHead>
                <TableHead>وضعیت</TableHead>
                <TableHead>تاریخ ثبت‌نام</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[1, 2, 3].map((i) => (
                <TableRow key={i}>
                  <TableCell>کاربر تستی {i}</TableCell>
                  <TableCell dir="ltr" style={{textAlign: 'right'}}>0912345678{i}</TableCell>
                  <TableCell>تیم تستی {i}</TableCell>
                  <TableCell><Badge variant="success">فعال</Badge></TableCell>
                  <TableCell>۱۴۰۳/۰۴/۱۵</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>
    </div>
  );
}
