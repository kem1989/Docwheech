"""
Static definition and helpers for ACORD 125 General Questions.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Canonical ordering and copy-friendly metadata for each question.
GENERAL_QUESTION_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "id": "is_subsidiary",
        "label": "Is the applicant a subsidiary of another entity?",
        "details_label": "Provide information about the parent company.",
        "detail_fields": [
            {
                "id": "parent_company",
                "label": "Parent Company",
                "placeholder": "Enter parent company name",
            },
            {
                "id": "relationship_description",
                "label": "Relationship Description",
                "placeholder": "Describe the relationship",
            },
            {
                "id": "ownership_percentage",
                "label": "Ownership Percentage",
                "placeholder": "Enter ownership percentage (e.g., 75%)",
            },
        ],
    },
    {
        "id": "has_subsidiaries",
        "label": "Does the applicant have any subsidiaries?",
        "details_label": "Provide information about the subsidiary.",
        "detail_fields": [
            {
                "id": "subsidiary_company",
                "label": "Subsidiary Company Name",
                "placeholder": "Enter subsidiary company name",
            },
            {
                "id": "relationship_description",
                "label": "Relationship Description",
                "placeholder": "Describe the relationship",
            },
            {
                "id": "ownership_percentage",
                "label": "Ownership Percentage",
                "placeholder": "Enter ownership percentage (e.g., 60%)",
            },
        ],
    },
    {
        "id": "formal_safety_program",
        "label": "Is there a formal written safety or loss control program in place?",
        "details_label": "Provide brief details (manuals, meetings, OSHA role, etc.).",
    },
    {
        "id": "flammables_exposure",
        "label": "Are any flammables, explosives, or hazardous materials stored or processed?",
        "details_label": "Describe the materials and how they are controlled.",
    },
    {
        "id": "other_insurance_with_company",
        "label": "Does the applicant have other insurance policies with this carrier?",
        "details_label": "List the line of business and policy number.",
    },
    {
        "id": "policy_declined_cancelled",
        "label": "Has any policy been declined, cancelled, or non-renewed in the past 3 years?",
        "details_label": "Describe the date, reason, and corrective actions.",
    },
    {
        "id": "sexual_abuse_claims",
        "label": "Any sexual abuse, molestation, or discrimination claims?",
        "details_label": "Provide claim date(s) and outcomes.",
    },
    {
        "id": "fraud_arson_conviction",
        "label": "Any fraud, arson, or insurance-related felony convictions?",
        "details_label": "Provide details, dates, and jurisdictions.",
    },
    {
        "id": "fire_code_violations",
        "label": "Any outstanding fire or building code violations?",
        "details_label": "Describe violations and corrective steps.",
    },
    {
        "id": "foreclosure_bankruptcy",
        "label": "Any foreclosure or bankruptcy proceedings in the last 5 years?",
        "details_label": "Provide dates and current status.",
    },
    {
        "id": "judgement_or_lien",
        "label": "Any outstanding judgments or tax liens?",
        "details_label": "Describe amounts, creditors, and status.",
    },
    {
        "id": "business_in_trust",
        "label": "Is any part of the business held in trust?",
        "details_label": "Provide the trust name and role.",
    },
    {
        "id": "foreign_operations",
        "label": "Are there any foreign operations, sales, or exposures?",
        "details_label": "List countries and describe activities.",
    },
    {
        "id": "other_business_ventures",
        "label": "Are owners or principals involved in other business ventures?",
        "details_label": "Describe the ventures and relationship.",
    },
    {
        "id": "drones",
        "label": "Does the applicant own, lease, or use drones/UAS?",
        "details_label": "Describe usage, pilots, and any hired services.",
    },
]


def get_default_general_question_responses() -> List[Dict[str, Any]]:
    """
    Create a default response payload with the correct ordering and blank answers.
    """
    responses: List[Dict[str, Any]] = []
    for question in GENERAL_QUESTION_DEFINITIONS:
        detail_fields = question.get("detail_fields")
        default_details: Any = ""
        if detail_fields:
            default_details = {
                field["id"]: ""
                for field in detail_fields
            }
        responses.append(
            {
                "id": question["id"],
                "answer": None,
                "details": default_details,
            }
        )
    return responses


def get_general_question_lookup() -> Dict[str, Dict[str, str]]:
    """Helper to quickly look up metadata by id."""
    return {question["id"]: question for question in GENERAL_QUESTION_DEFINITIONS}

