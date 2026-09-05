export interface Customer {
  id: number;
  customer_id: string;
  name: string;
  created_at: string;
  transaction_count?: number;
  total_volume?: number;
  profile?: string;
  expected_result?: string;
}

export interface Transaction {
  id: number;
  transaction_id: string;
  customer_id: string;
  timestamp: string;
  description: string;
  payee: string;
  amount: number;
  channel: string;
  created_at?: string;
}

export interface EvidenceItem {
  id?: number;
  finding_id: string;
  transaction_id: string;
  evidence_type: string;
  observed_value: string;
  baseline_value: string;
  deviation: string;
  explanation: string;
  transaction_details?: Partial<Transaction>;
  source?: {
    source_table: string;
    transaction_id: string;
    timestamp: string;
    amount: number;
    payee: string;
    channel: string;
    description: string;
  };
}

export interface Finding {
  finding_id: string;
  rule_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  title: string;
  description: string;
  confidence: number;
  transaction_ids: string[];
  evidence: EvidenceItem[];
  observed_amount?: number;
  baseline_median?: number;
  multiplier?: number;
  payee?: string;
  first_seen?: string;
  duration_minutes?: number;
  total_amount?: number;
  primary_divergent_channel?: string;
  deviation_pct?: number;
  channel_shifts?: Record<string, { historical_pct: number; recent_pct: number; difference_pct: number }>;
}

export interface CorrelatedEvent {
  event_id: string;
  title: string;
  transaction_count: number;
  transaction_ids: string[];
  total_amount: number;
  formatted_amount: string;
  payees: string[];
  channels: string[];
  rules_involved: string[];
  time_window: {
    start: string;
    end: string;
    duration_minutes: number;
  };
  summary: string;
}

export interface Baseline {
  is_reliable: boolean;
  reason?: string;
  transaction_count: number;
  date_span_days: number;
  median_amount: number;
  mean_amount: number;
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
    iqr: number;
  };
  typical_range: {
    min: number;
    max: number;
    upper_bound_iqr: number;
  };
  daily_frequency: {
    mean: number;
    median: number;
  };
  odd_hours: {
    count: number;
    ratio: number;
    percentage: number;
  };
  typical_hours: {
    min: number;
    max: number;
    display: string;
  };
  hourly_distribution: Record<number, number>;
  known_payees_count: number;
  known_payees: string[];
  payee_frequencies: Record<string, number>;
  channel_distribution_count_pct: Record<string, number>;
  channel_distribution_volume_pct: Record<string, number>;
  total_volume: number;
}

export interface Scoring {
  priority_score: number;
  max_score: number;
  risk_level: 'NORMAL' | 'LOW' | 'MODERATE' | 'HIGH' | 'UNKNOWN';
  investigation_status: 'NO_ATTENTION' | 'ATTENTION_REQUIRED' | 'REVIEW_REQUIRED';
  badge_text: string;
  contributing_rules: Array<{ rule_id: string; points: number; rule_name: string }>;
  disclaimer: string;
}

export interface InvestigationResult {
  id?: number;
  customer_id: string;
  customer_name: string;
  investigation_status: 'NO_ATTENTION' | 'ATTENTION_REQUIRED' | 'REVIEW_REQUIRED';
  risk_level: 'NORMAL' | 'LOW' | 'MODERATE' | 'HIGH' | 'UNKNOWN';
  priority_score: number;
  badge_text: string;
  summary: string;
  baseline: Baseline;
  findings: Finding[];
  correlated_events: CorrelatedEvent[];
  scoring: Scoring;
  recommended_actions: string[];
  unknowns: string[];
  created_at: string;
}

export interface InvestigationExplanation {
  summary: string;
  attention_required: boolean;
  priority: string;
  key_findings: Array<{
    finding_id: string;
    rule_id: string;
    transaction_ids: string[];
    explanation: string;
  }>;
  investigator_actions: Array<{
    priority_level: string;
    action_text: string;
    target_reference?: string;
  }>;
  unknowns: string[];
  human_review_disclaimer: string;
  is_deterministic_fallback?: boolean;
  fallback_notice?: string;
}

export interface InvestigationSummaryItem {
  id: number;
  customer_id: string;
  customer_name: string;
  status: string;
  risk_level: string;
  started_at: string;
  completed_at: string;
  summary: string;
  findings_count: number;
  transactions_count: number;
}
