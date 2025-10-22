/**
 * Zustand store for submission state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Document {
  id: string;
  submission_id: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  mime_type: string;
  s3_bucket: string;
  s3_key: string;
  s3_url?: string;
  processing_status: string;
  extraction_data?: string;
  extraction_confidence?: number;
  extraction_error?: string;
  is_valid: boolean;
  validation_error?: string;
  created_at: string;
  updated_at: string;
  processed_at?: string;
}

export interface Submission {
  id: string;
  user_id: string;
  title?: string;
  status: 'draft' | 'processing' | 'completed' | 'failed';
  submission_type: 'acord_125' | 'custom';
  acord_data?: any;
  extracted_data?: any;
  extraction_status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_progress: number;
  extraction_error?: string;
  total_files: number;
  processed_files: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  documents?: Document[];
}

interface SubmissionState {
  // Current submission
  currentSubmission: Submission | null;
  documents: Document[];
  
  // Submission list
  submissions: Submission[];
  isLoadingSubmissions: boolean;
  
  // Upload state
  isUploading: boolean;
  uploadProgress: Record<string, number>;
  
  // UI state
  showUploadModal: boolean;
  selectedFiles: File[];
  
  // Actions
  setCurrentSubmission: (submission: Submission | null) => void;
  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (documentId: string) => void;
  updateDocument: (documentId: string, updates: Partial<Document>) => void;
  
  setSubmissions: (submissions: Submission[]) => void;
  addSubmission: (submission: Submission) => void;
  updateSubmission: (submissionId: string, updates: Partial<Submission>) => void;
  setLoadingSubmissions: (loading: boolean) => void;
  
  setUploading: (uploading: boolean) => void;
  setUploadProgress: (fileName: string, progress: number) => void;
  clearUploadProgress: () => void;
  
  setShowUploadModal: (show: boolean) => void;
  setSelectedFiles: (files: File[]) => void;
  addSelectedFile: (file: File) => void;
  removeSelectedFile: (fileName: string) => void;
  clearSelectedFiles: () => void;
  
  // Reset
  reset: () => void;
}

export const useSubmissionStore = create<SubmissionState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentSubmission: null,
      documents: [],
      submissions: [],
      isLoadingSubmissions: false,
      isUploading: false,
      uploadProgress: {},
      showUploadModal: false,
      selectedFiles: [],

      // Current submission actions
      setCurrentSubmission: (submission) => set({ currentSubmission: submission }),
      
      setDocuments: (documents) => set({ documents }),
      
      addDocument: (document) => set((state) => ({
        documents: [...state.documents, document]
      })),
      
      removeDocument: (documentId) => set((state) => ({
        documents: state.documents.filter(doc => doc.id !== documentId)
      })),
      
      updateDocument: (documentId, updates) => set((state) => ({
        documents: state.documents.map(doc =>
          doc.id === documentId ? { ...doc, ...updates } : doc
        )
      })),

      // Submission list actions
      setSubmissions: (submissions) => set({ submissions }),
      
      addSubmission: (submission) => set((state) => ({
        submissions: [submission, ...state.submissions]
      })),
      
      updateSubmission: (submissionId, updates) => set((state) => ({
        submissions: state.submissions.map(sub =>
          sub.id === submissionId ? { ...sub, ...updates } : sub
        )
      })),
      
      setLoadingSubmissions: (loading) => set({ isLoadingSubmissions: loading }),

      // Upload actions
      setUploading: (uploading) => set({ isUploading: uploading }),
      
      setUploadProgress: (fileName, progress) => set((state) => ({
        uploadProgress: {
          ...state.uploadProgress,
          [fileName]: progress
        }
      })),
      
      clearUploadProgress: () => set({ uploadProgress: {} }),

      // UI actions
      setShowUploadModal: (show) => set({ showUploadModal: show }),
      
      setSelectedFiles: (files) => set({ selectedFiles: files }),
      
      addSelectedFile: (file) => set((state) => ({
        selectedFiles: [...state.selectedFiles, file]
      })),
      
      removeSelectedFile: (fileName) => set((state) => ({
        selectedFiles: state.selectedFiles.filter(file => file.name !== fileName)
      })),
      
      clearSelectedFiles: () => set({ selectedFiles: [] }),

      // Reset
      reset: () => set({
        currentSubmission: null,
        documents: [],
        submissions: [],
        isLoadingSubmissions: false,
        isUploading: false,
        uploadProgress: {},
        showUploadModal: false,
        selectedFiles: []
      })
    }),
    {
      name: 'submission-store'
    }
  )
);



