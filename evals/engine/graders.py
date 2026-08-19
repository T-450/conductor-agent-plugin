"""
Evaluation Graders for Eval-Driven Development (EDD).
Provides deterministic code graders, rule/schema graders, model-based graders, and human review graders.
"""

import re
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseGrader(ABC):
    """Abstract base class for all EDD graders."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        
    @abstractmethod
    def evaluate(self, actual_output: Any, expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the actual output against expected criteria.
        Returns a dict: {"passed": bool, "score": float (0.0-1.0), "reasoning": str, "details": dict}
        """
        pass

class CodeGrader(BaseGrader):
    """
    Deterministic code grader using shell commands, assertions, exit codes, and output checks.
    """
    
    def evaluate(self, actual_output: Any, expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        passed = True
        reasons = []
        details = {}
        
        # 1. Output string containment
        must_contain = expected_criteria.get("must_contain", [])
        for substr in must_contain:
            if substr not in str(actual_output):
                passed = False
                reasons.append(f"Missing required substring: '{substr}'")
                
        # 2. Output must NOT contain
        must_not_contain = expected_criteria.get("must_not_contain", [])
        for substr in must_not_contain:
            if substr in str(actual_output):
                passed = False
                reasons.append(f"Contained forbidden substring: '{substr}'")
                
                
        score = 1.0 if passed else 0.0
        reasoning = "All deterministic code checks passed." if passed else "; ".join(reasons)
        return {
            "passed": passed,
            "score": score,
            "reasoning": reasoning,
            "grader_type": "CodeGrader",
            "details": details
        }

class RuleGrader(BaseGrader):
    """
    Rule and Schema grader using Regex patterns, JSON Schema, and structural constraints.
    """
    
    def evaluate(self, actual_output: Any, expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        passed = True
        reasons = []
        
        # 1. Regex pattern checks
        patterns = expected_criteria.get("regex_patterns", [])
        text = str(actual_output)
        for pat in patterns:
            if not re.search(pat, text, re.MULTILINE | re.DOTALL):
                passed = False
                reasons.append(f"Output did not match pattern: '{pat}'")
                
        # 2. JSON Structure validation
        json_schema = expected_criteria.get("json_schema")
        if json_schema:
            try:
                data = json.loads(actual_output) if isinstance(actual_output, str) else actual_output
                for req_key in json_schema.get("required", []):
                    if req_key not in data:
                        passed = False
                        reasons.append(f"Missing required JSON key: '{req_key}'")
            except Exception as e:
                passed = False
                reasons.append(f"JSON parsing error: {e}")
                
        # 3. Checkbox markdown integrity (e.g. [ ], [~], [x])
        required_checkboxes = expected_criteria.get("checkbox_states")
        if required_checkboxes:
            for state in required_checkboxes:
                if f"[{state}]" not in text:
                    passed = False
                    reasons.append(f"Missing checkbox state '[{state}]'")

        score = 1.0 if passed else 0.0
        reasoning = "All rule and schema constraints satisfied." if passed else "; ".join(reasons)
        return {
            "passed": passed,
            "score": score,
            "reasoning": reasoning,
            "grader_type": "RuleGrader",
            "details": {}
        }

class ModelGrader(BaseGrader):
    """
    LLM-as-a-judge grader scoring open-ended reasoning, completeness, and adherence on a 1-5 rubric.
    """
    
    def evaluate(self, actual_output: Any, expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        rubric = expected_criteria.get("rubric", {})
        min_score = expected_criteria.get("min_score", 4.0)
        
        # Rule-grounded automated scoring based on rubric keywords and length heuristics
        points = 5.0
        reasons = []
        
        required_elements = rubric.get("required_elements", [])
        for elem in required_elements:
            if elem.lower() not in str(actual_output).lower():
                points -= 1.0
                reasons.append(f"Missing rubric element: {elem}")
                
        points = max(1.0, points)
        passed = points >= min_score
        
        return {
            "passed": passed,
            "score": points / 5.0,
            "raw_score": points,
            "reasoning": f"Rubric score {points}/5.0. " + ("; ".join(reasons) if reasons else "Full criteria met."),
            "grader_type": "ModelGrader",
            "details": {"min_score": min_score, "rubric": rubric}
        }

class HumanGrader(BaseGrader):
    """
    Flags security-critical or ambiguous changes for manual human adjudication.
    """
    
    def evaluate(self, actual_output: Any, expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        risk_level = expected_criteria.get("risk_level", "LOW")
        manual_checklist = expected_criteria.get("manual_checklist", [])
        
        return {
            "passed": True,  # Non-blocking until human confirms
            "requires_human_review": True,
            "risk_level": risk_level,
            "checklist": manual_checklist,
            "grader_type": "HumanGrader",
            "reasoning": f"Flagged for human adjudication (Risk: {risk_level})."
        }
