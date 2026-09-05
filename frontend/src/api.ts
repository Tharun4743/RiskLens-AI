import { Customer, Transaction, InvestigationResult, InvestigationSummaryItem, InvestigationExplanation, EvidenceItem } from './types';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

async function handleResponse<T>(res: Response): Promise<T> {
  const json = await res.json();
  if (!res.ok || !json.success) {
    const errMsg = json.error?.message || `Request failed with status ${res.status}`;
    throw new Error(errMsg);
  }
  return json.data;
}

export const api = {
  async getHealth() {
    const res = await fetch(`${BASE_URL}/api/health`);
    return handleResponse<any>(res);
  },

  async getCustomers(): Promise<Customer[]> {
    const res = await fetch(`${BASE_URL}/api/customers`);
    return handleResponse<Customer[]>(res);
  },

  async getCustomer(customerId: string): Promise<Customer> {
    const res = await fetch(`${BASE_URL}/api/customers/${customerId}`);
    return handleResponse<Customer>(res);
  },

  async getTransactions(
    customerId: string,
    params?: { channel?: string; min_amount?: number; max_amount?: number; search?: string; sort_by?: string; sort_order?: string; limit?: number; offset?: number }
  ): Promise<{ transactions: Transaction[]; total_count: number }> {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') {
          query.append(k, String(v));
        }
      });
    }
    const res = await fetch(`${BASE_URL}/api/customers/${customerId}/transactions?${query.toString()}`);
    return handleResponse<{ transactions: Transaction[]; total_count: number }>(res);
  },

  async uploadCSV(file: File, customerId?: string, customerName?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (customerId) formData.append('customer_id', customerId);
    if (customerName) formData.append('customer_name', customerName);

    const res = await fetch(`${BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData
    });
    return handleResponse<any>(res);
  },

  async createInvestigation(customerId: string): Promise<InvestigationResult> {
    const res = await fetch(`${BASE_URL}/api/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId })
    });
    return handleResponse<InvestigationResult>(res);
  },

  async getInvestigations(): Promise<InvestigationSummaryItem[]> {
    const res = await fetch(`${BASE_URL}/api/investigations`);
    return handleResponse<InvestigationSummaryItem[]>(res);
  },

  async getInvestigation(id: number): Promise<InvestigationResult> {
    const res = await fetch(`${BASE_URL}/api/investigations/${id}`);
    return handleResponse<InvestigationResult>(res);
  },

  async explainInvestigation(id: number): Promise<InvestigationExplanation> {
    const res = await fetch(`${BASE_URL}/api/investigations/${id}/explain`, {
      method: 'POST'
    });
    return handleResponse<InvestigationExplanation>(res);
  },

  async getEvidence(id: number): Promise<{ investigation_id: number; evidence_count: number; evidence: EvidenceItem[] }> {
    const res = await fetch(`${BASE_URL}/api/investigations/${id}/evidence`);
    return handleResponse<any>(res);
  },

  async getReport(id: number): Promise<any> {
    const res = await fetch(`${BASE_URL}/api/investigations/${id}/report`, {
      method: 'POST'
    });
    return handleResponse<any>(res);
  },

  async askChat(id: number, question: string): Promise<{ answer: string; grounded_on: string; is_ai: boolean }> {
    const res = await fetch(`${BASE_URL}/api/investigations/${id}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    return handleResponse<{ answer: string; grounded_on: string; is_ai: boolean }>(res);
  },

  getPdfUrl(id: number): string {
    return `${BASE_URL}/api/investigations/${id}/pdf`;
  }
};
