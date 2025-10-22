/**
 * Custom hook for managing file uploads
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

export interface FileUploadState {
  files: File[];
  isUploading: boolean;
  uploadProgress: Record<string, number>;
  errors: Record<string, string>;
  isDragActive: boolean;
}

export interface FileUploadOptions {
  maxFiles?: number;
  maxSize?: number; // in bytes
  acceptedFileTypes?: string[];
  onUploadComplete?: (files: File[]) => void;
  onUploadError?: (error: string) => void;
}

export const useFileUpload = (options: FileUploadOptions = {}) => {
  const {
    maxFiles = 10,
    maxSize = 10 * 1024 * 1024, // 10MB
    acceptedFileTypes = ['.pdf', '.docx', '.xlsx', '.jpg', '.jpeg', '.png'],
    onUploadComplete,
    onUploadError
  } = options;

  const [state, setState] = useState<FileUploadState>({
    files: [],
    isUploading: false,
    uploadProgress: {},
    errors: {},
    isDragActive: false
  });

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > maxSize) {
      return `File ${file.name} is too large. Maximum size is ${Math.round(maxSize / (1024 * 1024))}MB`;
    }

    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFileTypes.includes(fileExtension)) {
      return `File ${file.name} has an unsupported format. Allowed types: ${acceptedFileTypes.join(', ')}`;
    }

    return null;
  }, [maxSize, acceptedFileTypes]);

  const addFiles = useCallback((newFiles: File[]) => {
    const validFiles: File[] = [];
    const errors: Record<string, string> = {};

    newFiles.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors[file.name] = error;
      } else {
        validFiles.push(file);
      }
    });

    setState(prev => ({
      ...prev,
      files: [...prev.files, ...validFiles].slice(0, maxFiles),
      errors: { ...prev.errors, ...errors }
    }));

    if (Object.keys(errors).length > 0) {
      onUploadError?.(`Some files were rejected: ${Object.values(errors).join(', ')}`);
    }

    // Trigger upload for valid files
    if (validFiles.length > 0) {
      onUploadComplete?.(validFiles);
    }
  }, [validateFile, maxFiles, onUploadError, onUploadComplete]);

  const removeFile = useCallback((fileName: string) => {
    setState(prev => ({
      ...prev,
      files: prev.files.filter(file => file.name !== fileName),
      errors: Object.fromEntries(
        Object.entries(prev.errors).filter(([key]) => key !== fileName)
      ),
      uploadProgress: Object.fromEntries(
        Object.entries(prev.uploadProgress).filter(([key]) => key !== fileName)
      )
    }));
  }, []);

  const clearFiles = useCallback(() => {
    setState(prev => ({
      ...prev,
      files: [],
      errors: {},
      uploadProgress: {}
    }));
  }, []);

  const setUploadProgress = useCallback((fileName: string, progress: number) => {
    setState(prev => ({
      ...prev,
      uploadProgress: {
        ...prev.uploadProgress,
        [fileName]: progress
      }
    }));
  }, []);

  const setUploading = useCallback((isUploading: boolean) => {
    setState(prev => ({ ...prev, isUploading }));
  }, []);

  const dropzoneProps = useDropzone({
    onDrop: addFiles,
    onDragEnter: () => setState(prev => ({ ...prev, isDragActive: true })),
    onDragLeave: () => setState(prev => ({ ...prev, isDragActive: false })),
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles,
    maxSize,
    multiple: true,
    disabled: state.isUploading
  });

  return {
    ...state,
    addFiles,
    removeFile,
    clearFiles,
    setUploadProgress,
    setUploading,
    dropzoneProps,
    canAddMoreFiles: state.files.length < maxFiles
  };
};



