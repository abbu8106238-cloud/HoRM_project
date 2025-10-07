import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class VisualizationEngine:
    """
    Advanced visualization engine for creating interactive charts and graphs
    with professional styling for the attendance dashboard.
    """
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#FF6B35',      # Mu Sigma Orange
            'secondary': '#004E89',     # Mu Sigma Blue  
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'info': '#17A2B8',
            'light': '#F8F9FA',
            'dark': '#343A40'
        }
        
        self.risk_colors = {
            'Low': self.color_scheme['success'],
            'Medium': self.color_scheme['warning'],
            'High': self.color_scheme['danger']
        }
    
    def create_employee_comparison_chart(self, employee_data, account_data, 
                                       company_stats, metric='Office Hours'):
        """Create comparison chart for employee vs account vs company."""
        
        if metric == 'Office Hours':
            emp_value = employee_data.get('Office_Hours_Minutes', 0) / 60
            account_avg = account_data.get('avg_office_hours', 0)
            company_avg = company_stats.get('avg_office_hours', 0)
            required = 9
        else:  # Bay Hours
            emp_value = employee_data.get('Bay_Hours_Minutes', 0) / 60
            account_avg = account_data.get('avg_bay_hours', 0)
            company_avg = company_stats.get('avg_bay_hours', 0)
            required = 7
        
        categories = ['Employee', 'Account Avg', 'Company Avg', 'Required']
        values = [emp_value, account_avg, company_avg, required]
        colors = [self.color_scheme['primary'], self.color_scheme['secondary'], 
                 self.color_scheme['info'], self.color_scheme['dark']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f'{v:.1f}h' for v in values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=f'{metric} Comparison',
            xaxis_title='Comparison Groups',
            yaxis_title='Hours',
            template='plotly_white',
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_attendance_breakdown_chart(self, employee_data):
        """Create pie chart showing time breakdown."""
        
        office_hrs = employee_data.get('Office_Hours_Minutes', 0) / 60
        bay_hrs = employee_data.get('Bay_Hours_Minutes', 0) / 60
        break_hrs = employee_data.get('Break_Hours_Minutes', 0) / 60
        cafeteria_hrs = employee_data.get('Avg. Cafeteria hrs', pd.Timedelta(0)).total_seconds() / 3600
        ooo_hrs = employee_data.get('Avg. OOO hrs', pd.Timedelta(0)).total_seconds() / 3600
        
        # Calculate productive vs non-productive time
        productive_time = bay_hrs
        break_time = break_hrs + cafeteria_hrs
        other_office_time = max(0, office_hrs - bay_hrs - break_time)
        out_of_office = ooo_hrs
        
        labels = ['Productive Time', 'Break Time', 'Other Office Time', 'Out of Office']
        values = [productive_time, break_time, other_office_time, out_of_office]
        colors = [self.color_scheme['success'], self.color_scheme['warning'], 
                 self.color_scheme['info'], self.color_scheme['danger']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='auto',
        )])
        
        fig.update_layout(
            title='Daily Time Allocation Breakdown',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_department_comparison_chart(self, df, selected_account):
        """Create comparison chart across different accounts/departments."""
        
        # Calculate metrics by account
        account_stats = df.groupby('Account code').agg({
            'Office_Hours_Minutes': 'mean',
            'Bay_Hours_Minutes': 'mean',
            'Break_Hours_Minutes': 'mean',
            'Total_Leave_Days': 'mean'
        }).reset_index()
        
        account_stats['Avg_Office_Hours'] = account_stats['Office_Hours_Minutes'] / 60
        account_stats['Avg_Bay_Hours'] = account_stats['Bay_Hours_Minutes'] / 60
        
        # Highlight selected account
        colors = [self.color_scheme['primary'] if acc == selected_account 
                 else self.color_scheme['light'] for acc in account_stats['Account code']]
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Average Office Hours by Account', 'Average Bay Hours by Account'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Office Hours
        fig.add_trace(
            go.Bar(
                x=account_stats['Account code'],
                y=account_stats['Avg_Office_Hours'],
                name='Office Hours',
                marker_color=colors,
                text=[f'{v:.1f}h' for v in account_stats['Avg_Office_Hours']],
                textposition='auto',
            ),
            row=1, col=1
        )
        
        # Bay Hours
        fig.add_trace(
            go.Bar(
                x=account_stats['Account code'],
                y=account_stats['Avg_Bay_Hours'],
                name='Bay Hours',
                marker_color=colors,
                text=[f'{v:.1f}h' for v in account_stats['Avg_Bay_Hours']],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Add required lines
        fig.add_hline(y=9, line_dash="dash", line_color="red", 
                     annotation_text="Required: 9h", row=1, col=1)
        fig.add_hline(y=7, line_dash="dash", line_color="red", 
                     annotation_text="Required: 7h", row=1, col=2)
        
        fig.update_layout(
            title='Account-wise Performance Comparison',
            template='plotly_white',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_risk_distribution_chart(self, df):
        """Create risk level distribution chart."""
        
        # Calculate risk levels (simplified for visualization)
        def calculate_simple_risk(row):
            office_compliance = row['Office_Hours_Minutes'] >= 540
            bay_compliance = row['Bay_Hours_Minutes'] >= 420
            leave_ok = row['Total_Leave_Days'] <= 15
            
            if office_compliance and bay_compliance and leave_ok:
                return 'Low'
            elif (office_compliance and bay_compliance) or (office_compliance and leave_ok):
                return 'Medium' 
            else:
                return 'High'
        
        df['Risk_Level'] = df.apply(calculate_simple_risk, axis=1)
        risk_counts = df['Risk_Level'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            hole=0.5,
            marker_colors=[self.risk_colors[level] for level in risk_counts.index],
            textinfo='label+percent+value',
            textposition='auto',
        )])
        
        fig.update_layout(
            title='Employee Risk Distribution Across Organization',
            template='plotly_white',
            height=400,
            annotations=[dict(text='Risk<br>Levels', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def create_trend_analysis_chart(self, df):
        """Create trend analysis for key metrics."""
        
        # Group by designation for trend analysis
        designation_stats = df.groupby('Designation').agg({
            'Office_Hours_Minutes': 'mean',
            'Bay_Hours_Minutes': 'mean',
            'Total_Leave_Days': 'mean',
            'Productivity_Ratio': 'mean'
        }).reset_index()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Office Hours by Designation', 'Bay Hours by Designation',
                          'Leave Days by Designation', 'Productivity Ratio by Designation')
        )
        
        # Office Hours
        fig.add_trace(
            go.Scatter(
                x=designation_stats['Designation'],
                y=designation_stats['Office_Hours_Minutes'] / 60,
                mode='lines+markers',
                name='Office Hours',
                line_color=self.color_scheme['primary']
            ),
            row=1, col=1
        )
        
        # Bay Hours
        fig.add_trace(
            go.Scatter(
                x=designation_stats['Designation'],
                y=designation_stats['Bay_Hours_Minutes'] / 60,
                mode='lines+markers',
                name='Bay Hours',
                line_color=self.color_scheme['secondary']
            ),
            row=1, col=2
        )
        
        # Leave Days
        fig.add_trace(
            go.Scatter(
                x=designation_stats['Designation'],
                y=designation_stats['Total_Leave_Days'],
                mode='lines+markers',
                name='Leave Days',
                line_color=self.color_scheme['warning']
            ),
            row=2, col=1
        )
        
        # Productivity Ratio
        fig.add_trace(
            go.Scatter(
                x=designation_stats['Designation'],
                y=designation_stats['Productivity_Ratio'],
                mode='lines+markers',
                name='Productivity Ratio',
                line_color=self.color_scheme['info']
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Performance Trends by Designation',
            template='plotly_white',
            height=600,
            showlegend=False
        )
        
        return fig
