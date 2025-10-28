'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  FileText,
  Zap
} from 'lucide-react';

interface ExtractionProgressProps {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  processedFiles: number;
  totalFiles: number;
  estimatedTime?: string;
  onRefresh?: () => void;
  onRetry?: () => void;
}

const StatusIcon = ({ status }: { status: string }) => {
  const iconProps = { className: "h-5 w-5" };
  
  switch (status) {
    case 'completed':
      return <CheckCircle {...iconProps} className="text-green-500" />;
    case 'processing':
      return <RefreshCw {...iconProps} className="text-blue-500 animate-spin" />;
    case 'failed':
      return <AlertCircle {...iconProps} className="text-red-500" />;
    default:
      return <Clock {...iconProps} className="text-gray-500" />;
  }
};

const StatusBadge = ({ status }: { status: string }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Badge className={getStatusColor(status)}>
      <StatusIcon status={status} />
      <span className="ml-1 capitalize">{status}</span>
    </Badge>
  );
};

const ProcessingSteps = ({ currentStep }: { currentStep: number }) => {
  const steps = [
    { id: 1, name: 'Document Analysis', description: 'Analyzing uploaded documents' },
    { id: 2, name: 'Text Extraction', description: 'Extracting text using AWS Textract' },
    { id: 3, name: 'AI Processing', description: 'Processing with OpenAI GPT-4' },
    { id: 4, name: 'Data Validation', description: 'Validating and structuring data' },
    { id: 5, name: 'ACORD Mapping', description: 'Mapping to ACORD 125 schema' }
  ];

  return (
    <div className="space-y-3">
      {steps.map((step) => (
        <div key={step.id} className="flex items-center space-x-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            step.id <= currentStep 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-500'
          }`}>
            {step.id < currentStep ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              step.id
            )}
          </div>
          <div className="flex-1">
            <div className={`text-sm font-medium ${
              step.id <= currentStep ? 'text-gray-900' : 'text-gray-500'
            }`}>
              {step.name}
            </div>
            <div className={`text-xs ${
              step.id <= currentStep ? 'text-gray-600' : 'text-gray-400'
            }`}>
              {step.description}
            </div>
          </div>
          {step.id === currentStep && (
            <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
          )}
        </div>
      ))}
    </div>
  );
};

export default function ExtractionProgress({
  status,
  progress,
  processedFiles,
  totalFiles,
  estimatedTime = "2-5 minutes",
  onRefresh,
  onRetry
}: ExtractionProgressProps) {
  // Debug logging
  console.log('🎨 ExtractionProgress Render:', { status, progress, processedFiles, totalFiles });
  
  const getCurrentStep = () => {
    if (progress < 20) return 1;
    if (progress < 40) return 2;
    if (progress < 60) return 3;
    if (progress < 80) return 4;
    return 5;
  };

  const getStatusMessage = () => {
    switch (status) {
      case 'pending':
        return 'Ready to start extraction';
      case 'processing':
        return `Processing documents... ${processedFiles}/${totalFiles} files completed`;
      case 'completed':
        return 'Extraction completed successfully';
      case 'failed':
        return 'Extraction failed. Please try again';
      default:
        return 'Unknown status';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>AI Data Extraction</span>
          </div>
          <StatusBadge status={status} />
        </CardTitle>
        <CardDescription>
          {getStatusMessage()}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        {status === 'processing' && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Overall Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="w-full" />
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{processedFiles} of {totalFiles} files processed</span>
              <span>Estimated time: {estimatedTime}</span>
            </div>
          </div>
        )}

        {/* Processing Steps */}
        {status === 'processing' && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Processing Steps</h4>
            <ProcessingSteps currentStep={getCurrentStep()} />
          </div>
        )}

        {/* File Processing Status */}
        {status === 'processing' && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">File Processing</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <FileText className="h-4 w-4 text-blue-500" />
                <span>Total Files: {totalFiles}</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>Processed: {processedFiles}</span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-2">
          {status === 'processing' && onRefresh && (
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Status
            </Button>
          )}
          {status === 'failed' && onRetry && (
            <Button size="sm" onClick={onRetry}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Extraction
            </Button>
          )}
        </div>

        {/* Completion Message */}
        {status === 'completed' && (
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm font-medium text-green-800">
                Extraction completed successfully!
              </span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              All documents have been processed and data has been extracted.
            </p>
          </div>
        )}

        {/* Error Message */}
        {status === 'failed' && (
          <div className="p-4 bg-red-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-sm font-medium text-red-800">
                Extraction failed
              </span>
            </div>
            <p className="text-sm text-red-700 mt-1">
              There was an error processing the documents. Please try again or contact support.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}




