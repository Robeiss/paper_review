export type RuleSeverity = 'normal' | 'important' | 'critical';

export interface ThesisRule {
  id: string;
  name: string;
  summary: string;
  specs: Array<{
    label: string;
    value: string;
  }>;
  notes: string[];
  commonMistakes: string[];
  severity: RuleSeverity;
  updatedAt: string;
}

export interface ThesisBlock {
  id: string;
  title: string;
  type:
    | 'cover'
    | 'statement'
    | 'abstract'
    | 'toc'
    | 'heading'
    | 'paragraph'
    | 'figure'
    | 'table'
    | 'formula'
    | 'references'
    | 'acknowledgement'
    | 'appendix';
  ruleId: string;
  content: string[];
  level?: 1 | 2 | 3;
}

export interface RuleVersion {
  id: string;
  name: string;
  publishedAt: string;
  source: string;
  changes: string[];
}

export interface RuleChange {
  ruleId: string;
  title: string;
  previous: string;
  current: string;
  impact: string;
  risk: 'low' | 'medium' | 'high';
}

export type DataSourceStatus = 'loading' | 'remote' | 'fallback';

export interface RulePack {
  previousVersion: RuleVersion;
  currentVersion: RuleVersion;
  ruleChanges: RuleChange[];
  thesisRules: ThesisRule[];
}

export interface AuthUser {
  account: string;
  name: string;
  role: 'student' | 'admin';
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}
