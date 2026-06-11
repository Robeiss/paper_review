import type { AuthSession } from '../types/thesis';

export async function login(account: string, password: string): Promise<AuthSession> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ account, password }),
  });

  if (!response.ok) {
    throw new Error('账号或密码错误');
  }

  return response.json() as Promise<AuthSession>;
}
