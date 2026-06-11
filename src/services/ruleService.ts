import type { RulePack } from '../types/thesis';

export async function fetchRulePack(token: string): Promise<RulePack> {
  const response = await fetch('/api/rule-pack', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Rule pack request failed: ${response.status}`);
  }

  return response.json() as Promise<RulePack>;
}
