"""
Context-Aware Gap Detection Service

This service analyzes extracted data and identifies missing data fields
based on the specific coverages the client is requesting.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.coverage_requirements import (
    COVERAGE_REQUIREMENTS,
    UNIVERSAL_REQUIREMENTS,
    RequirementSeverity,
    get_requirements_for_coverages,
)
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class GapDetectionService:
    """Service for context-aware gap detection in insurance submissions"""
    
    def __init__(self):
        self.openai_service = openai_service
    
    async def analyze_submission(
        self,
        extracted_data: Dict[str, Any],
        acord_schema: Dict[str, Any],
        use_ai_enhancement: bool = True,
    ) -> Dict[str, Any]:
        """
        Analyze a submission for completeness based on detected coverages.
        
        Args:
            extracted_data: Raw extracted data from AI extraction
            acord_schema: Normalized ACORD schema data
            use_ai_enhancement: Whether to use AI for additional analysis
            
        Returns:
            Gap detection report with missing items and completeness score
        """
        try:
            # Step 1: Detect which coverages are being requested
            detected_coverages = self._detect_coverages(extracted_data, acord_schema)
            logger.info(f"Detected coverages: {detected_coverages}")
            
            # Step 2: Get requirements for detected coverages
            requirements = get_requirements_for_coverages(detected_coverages)
            
            # Step 3: Check extracted data against requirements
            data_gaps = self._check_data_requirements(
                acord_schema, 
                requirements["required_data"]
            )
            
            # Step 4: Check conditional requirements
            conditional_gaps = self._check_conditional_requirements(
                acord_schema,
                extracted_data,
                requirements["conditional_requirements"]
            )
            
            # Step 5: Use AI for enhanced analysis (optional)
            ai_insights = []
            if use_ai_enhancement and self.openai_service.client:
                ai_insights = await self._get_ai_insights(
                    extracted_data,
                    detected_coverages,
                    data_gaps
                )
            
            # Step 6: Calculate completeness score
            completeness_score = self._calculate_completeness(
                requirements,
                data_gaps,
                conditional_gaps
            )
            
            # Step 7: Group missing data by section for better display
            missing_data_by_section = self._group_missing_by_section(data_gaps)
            
            # Step 8: Build the report
            report = {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "detected_coverages": [
                    {
                        "code": cov,
                        "display_name": COVERAGE_REQUIREMENTS.get(cov, {}).get("display_name", cov),
                    }
                    for cov in detected_coverages
                ],
                "completeness_score": completeness_score,
                "ready_to_submit": completeness_score >= 80 and not any(
                    gap["severity"] == RequirementSeverity.CRITICAL.value 
                    for gap in data_gaps
                ),
                "summary": self._generate_summary(completeness_score, detected_coverages),
                "missing_data": data_gaps,  # Flat list for backward compatibility
                "missing_data_by_section": missing_data_by_section,  # Grouped by section
                "conditional_gaps": conditional_gaps,
                "ai_insights": ai_insights,
                "total_requirements": len(requirements["required_data"]),
                "found_items": len(requirements["required_data"]) - len(data_gaps),
                "total_missing": len(data_gaps),
                "critical_missing": sum(1 for gap in data_gaps if gap.get("severity") == "critical"),
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Gap detection failed: {str(e)}", exc_info=True)
            raise
    
    # Coverage name aliases for normalization
    COVERAGE_ALIASES = {
        # GL aliases
        "GL": "COMMERCIAL_GENERAL_LIABILITY",
        "GENERAL LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",
        "GENERAL_LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",
        "CGL": "COMMERCIAL_GENERAL_LIABILITY",
        "LIABILITY": "COMMERCIAL_GENERAL_LIABILITY",
        # Property aliases
        "PROPERTY": "COMMERCIAL_PROPERTY",
        "COMMERCIAL PROPERTY": "COMMERCIAL_PROPERTY",
        "BPP": "COMMERCIAL_PROPERTY",
        "BUILDING": "COMMERCIAL_PROPERTY",
        # WC aliases
        "WC": "WORKERS_COMPENSATION",
        "WORKERS COMP": "WORKERS_COMPENSATION",
        "WORKERS' COMPENSATION": "WORKERS_COMPENSATION",
        "WORKCOMP": "WORKERS_COMPENSATION",
        # Auto aliases
        "AUTO": "BUSINESS_AUTO",
        "COMMERCIAL AUTO": "BUSINESS_AUTO",
        "BUSINESS AUTO": "BUSINESS_AUTO",
        "VEHICLE": "BUSINESS_AUTO",
        # Other aliases
        "UMBRELLA": "UMBRELLA",
        "EXCESS": "UMBRELLA",
        "BOP": "BUSINESS_OWNERS",
        "LIQUOR": "LIQUOR_LIABILITY",
        "CYBER": "CYBER_AND_PRIVACY",
        "E&O": "PROFESSIONAL_LIABILITY",
        "PROFESSIONAL": "PROFESSIONAL_LIABILITY",
        "TRUCKING": "TRUCKERS",
        "MOTOR CARRIER": "MOTOR_CARRIER",
    }
    
    def _normalize_coverage(self, coverage_str: str) -> Optional[str]:
        """
        Normalize a coverage string to a standard coverage code.
        """
        if not coverage_str:
            return None
            
        coverage_upper = str(coverage_str).upper().strip().replace("-", "_").replace(" ", "_")
        
        # Direct match against COVERAGE_REQUIREMENTS
        if coverage_upper in COVERAGE_REQUIREMENTS:
            return coverage_upper
        
        # Check aliases
        coverage_clean = str(coverage_str).upper().strip()
        if coverage_clean in self.COVERAGE_ALIASES:
            return self.COVERAGE_ALIASES[coverage_clean]
        
        # Fuzzy match - check if any alias is contained in the string
        for alias, normalized in self.COVERAGE_ALIASES.items():
            if alias in coverage_clean:
                return normalized
        
        # Try partial match against COVERAGE_REQUIREMENTS keys
        for key in COVERAGE_REQUIREMENTS.keys():
            if coverage_upper in key or key in coverage_upper:
                return key
        
        return None
    
    def _detect_coverages(
        self, 
        extracted_data: Dict[str, Any], 
        acord_schema: Dict[str, Any]
    ) -> List[str]:
        """
        Detect which coverage types are being requested using TWO-TIER approach.
        
        TIER 1 (Primary): Check for explicit coverage_requested field
        TIER 2 (Fallback): Infer from lines_of_business and ACORD schema
        
        Args:
            extracted_data: Raw extracted data from AI extraction
            acord_schema: Normalized ACORD schema data
            
        Returns:
            List of normalized coverage type codes
        """
        detected = []
        detection_method = "NONE"
        
        # =====================================================================
        # TIER 1: Check for EXPLICIT coverage requests from extraction
        # =====================================================================
        coverage_requested = extracted_data.get("coverage_requested", {})
        if isinstance(coverage_requested, dict):
            source = coverage_requested.get("source", "").upper()
            requested_values = coverage_requested.get("value", [])
            
            if source == "EXPLICIT" and isinstance(requested_values, list) and len(requested_values) > 0:
                logger.info(f"TIER 1: Found explicit coverage requests: {requested_values}")
                detection_method = "EXPLICIT"
                
                for cov in requested_values:
                    normalized = self._normalize_coverage(cov)
                    if normalized and normalized not in detected:
                        detected.append(normalized)
        
        # Also check if detection was already done in extraction phase
        coverage_detection = extracted_data.get("_coverage_detection", {})
        if coverage_detection.get("method") == "EXPLICIT":
            supported = coverage_detection.get("supported_coverages", [])
            if supported:
                logger.info(f"Using coverage detection from extraction phase: {supported}")
                detection_method = "EXPLICIT"
                for cov in supported:
                    if cov not in detected:
                        detected.append(cov)
        
        # =====================================================================
        # TIER 2: If no explicit coverages, INFER from available data
        # =====================================================================
        if not detected:
            logger.info("TIER 2: No explicit coverage found, inferring from available data")
            detection_method = "INFERRED"
            
            # Check lines_of_business in ACORD schema
            lines_of_business = acord_schema.get("lines_of_business", [])
            if isinstance(lines_of_business, list):
                for lob in lines_of_business:
                    if isinstance(lob, dict):
                        line = lob.get("line")
                        selected = lob.get("selected", False)
                        if line and selected:
                            normalized = self._normalize_coverage(line)
                            if normalized and normalized not in detected:
                                detected.append(normalized)
                    elif isinstance(lob, str):
                        normalized = self._normalize_coverage(lob)
                        if normalized and normalized not in detected:
                            detected.append(normalized)
            
            # Also check extracted_data lines_of_business
            extracted_lob = extracted_data.get("lines_of_business", {})
            if isinstance(extracted_lob, dict) and "value" in extracted_lob:
                lob_values = extracted_lob.get("value", [])
                if isinstance(lob_values, list):
                    for line in lob_values:
                        normalized = self._normalize_coverage(line)
                        if normalized and normalized not in detected:
                            detected.append(normalized)
            
            # Infer from nature of business if still empty
            if not detected:
                nature = extracted_data.get("nature_of_business", {})
                if isinstance(nature, dict):
                    desc = nature.get("description_of_primary_operations", {})
                    if isinstance(desc, dict):
                        desc = desc.get("value", "")
                    if desc:
                        desc_lower = str(desc).lower()
                        # Infer coverages from business description
                        if any(term in desc_lower for term in ["employee", "payroll", "workers comp", "construction", "contractor"]):
                            if "WORKERS_COMPENSATION" not in detected:
                                detected.append("WORKERS_COMPENSATION")
                        if any(term in desc_lower for term in ["restaurant", "food", "retail", "store", "office"]):
                            if "COMMERCIAL_GENERAL_LIABILITY" not in detected:
                                detected.append("COMMERCIAL_GENERAL_LIABILITY")
                        if any(term in desc_lower for term in ["liquor", "bar", "alcohol", "beer", "wine"]):
                            if "LIQUOR_LIABILITY" not in detected:
                                detected.append("LIQUOR_LIABILITY")
                        if any(term in desc_lower for term in ["building", "property", "real estate", "landlord"]):
                            if "COMMERCIAL_PROPERTY" not in detected:
                                detected.append("COMMERCIAL_PROPERTY")
        
        # If no coverages detected, default to GL (most common)
        if not detected:
            logger.warning("No coverages detected, defaulting to COMMERCIAL_GENERAL_LIABILITY")
            detected = ["COMMERCIAL_GENERAL_LIABILITY"]
            detection_method = "DEFAULT"
        
        logger.info(f"Coverage detection complete: method={detection_method}, coverages={detected}")
        return list(set(detected))
    
    def _check_data_requirements(
        self,
        acord_schema: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check which required data fields are missing from the extracted data.
        Checks ACORD 125 critical fields and returns missing items.
        """
        missing = []
        
        for req in requirements:
            field_path = req.get("field_path", "")
            check_type = req.get("check_type", "exists")
            
            value = self._get_nested_value(acord_schema, field_path)
            
            is_missing = False
            reason = ""
            
            if check_type == "exists":
                # Check if value is actually empty
                if value is None:
                    is_missing = True
                    reason = "Field not found"
                elif value == "":
                    is_missing = True
                    reason = "Field is empty"
                elif value == []:
                    is_missing = True
                    reason = "No items in list"
                elif isinstance(value, dict):
                    # For dict values, check if it has a 'value' key or is empty
                    inner_value = value.get('value') if 'value' in value else value
                    if inner_value is None or inner_value == "" or inner_value == {}:
                        is_missing = True
                        reason = "Field value is empty"
            
            elif check_type == "array_not_empty":
                if not isinstance(value, list) or len(value) == 0:
                    is_missing = True
                    reason = "No items found in list"
            
            elif check_type == "array_with_field":
                required_field = req.get("required_field", "")
                if not isinstance(value, list) or len(value) == 0:
                    is_missing = True
                    reason = f"No items found"
                else:
                    # Check if required field exists in array items
                    items_missing_field = [
                        i for i, item in enumerate(value)
                        if not item.get(required_field)
                    ]
                    if items_missing_field:
                        is_missing = True
                        reason = f"Missing {required_field} for {len(items_missing_field)} item(s)"
            
            elif check_type == "array_with_fields":
                required_fields = req.get("required_fields", [])
                if not isinstance(value, list) or len(value) == 0:
                    is_missing = True
                    reason = f"No items found"
                else:
                    missing_fields = []
                    for field in required_fields:
                        items_missing = [
                            i for i, item in enumerate(value)
                            if not item.get(field)
                        ]
                        if items_missing:
                            missing_fields.append(field)
                    if missing_fields:
                        is_missing = True
                        reason = f"Missing fields: {', '.join(missing_fields)}"
            
            if is_missing:
                # Get ACORD field name if available for display
                acord_field = req.get("acord_field", "")
                section = req.get("section", "Other")
                
                missing.append({
                    "id": req.get("id", ""),
                    "label": req.get("label", ""),
                    "field_path": field_path,
                    "section": section,
                    "acord_field": acord_field,
                    "severity": req.get("severity", RequirementSeverity.IMPORTANT).value if isinstance(req.get("severity"), RequirementSeverity) else req.get("severity", "important"),
                    "for_coverage": req.get("for_coverage", "UNIVERSAL"),
                    "reason": reason,
                    "current_value": str(value)[:100] if value else None,
                })
        
        return missing
    
    def _group_missing_by_section(
        self,
        missing_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Group missing data fields by section for better display.
        
        Returns a list like:
        [
            {
                "section": "Policy",
                "missing_count": 2,
                "fields": [
                    {"label": "Proposed Effective Date", "severity": "critical", ...},
                    {"label": "Proposed Expiration Date", "severity": "critical", ...}
                ]
            },
            ...
        ]
        """
        # Group by section
        sections = {}
        for item in missing_data:
            section = item.get("section", "Other")
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
        
        # Convert to list format with section headers
        result = []
        
        # Define section order for consistent display (matches ACORD 125 form layout)
        section_order = [
            "First Named Insured",
            "Policy",
            "Agency / Producer",
            "Transaction Status",
            "Lines of Business",
            "Nature of Business",
            "Contacts",
            "Premises Information",
            "Loss History",
            "Prior Carriers",
            "Other"
        ]
        
        # Add sections in order
        for section_name in section_order:
            if section_name in sections:
                fields = sections[section_name]
                result.append({
                    "section": section_name,
                    "section_display": f"{section_name} Section",
                    "missing_count": len(fields),
                    "has_critical": any(f.get("severity") == "critical" for f in fields),
                    "fields": fields
                })
        
        # Add any remaining sections not in the order list
        for section_name, fields in sections.items():
            if section_name not in section_order:
                result.append({
                    "section": section_name,
                    "section_display": f"{section_name} Section",
                    "missing_count": len(fields),
                    "has_critical": any(f.get("severity") == "critical" for f in fields),
                    "fields": fields
                })
        
        return result
    
    def _check_conditional_requirements(
        self,
        acord_schema: Dict[str, Any],
        extracted_data: Dict[str, Any],
        conditional_requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Check conditional requirements based on business characteristics.
        """
        triggered_gaps = []
        
        for cond_req in conditional_requirements:
            condition = cond_req.get("condition", "")
            requires = cond_req.get("requires", [])
            
            # Evaluate the condition (simplified evaluation)
            condition_met = self._evaluate_condition(condition, acord_schema, extracted_data)
            
            if condition_met:
                for req in requires:
                    # Check if the required item is present
                    # For now, we'll just flag it as a potential gap
                    triggered_gaps.append({
                        "id": req.get("id", ""),
                        "label": req.get("label", ""),
                        "severity": req.get("severity", RequirementSeverity.IMPORTANT).value if isinstance(req.get("severity"), RequirementSeverity) else req.get("severity", "important"),
                        "for_coverage": cond_req.get("for_coverage", "UNIVERSAL"),
                        "triggered_by": condition,
                        "status": "needs_review",
                    })
        
        return triggered_gaps
    
    def _evaluate_condition(
        self,
        condition: str,
        acord_schema: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition string against the data.
        
        Supports simple conditions like:
        - "field contains 'value'"
        - "field in ['value1', 'value2']"
        - "field < number"
        """
        try:
            condition_lower = condition.lower()
            
            # Check for "contains" conditions
            if " contains " in condition_lower:
                parts = condition.split(" contains ")
                if len(parts) == 2:
                    field_path = parts[0].strip()
                    search_value = parts[1].strip().strip("'\"").lower()
                    
                    field_value = self._get_nested_value(acord_schema, field_path)
                    if field_value is None:
                        field_value = self._get_nested_value(extracted_data, field_path)
                    
                    if field_value:
                        if isinstance(field_value, list):
                            return any(search_value in str(v).lower() for v in field_value)
                        return search_value in str(field_value).lower()
            
            # Check for "in" conditions for states
            if " in [" in condition_lower:
                parts = condition.split(" in ")
                if len(parts) == 2:
                    field_path = parts[0].strip()
                    values_str = parts[1].strip()
                    # Parse the list
                    try:
                        import ast
                        values = ast.literal_eval(values_str)
                        field_value = self._get_nested_value(acord_schema, field_path)
                        if field_value:
                            return str(field_value).upper() in [v.upper() for v in values]
                    except:
                        pass
            
            # Check for comparison conditions
            if " < " in condition:
                parts = condition.split(" < ")
                if len(parts) == 2:
                    field_path = parts[0].strip()
                    threshold = parts[1].strip()
                    field_value = self._get_nested_value(acord_schema, field_path)
                    if field_value and str(field_value).isdigit() and threshold.isdigit():
                        return int(field_value) < int(threshold)
            
            return False
            
        except Exception as e:
            logger.warning(f"Failed to evaluate condition '{condition}': {str(e)}")
            return False
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a nested value from a dictionary using dot notation.
        Supports array indexing like "premises[0].city"
        """
        if not path or not data:
            return None
        
        try:
            current = data
            parts = path.replace("]", "").split(".")
            
            for part in parts:
                if "[" in part:
                    # Handle array indexing
                    name, idx_str = part.split("[")
                    idx = int(idx_str)
                    
                    if isinstance(current, dict):
                        current = current.get(name)
                    
                    if isinstance(current, list) and len(current) > idx:
                        current = current[idx]
                    else:
                        return None
                else:
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        return None
                
                if current is None:
                    return None
            
            return current
            
        except Exception:
            return None
    
    async def _get_ai_insights(
        self,
        extracted_data: Dict[str, Any],
        detected_coverages: List[str],
        data_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Use AI to provide additional insights about the submission.
        """
        if not self.openai_service.client:
            return []
        
        try:
            # Build context for AI
            coverage_names = [
                COVERAGE_REQUIREMENTS.get(c, {}).get("display_name", c)
                for c in detected_coverages
            ]
            
            prompt = f"""
You are an expert insurance underwriter reviewing a commercial insurance submission.

COVERAGES REQUESTED: {', '.join(coverage_names)}

EXTRACTED BUSINESS INFORMATION:
{json.dumps(extracted_data, indent=2)[:3000]}

IDENTIFIED DATA GAPS:
- Missing Data Fields: {len(data_gaps)} items

Based on this information, provide 2-3 specific, actionable insights about:
1. Any additional information that would strengthen this submission
2. Potential red flags or areas that need clarification
3. Suggestions for the broker to improve quote results

Return as JSON array:
[
  {{"type": "recommendation", "message": "...", "priority": "high/medium/low"}},
  ...
]

Be specific to THIS business and THESE coverages. Do not give generic advice.
"""
            
            response = self.openai_service.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert insurance underwriter providing submission review insights. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Handle both array and object responses
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "insights" in result:
                return result["insights"]
            elif isinstance(result, dict):
                return [result]
            
            return []
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {str(e)}")
            return []
    
    def _calculate_completeness(
        self,
        requirements: Dict[str, Any],
        data_gaps: List[Dict[str, Any]],
        conditional_gaps: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate an overall completeness score (0-100) based on data field coverage.
        """
        total_fields = len(requirements.get("required_data", []))
        
        if total_fields == 0:
            return 100
        
        # Count missing items by severity
        missing_critical = sum(
            1 for gap in data_gaps 
            if gap.get("severity") == RequirementSeverity.CRITICAL.value
        )
        missing_important = sum(
            1 for gap in data_gaps 
            if gap.get("severity") == RequirementSeverity.IMPORTANT.value
        )
        
        # Simple percentage calculation
        found_fields = total_fields - len(data_gaps)
        score = int((found_fields / total_fields) * 100)
        
        # Apply penalties for critical gaps (each critical gap costs 10 points)
        score = max(0, score - (missing_critical * 10))
        
        return min(100, max(0, score))
    
    def _generate_summary(self, score: int, coverages: List[str]) -> str:
        """Generate a human-readable summary."""
        coverage_names = [
            COVERAGE_REQUIREMENTS.get(c, {}).get("display_name", c)
            for c in coverages
        ]
        coverage_str = ", ".join(coverage_names)
        
        if score >= 90:
            return f"Excellent! This submission for {coverage_str} is nearly complete and ready for carrier submission."
        elif score >= 70:
            return f"Good progress on this {coverage_str} submission. A few items need attention before submitting to carriers."
        elif score >= 50:
            return f"This {coverage_str} submission needs additional information. Please review the missing items below."
        else:
            return f"This {coverage_str} submission is incomplete. Significant information is missing."


# Global service instance
gap_detection_service = GapDetectionService()








