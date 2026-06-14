import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

export class ApiClient {
  private static getHeaders() {
    const token = Cookies.get('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
  }

  static async request(endpoint: string, options: RequestInit = {}) {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Request failed');
    }
    return res.json();
  }

  static async get(endpoint: string) {
    return this.request(endpoint, { method: 'GET' });
  }

  static async post(endpoint: string, body: any) {
    return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) });
  }

  static async put(endpoint: string, body: any) {
    return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) });
  }

  static async delete(endpoint: string) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  static async sendOtp(phone: string) {
    const res = await fetch(`${API_BASE_URL}/auth/login/send-otp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ phone }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to send OTP');
    }
    return res.json();
  }

  static async verifyOtp(phone: string, code: string) {
    const res = await fetch(`${API_BASE_URL}/auth/login/verify-otp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ phone, code }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to verify OTP');
    }
    const data = await res.json();
    if (data.access_token) {
      // Set cookie for 7 days
      Cookies.set('access_token', data.access_token, { expires: 7, path: '/' });
    }
    return data;
  }

  static async adminLogin(username: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/auth/admin/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'نام کاربری یا رمز عبور اشتباه است');
    }
    const data = await res.json();
    if (data.access_token) {
      Cookies.set('access_token', data.access_token, { expires: 7, path: '/' });
    }
    return data;
  }

  static logout() {
    if (typeof window !== 'undefined') {
      Cookies.remove('access_token', { path: '/' });
      window.location.href = '/login';
    }
  }
}
