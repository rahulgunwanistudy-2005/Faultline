/* eslint-disable @typescript-eslint/no-explicit-any */
import axios from 'axios';

// Create a configured Axios instance pointing to the FastAPI backend
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Types ─────────────────────────────────────────────────────────────

export type HealthStatus = {
  status: string;
  service: string;
  mode: string;
};

export type Student = {
  id: string;
  name?: string;
  diagnostic_items?: any[];
};

export type AnalysisUploadResult = {
  analysis_id: string;
  status: string;
  progress: number;
  mode: string;
  disclosure: string;
  upload: any;
};

export type AnalysisSnapshot = {
  status: string;
  progress: number;
  mode: string;
  result?: any;
};

// ── API Service ───────────────────────────────────────────────────────

export const FaultlineAPI = {
  getHealth: async (): Promise<HealthStatus> => {
    const { data } = await apiClient.get<HealthStatus>('/health');
    return data;
  },

  getDemoClass: async (classId: string = 'period-3'): Promise<any> => {
    const { data } = await apiClient.get(`/v1/demo/classes/${classId}`);
    return data;
  },

  uploadWorksheet: async (file: File): Promise<AnalysisUploadResult> => {
    const { data } = await apiClient.post<AnalysisUploadResult>(
      '/v1/analyses?template_id=fractions-v1',
      file,
      {
        headers: {
          'Content-Type': file.type,
          'X-Filename': file.name,
        },
      }
    );
    return data;
  },

  getAnalysis: async (analysisId: string): Promise<AnalysisSnapshot> => {
    const { data } = await apiClient.get<AnalysisSnapshot>(`/v1/analyses/${analysisId}`);
    return data;
  },

  correctReading: async (analysisId: string, readingId: string, correction: any): Promise<any> => {
    const { data } = await apiClient.patch(
      `/v1/analyses/${analysisId}/readings/${readingId}`,
      correction
    );
    return data;
  },

  getDiagnosticItems: async (studentId: string): Promise<{ student_id: string; items: any[] }> => {
    const { data } = await apiClient.get(`/v1/students/${studentId}/diagnostic-items`);
    return data;
  },

  lockPrediction: async (studentId: string): Promise<any> => {
    const { data } = await apiClient.post(`/v1/students/${studentId}/held-out-prediction`);
    return data;
  },

  revealPrediction: async (studentId: string, proofToken: string): Promise<any> => {
    const { data } = await apiClient.post(`/v1/students/${studentId}/held-out-reveal`, {
      proof_token: proofToken,
    });
    return data;
  },
};
