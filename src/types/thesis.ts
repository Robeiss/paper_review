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
