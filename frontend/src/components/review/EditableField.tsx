'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Edit2, 
  Check, 
  X, 
  RotateCcw,
  AlertCircle,
  Loader2,
  History
} from 'lucide-react';

export interface FieldData {
  value: any;
  confidence: number;
  validation_status: 'validated' | 'pending' | 'failed';
  source?: string;
}

export interface EditableFieldProps {
  label: string;
  fieldPath: string;
  fieldData: FieldData;
  originalValue?: any;
  isEdited?: boolean;
  isSaving?: boolean;
  saveError?: string | null;
  fieldType?: 'text' | 'number' | 'date' | 'email' | 'phone' | 'currency' | 'textarea';
  placeholder?: string;
  required?: boolean;
  validation?: (value: any) => string | null; // Returns error message or null
  onEdit: (fieldPath: string, newValue: any, originalValue: any) => void;
  onSave?: (fieldPath: string) => void;
  onRevert?: (fieldPath: string) => void;
}

// Confidence Badge Component
const ConfidenceBadge = ({ confidence, isEdited }: { confidence: number; isEdited?: boolean }) => {
  if (isEdited) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
        <Edit2 className="h-3 w-3 mr-1" />
        Edited
      </span>
    );
  }
  
  const percent = Math.round(confidence * 100);
  if (confidence >= 0.9) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
        {percent}%
      </span>
    );
  } else if (confidence >= 0.7) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
        {percent}%
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-50 text-rose-700 border border-rose-200">
      {percent}%
    </span>
  );
};

// Validation Status Dot
const ValidationDot = ({ status }: { status: string }) => {
  switch (status) {
    case 'validated':
      return <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" title="Validated" />;
    case 'failed':
      return <span className="w-2 h-2 rounded-full bg-rose-500 shrink-0" title="Failed" />;
    default:
      return <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0" title="Pending" />;
  }
};

export default function EditableField({
  label,
  fieldPath,
  fieldData,
  originalValue,
  isEdited = false,
  isSaving = false,
  saveError = null,
  fieldType = 'text',
  placeholder,
  required = false,
  validation,
  onEdit,
  onSave,
  onRevert,
}: EditableFieldProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState<string>('');
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Initialize edit value when entering edit mode
  useEffect(() => {
    if (isEditing) {
      setEditValue(formatValueForEdit(fieldData.value));
      setValidationError(null);
    }
  }, [isEditing, fieldData.value]);

  // Focus input when entering edit mode
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select?.();
    }
  }, [isEditing]);

  // Format value for editing
  const formatValueForEdit = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object') return JSON.stringify(value);
    return String(value);
  };

  // Format value for display
  const formatValueForDisplay = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (fieldType === 'currency' && typeof value === 'number') {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
    }
    if (fieldType === 'date' && value) {
      try {
        return new Date(value).toLocaleDateString();
      } catch {
        return String(value);
      }
    }
    return String(value);
  };

  // Parse value from edit input
  const parseEditValue = (value: string): any => {
    if (fieldType === 'number' || fieldType === 'currency') {
      const parsed = parseFloat(value.replace(/[^0-9.-]/g, ''));
      return isNaN(parsed) ? value : parsed;
    }
    return value;
  };

  // Handle save
  const handleSave = () => {
    const parsedValue = parseEditValue(editValue);
    
    // Run validation
    if (validation) {
      const error = validation(parsedValue);
      if (error) {
        setValidationError(error);
        return;
      }
    }
    
    // Required field check
    if (required && !editValue.trim()) {
      setValidationError('This field is required');
      return;
    }
    
    onEdit(fieldPath, parsedValue, originalValue ?? fieldData.value);
    setIsEditing(false);
    onSave?.(fieldPath);
  };

  // Handle cancel
  const handleCancel = () => {
    setIsEditing(false);
    setEditValue('');
    setValidationError(null);
  };

  // Handle revert to original
  const handleRevert = () => {
    onRevert?.(fieldPath);
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && fieldType !== 'textarea') {
      e.preventDefault();
      handleSave();
    }
    if (e.key === 'Escape') {
      handleCancel();
    }
  };

  // Get input type for HTML input
  const getInputType = (): string => {
    switch (fieldType) {
      case 'number':
      case 'currency':
        return 'text'; // Use text for better formatting control
      case 'date':
        return 'date';
      case 'email':
        return 'email';
      case 'phone':
        return 'tel';
      default:
        return 'text';
    }
  };

  // Editing mode
  if (isEditing) {
    return (
      <div className="p-4 bg-white rounded-xl border-2 border-indigo-300 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
            {label}
            {required && <span className="text-rose-500 ml-1">*</span>}
          </span>
          {isEdited && originalValue !== undefined && (
            <span className="text-xs text-slate-400">
              Original: {formatValueForDisplay(originalValue)}
            </span>
          )}
        </div>
        
        {fieldType === 'textarea' ? (
          <Textarea
            ref={inputRef as React.RefObject<HTMLTextAreaElement>}
            value={editValue}
            onChange={(e) => {
              setEditValue(e.target.value);
              setValidationError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`min-h-[100px] text-sm ${validationError ? 'border-rose-300 focus:border-rose-500' : ''}`}
          />
        ) : (
          <Input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type={getInputType()}
            value={editValue}
            onChange={(e) => {
              setEditValue(e.target.value);
              setValidationError(null);
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`text-sm ${validationError ? 'border-rose-300 focus:border-rose-500' : ''}`}
          />
        )}
        
        {validationError && (
          <div className="flex items-center gap-1 mt-2 text-xs text-rose-600">
            <AlertCircle className="h-3 w-3" />
            {validationError}
          </div>
        )}
        
        <div className="flex items-center gap-2 mt-3">
          <Button 
            size="sm" 
            onClick={handleSave}
            disabled={isSaving}
            className="h-8 px-3 text-xs"
          >
            {isSaving ? (
              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            ) : (
              <Check className="h-3 w-3 mr-1" />
            )}
            Save
          </Button>
          <Button 
            size="sm" 
            variant="ghost" 
            onClick={handleCancel}
            className="h-8 px-3 text-xs"
          >
            <X className="h-3 w-3 mr-1" />
            Cancel
          </Button>
          <div className="flex-1" />
          <span className="text-xs text-slate-400">
            Press Enter to save, Esc to cancel
          </span>
        </div>
      </div>
    );
  }

  // Display mode
  return (
    <div 
      className={`
        group p-4 rounded-xl border transition-all duration-200 cursor-pointer
        ${isEdited 
          ? 'bg-blue-50/50 border-blue-200 hover:border-blue-300' 
          : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-md'
        }
      `}
      onClick={() => setIsEditing(true)}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <ValidationDot status={fieldData.validation_status} />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide truncate">
            {label}
            {required && <span className="text-rose-500 ml-0.5">*</span>}
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ConfidenceBadge confidence={fieldData.confidence} isEdited={isEdited} />
          
          {isEdited && onRevert && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleRevert();
              }}
              className="p-1.5 rounded-lg hover:bg-amber-100 transition-all"
              title="Revert to original"
            >
              <RotateCcw className="h-3.5 w-3.5 text-amber-600" />
            </button>
          )}
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsEditing(true);
            }}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-indigo-50 transition-all"
            title="Edit field"
          >
            <Edit2 className="h-3.5 w-3.5 text-indigo-500" />
          </button>
        </div>
      </div>
      
      <div className="flex items-start justify-between gap-2">
        <div className="text-sm text-slate-800 font-medium break-words leading-relaxed flex-1">
          {fieldData.value ? (
            formatValueForDisplay(fieldData.value)
          ) : (
            <span className="text-slate-400 italic font-normal">Not provided</span>
          )}
        </div>
        
        {isSaving && (
          <Loader2 className="h-4 w-4 text-blue-500 animate-spin shrink-0" />
        )}
      </div>
      
      {saveError && (
        <div className="flex items-center gap-1 mt-2 text-xs text-rose-600">
          <AlertCircle className="h-3 w-3" />
          {saveError}
        </div>
      )}
      
      {isEdited && originalValue !== undefined && originalValue !== fieldData.value && (
        <div className="mt-2 flex items-center gap-1 text-xs text-slate-400">
          <History className="h-3 w-3" />
          <span>
            Changed from: <span className="text-slate-500">{formatValueForDisplay(originalValue)}</span>
          </span>
        </div>
      )}
    </div>
  );
}

















