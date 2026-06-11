import type { RuleChange, RuleVersion } from '../types/thesis';

export interface RuleVersionPayload {
  previousVersion: RuleVersion;
  currentVersion: RuleVersion;
  ruleChanges: RuleChange[];
}

export async function fetchCurrentRuleVersion(): Promise<RuleVersionPayload> {
  const response = await fetch('/api/rule-versions/current');

  if (!response.ok) {
    throw new Error(`Rule version request failed: ${response.status}`);
  }

  return response.json() as Promise<RuleVersionPayload>;
}
