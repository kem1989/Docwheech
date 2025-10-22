'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import { useSubmissionStore } from '@/store/submission-store';
import { apiClient } from '@/lib/api';
import FileUpload from '@/components/forms/file-upload';
import SessionRecovery from '@/components/session-recovery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, FileText, CheckCircle, AlertCircle, Trash2, History } from 'lucide-react';

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const {
    currentSubmission,
    documents,
    isUploading,
    uploadProgress,
    setCurrentSubmission,
    setDocuments,
    addDocument,
    removeDocument,
    setUploading,
    setUploadProgress,
    clearUploadProgress
  } = useSubmissionStore();

  const [submissionTitle, setSubmissionTitle] = useState('');
  const [isCreatingSubmission, setIsCreatingSubmission] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showSessionRecovery, setShowSessionRecovery] = useState(false);
  const [hasIncompleteSubmissions, setHasIncompleteSubmissions] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Create new submission
  const createSubmission = async () => {
    if (!submissionTitle.trim()) {
      setError('Please enter a submission title');
      return;
    }

    setIsCreatingSubmission(true);
    setError(null);

    try {
      const submission = await apiClient.createSubmission({
        title: submissionTitle.trim(),
        submission_type: 'acord_125'
      });

      setCurrentSubmission(submission);
      setSuccess('Submission created successfully! You can now upload files.');
    } catch (err: any) {
      setError(err.message || 'Failed to create submission');
    } finally {
      setIsCreatingSubmission(false);
    }
  };

  // Handle file upload
  const handleFileUpload = async (files: File[]) => {
    if (!currentSubmission) {
      setError('Please create a submission first');
      return;
    }

    setUploading(true);
    setError(null);
    clearUploadProgress();

    try {
      // Generate upload URLs
      const fileNames = files.map(file => file.name);
      const uploadResponse = await apiClient.generateUploadUrls(
        currentSubmission.id,
        fileNames
      );

      // Upload files to S3
      const uploadPromises = files.map(async (file, index) => {
        const fileName = file.name;
        const uploadData = uploadResponse.upload_urls[fileName];

        if (!uploadData) {
          throw new Error(`No upload data for file: ${fileName}`);
        }

        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setUploadProgress(fileName, Math.min(90, Math.random() * 100));
        }, 200);

        try {
          // Upload to S3
          await apiClient.uploadToS3(
            uploadData.upload_url,
            uploadData.fields,
            file
          );

          clearInterval(progressInterval);
          setUploadProgress(fileName, 100);

          // Confirm upload with backend
          const confirmResponse = await apiClient.confirmFileUpload(
            currentSubmission.id,
            {
              filename: fileName,
              s3_key: uploadData.s3_key,
              file_size: file.size,
              content_type: uploadData.content_type
            }
          );

          // Add document to store
          const document = {
            id: confirmResponse.document_id,
            submission_id: currentSubmission.id,
            original_filename: fileName,
            file_type: fileName.split('.').pop() || '',
            file_size: file.size,
            mime_type: uploadData.content_type,
            s3_bucket: '',
            s3_key: uploadData.s3_key,
            processing_status: 'uploaded',
            is_valid: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };

          addDocument(document);

        } catch (uploadError) {
          clearInterval(progressInterval);
          throw uploadError;
        }
      });

      await Promise.all(uploadPromises);
      setSuccess(`Successfully uploaded ${files.length} file(s)`);

      // Refresh submission data
      const updatedSubmission = await apiClient.getSubmission(currentSubmission.id);
      setCurrentSubmission(updatedSubmission);

    } catch (err: any) {
      setError(err.message || 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  // Delete file
  const handleDeleteFile = async (documentId: string) => {
    try {
      await apiClient.deleteFile(documentId);
      removeDocument(documentId);
      // Refresh submission header counts and file list to stay in sync with backend
      if (currentSubmission) {
        try {
          const [refreshedSubmission, filesResponse] = await Promise.all([
            apiClient.getSubmission(currentSubmission.id),
            apiClient.getSubmissionFiles(currentSubmission.id)
          ]);
          setCurrentSubmission(refreshedSubmission);
          setDocuments(filesResponse.documents);
        } catch (_) {
          // Ignore refresh errors; UI already reflects local removal
        }
      }
      setSuccess('File deleted successfully');
    } catch (err: any) {
      setError(err.message || 'Failed to delete file');
    }
  };

  // Load existing submission if in URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const submissionId = urlParams.get('submission');
    
    if (submissionId && !currentSubmission) {
      loadSubmission(submissionId);
    } else if (!submissionId && !currentSubmission) {
      // Check for incomplete submissions when no specific submission is loaded
      checkForIncompleteSubmissions();
    }
  }, []);

  const checkForIncompleteSubmissions = async () => {
    try {
      const incompleteSubmissions = await apiClient.getIncompleteSubmissions();
      setHasIncompleteSubmissions(incompleteSubmissions.length > 0);
      
      // Show session recovery modal if there are incomplete submissions
      if (incompleteSubmissions.length > 0) {
        setShowSessionRecovery(true);
      }
    } catch (err: any) {
      console.error('Failed to check incomplete submissions:', err);
    }
  };

  const loadSubmission = async (submissionId: string) => {
    try {
      const [submission, filesResponse] = await Promise.all([
        apiClient.getSubmission(submissionId),
        apiClient.getSubmissionFiles(submissionId)
      ]);

      setCurrentSubmission(submission);
      setDocuments(filesResponse.documents);
    } catch (err: any) {
      setError(err.message || 'Failed to load submission');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      {/* Session Recovery Modal */}
      {showSessionRecovery && (
        <SessionRecovery onClose={() => setShowSessionRecovery(false)} />
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">File Upload</h1>
          <p className="mt-2 text-gray-600">
            Upload your insurance documents for AI processing and ACORD form generation.
          </p>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Create Submission */}
        {!currentSubmission && (
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Create New Submission</CardTitle>
                  <CardDescription>
                    Start a new insurance submission by giving it a title.
                  </CardDescription>
                </div>
                {hasIncompleteSubmissions && (
                  <Button
                    variant="outline"
                    onClick={() => setShowSessionRecovery(true)}
                    className="flex items-center space-x-2"
                  >
                    <History className="w-4 h-4" />
                    <span>Resume Previous</span>
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-4">
                <Input
                  placeholder="Enter submission title (e.g., 'Acme Corp - General Liability')"
                  value={submissionTitle}
                  onChange={(e) => setSubmissionTitle(e.target.value)}
                  className="flex-1"
                />
                <Button
                  onClick={createSubmission}
                  disabled={isCreatingSubmission || !submissionTitle.trim()}
                >
                  {isCreatingSubmission ? 'Creating...' : 'Create Submission'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Current Submission */}
        {currentSubmission && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>{currentSubmission.title || 'Untitled Submission'}</span>
              </CardTitle>
              <CardDescription>
                Status: {currentSubmission.status} • Files: {currentSubmission.total_files}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUpload
                onUploadComplete={handleFileUpload}
                maxFiles={10}
                maxSize={10 * 1024 * 1024}
                disabled={isUploading}
              />
            </CardContent>
          </Card>
        )}

        {/* Uploaded Files */}
        {documents.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Uploaded Files ({documents.length})</CardTitle>
              <CardDescription>
                Files ready for AI processing and data extraction.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="h-8 w-8 text-blue-600" />
                      <div>
                        <p className="font-medium text-gray-900">{doc.original_filename}</p>
                        <p className="text-sm text-gray-500">
                          {doc.file_type.toUpperCase()} • {(doc.file_size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-500 capitalize">
                        {doc.processing_status}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteFile(doc.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Next Steps */}
        {currentSubmission && documents.length > 0 && (
          <div className="mt-8 text-center">
            <Button
              size="lg"
              onClick={() => router.push(`/review?submission=${currentSubmission.id}`)}
              disabled={isUploading}
            >
              Continue to Data Extraction
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
