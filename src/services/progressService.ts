import type { StudentProgress } from '../types/thesis';

function headers(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

export async function fetchStudentProgress(token: string): Promise<StudentProgress> {
  const response = await fetch('/api/me/progress', {
    headers: headers(token),
  });

  if (!response.ok) {
    throw new Error(`Progress request failed: ${response.status}`);
  }

  return response.json() as Promise<StudentProgress>;
}

export async function saveStudentProgress(token: string, ruleId: string, checkedKeys: string[]): Promise<void> {
  const response = await fetch(`/api/me/progress/${encodeURIComponent(ruleId)}`, {
    method: 'PUT',
    headers: headers(token),
    body: JSON.stringify({ checkedKeys }),
  });

  if (!response.ok) {
    throw new Error(`Progress save failed: ${response.status}`);
  }
}
