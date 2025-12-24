'use client';

import { useMemo } from 'react';
import { 
  Sheet, 
  SheetContent, 
  SheetHeader, 
  SheetTitle, 
  SheetDescription 
} from '@/components/ui/sheet';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  CheckCircle,
  FileText,
  Shield,
  Car,
  HardHat,
  Building2,
  Lightbulb,
  Sparkles
} from 'lucide-react';
import { MissingSectionItem, GapAnalysisResponse } from '@/lib/api';

// Map form types to coverage codes (for gap analysis matching)
const FORM_TO_COVERAGE_CODE_MAP: Record<string, string[]> = {
  'ACORD_125': ['UNIVERSAL', 'BASE'], // Base form covers universal requirements
  'ACORD_126': ['COMMERCIAL_GENERAL_LIABILITY', 'GENERAL_LIABILITY', 'GL'],
  'ACORD_127': ['BUSINESS_AUTO', 'COMMERCIAL_AUTO', 'AUTO'],
  'ACORD_130': ['WORKERS_COMPENSATION', 'WORKERS_COMP', 'WC'],
  'ACORD_140': ['COMMERCIAL_PROPERTY', 'PROPERTY'],
};

// Form themes for consistent styling
const FORM_THEMES: Record<string, {
  icon: React.ElementType;
  gradient: string;
  headerBg: string;
  accentColor: string;
  lightBg: string;
  border: string;
}> = {
  'ACORD_125': {
    icon: FileText,
    gradient: 'from-slate-600 to-slate-700',
    headerBg: 'bg-gradient-to-r from-slate-600 to-slate-700',
    accentColor: 'text-slate-600',
    lightBg: 'bg-slate-50',
    border: 'border-slate-200',
  },
  'ACORD_126': {
    icon: Shield,
    gradient: 'from-emerald-500 to-emerald-600',
    headerBg: 'bg-gradient-to-r from-emerald-500 to-emerald-600',
    accentColor: 'text-emerald-600',
    lightBg: 'bg-emerald-50',
    border: 'border-emerald-200',
  },
  'ACORD_127': {
    icon: Car,
    gradient: 'from-orange-500 to-orange-600',
    headerBg: 'bg-gradient-to-r from-orange-500 to-orange-600',
    accentColor: 'text-orange-600',
    lightBg: 'bg-orange-50',
    border: 'border-orange-200',
  },
  'ACORD_130': {
    icon: HardHat,
    gradient: 'from-violet-500 to-violet-600',
    headerBg: 'bg-gradient-to-r from-violet-500 to-violet-600',
    accentColor: 'text-violet-600',
    lightBg: 'bg-violet-50',
    border: 'border-violet-200',
  },
  'ACORD_140': {
    icon: Building2,
    gradient: 'from-rose-500 to-rose-600',
    headerBg: 'bg-gradient-to-r from-rose-500 to-rose-600',
    accentColor: 'text-rose-600',
    lightBg: 'bg-rose-50',
    border: 'border-rose-200',
  },
};

const DEFAULT_THEME = {
  icon: FileText,
  gradient: 'from-gray-500 to-gray-600',
  headerBg: 'bg-gradient-to-r from-gray-500 to-gray-600',
  accentColor: 'text-gray-600',
  lightBg: 'bg-gray-50',
  border: 'border-gray-200',
};

interface FormGapDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  formType: string;
  formDisplayName: string;
  gapData: GapAnalysisResponse | null;
}

export default function FormGapDrawer({
  isOpen,
  onClose,
  formType,
  formDisplayName,
  gapData,
}: FormGapDrawerProps) {
  const theme = FORM_THEMES[formType] || DEFAULT_THEME;
  const IconComponent = theme.icon;
  const coverageCodes = FORM_TO_COVERAGE_CODE_MAP[formType] || [];

  // Get form-specific missing data by filtering on for_coverage
  const formMissingFields = useMemo(() => {
    if (!gapData?.missing_data) return [];
    
    return gapData.missing_data.filter(item => {
      const itemCoverage = item.for_coverage?.toUpperCase() || '';
      return coverageCodes.some(code => 
        itemCoverage === code || itemCoverage.includes(code)
      );
    });
  }, [gapData, coverageCodes]);

  // Create a structure similar to MissingSectionItem for display
  const formGaps = useMemo(() => {
    if (formMissingFields.length === 0) return null;
    
    return {
      section: formType,
      section_display: formDisplayName,
      missing_count: formMissingFields.length,
      has_critical: formMissingFields.some(f => f.severity === 'critical'),
      fields: formMissingFields,
    };
  }, [formMissingFields, formType, formDisplayName]);

  // Get form-specific AI insights
  const formInsights = useMemo(() => {
    if (!gapData?.ai_insights) return [];
    
    // Get coverage display names for matching
    const coverageKeywords = coverageCodes.map(c => c.toLowerCase().replace(/_/g, ' '));
    
    // Filter insights relevant to this form's coverage
    return gapData.ai_insights.filter(insight => {
      const message = insight.message.toLowerCase();
      return coverageKeywords.some(keyword => message.includes(keyword)) || 
             message.includes(formType.toLowerCase().replace('_', ' '));
    }).slice(0, 3); // Max 3 insights
  }, [gapData, coverageCodes, formType]);

  // Calculate form-specific completeness
  const formCompleteness = useMemo(() => {
    if (formMissingFields.length === 0) return 100;
    
    // Estimate: assume each form has roughly 15-25 required fields
    const estimatedTotal = Math.max(20, formMissingFields.length + 15);
    const found = estimatedTotal - formMissingFields.length;
    return Math.round((found / estimatedTotal) * 100);
  }, [formMissingFields]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />;
      case 'important':
        return <AlertTriangle className="h-4 w-4 text-amber-500 flex-shrink-0" />;
      default:
        return <Info className="h-4 w-4 text-blue-500 flex-shrink-0" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return (
          <Badge className="text-[10px] px-2 py-0.5 bg-red-100 text-red-700 border-red-200 uppercase tracking-wide font-semibold">
            Critical
          </Badge>
        );
      case 'important':
        return (
          <Badge className="text-[10px] px-2 py-0.5 bg-amber-100 text-amber-700 border-amber-200 uppercase tracking-wide font-semibold">
            Important
          </Badge>
        );
      default:
        return (
          <Badge className="text-[10px] px-2 py-0.5 bg-blue-100 text-blue-700 border-blue-200 uppercase tracking-wide font-semibold">
            Optional
          </Badge>
        );
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const criticalCount = formMissingFields.filter(f => f.severity === 'critical').length;
  const importantCount = formMissingFields.filter(f => f.severity === 'important').length;
  const optionalCount = formMissingFields.filter(f => f.severity === 'recommended').length;

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-md overflow-y-auto">
        {/* Colored Header */}
        <div className={`${theme.headerBg} -mx-0 -mt-0 px-6 py-5 text-white`}>
          <SheetHeader className="space-y-1">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center backdrop-blur-sm">
                <IconComponent className="h-5 w-5" />
              </div>
              <div>
                <SheetTitle className="text-white text-lg">{formDisplayName}</SheetTitle>
                <SheetDescription className="text-white/80 text-sm">
                  Missing Fields Analysis
                </SheetDescription>
              </div>
            </div>
          </SheetHeader>
        </div>

        {/* Content */}
        <div className="px-6 py-5 space-y-6">
          {/* Completeness Score */}
          <div className={`${theme.lightBg} rounded-xl p-4 ${theme.border} border`}>
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-gray-600">Form Completeness</span>
              <span className={`text-2xl font-bold ${getScoreColor(formCompleteness)}`}>
                {formCompleteness}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${getProgressColor(formCompleteness)}`}
                style={{ width: `${formCompleteness}%` }}
              />
            </div>
            
            {/* Stats */}
            {formGaps && (
              <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-200/50">
                {criticalCount > 0 && (
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                    <span className="text-xs text-gray-600">
                      <span className="font-semibold text-red-600">{criticalCount}</span> Critical
                    </span>
                  </div>
                )}
                {importantCount > 0 && (
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-amber-500" />
                    <span className="text-xs text-gray-600">
                      <span className="font-semibold text-amber-600">{importantCount}</span> Important
                    </span>
                  </div>
                )}
                {optionalCount > 0 && (
                  <div className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    <span className="text-xs text-gray-600">
                      <span className="font-semibold text-blue-600">{optionalCount}</span> Optional
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Missing Fields List */}
          {formGaps && formGaps.fields.length > 0 ? (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                Missing Fields ({formGaps.missing_count})
              </h3>
              
              {/* Critical Fields */}
              {criticalCount > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-red-600">
                    <AlertCircle className="h-3.5 w-3.5" />
                    Critical Fields
                  </div>
                  {formGaps.fields
                    .filter(f => f.severity === 'critical')
                    .map((field, idx) => (
                      <div 
                        key={`critical-${idx}`}
                        className="flex items-center justify-between p-3 rounded-lg bg-red-50 border border-red-100 hover:bg-red-100/50 transition-colors"
                      >
                        <div className="flex items-center gap-2.5">
                          {getSeverityIcon(field.severity)}
                          <span className="font-medium text-sm text-gray-800">{field.label}</span>
                        </div>
                        {getSeverityBadge(field.severity)}
                      </div>
                    ))}
                </div>
              )}

              {/* Important Fields */}
              {importantCount > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-amber-600">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    Important Fields
                  </div>
                  {formGaps.fields
                    .filter(f => f.severity === 'important')
                    .map((field, idx) => (
                      <div 
                        key={`important-${idx}`}
                        className="flex items-center justify-between p-3 rounded-lg bg-amber-50 border border-amber-100 hover:bg-amber-100/50 transition-colors"
                      >
                        <div className="flex items-center gap-2.5">
                          {getSeverityIcon(field.severity)}
                          <span className="font-medium text-sm text-gray-800">{field.label}</span>
                        </div>
                        {getSeverityBadge(field.severity)}
                      </div>
                    ))}
                </div>
              )}

              {/* Optional/Recommended Fields */}
              {optionalCount > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-medium text-blue-600">
                    <Info className="h-3.5 w-3.5" />
                    Optional Fields
                  </div>
                  {formGaps.fields
                    .filter(f => f.severity === 'recommended')
                    .map((field, idx) => (
                      <div 
                        key={`optional-${idx}`}
                        className="flex items-center justify-between p-3 rounded-lg bg-blue-50 border border-blue-100 hover:bg-blue-100/50 transition-colors"
                      >
                        <div className="flex items-center gap-2.5">
                          {getSeverityIcon(field.severity)}
                          <span className="font-medium text-sm text-gray-800">{field.label}</span>
                        </div>
                        {getSeverityBadge(field.severity)}
                      </div>
                    ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto rounded-full bg-emerald-100 flex items-center justify-center mb-4">
                <CheckCircle className="h-8 w-8 text-emerald-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">All Fields Complete!</h3>
              <p className="text-sm text-gray-500">
                All required data for this form has been extracted.
              </p>
            </div>
          )}

          {/* AI Insights for this form */}
          {formInsights.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-500" />
                AI Insights
              </h3>
              <div className="space-y-2">
                {formInsights.map((insight, idx) => (
                  <div 
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-100"
                  >
                    <Lightbulb className="h-4 w-4 text-amber-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-amber-900 flex-1">{insight.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}

