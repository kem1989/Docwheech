'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSubmissionStore } from '@/store/submission-store';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, Clock, AlertCircle, X, RefreshCw } from 'lucide-react';

interface SessionRecoveryProps {
  onClose: () => void;
}

export default function SessionRecovery({ onClose }: SessionRecoveryProps) {
  const router = useRouter();
  const { setCurrentSubmission, setDocuments } = useSubmissionStore();
  const [incompleteSubmissions, setIncompleteSubmissions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadIncompleteSubmissions();
  }, []);

  const loadIncompleteSubmissions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const submissions = await apiClient.getIncompleteSubmissions();
      setIncompleteSubmissions(submissions);
    } catch (err: any) {
      setError(err.message || 'Failed to load incomplete submissions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResumeSubmission = async (submissionId: string) => {
    try {
      // Load submission details and files
      const [submission, filesResponse] = await Promise.all([
        apiClient.getSubmission(submissionId),
        apiClient.getSubmissionFiles(submissionId)
      ]);

      setCurrentSubmission(submission);
      setDocuments(filesResponse.documents);

      // Navigate to upload page with the submission
      router.push(`/upload?submission=${submissionId}`);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to resume submission');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processing':
        return <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />;
      case 'draft':
        return <Clock className="w-4 h-4 text-gray-500" />;
      default:
        return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'processing':
        return 'In Progress';
      case 'draft':
        return 'Draft';
      default:
        return 'Unknown';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="p-6">
            <div className="flex items-center justify-center space-x-2">
              <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
              <span>Loading incomplete submissions...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (incompleteSubmissions.length === 0) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>No Incomplete Submissions</CardTitle>
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="w-4 h-4" />
              </Button>
            </div>
            <CardDescription>
              You don't have any incomplete submissions to resume.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={onClose} className="w-full">
              Start New Submission
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Resume Previous Work</CardTitle>
              <CardDescription>
                You have {incompleteSubmissions.length} incomplete submission{incompleteSubmissions.length !== 1 ? 's' : ''} that you can resume.
              </CardDescription>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="overflow-y-auto">
          {error && (
            <Alert className="mb-4 border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-3">
            {incompleteSubmissions.map((submission) => (
              <div
                key={submission.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <FileText className="w-8 h-8 text-blue-600" />
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {submission.title || 'Untitled Submission'}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{submission.total_files} files</span>
                      <span>•</span>
                      <span>{formatDate(submission.updated_at)}</span>
                      <span>•</span>
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(submission.status)}
                        <span>{getStatusText(submission.status)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {submission.extraction_progress > 0 && (
                    <div className="w-20 bg-gray-200 rounded-full h-2 mr-3">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${submission.extraction_progress}%` }}
                      />
                    </div>
                  )}
                  <Button
                    onClick={() => handleResumeSubmission(submission.id)}
                    size="sm"
                  >
                    Resume
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex space-x-3">
            <Button
              variant="outline"
              onClick={loadIncompleteSubmissions}
              className="flex-1"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
            <Button onClick={onClose} className="flex-1">
              Start New Submission
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}



