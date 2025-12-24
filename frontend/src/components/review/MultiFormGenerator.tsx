'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  FileText, 
  Download, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  FileCheck,
  ExternalLink,
  Loader2,
  AlertTriangle,
  ChevronRight,
  Shield,
  Car,
  HardHat,
  Building2,
  Package
} from 'lucide-react';
import { apiClient, ACORDForm, FormGenerationResult, MultiFormResponse, GapAnalysisResponse } from '@/lib/api';
import FormGapDrawer from './FormGapDrawer';

interface MultiFormGeneratorProps {
  submissionId: string;
  userId: string;
  extractedData: any;
  acordSchema: any;
  detectedCoverages?: string[];
  formSpecificExtractions?: string[];
}

interface FormSelectionState {
  [key: string]: boolean;
}

// Map form types to coverage types
const FORM_TO_COVERAGE_MAP: Record<string, string> = {
  'ACORD_125': 'BASE', // Always has data
  'ACORD_126': 'COMMERCIAL_GENERAL_LIABILITY',
  'ACORD_127': 'BUSINESS_AUTO',
  'ACORD_130': 'WORKERS_COMPENSATION',
  'ACORD_140': 'COMMERCIAL_PROPERTY',
};

// Map form types to extracted data keys
const FORM_TO_DATA_KEY_MAP: Record<string, string> = {
  'ACORD_125': 'first_named_insured', // Base form always has data
  'ACORD_126': 'general_liability',
  'ACORD_127': 'commercial_auto',
  'ACORD_130': 'workers_compensation',
  'ACORD_140': 'property',
};

// Map form types to coverage codes (for gap analysis matching)
const FORM_TO_COVERAGE_CODE_MAP: Record<string, string[]> = {
  'ACORD_125': ['UNIVERSAL', 'BASE'], // Base form covers universal requirements
  'ACORD_126': ['COMMERCIAL_GENERAL_LIABILITY', 'GENERAL_LIABILITY', 'GL'],
  'ACORD_127': ['BUSINESS_AUTO', 'COMMERCIAL_AUTO', 'AUTO'],
  'ACORD_130': ['WORKERS_COMPENSATION', 'WORKERS_COMP', 'WC'],
  'ACORD_140': ['COMMERCIAL_PROPERTY', 'PROPERTY'],
};

// Coverage display configuration
const COVERAGE_DISPLAY: Record<string, {
  name: string;
  shortName: string;
  icon: React.ElementType;
  gradient: string;
  bgColor: string;
  textColor: string;
  borderColor: string;
}> = {
  'COMMERCIAL_GENERAL_LIABILITY': {
    name: 'Commercial General Liability',
    shortName: 'General Liability',
    icon: Shield,
    gradient: 'from-emerald-500 to-emerald-600',
    bgColor: 'bg-emerald-50',
    textColor: 'text-emerald-700',
    borderColor: 'border-emerald-200',
  },
  'BUSINESS_AUTO': {
    name: 'Business Auto',
    shortName: 'Commercial Auto',
    icon: Car,
    gradient: 'from-orange-500 to-orange-600',
    bgColor: 'bg-orange-50',
    textColor: 'text-orange-700',
    borderColor: 'border-orange-200',
  },
  'WORKERS_COMPENSATION': {
    name: 'Workers Compensation',
    shortName: 'Workers Comp',
    icon: HardHat,
    gradient: 'from-violet-500 to-violet-600',
    bgColor: 'bg-violet-50',
    textColor: 'text-violet-700',
    borderColor: 'border-violet-200',
  },
  'COMMERCIAL_PROPERTY': {
    name: 'Commercial Property',
    shortName: 'Property',
    icon: Building2,
    gradient: 'from-rose-500 to-rose-600',
    bgColor: 'bg-rose-50',
    textColor: 'text-rose-700',
    borderColor: 'border-rose-200',
  },
};

// Default coverage display for unknown types
const DEFAULT_COVERAGE_DISPLAY = {
  name: 'Coverage',
  shortName: 'Coverage',
  icon: Package,
  gradient: 'from-gray-500 to-gray-600',
  bgColor: 'bg-gray-50',
  textColor: 'text-gray-700',
  borderColor: 'border-gray-200',
};

// Form display configuration (maps form types to their visual styling)
const FORM_DISPLAY: Record<string, {
  icon: React.ElementType;
  gradient: string;
  bgColor: string;
  selectedBg: string;
  textColor: string;
  borderColor: string;
  selectedBorder: string;
}> = {
  'ACORD_125': {
    icon: FileText,
    gradient: 'from-slate-600 to-slate-700',
    bgColor: 'bg-white',
    selectedBg: 'bg-slate-50',
    textColor: 'text-slate-700',
    borderColor: 'border-gray-200',
    selectedBorder: 'border-slate-500',
  },
  'ACORD_126': {
    icon: Shield,
    gradient: 'from-emerald-500 to-emerald-600',
    bgColor: 'bg-white',
    selectedBg: 'bg-emerald-50',
    textColor: 'text-emerald-700',
    borderColor: 'border-gray-200',
    selectedBorder: 'border-emerald-500',
  },
  'ACORD_127': {
    icon: Car,
    gradient: 'from-orange-500 to-orange-600',
    bgColor: 'bg-white',
    selectedBg: 'bg-orange-50',
    textColor: 'text-orange-700',
    borderColor: 'border-gray-200',
    selectedBorder: 'border-orange-500',
  },
  'ACORD_130': {
    icon: HardHat,
    gradient: 'from-violet-500 to-violet-600',
    bgColor: 'bg-white',
    selectedBg: 'bg-violet-50',
    textColor: 'text-violet-700',
    borderColor: 'border-gray-200',
    selectedBorder: 'border-violet-500',
  },
  'ACORD_140': {
    icon: Building2,
    gradient: 'from-rose-500 to-rose-600',
    bgColor: 'bg-white',
    selectedBg: 'bg-rose-50',
    textColor: 'text-rose-700',
    borderColor: 'border-gray-200',
    selectedBorder: 'border-rose-500',
  },
};

// Default form display
const DEFAULT_FORM_DISPLAY = {
  icon: FileText,
  gradient: 'from-gray-500 to-gray-600',
  bgColor: 'bg-white',
  selectedBg: 'bg-gray-50',
  textColor: 'text-gray-700',
  borderColor: 'border-gray-200',
  selectedBorder: 'border-gray-500',
};

export default function MultiFormGenerator({
  submissionId,
  userId,
  extractedData,
  acordSchema,
  detectedCoverages = [],
  formSpecificExtractions = []
}: MultiFormGeneratorProps) {
  const [availableForms, setAvailableForms] = useState<ACORDForm[]>([]);
  const [selectedForms, setSelectedForms] = useState<FormSelectionState>({});
  const [generatedForms, setGeneratedForms] = useState<FormGenerationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  
  // Gap analysis state
  const [gapData, setGapData] = useState<GapAnalysisResponse | null>(null);
  const [isLoadingGaps, setIsLoadingGaps] = useState(false);
  
  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedFormForGaps, setSelectedFormForGaps] = useState<{ type: string; name: string } | null>(null);

  // Load available forms and gap analysis on mount
  useEffect(() => {
    loadAvailableForms();
    loadGapAnalysis();
  }, [submissionId]);

  // Load gap analysis data
  const loadGapAnalysis = useCallback(async () => {
    try {
      setIsLoadingGaps(true);
      const result = await apiClient.getGapAnalysis(submissionId);
      if (result) {
        setGapData(result);
      } else {
        // If no stored results, run analysis
        const freshResult = await apiClient.analyzeGaps(submissionId, true);
        setGapData(freshResult);
      }
    } catch (err) {
      console.error('Failed to load gap analysis:', err);
      // Non-blocking error - we just won't show gap info
    } finally {
      setIsLoadingGaps(false);
    }
  }, [submissionId]);

  // Get missing fields for a specific form based on coverage type
  const getMissingFieldsForForm = (formType: string) => {
    if (!gapData?.missing_data) return [];
    
    const coverageCodes = FORM_TO_COVERAGE_CODE_MAP[formType] || [];
    
    return gapData.missing_data.filter(item => {
      const itemCoverage = item.for_coverage?.toUpperCase() || '';
      return coverageCodes.some(code => 
        itemCoverage === code || itemCoverage.includes(code)
      );
    });
  };

  // Get missing count for a specific form
  const getMissingCountForForm = (formType: string): number => {
    return getMissingFieldsForForm(formType).length;
  };

  // Check if form has critical gaps
  const hasCriticalGaps = (formType: string): boolean => {
    const missingFields = getMissingFieldsForForm(formType);
    return missingFields.some(f => f.severity === 'critical');
  };

  // Open drawer for a specific form
  const openGapDrawer = (formType: string, displayName: string) => {
    setSelectedFormForGaps({ type: formType, name: displayName });
    setDrawerOpen(true);
  };

  // Check if a form has extracted data available
  const hasDataForForm = (formType: string): boolean => {
    // ACORD 125 always has data (base form)
    if (formType === 'ACORD_125') return true;
    
    // Check if form was in the form_specific_extractions list
    if (formSpecificExtractions.includes(formType)) return true;
    
    // Check if the data key exists in extractedData
    const dataKey = FORM_TO_DATA_KEY_MAP[formType];
    if (dataKey && extractedData && extractedData[dataKey]) {
      return true;
    }
    
    // Check if the coverage was detected
    const coverage = FORM_TO_COVERAGE_MAP[formType];
    if (coverage && detectedCoverages.includes(coverage)) return true;
    
    return false;
  };

  const loadAvailableForms = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.getAvailableForms();
      setAvailableForms(response.forms);
      
      // Auto-select forms that have extracted data
      const defaultSelection: FormSelectionState = {};
      response.forms.forEach(form => {
        if (form.template_exists) {
          // Select form if it has data extracted
          defaultSelection[form.form_type] = hasDataForForm(form.form_type);
        }
      });
      setSelectedForms(defaultSelection);
    } catch (err) {
      console.error('Failed to load available forms:', err);
      setError('Failed to load available forms');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleFormSelection = (formType: string) => {
    setSelectedForms(prev => ({
      ...prev,
      [formType]: !prev[formType]
    }));
  };

  const selectAllForms = () => {
    const newSelection: FormSelectionState = {};
    availableForms.forEach(form => {
      if (form.template_exists) {
        newSelection[form.form_type] = true;
      }
    });
    setSelectedForms(newSelection);
  };

  const selectFormsWithData = () => {
    const newSelection: FormSelectionState = {};
    availableForms.forEach(form => {
      if (form.template_exists && hasDataForForm(form.form_type)) {
        newSelection[form.form_type] = true;
      }
    });
    setSelectedForms(newSelection);
  };

  const deselectAllForms = () => {
    setSelectedForms({});
  };

  const getSelectedFormTypes = (): string[] => {
    return Object.entries(selectedForms)
      .filter(([_, selected]) => selected)
      .map(([formType]) => formType);
  };

  const generateForms = async () => {
    const formTypes = getSelectedFormTypes();
    if (formTypes.length === 0) {
      setError('Please select at least one form to generate');
      return;
    }

    try {
      setIsGenerating(true);
      setError(null);
      setGeneratedForms([]);
      setProgress(10);

      const response = await apiClient.generateFormsFromExtraction({
        user_id: userId,
        submission_id: submissionId,
        form_types: formTypes,
        extracted_data: extractedData,
        acord_schema: acordSchema
      });

      setProgress(100);
      setGeneratedForms(response.results);

      if (response.failed && response.failed > 0) {
        setError(`${response.failed} form(s) failed to generate`);
      }
    } catch (err) {
      console.error('Failed to generate forms:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate forms');
    } finally {
      setIsGenerating(false);
    }
  };

  const getFormDescription = (formType: string): string => {
    const descriptions: Record<string, string> = {
      'ACORD_125': 'Commercial Insurance Application - Main application form with business information',
      'ACORD_126': 'GL Section - Detailed General Liability coverage information',
      'ACORD_130': 'Workers Comp Application - Payroll, classifications, and experience mod',
      'ACORD_140': 'Property Section - Building and coverage details'
    };
    return descriptions[formType] || 'ACORD form';
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2">Loading available forms...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center">
                <FileCheck className="h-5 w-5 mr-2" />
                Generate ACORD Forms
              </CardTitle>
              <CardDescription>
                Select and generate multiple ACORD forms from extracted data
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={selectFormsWithData}>
                Select With Data
              </Button>
              <Button variant="outline" size="sm" onClick={selectAllForms}>
                Select All
              </Button>
              <Button variant="outline" size="sm" onClick={deselectAllForms}>
                Clear
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {error && (
            <Alert className="border-red-200 bg-red-50">
              <AlertCircle className="h-4 w-4 text-red-600" />
              <AlertDescription className="text-red-800">{error}</AlertDescription>
            </Alert>
          )}

          {/* Detected Coverages - Use prop or fallback to gap data */}
          {(() => {
            // Get coverages from prop or from gap analysis data
            const coverageList = detectedCoverages && detectedCoverages.length > 0
              ? detectedCoverages
              : gapData?.detected_coverages?.map(c => c.code) || [];
            
            if (coverageList.length === 0) return null;
            
            return (
              <div className="bg-gradient-to-r from-slate-50 to-slate-100/50 rounded-xl p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-3">
                  <Package className="h-4 w-4 text-slate-500" />
                  <span className="text-sm font-medium text-slate-600">Detected Coverages</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {coverageList.map((coverage) => {
                    const displayConfig = COVERAGE_DISPLAY[coverage] || {
                      ...DEFAULT_COVERAGE_DISPLAY,
                      name: coverage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                      shortName: coverage.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    };
                    const IconComponent = displayConfig.icon;
                    
                    return (
                      <div
                        key={coverage}
                        className={`
                          flex items-center gap-2 px-3 py-2 rounded-lg border
                          ${displayConfig.bgColor} ${displayConfig.borderColor}
                          transition-all hover:shadow-sm
                        `}
                      >
                        <div className={`w-7 h-7 rounded-md bg-gradient-to-br ${displayConfig.gradient} flex items-center justify-center`}>
                          <IconComponent className="h-4 w-4 text-white" />
                        </div>
                        <span className={`text-sm font-medium ${displayConfig.textColor}`}>
                          {displayConfig.shortName}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}

          {/* Form Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableForms.map((form) => {
              const missingCount = getMissingCountForForm(form.form_type);
              const hasCritical = hasCriticalGaps(form.form_type);
              const formDisplay = FORM_DISPLAY[form.form_type] || DEFAULT_FORM_DISPLAY;
              const FormIcon = formDisplay.icon;
              const isSelected = selectedForms[form.form_type];
              
              return (
                <div
                  key={form.form_type}
                  className={`
                    border rounded-xl p-4 transition-all duration-200
                    ${form.template_exists 
                      ? isSelected
                        ? `${formDisplay.selectedBorder} ${formDisplay.selectedBg} shadow-sm`
                        : `${formDisplay.borderColor} ${formDisplay.bgColor} hover:shadow-md hover:border-gray-300`
                      : 'border-gray-200 bg-gray-50 opacity-60'
                    }
                  `}
                >
                  {/* Clickable header for selection */}
                  <div 
                    className={`${form.template_exists ? 'cursor-pointer' : 'cursor-not-allowed'}`}
                    onClick={() => form.template_exists && toggleFormSelection(form.form_type)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        {/* Colored icon with gradient */}
                        <div className={`
                          w-10 h-10 rounded-lg flex items-center justify-center shadow-sm
                          bg-gradient-to-br ${formDisplay.gradient}
                        `}>
                          <FormIcon className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <h4 className={`font-semibold ${isSelected ? formDisplay.textColor : 'text-gray-900'}`}>
                            {form.display_name}
                          </h4>
                          <p className="text-sm text-gray-500 mt-0.5">
                            {getFormDescription(form.form_type)}
                          </p>
                          <div className="flex gap-2 mt-2 flex-wrap">
                            <Badge 
                              variant="outline" 
                              className={`text-xs ${
                                isSelected 
                                  ? `${formDisplay.textColor} border-current bg-white/50` 
                                  : 'bg-gray-100 text-gray-600 border-gray-200'
                              }`}
                            >
                              {form.form_type.replace('_', ' ')}
                            </Badge>
                            {hasDataForForm(form.form_type) ? (
                              <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Data Available
                              </Badge>
                            ) : (
                              <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 text-xs">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                No Data
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      {form.template_exists && (
                        <div className={`
                          w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all
                          ${isSelected 
                            ? `${formDisplay.selectedBorder} bg-gradient-to-br ${formDisplay.gradient}` 
                            : 'border-gray-300 bg-white'
                          }
                        `}>
                          {isSelected && (
                            <CheckCircle className="h-4 w-4 text-white" />
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Missing Fields Link - Separate clickable area */}
                  {form.template_exists && (
                    <div className="mt-3 pt-3 border-t border-gray-200/70">
                      {isLoadingGaps ? (
                        <div className="flex items-center text-xs text-gray-400">
                          <Loader2 className="h-3 w-3 mr-1.5 animate-spin" />
                          Checking completeness...
                        </div>
                      ) : missingCount > 0 ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            openGapDrawer(form.form_type, form.display_name);
                          }}
                          className={`
                            flex items-center justify-between w-full text-left group
                            py-1.5 px-2 -mx-2 rounded-md transition-colors
                            ${hasCritical 
                              ? 'hover:bg-red-50 text-red-600' 
                              : 'hover:bg-amber-50 text-amber-600'
                            }
                          `}
                        >
                          <div className="flex items-center gap-1.5">
                            {hasCritical ? (
                              <AlertCircle className="h-3.5 w-3.5" />
                            ) : (
                              <AlertTriangle className="h-3.5 w-3.5" />
                            )}
                            <span className="text-sm font-medium">
                              {missingCount} Missing Field{missingCount !== 1 ? 's' : ''}
                            </span>
                            {hasCritical && (
                              <Badge className="text-[9px] px-1.5 py-0 h-4 bg-red-100 text-red-700 border-red-200 ml-1">
                                Critical
                              </Badge>
                            )}
                          </div>
                          <ChevronRight className="h-4 w-4 opacity-50 group-hover:opacity-100 transition-opacity" />
                        </button>
                      ) : (
                        <div className="flex items-center text-xs text-emerald-600">
                          <CheckCircle className="h-3.5 w-3.5 mr-1.5" />
                          All required fields complete
                        </div>
                      )}
                    </div>
                  )}
                  
                  {!form.template_exists && (
                    <p className="text-xs text-amber-600 mt-2">
                      Template not available
                    </p>
                  )}
                  {form.template_exists && !hasDataForForm(form.form_type) && selectedForms[form.form_type] && (
                    <p className="text-xs text-amber-600 mt-2">
                      ⚠️ No form-specific data extracted. The form will be partially filled with base data only.
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          {/* Generate Button */}
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-gray-600">
              {getSelectedFormTypes().length} form(s) selected
            </div>
            <Button 
              onClick={generateForms}
              disabled={isGenerating || getSelectedFormTypes().length === 0}
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Generate Selected Forms
                </>
              )}
            </Button>
          </div>

          {/* Progress */}
          {isGenerating && (
            <div className="space-y-2">
              <Progress value={progress} className="h-2" />
              <p className="text-sm text-gray-600 text-center">
                Generating {getSelectedFormTypes().length} form(s)...
              </p>
            </div>
          )}

          {/* Generated Forms */}
          {generatedForms.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-medium flex items-center">
                <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                Generated Forms
              </h4>
              <div className="grid grid-cols-1 gap-3">
                {generatedForms.map((result, index) => (
                  <div
                    key={index}
                    className={`
                      border rounded-lg p-4 flex items-center justify-between
                      ${result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}
                    `}
                  >
                    <div className="flex items-center space-x-3">
                      {result.success ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      )}
                      <div>
                        <p className="font-medium">{result.display_name}</p>
                        <p className="text-sm text-gray-600">{result.form_type}</p>
                        {result.error && (
                          <p className="text-sm text-red-600 mt-1">{result.error}</p>
                        )}
                      </div>
                    </div>
                    {result.success && result.download_url && (
                      <a
                        href={result.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center text-blue-600 hover:text-blue-800"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                        <ExternalLink className="h-3 w-3 ml-1" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gap Detection Drawer */}
      {selectedFormForGaps && (
        <FormGapDrawer
          isOpen={drawerOpen}
          onClose={() => {
            setDrawerOpen(false);
            setSelectedFormForGaps(null);
          }}
          formType={selectedFormForGaps.type}
          formDisplayName={selectedFormForGaps.name}
          gapData={gapData}
        />
      )}
    </>
  );
}
