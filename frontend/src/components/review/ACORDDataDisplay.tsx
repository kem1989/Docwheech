'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Edit2, 
  Check, 
  X, 
  AlertCircle,
  Building2,
  User,
  Users,
  FileText,
  MapPin,
  Phone,
  Calendar,
  DollarSign,
  Sparkles,
  Clock,
  ChevronLeft,
  ChevronRight,
  LayoutGrid
} from 'lucide-react';

interface FieldData {
  value: any;
  confidence: number;
  validation_status: 'validated' | 'pending' | 'failed';
  source?: string;
}

interface ACORDDataDisplayProps {
  extractedData: any;
  acordSchema: any;
  processingStats: {
    total_documents: number;
    total_pages: number;
    average_confidence: number;
    extraction_method: string;
    completion_percentage: number;
    missing_fields: string[];
  };
  onFieldEdit?: (fieldPath: string, newValue: any) => void;
  onFieldValidate?: (fieldPath: string) => void;
}

// ============================================================================
// Utility Functions
// ============================================================================

const formatLabel = (label: string): string =>
  label
    .replace(/\[\d+\]/g, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());

const isGeneralQuestionsSection = (sectionKey: string): boolean => {
  const normalized = sectionKey.toLowerCase();
  return normalized.includes('general_question') || normalized.includes('generalquestion');
};

const isPrimitiveValue = (val: any): boolean =>
  val === null || val === undefined || typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean';

const isFieldDataObject = (val: any): val is FieldData =>
  typeof val === 'object' &&
  val !== null &&
  'value' in val &&
  'confidence' in val &&
  'validation_status' in val;

// ============================================================================
// Icon Mappings
// ============================================================================

const sectionIconMap: Record<string, React.ComponentType<any>> = {
  agency: Building2,
  transaction_status: Clock,
  policy: FileText,
  lines_of_business: FileText,
  first_named_insured: User,
  other_named_insureds: Users,
  contacts: Phone,
  nature_of_business: FileText,
  premises: MapPin,
  prior_carriers: DollarSign,
  loss_history: AlertCircle,
  signatures: Edit2,
};

// ============================================================================
// Small Components
// ============================================================================

const ConfidenceBadge = ({ confidence }: { confidence: number }) => {
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

// ============================================================================
// Field Editor
// ============================================================================

const FieldEditor = ({ 
  value, 
  fieldType = 'text',
  onSave,
  onCancel 
}: {
  value: any;
  fieldType?: string;
  onSave: (newValue: any) => void;
  onCancel: () => void;
}) => {
  const [editValue, setEditValue] = useState(value || '');

  return (
    <div className="space-y-3">
      {fieldType === 'textarea' ? (
        <Textarea
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          className="min-h-[80px] text-sm"
          autoFocus
        />
      ) : (
        <Input
          type={fieldType === 'number' ? 'number' : fieldType === 'date' ? 'date' : 'text'}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          className="text-sm"
          autoFocus
        />
      )}
      <div className="flex gap-2">
        <Button size="sm" onClick={() => onSave(editValue)} className="h-7 px-3 text-xs">
          <Check className="h-3 w-3 mr-1" />
          Save
        </Button>
        <Button size="sm" variant="ghost" onClick={onCancel} className="h-7 px-3 text-xs">
          <X className="h-3 w-3 mr-1" />
          Cancel
        </Button>
      </div>
    </div>
  );
};

// ============================================================================
// Single Field Display
// ============================================================================

const FieldItem = ({ 
  label,
  fieldData, 
  onEdit,
  onValidate,
  fieldPath
}: {
  label: string;
  fieldData: FieldData;
  onEdit?: (fieldPath: string) => void;
  onValidate?: (fieldPath: string) => void;
  fieldPath: string;
}) => {
  const [isEditing, setIsEditing] = useState(false);

  if (isEditing) {
    return (
      <div className="p-4 bg-white rounded-xl border-2 border-indigo-200 shadow-sm">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">{label}</div>
        <FieldEditor
          value={fieldData.value}
          onSave={() => {
            onEdit?.(fieldPath);
            setIsEditing(false);
          }}
          onCancel={() => setIsEditing(false)}
        />
      </div>
    );
  }

  return (
    <div className="group p-4 bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <ValidationDot status={fieldData.validation_status} />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide truncate">{label}</span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ConfidenceBadge confidence={fieldData.confidence} />
          <button
            onClick={() => setIsEditing(true)}
            className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-indigo-50 transition-all"
          >
            <Edit2 className="h-3.5 w-3.5 text-indigo-500" />
          </button>
        </div>
      </div>
      <div className="text-sm text-slate-800 font-medium break-words leading-relaxed">
        {fieldData.value || <span className="text-slate-400 italic font-normal">Not provided</span>}
      </div>
    </div>
  );
};

// ============================================================================
// Section Content Component
// ============================================================================

const SectionContent = ({ 
  data, 
  onFieldEdit,
  onFieldValidate,
  isLegacyLayout = false,
}: {
  data: any;
  onFieldEdit?: (fieldPath: string) => void;
  onFieldValidate?: (fieldPath: string) => void;
  isLegacyLayout?: boolean;
}) => {
  const renderFields = (obj: any, prefix = ''): React.ReactNode[] => {
    const nodes: React.ReactNode[] = [];

    if (!obj || typeof obj !== 'object') return nodes;

    Object.entries(obj).forEach(([key, value]) => {
      const path = prefix ? `${prefix}.${key}` : key;
      const label = formatLabel(key);

      if (isFieldDataObject(value)) {
        nodes.push(
          <FieldItem
            key={path}
            label={label}
            fieldData={value}
            fieldPath={path}
            onEdit={onFieldEdit}
            onValidate={onFieldValidate}
          />
        );
        return;
      }

      if (isPrimitiveValue(value)) {
        const fieldData: FieldData = {
          value: value === null || value === undefined ? null : String(value),
          confidence: 0.85,
          validation_status: 'validated',
        };
        nodes.push(
          <FieldItem
            key={path}
            label={label}
            fieldData={fieldData}
            fieldPath={path}
            onEdit={onFieldEdit}
            onValidate={onFieldValidate}
          />
        );
        return;
      }

      if (Array.isArray(value)) {
        if (value.length === 0) {
          nodes.push(
            <FieldItem
              key={path}
              label={label}
              fieldData={{ value: 'No entries', confidence: 0.6, validation_status: 'pending' }}
              fieldPath={path}
              onEdit={onFieldEdit}
              onValidate={onFieldValidate}
            />
          );
          return;
        }

        const isPrimitiveArray = value.every(item => isPrimitiveValue(item) || isFieldDataObject(item));
        if (isPrimitiveArray) {
          const displayValue = value.map(item => 
            isFieldDataObject(item) ? item.value : (item ?? '—')
          ).join(', ');
          nodes.push(
            <FieldItem
              key={path}
              label={label}
              fieldData={{ value: displayValue, confidence: 0.85, validation_status: 'validated' }}
              fieldPath={path}
              onEdit={onFieldEdit}
              onValidate={onFieldValidate}
            />
          );
          return;
        }

        nodes.push(
          <div key={path} className="col-span-full">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-sm font-bold text-slate-700">{label}</span>
              <Badge className="bg-indigo-100 text-indigo-700 border-0">{value.length}</Badge>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {value.map((item, idx) => (
                <div key={`${path}[${idx}]`} className="p-5 bg-gradient-to-br from-slate-50 to-white rounded-2xl border border-slate-200">
                  <div className="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-4">
                    {label} {idx + 1}
                  </div>
                  <div className="space-y-3">
                    {typeof item === 'object' && item !== null
                      ? renderFields(item, `${path}[${idx}]`)
                      : (
                        <FieldItem
                          label={`Item ${idx + 1}`}
                          fieldData={{ value: String(item), confidence: 0.85, validation_status: 'validated' }}
                          fieldPath={`${path}[${idx}]`}
                          onEdit={onFieldEdit}
                          onValidate={onFieldValidate}
                        />
                      )
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
        return;
      }

      if (typeof value === 'object' && value !== null) {
        const nestedFields = renderFields(value, path);
        if (nestedFields.length > 0) {
          nodes.push(
            <div key={path} className="col-span-full">
              <div className="text-sm font-bold text-slate-700 mb-4">{label}</div>
              <div className="p-5 bg-gradient-to-br from-slate-50 to-white rounded-2xl border border-slate-200">
                <div className="grid gap-3 sm:grid-cols-2">
                  {nestedFields}
                </div>
              </div>
            </div>
          );
        }
      }
    });

    return nodes;
  };

  const fields = renderFields(data);
  const gridClass = isLegacyLayout 
    ? 'space-y-4' 
    : 'grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';

  return (
    <div className={gridClass}>
      {fields.length > 0 ? fields : (
        <div className="text-sm text-slate-400 italic py-8 text-center col-span-full">No data available</div>
      )}
    </div>
  );
};

// ============================================================================
// Stats Summary Component
// ============================================================================

const StatsSummary = ({ processingStats }: { processingStats: ACORDDataDisplayProps['processingStats'] }) => (
  <div className="grid grid-cols-4 gap-3">
    <div className="text-center p-4 bg-white rounded-2xl border border-slate-200">
      <div className="text-2xl font-bold text-blue-600">{processingStats.total_documents}</div>
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mt-1">Documents</div>
    </div>
    <div className="text-center p-4 bg-white rounded-2xl border border-slate-200">
      <div className="text-2xl font-bold text-emerald-600">{Math.round(processingStats.average_confidence * 100)}%</div>
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mt-1">Confidence</div>
    </div>
    <div className="text-center p-4 bg-white rounded-2xl border border-slate-200">
      <div className="text-2xl font-bold text-violet-600">{Math.round(processingStats.completion_percentage)}%</div>
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mt-1">Complete</div>
    </div>
    <div className="text-center p-4 bg-white rounded-2xl border border-slate-200">
      <div className="text-2xl font-bold text-amber-600">{processingStats.missing_fields.length}</div>
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mt-1">Missing</div>
    </div>
  </div>
);

// ============================================================================
// Main Component
// ============================================================================

export default function ACORDDataDisplay({ 
  extractedData, 
  acordSchema, 
  processingStats,
  onFieldEdit,
  onFieldValidate 
}: ACORDDataDisplayProps) {
  const [activeDataTab, setActiveDataTab] = useState<'extracted' | 'acord'>('extracted');
  const [activeSectionIndex, setActiveSectionIndex] = useState(0);

  const currentData = activeDataTab === 'extracted' ? extractedData : acordSchema;

  const sections = currentData 
    ? Object.keys(currentData).map(key => ({
        id: key,
        title: formatLabel(key),
        icon: sectionIconMap[key] ?? FileText
      }))
    : [];

  const currentSection = sections[activeSectionIndex];
  const currentSectionData = currentSection ? currentData[currentSection.id] : null;
  const isLegacy = currentSection ? isGeneralQuestionsSection(currentSection.id) : false;

  const handleFieldEdit = (fieldPath: string) => {
    onFieldEdit?.(fieldPath, '');
  };

  const handleFieldValidate = (fieldPath: string) => {
    onFieldValidate?.(fieldPath);
  };

  const goToPrevSection = () => {
    if (activeSectionIndex > 0) {
      setActiveSectionIndex(activeSectionIndex - 1);
    }
  };

  const goToNextSection = () => {
    if (activeSectionIndex < sections.length - 1) {
      setActiveSectionIndex(activeSectionIndex + 1);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header with Stats */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-900 rounded-3xl p-6 text-white">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">ACORD Form Review</h1>
            <p className="text-slate-300 text-sm mt-1">Review and validate extracted insurance data</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveDataTab('extracted')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeDataTab === 'extracted'
                  ? 'bg-white text-slate-900'
                  : 'bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              <span className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Extracted
              </span>
            </button>
            <button
              onClick={() => setActiveDataTab('acord')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeDataTab === 'acord'
                  ? 'bg-white text-slate-900'
                  : 'bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              <span className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                ACORD Schema
              </span>
            </button>
          </div>
        </div>
        <StatsSummary processingStats={processingStats} />
      </div>

      {/* Horizontal Tab Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Scrollable Tabs */}
        <div className="border-b border-slate-200">
          <div className="flex overflow-x-auto scrollbar-hide">
            {sections.map((section, index) => {
              const Icon = section.icon;
              const isActive = index === activeSectionIndex;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSectionIndex(index)}
                  className={`flex items-center gap-2 px-5 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-all ${
                    isActive
                      ? 'border-indigo-600 text-indigo-600 bg-indigo-50/50'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{section.title}</span>
                  {isActive && (
                    <span className="ml-1 px-2 py-0.5 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                      {index + 1}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Section Header */}
        {currentSection && (
          <div className="px-6 py-4 bg-gradient-to-r from-slate-50 to-white border-b border-slate-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-indigo-100">
                  <currentSection.icon className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-800">{currentSection.title}</h2>
                  <p className="text-sm text-slate-500">
                    Section {activeSectionIndex + 1} of {sections.length}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={goToPrevSection}
                  disabled={activeSectionIndex === 0}
                  className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="h-5 w-5 text-slate-600" />
                </button>
                <button
                  onClick={goToNextSection}
                  disabled={activeSectionIndex === sections.length - 1}
                  className="p-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="h-5 w-5 text-slate-600" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Section Content */}
        <div className="p-6 bg-slate-50/30 min-h-[400px]">
          {currentSectionData ? (
            <SectionContent
              data={currentSectionData}
              onFieldEdit={handleFieldEdit}
              onFieldValidate={handleFieldValidate}
              isLegacyLayout={isLegacy}
            />
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-slate-400">
              <LayoutGrid className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-sm">No data available for this section</p>
            </div>
          )}
        </div>

        {/* Footer Navigation */}
        <div className="px-6 py-4 bg-white border-t border-slate-200">
          <div className="flex items-center justify-between">
            <button
              onClick={goToPrevSection}
              disabled={activeSectionIndex === 0}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>
            
            {/* Progress Dots */}
            <div className="flex items-center gap-1.5">
              {sections.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setActiveSectionIndex(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === activeSectionIndex
                      ? 'w-6 bg-indigo-600'
                      : index < activeSectionIndex
                      ? 'bg-indigo-300'
                      : 'bg-slate-300'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={goToNextSection}
              disabled={activeSectionIndex === sections.length - 1}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Missing Fields Alert */}
      {processingStats.missing_fields.length > 0 && (
        <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-amber-800">
              <AlertCircle className="h-5 w-5" />
              <span>Missing Fields</span>
              <Badge className="bg-amber-200 text-amber-800 border-0 ml-2">
                {processingStats.missing_fields.length}
              </Badge>
            </CardTitle>
            <CardDescription className="text-amber-700">
              These fields could not be extracted from the documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {processingStats.missing_fields.map((field, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="bg-white border-amber-300 text-amber-700 px-3 py-1"
                >
                  {field.replace(/_/g, ' ')}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
