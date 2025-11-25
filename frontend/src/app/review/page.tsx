'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useSubmissionStore } from '@/store/submission-store';
import { useAuthStore } from '@/store/auth-store';
import { apiClient, setAuthToken } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Download, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  RefreshCw,
  ArrowLeft,
  Eye,
  Edit
} from 'lucide-react';
import ACORDDataDisplay from '@/components/review/ACORDDataDisplay';
import ExtractionProgress from '@/components/review/ExtractionProgress';
import GeneralQuestionsForm from '@/components/review/GeneralQuestionsForm';

interface ExtractionStatus {
  submission_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_status: 'pending' | 'processing' | 'completed' | 'failed';
  extraction_progress: number;
  total_files: number;
  processed_files: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface ExtractedData {
  extraction_id: string;
  status: string;
  extracted_data: any;
  acord_schema: any;
  risk_narrative: string;
  processing_stats: {
    total_documents: number;
    total_pages: number;
    average_confidence: number;
    extraction_method: string;
    completion_percentage: number;
    missing_fields: string[];
  };
  extraction_timestamp: string;
}

export default function ReviewPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const submissionId = searchParams.get('submission');
  
  const { currentSubmission, documents, setCurrentSubmission, setDocuments } = useSubmissionStore();
  const { user, token } = useAuthStore();
  
  // Debug: Log submission ID and current submission
  console.log('=== Review Page Debug ===');
  console.log('Submission ID from URL:', submissionId);
  console.log('Current Submission in Store:', currentSubmission?.id);
  console.log('Extraction Status:', currentSubmission?.extraction_status);
  
  const [extractionStatus, setExtractionStatus] = useState<ExtractionStatus | null>(null);
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRawData, setShowRawData] = useState(false);
  const [isFillingPdf, setIsFillingPdf] = useState(false);
  const [pdfDownloadUrl, setPdfDownloadUrl] = useState<string | null>(null);

  const sanitizeAcordForFill = (acord: any) => {
    try {
      const clone = JSON.parse(JSON.stringify(acord));
      // Remove Workers Comp from lines_of_business
      if (Array.isArray(clone?.lines_of_business)) {
        clone.lines_of_business = clone.lines_of_business.filter((lob: any) => lob?.line !== 'WORKERS_COMPENSATION');
      }
      // Remap Workers Comp prior_carriers to OTHER
      if (Array.isArray(clone?.prior_carriers)) {
        clone.prior_carriers = clone.prior_carriers.map((pc: any) => {
          if (pc && pc.category === 'WORKERS_COMPENSATION') {
            return { ...pc, category: 'OTHER' };
          }
          return pc;
        });
      }
      return clone;
    } catch {
      return acord;
    }
  };

  // Load submission data on mount and when submission ID changes
  useEffect(() => {
    if (submissionId && token) {
      // Clear old state when loading new submission
      setExtractedData(null);
      setExtractionStatus(null);
      setError(null);
      setShowRawData(false);
      
      // Set the auth token in the API client
      setAuthToken(token);
      loadSubmissionData();
    }
  }, [submissionId, token]);

  // Poll for extraction status when processing
  useEffect(() => {
    const isProcessing = 
      extractionStatus?.status === 'processing' || 
      extractionStatus?.extraction_status === 'processing' ||
      currentSubmission?.extraction_status === 'processing';
    
    console.log('🔄 Polling check:', { isProcessing, extractionStatus: extractionStatus?.extraction_status, submission: currentSubmission?.extraction_status });
    
    if (isProcessing) {
      console.log('✅ Starting polling interval...', { submissionId, hasToken: !!token });
      const interval = setInterval(() => {
        console.log('⏰ Polling tick - checking extraction status...', { submissionId, hasToken: !!token });
        checkExtractionStatus();
      }, 2000); // Poll every 2 seconds
      
      return () => {
        console.log('🛑 Stopping polling interval');
        clearInterval(interval);
      };
    }
  }, [extractionStatus?.extraction_status, currentSubmission?.extraction_status]);

  const loadSubmissionData = async () => {
    if (!submissionId || !token) return;
    
    try {
      setIsLoadingData(true);
      setError(null);
      
      console.log('Loading submission data for ID:', submissionId);
      console.log('Using token:', token ? 'Present' : 'Missing');
      
      // Load submission details
      const submission = await apiClient.getSubmission(submissionId);
      console.log('Loaded submission:', submission);
      setCurrentSubmission(submission);
      
      // Load documents
      const filesData = await apiClient.getSubmissionFiles(submissionId);
      console.log('Loaded files:', filesData);
      setDocuments(filesData.documents);
      
      // Reset extraction state based on submission status
      if (submission.extraction_status === 'pending') {
        // Clear any old extraction data for pending submissions
        setExtractedData(null);
        setExtractionStatus(null);
        console.log('Submission is pending - ready for extraction');
      } else if (submission.extraction_status === 'processing') {
        // Start polling for progress
        console.log('Submission is processing - starting status check');
        checkExtractionStatus();
      } else if (submission.extraction_status === 'completed') {
        // Load the results
        console.log('Submission is completed - loading results');
        loadExtractionResults();
      } else if (submission.extraction_status === 'failed') {
        // Show error state
        console.log('Submission failed - showing error');
        setError(submission.extraction_error || 'Extraction failed. Please try again.');
      }
      
    } catch (err) {
      console.error('Failed to load submission data:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(`Failed to load submission data: ${errorMessage}`);
    } finally {
      setIsLoadingData(false);
    }
  };

  const startExtraction = async () => {
    if (!submissionId || !token || documents.length === 0) return;
    
    try {
      setIsExtracting(true);
      setError(null);
      
      // Get document keys for extraction
      const documentKeys = documents.map(doc => doc.s3_key);
      
      // Immediately update UI to show processing state
      if (currentSubmission) {
        setCurrentSubmission({
          ...currentSubmission,
          extraction_status: 'processing',
          extraction_progress: 0,
          processed_files: 0,
          total_files: documents.length
        });
      }
      
      // Initialize extraction status for immediate display
      setExtractionStatus({
        submission_id: submissionId,
        status: 'processing',
        extraction_status: 'processing',
        extraction_progress: 0,
        total_files: documents.length,
        processed_files: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      
      // Start extraction
      const response = await apiClient.startExtraction(submissionId, documentKeys);
      
      // Start polling for status immediately
      setTimeout(() => checkExtractionStatus(), 500);
      
    } catch (err) {
      console.error('Failed to start extraction:', err);
      setError('Failed to start extraction. Please try again.');
      // Reset status on error
      if (currentSubmission) {
        setCurrentSubmission({
          ...currentSubmission,
          extraction_status: 'pending'
        });
      }
      setExtractionStatus(null);
    } finally {
      setIsExtracting(false);
    }
  };

  const checkExtractionStatus = async () => {
    if (!submissionId || !token) {
      console.warn('⚠️ checkExtractionStatus: Missing submissionId or token');
      return;
    }
    
    console.log('🔍 checkExtractionStatus: Starting API call for', submissionId);
    
    try {
      setIsLoadingStatus(true);
      const status = await apiClient.getExtractionStatus(submissionId);
      console.log('📊 Extraction Status Update:', {
        status: status.extraction_status,
        progress: status.extraction_progress,
        processedFiles: status.processed_files,
        totalFiles: status.total_files,
        fullResponse: status
      });
      setExtractionStatus(status);
      
      // Update submission in store
      if (currentSubmission) {
        setCurrentSubmission({
          ...currentSubmission,
          extraction_status: status.extraction_status,
          extraction_progress: status.extraction_progress,
          processed_files: status.processed_files,
          total_files: status.total_files
        });
      }
      
      // If completed, load results
      if (status.status === 'completed') {
        console.log('✅ Extraction completed - loading results');
        loadExtractionResults();
      }
      
    } catch (err) {
      console.error('❌ Failed to check extraction status:', err);
      console.error('Error details:', {
        message: err instanceof Error ? err.message : 'Unknown error',
        submissionId,
        hasToken: !!token
      });
    } finally {
      setIsLoadingStatus(false);
    }
  };

  const loadExtractionResults = async () => {
    if (!submissionId || !token) return;
    
    try {
      const results = await apiClient.getExtractionResults(submissionId);
      setExtractedData(results);
      
      // Update submission status
      if (currentSubmission) {
        setCurrentSubmission({
          ...currentSubmission,
          extraction_status: 'completed',
          extracted_data: results.extracted_data,
          acord_data: results.acord_schema
        });
      }
      
    } catch (err) {
      console.error('Failed to load extraction results:', err);
      setError('Failed to load extraction results. Please try again.');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

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

  if (!submissionId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No submission ID provided. Please navigate from the upload page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!currentSubmission && isLoadingData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading submission...</span>
        </div>
      </div>
    );
  }

  if (!currentSubmission && !isLoadingData) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No submission found. Please navigate from the upload page.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => router.push('/upload')}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Upload
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Review & Extract Data</h1>
            <p className="text-gray-600">
              Submission: {currentSubmission.title || `Submission ${submissionId.slice(0, 8)}`}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge className={getStatusColor(currentSubmission.extraction_status)}>
            {getStatusIcon(currentSubmission.extraction_status)}
            <span className="ml-1 capitalize">{currentSubmission.extraction_status}</span>
          </Badge>
        </div>
      </div>

      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              {currentSubmission?.extraction_status === 'failed' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      await apiClient.resetExtractionStatus(currentSubmission.id);
                      setError(null);
                      // Reload submission data
                      await loadSubmissionData();
                    } catch (err: any) {
                      setError('Failed to reset extraction status: ' + (err.message || 'Unknown error'));
                    }
                  }}
                  className="ml-4"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset and Retry
                </Button>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Documents Section */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Uploaded Documents ({documents.length})
          </CardTitle>
          <CardDescription>
            Documents ready for AI extraction and review
          </CardDescription>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                No documents found. Please upload documents first.
              </AlertDescription>
            </Alert>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documents.map((doc) => (
                <div key={doc.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium truncate">{doc.original_filename}</h4>
                    <Badge variant="outline">{doc.file_type}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                    <Badge 
                      variant={doc.processing_status === 'completed' ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {doc.processing_status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Extraction Progress - Only show when processing, completed, or failed */}
      {currentSubmission.extraction_status !== 'pending' && (
        <ExtractionProgress
          status={currentSubmission.extraction_status}
          progress={extractionStatus?.extraction_progress || currentSubmission.extraction_progress || 0}
          processedFiles={extractionStatus?.processed_files || currentSubmission.processed_files || 0}
          totalFiles={extractionStatus?.total_files || currentSubmission.total_files || 0}
          estimatedTime="2-5 minutes"
          onRefresh={checkExtractionStatus}
          onRetry={startExtraction}
        />
      )}

      {/* Start Extraction Button */}
      {currentSubmission.extraction_status === 'pending' && (
        <Card className="mb-6">
          <CardContent className="text-center py-8">
            <p className="text-gray-600 mb-4">
              Ready to extract data from {documents.length} document(s)
            </p>
            <Button 
              onClick={startExtraction}
              disabled={isExtracting || documents.length === 0}
              size="lg"
            >
              {isExtracting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Starting Extraction...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Start AI Extraction
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Results Section */}
      {currentSubmission.extraction_status === 'completed' && extractedData && (
        <div className="space-y-6">
          {/* Action Buttons */}
          <Card>
            <CardContent className="py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="font-medium text-green-700">Extraction Completed</span>
                </div>
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={async () => {
                      if (!user || !submissionId || !extractedData?.acord_schema) return;
                      try {
                        setIsFillingPdf(true);
                        setError(null);
                        setPdfDownloadUrl(null);
                        const sanitized = sanitizeAcordForFill(extractedData.acord_schema);
                        const res = await apiClient.fillAcord125({
                          user_id: user.uid || user.id || 'demo-user',
                          submission_id: submissionId,
                          acord: sanitized,
                        });
                        setPdfDownloadUrl(res.download_url);
                      } catch (e: any) {
                        setError(e?.message || 'Failed to fill ACORD 125 PDF');
                      } finally {
                        setIsFillingPdf(false);
                      }
                    }}
                    disabled={isFillingPdf}
                  >
                    {isFillingPdf ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Filling PDF...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Fill ACORD 125 PDF
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowRawData(!showRawData)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    {showRawData ? 'Hide' : 'Show'} Raw Data
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push('/export')}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export PDF
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {pdfDownloadUrl && (
            <Card>
              <CardHeader>
                <CardTitle>Filled ACORD 125 PDF</CardTitle>
                <CardDescription>Your filled form is ready to download.</CardDescription>
              </CardHeader>
              <CardContent>
                <a
                  href={pdfDownloadUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-blue-600 hover:underline"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Filled ACORD 125
                </a>
              </CardContent>
            </Card>
          )}

          {/* Risk Narrative */}
          {extractedData.risk_narrative && (
            <Card>
              <CardHeader>
                <CardTitle>Risk Narrative</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">{extractedData.risk_narrative}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ACORD Data Display */}
          <ACORDDataDisplay
            extractedData={extractedData.extracted_data}
            acordSchema={extractedData.acord_schema}
            processingStats={extractedData.processing_stats}
            onFieldEdit={(fieldPath, newValue) => {
              console.log('Field edit:', fieldPath, newValue);
              // TODO: Implement field editing
            }}
            onFieldValidate={(fieldPath) => {
              console.log('Field validate:', fieldPath);
              // TODO: Implement field validation
            }}
          />

          {/* General Questions Section */}
          <GeneralQuestionsForm
            submissionId={submissionId!}
            initialQuestions={currentSubmission?.general_questions}
            onSave={(questions) => {
              // Update submission in store
              if (currentSubmission) {
                setCurrentSubmission({
                  ...currentSubmission,
                  general_questions: questions
                });
              }
            }}
          />

          {/* Raw Data Display */}
          {showRawData && (
            <Card>
              <CardHeader>
                <CardTitle>Raw Extracted Data</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-xs">
                  {JSON.stringify(extractedData.extracted_data, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
