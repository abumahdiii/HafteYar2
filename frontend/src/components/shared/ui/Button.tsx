import React, { ButtonHTMLAttributes } from 'react';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  isLoading?: boolean;
}

export function Button({ 
  children, 
  variant = 'primary', 
  isLoading, 
  className = '', 
  disabled,
  ...props 
}: ButtonProps) {
  const rootClass = `${styles.btn} ${styles[variant]} ${className}`;
  
  return (
    <button 
      className={rootClass} 
      disabled={isLoading || disabled} 
      {...props}
    >
      {isLoading ? <span className={styles.loader}></span> : children}
    </button>
  );
}
