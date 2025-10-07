import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class AttendanceDataProcessor:
    """
    Advanced data processor for attendance analytics with comprehensive
    feature engineering and statistical analysis capabilities.
    """
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.processed_df = None
        self.company_stats = {}
        
    @st.cache_data
    def load_data(_self):
        """Load and preprocess attendance data from Excel file."""
        try:
            _self.df = pd.read_excel(_self.file_path)
            _self._clean_data()
            _self._engineer_features()
            _self._calculate_company_stats()
            return _self.df
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    def _clean_data(self):
        """Clean and standardize data formats."""
        # Handle missing values
        self.df = self.df.fillna(0)
        
        # Convert time columns to timedelta
        time_columns = ['Avg. In Time', 'Avg. Out Time', 'Avg. Office hrs', 
                       'Avg. Bay hrs', 'Avg. Break hrs', 'Avg. Cafeteria hrs', 
                       'Avg. OOO hrs']
        
        for col in time_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_timedelta(self.df[col], errors='coerce')
        
        # Clean text columns
        text_columns = ['Designation', 'Recruitment Type', 'Account code', 'Unbilled']
        for col in text_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
    
    def _engineer_features(self):
        """Create additional features for analysis."""
        # Calculate productivity scores
        self.df['Office_Hours_Minutes'] = self.df['Avg. Office hrs'].dt.total_seconds() / 60
        self.df['Bay_Hours_Minutes'] = self.df['Avg. Bay hrs'].dt.total_seconds() / 60
        self.df['Break_Hours_Minutes'] = self.df['Avg. Break hrs'].dt.total_seconds() / 60
        
        # Efficiency metrics
        self.df['Productivity_Ratio'] = (
            self.df['Bay_Hours_Minutes'] / 
            np.maximum(self.df['Office_Hours_Minutes'], 1)
        )
        
        # Attendance issues
        self.df['Total_Leave_Days'] = (
            self.df['Half-Day leave'] * 0.5 + self.df['Full-Day leave']
        )
        
        # Performance indicators
        self.df['Office_Hours_Compliance'] = (
            self.df['Office_Hours_Minutes'] >= 540  # 9 hours
        )
        self.df['Bay_Hours_Compliance'] = (
            self.df['Bay_Hours_Minutes'] >= 420  # 7 hours
        )
        
        # Break behavior analysis
        self.df['Break_Frequency_Score'] = np.where(
            self.df['Break_Hours_Minutes'] > 60, 'High',
            np.where(self.df['Break_Hours_Minutes'] > 30, 'Medium', 'Low')
        )
    
    def _calculate_company_stats(self):
        """Calculate organization-wide statistics."""
        self.company_stats = {
            'total_employees': len(self.df),
            'avg_office_hours': self.df['Office_Hours_Minutes'].mean() / 60,
            'avg_bay_hours': self.df['Bay_Hours_Minutes'].mean() / 60,
            'avg_break_hours': self.df['Break_Hours_Minutes'].mean() / 60,
            'office_compliance_rate': self.df['Office_Hours_Compliance'].mean() * 100,
            'bay_compliance_rate': self.df['Bay_Hours_Compliance'].mean() * 100,
            'total_accounts': self.df['Account code'].nunique(),
            'total_designations': self.df['Designation'].nunique(),
            'avg_leave_days': self.df['Total_Leave_Days'].mean(),
            'billed_employees_pct': (
                self.df['Unbilled'] == 'Billed'
            ).mean() * 100 if 'Unbilled' in self.df.columns else 0
        }
    
    def get_employee_data(self, employee_id):
        """Get detailed data for specific employee."""
        emp_data = self.df[self.df['Fake ID'] == employee_id]
        if emp_data.empty:
            return None
        return emp_data.iloc[0]
    
    def get_filtered_data(self, account=None, designation=None):
        """Get filtered data based on account and designation."""
        filtered_df = self.df.copy()
        
        if account and account != 'All':
            filtered_df = filtered_df[filtered_df['Account code'] == account]
            
        if designation and designation != 'All':
            filtered_df = filtered_df[filtered_df['Designation'] == designation]
            
        return filtered_df
    
    def get_account_stats(self, account_code):
        """Get statistics for specific account."""
        account_data = self.df[self.df['Account code'] == account_code]
        if account_data.empty:
            return {}
            
        return {
            'avg_office_hours': account_data['Office_Hours_Minutes'].mean() / 60,
            'avg_bay_hours': account_data['Bay_Hours_Minutes'].mean() / 60,
            'avg_break_hours': account_data['Break_Hours_Minutes'].mean() / 60,
            'employee_count': len(account_data),
            'office_compliance_rate': account_data['Office_Hours_Compliance'].mean() * 100,
            'bay_compliance_rate': account_data['Bay_Hours_Compliance'].mean() * 100
        }
