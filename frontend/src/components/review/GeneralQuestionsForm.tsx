'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CheckCircle, XCircle, Save, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { GeneralQuestion } from '@/store/submission-store';

interface DetailFieldDefinition {
  id: string;
  label: string;
  placeholder?: string;
  type?: 'text' | 'number';
}

interface GeneralQuestionDefinition {
  id: string;
  label: string;
  details_label?: string;
  detail_fields?: DetailFieldDefinition[];
}

interface GeneralQuestionsFormProps {
  submissionId: string;
  initialQuestions?: GeneralQuestion[];
  onSave?: (questions: GeneralQuestion[]) => void;
}

export default function GeneralQuestionsForm({
  submissionId,
  initialQuestions,
  onSave,
}: GeneralQuestionsFormProps) {
  const [questionDefinitions, setQuestionDefinitions] = useState<GeneralQuestionDefinition[]>([]);
  const [questions, setQuestions] = useState<GeneralQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const buildQuestionFromDefinition = (
    definition: GeneralQuestionDefinition,
    existing?: GeneralQuestion
  ): GeneralQuestion => {
    const hasStructuredDetails = Array.isArray(definition.detail_fields) && definition.detail_fields.length > 0;
    let normalizedDetails: string | Record<string, any> | null = null;

    if (hasStructuredDetails) {
      const sourceDetails =
        existing && typeof existing.details === 'object' && existing.details !== null
          ? existing.details
          : {};
      const structuredDetails: Record<string, any> = {};
      definition.detail_fields?.forEach((field) => {
        structuredDetails[field.id] = sourceDetails[field.id] ?? '';
      });
      normalizedDetails = structuredDetails;
    } else {
      if (typeof existing?.details === 'string') {
        normalizedDetails = existing.details;
      } else if (existing?.details === null || existing?.details === undefined) {
        normalizedDetails = '';
      } else if (typeof existing?.details === 'object' && existing.details !== null) {
        // Legacy data stored as object—flatten to JSON string to preserve information
        normalizedDetails = JSON.stringify(existing.details);
      } else {
        normalizedDetails = '';
      }
    }

    return {
      id: definition.id,
      answer: existing?.answer ?? null,
      details: normalizedDetails,
    };
  };

  // Load question definitions and initialize questions
  useEffect(() => {
    const loadQuestions = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Load question definitions
        const definitions = await apiClient.getGeneralQuestions();
        setQuestionDefinitions(definitions.questions);
        
        const existingMap = new Map((initialQuestions || []).map(q => [q.id, q]));
        const defaultMap = new Map(definitions.default_responses.map((q: GeneralQuestion) => [q.id, q]));

        const merged = definitions.questions.map((def: GeneralQuestionDefinition) => {
          const existing = existingMap.get(def.id) || defaultMap.get(def.id);
          return buildQuestionFromDefinition(def, existing);
        });

        setQuestions(merged);
      } catch (err) {
        console.error('Failed to load general questions:', err);
        setError('Failed to load general questions. Please refresh the page.');
      } finally {
        setIsLoading(false);
      }
    };

    loadQuestions();
  }, [submissionId, initialQuestions]);

  const updateQuestion = (id: string, field: 'answer' | 'details', value: boolean | string | Record<string, any> | null) => {
    setQuestions(prev => {
      const updated = prev.map(q => 
        q.id === id ? { ...q, [field]: value } : q
      );
      setHasChanges(true);
      setSuccess(false);
      return updated;
    });
  };

  const updateQuestionDetailField = (questionId: string, detailId: string, value: string) => {
    setQuestions(prev => {
      const updated = prev.map(q => {
        if (q.id !== questionId) return q;
        const existingDetails = typeof q.details === 'object' && q.details !== null ? q.details : {};
        return {
          ...q,
          details: {
            ...existingDetails,
            [detailId]: value,
          },
        };
      });
      setHasChanges(true);
      setSuccess(false);
      return updated;
    });
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      setSuccess(false);

      await apiClient.updateSubmission(submissionId, {
        general_questions: questions,
      });

      setSuccess(true);
      setHasChanges(false);
      
      if (onSave) {
        onSave(questions);
      }

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to save general questions:', err);
      setError(err instanceof Error ? err.message : 'Failed to save general questions. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const getQuestionDefinition = (id: string): GeneralQuestionDefinition | undefined => {
    return questionDefinitions.find(def => def.id === id);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <p className="text-gray-600">Loading general questions...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>General Questions</CardTitle>
        <CardDescription>
          Answer the following general questions for this ACORD 125 submission.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {error && (
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              General questions saved successfully!
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {questions.map((question) => {
            const definition = getQuestionDefinition(question.id);
            if (!definition) return null;
            const detailFields = definition.detail_fields || [];
            const hasStructuredDetails = detailFields.length > 0;
            const structuredDetails =
              hasStructuredDetails && typeof question.details === 'object' && question.details !== null
                ? question.details
                : {};
            const simpleDetails =
              !hasStructuredDetails && typeof question.details === 'string' ? question.details : '';

            return (
              <div key={question.id} className="border rounded-lg p-4 space-y-3 bg-gray-800">
                <div className="flex items-start justify-between">
                  <label className="text-sm font-medium text-white">
                    {definition.label}
                  </label>
                  <div className="flex items-center space-x-2">
                    {question.answer === true && (
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Yes
                      </Badge>
                    )}
                    {question.answer === false && (
                      <Badge variant="default" className="bg-red-100 text-red-800">
                        <XCircle className="h-3 w-3 mr-1" />
                        No
                      </Badge>
                    )}
                    {question.answer === null && (
                      <Badge variant="outline" className="text-gray-500">
                        Not Answered
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <Button
                    type="button"
                    variant={question.answer === true ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateQuestion(question.id, 'answer', true)}
                    className={question.answer === true ? 'bg-green-600 hover:bg-green-700' : ''}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Yes
                  </Button>
                  <Button
                    type="button"
                    variant={question.answer === false ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateQuestion(question.id, 'answer', false)}
                    className={question.answer === false ? 'bg-red-600 hover:bg-red-700' : ''}
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    No
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => updateQuestion(question.id, 'answer', null)}
                  >
                    Clear
                  </Button>
                </div>

                {question.answer === true && hasStructuredDetails && (
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    {detailFields.map((field) => (
                      <div key={field.id} className="space-y-2">
                        <label className="text-xs font-medium text-white">
                          {field.label}
                        </label>
                        <Input
                          type={field.type || 'text'}
                          value={structuredDetails[field.id] ?? ''}
                          placeholder={field.placeholder}
                          onChange={(e) => updateQuestionDetailField(question.id, field.id, e.target.value)}
                          className="bg-white text-gray-900"
                        />
                      </div>
                    ))}
                  </div>
                )}

                {question.answer === true && !hasStructuredDetails && definition.details_label && (
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-white">
                      {definition.details_label}
                    </label>
                    <Textarea
                      value={simpleDetails || ''}
                      onChange={(e) => updateQuestion(question.id, 'details', e.target.value || null)}
                      placeholder="Enter details..."
                      className="min-h-[80px]"
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-gray-600">
            {questions.filter(q => q.answer !== null).length} of {questions.length} questions answered
          </div>
          <Button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            size="sm"
          >
            {isSaving ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Answers
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

