import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import base64

# Import custom utilities
from utils.data_processor import AttendanceDataProcessor
from utils.risk_analyzer import RiskAnalyzer
from utils.recommendation_engine import RecommendationEngine
from utils.visualizations import VisualizationEngine

# Page configuration
st.set_page_config(
    page_title="Mu Sigma | Resource Management Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    """Load custom CSS for professional styling."""
    css_path = os.path.join('assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        # Fallback CSS if file doesn't exist
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1200px;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #FF6B35;
            margin-bottom: 1rem;
        }
        .risk-indicator {
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
        }
        .risk-low { background-color: #28A745; color: white; }
        .risk-medium { background-color: #FFC107; color: #333; }
        .risk-high { background-color: #DC3545; color: white; }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = None
    if 'risk_analyzer' not in st.session_state:
        st.session_state.risk_analyzer = RiskAnalyzer()
    if 'recommendation_engine' not in st.session_state:
        st.session_state.recommendation_engine = RecommendationEngine()
    if 'visualization_engine' not in st.session_state:
        st.session_state.visualization_engine = VisualizationEngine()

# Load data with caching
@st.cache_data
def load_attendance_data():
    """Load and process attendance data."""
    data_path = os.path.join('data', 'attendance.xlsx')
    
    if not os.path.exists(data_path):
        st.error(f"""
        ❌ **Data file not found!**
        
        Please ensure your attendance data file is located at: `{data_path}`
        
        The file should contain the following columns:
        - Fake ID, Designation, Recruitment Type, Account code
        - Avg. In Time, Avg. Out Time, Avg. Office hrs, Avg. Bay hrs
        - Avg. Break hrs, Avg. Cafeteria hrs, Avg. OOO hrs
        - Unbilled, Half-Day leave, Full-Day leave, Online Check-in, Excemptions
        """)
        return None
    
    try:
        processor = AttendanceDataProcessor(data_path)
        df = processor.load_data()
        return processor
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Company logo and header
def display_header():
    """Display company header with logo."""
    # Create header container
    header_container = st.container()
    
    with header_container:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            # Logo placeholder
            logo_path = os.path.join('assets', 'logo.png')
            if os.path.exists(logo_path):
                st.image(logo_path, width=100)
            else:
                st.markdown("🏢 **Mu Sigma**")
        
        with col2:
            st.markdown("""
            <div class="main-header">
                <h1 class="main-title">Resource Management Dashboard</h1>
                <p class="main-subtitle">Personalized Workforce Insights & Actions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Current datetime
            st.markdown(f"""
            <div style="text-align: right; color: #666; font-size: 0.9rem;">
                {datetime.now().strftime('%B %d, %Y<br>%I:%M %p')}
            </div>
            """, unsafe_allow_html=True)

# Organization statistics
def display_organization_stats(data_processor):
    """Display high-level organization statistics."""
    st.markdown("### 📈 Organization Overview")
    
    stats = data_processor.company_stats
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Employees",
            value=f"{stats['total_employees']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Avg Office Hours",
            value=f"{stats['avg_office_hours']:.1f}h",
            delta=f"{stats['avg_office_hours'] - 9:.1f}h from required"
        )
    
    with col3:
        st.metric(
            label="Avg Bay Hours", 
            value=f"{stats['avg_bay_hours']:.1f}h",
            delta=f"{stats['avg_bay_hours'] - 7:.1f}h from required"
        )
    
    with col4:
        st.metric(
            label="Office Compliance",
            value=f"{stats['office_compliance_rate']:.1f}%",
            delta=f"{stats['office_compliance_rate'] - 100:.1f}%" if stats['office_compliance_rate'] < 100 else "✅ Perfect"
        )
    
    with col5:
        st.metric(
            label="Bay Compliance", 
            value=f"{stats['bay_compliance_rate']:.1f}%",
            delta=f"{stats['bay_compliance_rate'] - 100:.1f}%" if stats['bay_compliance_rate'] < 100 else "✅ Perfect"
        )

# Filter section
def display_filters(data_processor):
    """Display filter controls."""
    st.markdown("### 🔍 Filter & Search Controls")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            accounts = ['All'] + sorted(data_processor.df['Account code'].unique().tolist())
            selected_account = st.selectbox(
                "🏢 Filter by Account",
                accounts,
                key="account_filter"
            )
        
        with col2:
            designations = ['All'] + sorted(data_processor.df['Designation'].unique().tolist())
            selected_designation = st.selectbox(
                "👥 Filter by Designation", 
                designations,
                key="designation_filter"
            )
        
        with col3:
            employee_id = st.text_input(
                "🔍 Search Employee by ID",
                placeholder="Enter Employee ID (e.g., 0, 1, 2...)",
                key="employee_search"
            ).strip()
    
    return selected_account, selected_designation, employee_id

# Employee dashboard
def display_employee_dashboard(employee_data, data_processor):
    """Display comprehensive employee dashboard."""
    
    st.markdown(f"# 👤 Employee Dashboard - ID: {employee_data['Fake ID']}")
    
    # Get additional analytics
    risk_analyzer = st.session_state.risk_analyzer
    rec_engine = st.session_state.recommendation_engine
    viz_engine = st.session_state.visualization_engine
    
    # Calculate risk and recommendations
    risk_score, risk_breakdown = risk_analyzer.calculate_risk_score(
        employee_data, data_processor.company_stats
    )
    risk_level = risk_analyzer.get_risk_level(risk_score)
    risk_reasons = risk_analyzer.get_risk_reasons(
        employee_data, risk_breakdown, data_processor.company_stats
    )
    
    # Get account statistics for comparison
    account_stats = data_processor.get_account_stats(employee_data['Account code'])
    
    # Generate recommendations
    recommendations = rec_engine.generate_recommendations(
        employee_data, risk_score, risk_reasons, 
        data_processor.company_stats, account_stats
    )
    
    # Employee basic info section
    st.markdown("### 📋 Employee Information")
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.markdown(f"""
        <div class="employee-info-card">
            <div class="info-label">Designation</div>
            <div class="info-value">{employee_data.get('Designation', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
        <div class="employee-info-card">
            <div class="info-label">Account</div>
            <div class="info-value">{employee_data.get('Account code', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col3:
        st.markdown(f"""
        <div class="employee-info-card">
            <div class="info-label">Recruitment Type</div>
            <div class="info-value">{employee_data.get('Recruitment Type', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col4:
        st.markdown(f"""
        <div class="employee-info-card">
            <div class="info-label">Billing Status</div>
            <div class="info-value">{employee_data.get('Unbilled', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Performance metrics section
    st.markdown("### ⏱️ Attendance Performance Metrics")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    office_hours = employee_data.get('Office_Hours_Minutes', 0) / 60
    bay_hours = employee_data.get('Bay_Hours_Minutes', 0) / 60
    break_hours = employee_data.get('Break_Hours_Minutes', 0) / 60
    total_leaves = employee_data.get('Total_Leave_Days', 0)
    productivity_ratio = employee_data.get('Productivity_Ratio', 0)
    
    with metric_col1:
        office_delta = office_hours - 9
        st.metric(
            "Office Hours",
            f"{office_hours:.1f}h",
            delta=f"{office_delta:+.1f}h from required",
            delta_color="normal" if office_delta >= 0 else "inverse"
        )
    
    with metric_col2:
        bay_delta = bay_hours - 7
        st.metric(
            "Bay Hours", 
            f"{bay_hours:.1f}h",
            delta=f"{bay_delta:+.1f}h from required",
            delta_color="normal" if bay_delta >= 0 else "inverse"
        )
    
    with metric_col3:
        st.metric(
            "Break Hours",
            f"{break_hours:.1f}h",
            delta=f"vs {data_processor.company_stats['avg_break_hours']:.1f}h avg"
        )
    
    with metric_col4:
        st.metric(
            "Leave Days",
            f"{total_leaves:.1f}",
            delta=f"vs {data_processor.company_stats['avg_leave_days']:.1f} avg"
        )
    
    with metric_col5:
        st.metric(
            "Productivity Ratio",
            f"{productivity_ratio:.2f}",
            delta="Higher is better"
        )
    
    st.markdown("---")
    
    # Risk assessment section
    st.markdown("### ⚠️ Risk Assessment")
    
    risk_col1, risk_col2 = st.columns([1, 2])
    
    with risk_col1:
        # Risk level indicator
        risk_class = f"risk-{risk_level.lower()}"
        risk_emoji = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Medium" else "🔴"
        
        st.markdown(f"""
        <div class="risk-indicator {risk_class}">
            <h3>{risk_emoji} Risk Level: {risk_level}</h3>
            <p>Risk Score: {risk_score:.1f}/100</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk breakdown
        if st.button("🔍 View Risk Breakdown", key="risk_breakdown"):
            st.markdown("#### Risk Factor Analysis:")
            for factor, score in risk_breakdown.items():
                st.write(f"**{factor.replace('_', ' ').title()}:** {score:.1f}/100")
    
    with risk_col2:
        # Risk reasons
        st.markdown("#### 📝 Risk Analysis Details:")
        for i, reason in enumerate(risk_reasons, 1):
            icon = "✅" if "Good" in reason else "⚠️" if any(word in reason for word in ["below", "above", "High"]) else "ℹ️"
            st.write(f"{icon} {reason}")
    
    st.markdown("---")
    
    # Next best actions section
    st.markdown("### 🎯 Next Best Action Recommendations")
    
    for i, action in enumerate(recommendations, 1):
        impact = rec_engine.get_action_impact(action)
        impact_class = impact.lower().replace(' ', '-')
        
        st.markdown(f"""
        <div class="action-card">
            <div class="action-title">🔹Action {i}:</div>
            <div class="action-description">{action}</div>
            <span class="action-impact {impact_class}">{impact}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Comparative analysis section
    st.markdown("### 📊 Comparative Performance Analysis")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Office hours comparison
        office_chart = viz_engine.create_employee_comparison_chart(
            employee_data, account_stats, data_processor.company_stats, 'Office Hours'
        )
        st.plotly_chart(office_chart, use_container_width=True)
    
    with chart_col2:
        # Bay hours comparison
        bay_chart = viz_engine.create_employee_comparison_chart(
            employee_data, account_stats, data_processor.company_stats, 'Bay Hours'
        )
        st.plotly_chart(bay_chart, use_container_width=True)
    
    # Time allocation breakdown
    st.markdown("### ⏰ Daily Time Allocation Analysis")
    breakdown_chart = viz_engine.create_attendance_breakdown_chart(employee_data)
    st.plotly_chart(breakdown_chart, use_container_width=True)

# Filtered data display
def display_filtered_data(data_processor, account, designation):
    """Display filtered employee data with analytics."""
    
    filtered_df = data_processor.get_filtered_data(account, designation)
    
    st.markdown(f"### 📊 Filtered Data Analysis")
    st.markdown(f"**Showing {len(filtered_df)} employees** " + 
                (f"from account **{account}**" if account != 'All' else "") +
                (" and " if account != 'All' and designation != 'All' else "") +
                (f"with designation **{designation}**" if designation != 'All' else ""))
    
    # Summary statistics for filtered data
    if len(filtered_df) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_office = filtered_df['Office_Hours_Minutes'].mean() / 60
            st.metric("Avg Office Hours", f"{avg_office:.1f}h")
        
        with col2:
            avg_bay = filtered_df['Bay_Hours_Minutes'].mean() / 60
            st.metric("Avg Bay Hours", f"{avg_bay:.1f}h")
        
        with col3:
            office_compliance = (filtered_df['Office_Hours_Minutes'] >= 540).mean() * 100
            st.metric("Office Compliance", f"{office_compliance:.1f}%")
        
        with col4:
            bay_compliance = (filtered_df['Bay_Hours_Minutes'] >= 420).mean() * 100
            st.metric("Bay Compliance", f"{bay_compliance:.1f}%")
        
        # Display charts
        viz_engine = st.session_state.visualization_engine
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk distribution
            risk_chart = viz_engine.create_risk_distribution_chart(filtered_df)
            st.plotly_chart(risk_chart, use_container_width=True)
        
        with col2:
            # Department comparison
            if account != 'All':
                dept_chart = viz_engine.create_department_comparison_chart(
                    data_processor.df, account
                )
                st.plotly_chart(dept_chart, use_container_width=True)
            else:
                trend_chart = viz_engine.create_trend_analysis_chart(filtered_df)
                st.plotly_chart(trend_chart, use_container_width=True)
        
        # Detailed data table
        with st.expander("📋 View Detailed Employee Data", expanded=False):
            # Prepare display dataframe
            display_columns = [
                'Fake ID', 'Designation', 'Account code', 'Recruitment Type',
                'Office_Hours_Minutes', 'Bay_Hours_Minutes', 'Break_Hours_Minutes',
                'Total_Leave_Days', 'Productivity_Ratio', 'Unbilled'
            ]
            
            display_df = filtered_df[display_columns].copy()
            
            # Convert minutes to hours for better readability
            display_df['Office Hours'] = (display_df['Office_Hours_Minutes'] / 60).round(1)
            display_df['Bay Hours'] = (display_df['Bay_Hours_Minutes'] / 60).round(1) 
            display_df['Break Hours'] = (display_df['Break_Hours_Minutes'] / 60).round(1)
            
            # Drop minute columns and rename
            display_df = display_df.drop(['Office_Hours_Minutes', 'Bay_Hours_Minutes', 'Break_Hours_Minutes'], axis=1)
            display_df = display_df.rename(columns={
                'Total_Leave_Days': 'Leave Days',
                'Productivity_Ratio': 'Productivity',
                'Account code': 'Account',
                'Recruitment Type': 'Recruitment'
            })
            
            st.dataframe(display_df, use_container_width=True, height=400)

# Main application
def main():
    """Main application entry point."""
    
    # Load custom styling
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Display header
    display_header()
    
    # Load data
    data_processor = load_attendance_data()
    
    if data_processor is None:
        st.stop()
    
    # Store in session state
    st.session_state.data_processor = data_processor
    
    # Display organization stats
    display_organization_stats(data_processor)
    
    st.markdown("---")
    
    # Display filters
    selected_account, selected_designation, employee_id = display_filters(data_processor)
    
    st.markdown("---")
    
    # Main content area
    if employee_id:
        # Employee search
        try:
            emp_id_int = int(employee_id)
            employee_data = data_processor.get_employee_data(emp_id_int)
            
            if employee_data is not None:
                display_employee_dashboard(employee_data, data_processor)
            else:
                st.warning(f"❌ No employee found with Fake ID: {employee_id}")
                st.info("💡 **Tip:** Try searching with a different Employee ID (e.g., 0, 1, 2, 3...)")
                
                # Show available IDs
                available_ids = sorted(data_processor.df['Fake ID'].unique())
                st.write(f"**Available Employee IDs:** {', '.join(map(str, available_ids[:20]))}" + 
                        (f" and {len(available_ids)-20} more..." if len(available_ids) > 20 else ""))
        except ValueError:
            st.error("❌ Please enter a valid numeric Employee ID")
    else:
        # Show filtered data
        display_filtered_data(data_processor, selected_account, selected_designation)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>Mu Sigma Resource Management Dashboard</strong></p>
        <p>Powered by Advanced Analytics</p>
        <p><em>Driving data-backed decisions for optimal resource management</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
