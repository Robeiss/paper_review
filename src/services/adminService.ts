import type { RuleVersion, ThesisRule } from '../types/thesis';

function authHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}

async function requestJson<T>(url: string, token: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...authHeaders(token),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchAdminRules(token: string): Promise<ThesisRule[]> {
  return requestJson('/api/admin/rules', token);
}

export function saveAdminRule(token: string, rule: ThesisRule): Promise<ThesisRule> {
  return requestJson(`/api/admin/rules/${encodeURIComponent(rule.id)}`, token, {
    method: 'PUT',
    body: JSON.stringify(rule),
  });
}

export function createAdminRule(token: string, rule: ThesisRule): Promise<ThesisRule> {
  return requestJson('/api/admin/rules', token, {
    method: 'POST',
    body: JSON.stringify(rule),
  });
}

export function deleteAdminRule(token: string, ruleId: string): Promise<{ ok: boolean }> {
  return requestJson(`/api/admin/rules/${encodeURIComponent(ruleId)}`, token, {
    method: 'DELETE',
  });
}

export function fetchAdminVersions(token: string): Promise<RuleVersion[]> {
  return requestJson('/api/admin/versions', token);
}

export function createAdminVersion(token: string, version: RuleVersion & { status: string }): Promise<RuleVersion> {
  return requestJson('/api/admin/versions', token, {
    method: 'POST',
    body: JSON.stringify(version),
  });
}

export function publishAdminVersion(token: string, versionId: string): Promise<{ ok: boolean }> {
  return requestJson(`/api/admin/versions/${encodeURIComponent(versionId)}/publish`, token, {
    method: 'POST',
  });
}

export function fetchAuditLogs(token: string): Promise<Array<Record<string, string | number>>> {
  return requestJson('/api/admin/audit-logs', token);
}
