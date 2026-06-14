import React from 'react';
import styles from './Table.module.css';

interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export function Table({ children, className = '' }: TableProps) {
  return (
    <div className={styles.wrapper}>
      <table className={`${styles.table} ${className}`}>{children}</table>
    </div>
  );
}

export function TableHeader({ children }: { children: React.ReactNode }) {
  return <thead className={styles.thead}>{children}</thead>;
}

export function TableBody({ children }: { children: React.ReactNode }) {
  return <tbody className={styles.tbody}>{children}</tbody>;
}

export function TableRow({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <tr className={`${styles.tr} ${className}`}>{children}</tr>;
}

export function TableHead({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <th className={`${styles.th} ${className}`}>{children}</th>;
}

export function TableCell({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  return <td className={`${styles.td} ${className}`}>{children}</td>;
}
