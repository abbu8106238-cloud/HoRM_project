import numpy as np
import pandas as pd
from datetime import timedelta

class RiskAnalyzer:
    """
    Advanced risk assessment engine for employee attendance patterns.
    Uses multiple indicators and weighted scoring for comprehensive evaluation.
    """
    
    def __init__(self):
        self.risk_weights = {
            'office_hours': 0.3,
            'bay_hours': 0.25,
            'leave_pattern': 0.2,
            'break_behavior': 0.15,
            'exceptions': 0.1
        }
        
    def calculate_risk_score(self, employee_data, company_stats):
        """Calculate comprehensive risk score for employee."""
        scores = {}
        
        # Office hours compliance
        office_minutes = employee_data.get('Office_Hours_Minutes', 0)
        scores['office_hours'] = self._score_office_hours(office_minutes)
        
        # Bay hours compliance
        bay_minutes = employee_data.get('Bay_Hours_Minutes', 0)
        scores['bay_hours'] = self._score_bay_hours(bay_minutes)
        
        # Leave pattern analysis
        total_leaves = employee_data.get('Total_Leave_Days', 0)
        scores['leave_pattern'] = self._score_leave_pattern(total_leaves, company_stats)
        
        # Break behavior
        break_minutes = employee_data.get('Break_Hours_Minutes', 0)
        scores['break_behavior'] = self._score_break_behavior(break_minutes, company_stats)
        
        # Exceptions and special cases
        exceptions = employee_data.get('Excemptions', 'No')
        online_checkin = employee_data.get('Online Check-in', 0)
        scores['exceptions'] = self._score_exceptions(exceptions, online_checkin)
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.risk_weights[key] 
            for key in scores
        )
        
        return total_score, scores
    
    def _score_office_hours(self, office_minutes):
        """Score office hours compliance (0-100, lower is higher risk)."""
        required_minutes = 540  # 9 hours
        
        if office_minutes >= required_minutes:
            return 100
        elif office_minutes >= required_minutes * 0.9:  # 90% compliance
            return 70
        elif office_minutes >= required_minutes * 0.8:  # 80% compliance
            return 40
        else:
            return 0
    
    def _score_bay_hours(self, bay_minutes):
        """Score bay hours compliance (0-100, lower is higher risk)."""
        required_minutes = 420  # 7 hours
        
        if bay_minutes >= required_minutes:
            return 100
        elif bay_minutes >= required_minutes * 0.95:  # 95% compliance
            return 75
        elif bay_minutes >= required_minutes * 0.9:  # 90% compliance
            return 50
        else:
            return 0
    
    def _score_leave_pattern(self, total_leaves, company_stats):
        """Score leave taking pattern."""
        avg_company_leaves = company_stats.get('avg_leave_days', 10)
        
        if total_leaves <= avg_company_leaves * 0.5:
            return 100
        elif total_leaves <= avg_company_leaves:
            return 80
        elif total_leaves <= avg_company_leaves * 1.5:
            return 50
        else:
            return 20
    
    def _score_break_behavior(self, break_minutes, company_stats):
        """Score break taking behavior."""
        avg_company_breaks = company_stats.get('avg_break_hours', 1) * 60
        
        if break_minutes <= avg_company_breaks:
            return 100
        elif break_minutes <= avg_company_breaks * 1.2:
            return 80
        elif break_minutes <= avg_company_breaks * 1.5:
            return 60
        else:
            return 30
    
    def _score_exceptions(self, exceptions, online_checkin):
        """Score exceptions and special cases."""
        score = 100
        
        if exceptions != 'No' and exceptions != '0':
            score -= 20
            
        if online_checkin > 5:  # More than 5 online check-ins
            score -= 15
            
        return max(0, score)
    
    def get_risk_level(self, risk_score):
        """Convert risk score to risk level."""
        if risk_score >= 80:
            return 'Low'
        elif risk_score >= 60:
            return 'Medium'
        else:
            return 'High'
    
    def get_risk_reasons(self, employee_data, scores, company_stats):
        """Get detailed reasons for risk assessment."""
        reasons = []
        
        # Office hours issues
        if scores['office_hours'] < 70:
            office_hrs = employee_data.get('Office_Hours_Minutes', 0) / 60
            reasons.append(f"Office hours ({office_hrs:.1f}h) below required 9 hours")
        
        # Bay hours issues
        if scores['bay_hours'] < 75:
            bay_hrs = employee_data.get('Bay_Hours_Minutes', 0) / 60
            reasons.append(f"Bay hours ({bay_hrs:.1f}h) below mandatory 7 hours")
        
        # Leave pattern issues
        if scores['leave_pattern'] < 80:
            total_leaves = employee_data.get('Total_Leave_Days', 0)
            avg_leaves = company_stats.get('avg_leave_days', 10)
            reasons.append(f"Leave days ({total_leaves:.1f}) above company average ({avg_leaves:.1f})")
        
        # Break behavior issues
        if scores['break_behavior'] < 80:
            break_hrs = employee_data.get('Break_Hours_Minutes', 0) / 60
            reasons.append(f"Extended break time ({break_hrs:.1f}h) impacting productivity")
        
        # Exception issues
        if scores['exceptions'] < 100:
            exceptions = employee_data.get('Excemptions', 'No')
            if exceptions != 'No':
                reasons.append(f"Has attendance exceptions: {exceptions}")
            
            online_checkin = employee_data.get('Online Check-in', 0)
            if online_checkin > 5:
                reasons.append(f"High online check-ins ({online_checkin}) may indicate attendance issues")
        
        return reasons if reasons else ["Good attendance pattern - meeting all requirements"]
