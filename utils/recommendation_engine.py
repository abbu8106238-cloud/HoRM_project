import pandas as pd
import numpy as np

class RecommendationEngine:
    """
    Intelligent recommendation system that provides data-driven next best actions
    for employee resource management based on attendance patterns and risk factors.
    """
    
    def __init__(self):
        self.action_templates = {
            'high_risk': [
                " Schedule immediate one-on-one performance review",
                " Implement attendance monitoring with weekly check-ins",
                " Consider flexible work arrangements or support programs",
                " Evaluate for project reassignment or role adjustment",
                " Provide productivity coaching and time management training"
            ],
            'medium_risk': [
                " Arrange informal coaching session on time management",
                " Monitor attendance trends for next 30 days",
                " Discuss workload balance and potential adjustments",
                " Recommend break optimization training",
                " Consider cross-training for better engagement"
            ],
            'low_risk': [
                " Recognize good attendance and performance",
                " Consider for leadership or mentoring opportunities",
                " Evaluate for project lead or increased responsibilities",
                " Continue current engagement strategies",
                " Use as peer mentor for attendance improvement"
            ]
        }
    
    def generate_recommendations(self, employee_data, risk_score, risk_reasons, 
                               company_stats, account_stats=None):
        """Generate personalized next best action recommendations."""
        risk_level = self._get_risk_level(risk_score)
        recommendations = []
        
        # Primary recommendations based on risk level
        primary_actions = self._get_primary_actions(
            employee_data, risk_level, risk_reasons
        )
        
        # Secondary recommendations based on specific issues
        secondary_actions = self._get_issue_specific_actions(
            employee_data, risk_reasons, company_stats
        )
        
        # Tertiary recommendations for positive reinforcement
        tertiary_actions = self._get_development_actions(
            employee_data, company_stats, account_stats
        )
        
        # Combine and prioritize recommendations
        all_actions = primary_actions + secondary_actions + tertiary_actions
        
        # Return top 3 most relevant recommendations
        return self._prioritize_actions(all_actions, employee_data, risk_level)[:3]
    
    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level."""
        if risk_score >= 80:
            return 'low_risk'
        elif risk_score >= 60:
            return 'medium_risk'
        else:
            return 'high_risk'
    
    def _get_primary_actions(self, employee_data, risk_level, risk_reasons):
        """Get primary actions based on overall risk level."""
        base_actions = self.action_templates[risk_level].copy()
        
        # Customize based on specific employee context
        office_hrs = employee_data.get('Office_Hours_Minutes', 0) / 60
        bay_hrs = employee_data.get('Bay_Hours_Minutes', 0) / 60
        designation = employee_data.get('Designation', '')
        
        customized_actions = []
        
        if risk_level == 'high_risk':
            if office_hrs < 8:
                customized_actions.append(
                    "Urgent: Address consistent late arrivals/early departures"
                )
            if bay_hrs < 6:
                customized_actions.append(
                    "Critical: Investigate low productive hours and engagement"
                )
                
        elif risk_level == 'medium_risk':
            if office_hrs < 9:
                customized_actions.append(
                    "Monitor and counsel on office hour expectations"
                )
            if bay_hrs < 7:
                customized_actions.append(
                    "Provide productivity enhancement support"
                )
        
        return base_actions + customized_actions
    
    def _get_issue_specific_actions(self, employee_data, risk_reasons, company_stats):
        """Generate actions targeting specific identified issues."""
        actions = []
        
        total_leaves = employee_data.get('Total_Leave_Days', 0)
        break_hrs = employee_data.get('Break_Hours_Minutes', 0) / 60
        exceptions = employee_data.get('Excemptions', 'No')
        unbilled_status = employee_data.get('Unbilled', '')
        
        # Leave pattern specific actions
        if total_leaves > company_stats.get('avg_leave_days', 10):
            actions.append(
                "Review leave pattern - consider wellness program or workload adjustment"
            )
        
        # Break behavior specific actions
        if break_hrs > 1.5:
            actions.append(
                "Implement break scheduling and productivity awareness training"
            )
        
        # Exception handling specific actions
        if exceptions != 'No' and exceptions != '0':
            actions.append(
                "Address attendance exceptions - review underlying causes"
            )
        
        # Billing status specific actions
        if unbilled_status == 'Unbilled':
            actions.append(
                "Move to billable project or improve utilization"
            )
        
        return actions
    
    def _get_development_actions(self, employee_data, company_stats, account_stats):
        """Generate development and growth focused actions."""
        actions = []
        
        designation = employee_data.get('Designation', '')
        recruitment_type = employee_data.get('Recruitment Type', '')
        productivity_ratio = employee_data.get('Productivity_Ratio', 0)
        
        # Career development based on designation
        if 'AL' in designation or 'Associate' in designation:
            if productivity_ratio > 0.8:
                actions.append(
                    "Consider for promotion to next level - showing good productivity"
                )
            else:
                actions.append(
                    "Provide skill development training for career advancement"
                )
        
        # Campus hire specific development
        if 'Campus' in recruitment_type:
            actions.append(
                "Enroll in campus hire development program and mentoring"
            )
        
        # High performer recognition
        if productivity_ratio > 0.9:
            actions.append(
                "Recognize as high performer - consider for special projects"
            )
        
        return actions
    
    def _prioritize_actions(self, all_actions, employee_data, risk_level):
        """Prioritize actions based on urgency and impact."""
        # Remove duplicates while preserving order
        unique_actions = []
        seen = set()
        for action in all_actions:
            if action not in seen:
                unique_actions.append(action)
                seen.add(action)
        
        # Sort by priority keywords
        priority_keywords = {
            'Urgent': 10,
            'Critical': 9,
            'Priority': 8,
            'Immediate': 7,
            'Schedule': 6,
            'Monitor': 5,
            'Consider': 4,
            'Provide': 3,
            'Recommend': 2,
            'Continue': 1
        }
        
        def get_priority(action):
            for keyword, priority in priority_keywords.items():
                if keyword in action:
                    return priority
            return 0
        
        prioritized_actions = sorted(unique_actions, key=get_priority, reverse=True)
        
        return prioritized_actions
    
    def get_action_impact(self, action):
        """Estimate the potential impact of an action."""
        high_impact_keywords = [
            'Urgent', 'Critical', 'Immediate', 'Priority', 'reassignment'
        ]
        medium_impact_keywords = [
            'Schedule', 'Monitor', 'training', 'coaching', 'support'
        ]
        
        action_lower = action.lower()
        
        if any(keyword.lower() in action_lower for keyword in high_impact_keywords):
            return 'High Impact'
        elif any(keyword.lower() in action_lower for keyword in medium_impact_keywords):
            return 'Medium Impact'
        else:
            return 'Low Impact'
