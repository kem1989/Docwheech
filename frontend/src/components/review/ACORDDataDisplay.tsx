'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  ChevronDown, 
  ChevronRight, 
  Edit, 
  Check, 
  X, 
  AlertCircle,
  CheckCircle,
  Clock,
  Building2,
  User,
  FileText,
  MapPin,
  Phone,
  Mail,
  Calendar,
  DollarSign
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

const FieldIcon = ({ fieldType }: { fieldType: string }) => {
  const iconProps = { className: "h-4 w-4" };
  
  switch (fieldType) {
    case 'company_name':
    case 'business_name':
      return <Building2 {...iconProps} />;
    case 'contact_name':
    case 'broker_name':
      return <User {...iconProps} />;
    case 'address':
    case 'mailing_address':
      return <MapPin {...iconProps} />;
    case 'phone':
    case 'fax':
      return <Phone {...iconProps} />;
    case 'email':
      return <Mail {...iconProps} />;
    case 'date':
    case 'effective_date':
    case 'expiration_date':
      return <Calendar {...iconProps} />;
    case 'premium':
    case 'amount':
      return <DollarSign {...iconProps} />;
    default:
      return <FileText {...iconProps} />;
  }
};

const ConfidenceBadge = ({ confidence }: { confidence: number }) => {
  if (confidence >= 0.9) {
    return <Badge className="bg-green-100 text-green-800">High ({Math.round(confidence * 100)}%)</Badge>;
  } else if (confidence >= 0.7) {
    return <Badge className="bg-yellow-100 text-yellow-800">Medium ({Math.round(confidence * 100)}%)</Badge>;
  } else {
    return <Badge className="bg-red-100 text-red-800">Low ({Math.round(confidence * 100)}%)</Badge>;
  }
};

const ValidationStatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'validated':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'failed':
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    default:
      return <Clock className="h-4 w-4 text-yellow-500" />;
  }
};

const FieldEditor = ({ 
  fieldPath, 
  value, 
  fieldType = 'text',
  onSave,
  onCancel 
}: {
  fieldPath: string;
  value: any;
  fieldType?: string;
  onSave: (newValue: any) => void;
  onCancel: () => void;
}) => {
  const [editValue, setEditValue] = useState(value || '');

  const handleSave = () => {
    onSave(editValue);
  };

  const renderInput = () => {
    switch (fieldType) {
      case 'textarea':
        return (
          <Textarea
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="min-h-[100px]"
          />
        );
      case 'number':
        return (
          <Input
            type="number"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
          />
        );
      case 'date':
        return (
          <Input
            type="date"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
          />
        );
      default:
        return (
          <Input
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
          />
        );
    }
  };

  return (
    <div className="space-y-2">
      {renderInput()}
      <div className="flex space-x-2">
        <Button size="sm" onClick={handleSave}>
          <Check className="h-3 w-3 mr-1" />
          Save
        </Button>
        <Button size="sm" variant="outline" onClick={onCancel}>
          <X className="h-3 w-3 mr-1" />
          Cancel
        </Button>
      </div>
    </div>
  );
};

const FieldDisplay = ({ 
  fieldPath, 
  fieldData, 
  fieldType = 'text',
  onEdit,
  onValidate 
}: {
  fieldPath: string;
  fieldData: FieldData;
  fieldType?: string;
  onEdit?: (fieldPath: string) => void;
  onValidate?: (fieldPath: string) => void;
}) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = (newValue: any) => {
    onEdit?.(fieldPath);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <FieldEditor
        fieldPath={fieldPath}
        value={fieldData.value}
        fieldType={fieldType}
        onSave={handleSave}
        onCancel={handleCancel}
      />
    );
  }

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-1">
          <FieldIcon fieldType={fieldPath.split('.').pop() || ''} />
          <span className="text-sm font-medium text-gray-700 capitalize">
            {fieldPath.split('.').pop()?.replace(/_/g, ' ')}
          </span>
          <ValidationStatusIcon status={fieldData.validation_status} />
        </div>
        <div className="text-sm text-gray-900 mb-2">
          {fieldData.value || <span className="text-gray-400 italic">No value</span>}
        </div>
        <div className="flex items-center space-x-2">
          <ConfidenceBadge confidence={fieldData.confidence} />
          {fieldData.source && (
            <Badge variant="outline" className="text-xs">
              {fieldData.source}
            </Badge>
          )}
        </div>
      </div>
      <div className="flex space-x-1">
        <Button
          size="sm"
          variant="outline"
          onClick={handleEdit}
        >
          <Edit className="h-3 w-3" />
        </Button>
        {onValidate && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onValidate(fieldPath)}
          >
            <CheckCircle className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  );
};

const SectionDisplay = ({ 
  title, 
  data, 
  icon: Icon,
  onFieldEdit,
  onFieldValidate 
}: {
  title: string;
  data: any;
  icon: React.ComponentType<any>;
  onFieldEdit?: (fieldPath: string) => void;
  onFieldValidate?: (fieldPath: string) => void;
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  // Handle primitive values (string, number, boolean) at the section level
  const isPrimitive = (val: any): boolean => {
    return (
      val === null ||
      val === undefined ||
      typeof val === 'string' ||
      typeof val === 'number' ||
      typeof val === 'boolean'
    );
  };

  const renderFields = (obj: any, prefix = '') => {
    // If obj is primitive, display it directly
    if (isPrimitive(obj)) {
      const fieldData: FieldData = {
        value: obj === null || obj === undefined ? null : String(obj),
        confidence: 0.9,
        validation_status: 'validated'
      };
      return (
        <FieldDisplay
          key={prefix || 'value'}
          fieldPath={prefix || title.toLowerCase().replace(/\s+/g, '_')}
          fieldData={fieldData}
          onEdit={onFieldEdit}
          onValidate={onFieldValidate}
        />
      );
    }

    // If obj is not an object, return null
    if (typeof obj !== 'object' || obj === null) {
      return null;
    }

    return Object.entries(obj).map(([key, value]) => {
      const fieldPath = prefix ? `${prefix}.${key}` : key;
      
      // Handle null/undefined
      if (value === null || value === undefined) {
        const fieldData: FieldData = {
          value: null,
          confidence: 0.0,
          validation_status: 'pending'
        };
        return (
          <FieldDisplay
            key={fieldPath}
            fieldPath={fieldPath}
            fieldData={fieldData}
            onEdit={onFieldEdit}
            onValidate={onFieldValidate}
          />
        );
      }
      
      // Handle arrays (must check before typeof object)
      if (Array.isArray(value)) {
        // Array - check if it contains objects or primitives
        const isPrimitiveArray = value.length > 0 && (typeof value[0] !== 'object' || value[0] === null);
        
        if (isPrimitiveArray) {
          // Array of primitives (strings, numbers, etc.)
          const fieldData: FieldData = {
            value: value.join(', '),  // Display as comma-separated list
            confidence: 0.9,
            validation_status: 'validated'
          };
          
          return (
            <div key={fieldPath} className="ml-4">
              <h5 className="text-sm font-medium text-gray-600 mb-2 capitalize">
                {key.replace(/_/g, ' ')} ({value.length})
              </h5>
              <FieldDisplay
                fieldPath={fieldPath}
                fieldData={fieldData}
                onEdit={onFieldEdit}
                onValidate={onFieldValidate}
              />
            </div>
          );
        } else {
          // Array of objects
          return (
            <div key={fieldPath} className="ml-4">
              <h5 className="text-sm font-medium text-gray-600 mb-2 capitalize">
                {key.replace(/_/g, ' ')} ({value.length})
              </h5>
              {value.map((item, index) => (
                <div key={index} className="ml-4 mb-2">
                  {typeof item === 'object' && item !== null ? (
                    renderFields(item, `${fieldPath}[${index}]`)
                  ) : (
                    <div className="text-sm text-gray-900">{String(item)}</div>
                  )}
                </div>
              ))}
            </div>
          );
        }
      }
      
      // Handle nested objects (after arrays, before primitives)
      if (typeof value === 'object' && value !== null) {
        return (
          <div key={fieldPath} className="ml-4">
            <h5 className="text-sm font-medium text-gray-600 mb-2 capitalize">
              {key.replace(/_/g, ' ')}
            </h5>
            {renderFields(value, fieldPath)}
          </div>
        );
      }
      
      // Handle primitive values (string, number, boolean)
      const fieldData: FieldData = {
        value: String(value), // Convert to string for display
        confidence: 0.9, // Default confidence for simple fields
        validation_status: 'validated'
      };
      
      return (
        <FieldDisplay
          key={fieldPath}
          fieldPath={fieldPath}
          fieldData={fieldData}
          onEdit={onFieldEdit}
          onValidate={onFieldValidate}
        />
      );
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Icon className="h-5 w-5" />
          <span>{title}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </CardTitle>
      </CardHeader>
      {isExpanded && (
        <CardContent>
          <div className="space-y-3">
            {renderFields(data)}
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default function ACORDDataDisplay({ 
  extractedData, 
  acordSchema, 
  processingStats,
  onFieldEdit,
  onFieldValidate 
}: ACORDDataDisplayProps) {
  const [activeTab, setActiveTab] = useState<'extracted' | 'acord'>('extracted');

  const handleFieldEdit = (fieldPath: string) => {
    onFieldEdit?.(fieldPath, '');
  };

  const handleFieldValidate = (fieldPath: string) => {
    onFieldValidate?.(fieldPath);
  };

  return (
    <div className="space-y-6">
      {/* Processing Stats */}
      <Card>
        <CardHeader>
          <CardTitle>Extraction Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {processingStats.total_documents}
              </div>
              <div className="text-sm text-gray-600">Documents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {Math.round(processingStats.average_confidence * 100)}%
              </div>
              <div className="text-sm text-gray-600">Confidence</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(processingStats.completion_percentage)}%
              </div>
              <div className="text-sm text-gray-600">Complete</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {processingStats.missing_fields.length}
              </div>
              <div className="text-sm text-gray-600">Missing</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <Button
          variant={activeTab === 'extracted' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('extracted')}
          className="flex-1"
        >
          Raw Extracted Data
        </Button>
        <Button
          variant={activeTab === 'acord' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('acord')}
          className="flex-1"
        >
          ACORD Schema
        </Button>
      </div>

      {/* Data Display */}
      {activeTab === 'extracted' && extractedData && (
        <div className="space-y-4">
          {Object.entries(extractedData).map(([section, data]) => (
            <SectionDisplay
              key={section}
              title={section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              data={data}
              icon={FileText}
              onFieldEdit={handleFieldEdit}
              onFieldValidate={handleFieldValidate}
            />
          ))}
        </div>
      )}

      {activeTab === 'acord' && acordSchema && (
        <div className="space-y-4">
          {Object.entries(acordSchema).map(([section, data]) => (
            <SectionDisplay
              key={section}
              title={section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              data={data}
              icon={FileText}
              onFieldEdit={handleFieldEdit}
              onFieldValidate={handleFieldValidate}
            />
          ))}
        </div>
      )}

      {/* Missing Fields */}
      {processingStats.missing_fields.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-orange-500" />
              <span>Missing Fields</span>
            </CardTitle>
            <CardDescription>
              Fields that could not be extracted from the documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {processingStats.missing_fields.map((field, index) => (
                <Badge key={index} variant="outline" className="text-orange-600">
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


