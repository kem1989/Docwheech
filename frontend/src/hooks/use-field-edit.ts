'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export interface FieldChange {
  fieldPath: string;
  originalValue: any;
  currentValue: any;
  confidence: number;
  isEdited: boolean;
  lastEditedAt?: Date;
}

export interface UseFieldEditOptions {
  submissionId: string;
  onSaveSuccess?: (fieldPath: string, newValue: any) => void;
  onSaveError?: (fieldPath: string, error: Error) => void;
  debounceMs?: number;
  autoSave?: boolean;
}

export interface UseFieldEditReturn {
  // State
  editingField: string | null;
  changes: Map<string, FieldChange>;
  isSaving: boolean;
  saveError: string | null;
  hasUnsavedChanges: boolean;
  
  // Actions
  startEdit: (fieldPath: string) => void;
  cancelEdit: () => void;
  updateField: (fieldPath: string, newValue: any, originalValue?: any) => void;
  saveField: (fieldPath: string) => Promise<void>;
  saveAllChanges: () => Promise<void>;
  discardChanges: (fieldPath?: string) => void;
  getFieldValue: (fieldPath: string, originalValue: any) => any;
  isFieldEdited: (fieldPath: string) => boolean;
  getFieldChange: (fieldPath: string) => FieldChange | undefined;
}

export function useFieldEdit(options: UseFieldEditOptions): UseFieldEditReturn {
  const { submissionId, onSaveSuccess, onSaveError, debounceMs = 1000, autoSave = true } = options;
  
  const [editingField, setEditingField] = useState<string | null>(null);
  const [changes, setChanges] = useState<Map<string, FieldChange>>(new Map());
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const pendingSaveRef = useRef<Set<string>>(new Set());
  
  // Check if there are unsaved changes
  const hasUnsavedChanges = changes.size > 0;
  
  // Start editing a field
  const startEdit = useCallback((fieldPath: string) => {
    setEditingField(fieldPath);
    setSaveError(null);
  }, []);
  
  // Cancel current edit
  const cancelEdit = useCallback(() => {
    setEditingField(null);
    setSaveError(null);
  }, []);
  
  // Update a field value (tracks the change)
  const updateField = useCallback((fieldPath: string, newValue: any, originalValue?: any) => {
    setChanges(prev => {
      const newChanges = new Map(prev);
      const existing = newChanges.get(fieldPath);
      
      const change: FieldChange = {
        fieldPath,
        originalValue: existing?.originalValue ?? originalValue,
        currentValue: newValue,
        confidence: 1.0, // Manual edits have 100% confidence
        isEdited: true,
        lastEditedAt: new Date(),
      };
      
      // If value is reverted to original, remove from changes
      if (change.originalValue === newValue) {
        newChanges.delete(fieldPath);
      } else {
        newChanges.set(fieldPath, change);
      }
      
      return newChanges;
    });
    
    // Auto-save with debounce
    if (autoSave) {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      
      pendingSaveRef.current.add(fieldPath);
      
      debounceTimerRef.current = setTimeout(() => {
        const fieldsToSave = Array.from(pendingSaveRef.current);
        pendingSaveRef.current.clear();
        
        fieldsToSave.forEach(field => {
          saveField(field).catch(console.error);
        });
      }, debounceMs);
    }
  }, [autoSave, debounceMs]);
  
  // Save a single field to the backend
  const saveField = useCallback(async (fieldPath: string) => {
    const change = changes.get(fieldPath);
    if (!change) return;
    
    try {
      setIsSaving(true);
      setSaveError(null);
      
      await apiClient.updateExtractedField(submissionId, fieldPath, change.currentValue);
      
      // Mark as saved (keep in changes for tracking but update status)
      setChanges(prev => {
        const newChanges = new Map(prev);
        const existing = newChanges.get(fieldPath);
        if (existing) {
          newChanges.set(fieldPath, {
            ...existing,
            // Keep the change tracked but it's now saved
          });
        }
        return newChanges;
      });
      
      onSaveSuccess?.(fieldPath, change.currentValue);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save field';
      setSaveError(errorMessage);
      onSaveError?.(fieldPath, error instanceof Error ? error : new Error(errorMessage));
    } finally {
      setIsSaving(false);
    }
  }, [submissionId, changes, onSaveSuccess, onSaveError]);
  
  // Save all pending changes
  const saveAllChanges = useCallback(async () => {
    if (changes.size === 0) return;
    
    setIsSaving(true);
    setSaveError(null);
    
    const allChanges: Record<string, any> = {};
    changes.forEach((change, path) => {
      allChanges[path] = change.currentValue;
    });
    
    try {
      await apiClient.updateMultipleExtractedFields(submissionId, allChanges);
      
      // Clear all changes after successful save
      setChanges(new Map());
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save changes';
      setSaveError(errorMessage);
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [submissionId, changes]);
  
  // Discard changes
  const discardChanges = useCallback((fieldPath?: string) => {
    if (fieldPath) {
      setChanges(prev => {
        const newChanges = new Map(prev);
        newChanges.delete(fieldPath);
        return newChanges;
      });
    } else {
      setChanges(new Map());
    }
    setSaveError(null);
  }, []);
  
  // Get the current value for a field (edited or original)
  const getFieldValue = useCallback((fieldPath: string, originalValue: any) => {
    const change = changes.get(fieldPath);
    return change ? change.currentValue : originalValue;
  }, [changes]);
  
  // Check if a field has been edited
  const isFieldEdited = useCallback((fieldPath: string) => {
    return changes.has(fieldPath);
  }, [changes]);
  
  // Get the change record for a field
  const getFieldChange = useCallback((fieldPath: string) => {
    return changes.get(fieldPath);
  }, [changes]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);
  
  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);
  
  return {
    editingField,
    changes,
    isSaving,
    saveError,
    hasUnsavedChanges,
    startEdit,
    cancelEdit,
    updateField,
    saveField,
    saveAllChanges,
    discardChanges,
    getFieldValue,
    isFieldEdited,
    getFieldChange,
  };
}

















