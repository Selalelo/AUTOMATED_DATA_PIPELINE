import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import psycopg2
import os
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .stAlert > div {
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Database connection configuration
st.sidebar.header("🔗 Database Connection")

# Default values for your Docker Compose setup
default_config = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'schema': os.getenv('DB_SCHEMA',)
}

# Connection settings in sidebar
with st.sidebar.expander("Database Settings", expanded=False):
    db_host = st.text_input("Host", value=default_config['host'])
    db_port = st.text_input("Port", value=default_config['port'])
    db_name = st.text_input("Database", value=default_config['database'])
    db_user = st.text_input("Username", value=default_config['username'])
    db_password = st.text_input("Password", value=default_config['password'], type="password")
    db_schema = st.text_input("Schema", value=default_config['schema'])

# Table name configuration
st.sidebar.subheader("📋 dbt Model Names")
table_names = {
    'descriptions': st.sidebar.text_input("Weather Descriptions Table", value="weather_condition_frequency"),
    'hourly': st.sidebar.text_input("Hourly Trends Table", value="fct_hourly_weather_trend"),
    'daily': st.sidebar.text_input("Daily Summary Table", value="fct_daily_weather_summary")
}

# Database connection function
@st.cache_resource
def get_database_connection():
    """Create database connection"""
    try:
        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Data loading functions
@st.cache_data
def load_weather_descriptions(_engine, table_name, schema):
    """Load weather descriptions from database"""
    try:
        query = f"""
        SELECT weather_description, frequency 
        FROM {schema}.{table_name} 
        ORDER BY frequency DESC
        """
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Error loading weather descriptions: {e}")
        return None

@st.cache_data
def load_hourly_data(_engine, table_name, schema):
    """Load hourly weather data from database"""
    try:
        query = f"""
        SELECT hour, avg_temp, avg_wind 
        FROM {schema}.{table_name} 
        ORDER BY hour
        """
        df = pd.read_sql(query, _engine)
        df['hour'] = pd.to_datetime(df['hour'])
        return df
    except Exception as e:
        st.error(f"Error loading hourly data: {e}")
        return None

@st.cache_data
def load_daily_data(_engine, table_name, schema):
    """Load daily weather summary from database"""
    try:
        query = f"""
        SELECT date, observations, avg_temp, min_temp, max_temp, avg_wind_speed 
        FROM {schema}.{table_name} 
        ORDER BY date
        """
        df = pd.read_sql(query, _engine)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Error loading daily data: {e}")
        return None

# Create sample data function for demo
@st.cache_data
def create_sample_data():
    """Create sample data for demonstration"""
    descriptions = pd.DataFrame({
        'weather_description': [
            'Clear sky', 'Few clouds', 'Scattered clouds', 'Broken clouds',
            'Overcast clouds', 'Light rain', 'Moderate rain', 'Heavy rain',
            'Thunderstorm', 'Snow', 'Mist', 'Fog', 'Drizzle'
        ],
        'frequency': [1250, 980, 750, 620, 450, 380, 180, 95, 120, 80, 200, 150, 300]
    })
    
    hours = pd.date_range('2024-01-01', periods=24*7, freq='H')
    np.random.seed(42)
    base_temp = 15 + 10 * np.sin(np.arange(len(hours)) * 2 * np.pi / 24)
    noise = np.random.normal(0, 2, len(hours))
    hourly = pd.DataFrame({
        'hour': hours,
        'avg_temp': np.round(base_temp + noise, 2),
        'avg_wind': np.round(np.random.uniform(5, 25, len(hours)), 2)
    })
    
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    daily = pd.DataFrame({
        'date': dates,
        'observations': np.random.randint(20, 50, len(dates)),
        'avg_temp': np.round(np.random.uniform(10, 25, len(dates)), 2),
        'min_temp': np.round(np.random.uniform(5, 15, len(dates)), 2),
        'max_temp': np.round(np.random.uniform(20, 35, len(dates)), 2),
        'avg_wind_speed': np.round(np.random.uniform(8, 20, len(dates)), 2)
    })
    
    return descriptions, hourly, daily

# Main title
st.title("🌤️ Weather Analytics Dashboard")
st.markdown("Real-time analysis of weather patterns from dbt models")

# Connection status and data loading
use_sample_data = st.sidebar.checkbox("Use Sample Data (Demo Mode)", value=False)

if use_sample_data:
    st.sidebar.success("Using sample data for demonstration")
    sample_desc, sample_hourly, sample_daily = create_sample_data()
    data = {
        'descriptions': sample_desc,
        'hourly': sample_hourly,
        'daily': sample_daily
    }
else:
    # Try to connect to database
    engine = get_database_connection()
    
    if engine is not None:
        st.sidebar.success("✅ Database connected successfully!")
        
        # Load data from database
        data = {}
        
        with st.spinner("Loading data from database..."):
            # Check which tables exist and load data
            for key, table_name in table_names.items():
                if table_name.strip():  # Only if table name is provided
                    try:
                        if key == 'descriptions':
                            data[key] = load_weather_descriptions(engine, table_name, db_schema)
                        elif key == 'hourly':
                            data[key] = load_hourly_data(engine, table_name, db_schema)
                        elif key == 'daily':
                            data[key] = load_daily_data(engine, table_name, db_schema)
                        
                        if data[key] is not None and len(data[key]) > 0:
                            st.sidebar.success(f"✅ {key.title()} data loaded: {len(data[key])} records")
                        else:
                            st.sidebar.warning(f"⚠️ {key.title()} table empty or not found")
                    except Exception as e:
                        st.sidebar.error(f"❌ Error loading {key}: {str(e)}")
    else:
        st.sidebar.error("❌ Database connection failed")
        st.warning("Please check your database connection settings or enable 'Use Sample Data' to see the dashboard.")
        st.stop()

# Navigation
st.sidebar.markdown("---")
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.selectbox(
    "Select Analysis View:",
    ["🏠 Overview", "☁️ Weather Descriptions", "⏰ Hourly Trends", "📅 Daily Summaries", "🔄 Multi-View Analysis"]
)

# Refresh data button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Overview Page
if page == "🏠 Overview":
    st.header("Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Available Analyses
        - **Weather Descriptions**: Frequency analysis of weather conditions
        - **Hourly Trends**: Temperature and wind patterns by hour
        - **Daily Summaries**: Daily weather statistics and trends
        """)
    
    with col2:
        if 'descriptions' in data and data['descriptions'] is not None:
            st.metric("Weather Types", len(data['descriptions']))
        if 'hourly' in data and data['hourly'] is not None:
            st.metric("Hourly Records", len(data['hourly']))
        if 'daily' in data and data['daily'] is not None:
            st.metric("Days of Data", len(data['daily']))
    
    with col3:
        st.markdown("""
        ### 🎯 Key Features
        - Direct database connection
        - Real-time dbt model analysis
        - Interactive visualizations
        - Multi-dimensional insights
        """)
    
    # Data status
    st.header("📊 Data Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'descriptions' in data and data['descriptions'] is not None:
            st.success(f"✅ Weather Descriptions: {len(data['descriptions'])} types")
            if st.checkbox("Preview Weather Descriptions"):
                st.dataframe(data['descriptions'].head(), use_container_width=True)
        else:
            st.error("❌ Weather Descriptions: Not available")
    
    with col2:
        if 'hourly' in data and data['hourly'] is not None:
            st.success(f"✅ Hourly Data: {len(data['hourly'])} records")
            if st.checkbox("Preview Hourly Data"):
                st.dataframe(data['hourly'].head(), use_container_width=True)
        else:
            st.error("❌ Hourly Data: Not available")
    
    with col3:
        if 'daily' in data and data['daily'] is not None:
            st.success(f"✅ Daily Summaries: {len(data['daily'])} days")
            if st.checkbox("Preview Daily Data"):
                st.dataframe(data['daily'].head(), use_container_width=True)
        else:
            st.error("❌ Daily Summaries: Not available")

# Weather Descriptions Page
elif page == "☁️ Weather Descriptions":
    if 'descriptions' not in data or data['descriptions'] is None:
        st.warning("Weather descriptions data not available. Please check your database connection and table name.")
        st.stop()
    
    df = data['descriptions']
    st.header("☁️ Weather Description Analysis")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Weather Types", len(df))
    with col2:
        st.metric("Total Observations", f"{df['frequency'].sum():,}")
    with col3:
        st.metric("Most Common", df.loc[df['frequency'].idxmax(), 'weather_description'])
    with col4:
        st.metric("Average Frequency", f"{df['frequency'].mean():.0f}")
    
    # Visualization controls
    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox("Chart Type:", ["Bar Chart", "Horizontal Bar", "Pie Chart", "Treemap"])
    with col2:
        top_n = st.slider("Show Top N:", 5, len(df), min(10, len(df)))
    
    # Create visualization
    df_filtered = df.head(top_n)
    
    if chart_type == "Bar Chart":
        fig = px.bar(df_filtered, x='weather_description', y='frequency',
                    title=f"Top {top_n} Weather Conditions", color='frequency',
                    color_continuous_scale='viridis')
        fig.update_xaxes(tickangle=-45)
    elif chart_type == "Horizontal Bar":
        fig = px.bar(df_filtered.sort_values('frequency'), x='frequency', y='weather_description',
                    orientation='h', title=f"Top {top_n} Weather Conditions",
                    color='frequency', color_continuous_scale='plasma')
    elif chart_type == "Pie Chart":
        fig = px.pie(df_filtered, values='frequency', names='weather_description',
                    title=f"Distribution of Top {top_n} Weather Conditions")
    else:  # Treemap
        fig = px.treemap(df_filtered, values='frequency', names='weather_description',
                        title=f"Weather Conditions Treemap", color='frequency',
                        color_continuous_scale='RdYlBu')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show full data table
    if st.checkbox("Show all data"):
        st.dataframe(df, use_container_width=True)

# Hourly Trends Page
elif page == "⏰ Hourly Trends":
    if 'hourly' not in data or data['hourly'] is None:
        st.warning("Hourly data not available. Please check your database connection and table name.")
        st.stop()
    
    df = data['hourly']
    st.header("⏰ Hourly Weather Trends")
    
    # Add hour of day for better analysis
    df['hour_of_day'] = df['hour'].dt.hour
    df['date'] = df['hour'].dt.date
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Hours", len(df))
    with col2:
        st.metric("Avg Temperature", f"{df['avg_temp'].mean():.1f}°C")
    with col3:
        st.metric("Avg Wind Speed", f"{df['avg_wind'].mean():.1f} m/s")
    with col4:
        st.metric("Temperature Range", f"{df['avg_temp'].max() - df['avg_temp'].min():.1f}°C")
    
    # Visualization options
    analysis_type = st.selectbox("Analysis Type:", 
                                ["Time Series", "Hourly Patterns", "Temperature vs Wind", "Correlation Analysis"])
    
    if analysis_type == "Time Series":
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           subplot_titles=('Temperature Over Time', 'Wind Speed Over Time'))
        fig.add_trace(go.Scatter(x=df['hour'], y=df['avg_temp'], name='Temperature',
                                line=dict(color='red')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['hour'], y=df['avg_wind'], name='Wind Speed',
                                line=dict(color='blue')), row=2, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Wind Speed (m/s)", row=2, col=1)
        fig.update_layout(height=600, title_text="Hourly Weather Trends Over Time")
    
    elif analysis_type == "Hourly Patterns":
        hourly_avg = df.groupby('hour_of_day').agg({
            'avg_temp': 'mean',
            'avg_wind': 'mean'
        }).reset_index()
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Average Temperature by Hour', 'Average Wind Speed by Hour'))
        fig.add_trace(go.Bar(x=hourly_avg['hour_of_day'], y=hourly_avg['avg_temp'],
                            name='Temperature', marker_color='red'), row=1, col=1)
        fig.add_trace(go.Bar(x=hourly_avg['hour_of_day'], y=hourly_avg['avg_wind'],
                            name='Wind Speed', marker_color='blue'), row=1, col=2)
        fig.update_layout(height=500, title_text="Daily Hourly Patterns")
    
    elif analysis_type == "Temperature vs Wind":
        fig = px.scatter(df, x='avg_temp', y='avg_wind', color='hour_of_day',
                        title="Temperature vs Wind Speed Relationship",
                        labels={'avg_temp': 'Temperature (°C)', 'avg_wind': 'Wind Speed (m/s)'})
    
    else:  # Correlation Analysis
        correlation = df['avg_temp'].corr(df['avg_wind'])
        fig = px.scatter(df, x='avg_temp', y='avg_wind',
                        title=f"Temperature vs Wind Speed (Correlation: {correlation:.3f})",
                        labels={'avg_temp': 'Temperature (°C)', 'avg_wind': 'Wind Speed (m/s)'},
                        trendline="ols")
    
    st.plotly_chart(fig, use_container_width=True)

# Daily Summaries Page
elif page == "📅 Daily Summaries":
    if 'daily' not in data or data['daily'] is None:
        st.warning("Daily data not available. Please check your database connection and table name.")
        st.stop()
    
    df = data['daily']
    st.header("📅 Daily Weather Summaries")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Days of Data", len(df))
    with col2:
        st.metric("Avg Daily Temp", f"{df['avg_temp'].mean():.1f}°C")
    with col3:
        st.metric("Total Observations", f"{df['observations'].sum():,}")
    with col4:
        st.metric("Avg Wind Speed", f"{df['avg_wind_speed'].mean():.1f} m/s")
    
    # Visualization options
    chart_type = st.selectbox("Visualization:", 
                             ["Temperature Trends", "Temperature Range", "Wind Analysis", "Observations Count"])
    
    if chart_type == "Temperature Trends":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['avg_temp'], name='Avg Temperature',
                                line=dict(color='orange', width=3)))
        fig.add_trace(go.Scatter(x=df['date'], y=df['min_temp'], name='Min Temperature',
                                line=dict(color='blue', dash='dot')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['max_temp'], name='Max Temperature',
                                line=dict(color='red', dash='dot')))
        fig.update_layout(title="Daily Temperature Trends", yaxis_title="Temperature (°C)")
    
    elif chart_type == "Temperature Range":
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['max_temp'], fill=None, mode='lines',
                                line_color='rgba(255,0,0,0)', showlegend=False))
        fig.add_trace(go.Scatter(x=df['date'], y=df['min_temp'], fill='tonexty', mode='lines',
                                line_color='rgba(255,0,0,0)', name='Temperature Range',
                                fillcolor='rgba(255,0,0,0.2)'))
        fig.add_trace(go.Scatter(x=df['date'], y=df['avg_temp'], mode='lines',
                                line=dict(color='orange', width=3), name='Average'))
        fig.update_layout(title="Daily Temperature Range", yaxis_title="Temperature (°C)")
    
    elif chart_type == "Wind Analysis":
        fig = px.bar(df, x='date', y='avg_wind_speed',
                    title="Daily Average Wind Speed", color='avg_wind_speed',
                    color_continuous_scale='Blues')
        fig.update_layout(yaxis_title="Wind Speed (m/s)")
    
    else:  # Observations Count
        fig = px.bar(df, x='date', y='observations',
                    title="Daily Observation Count", color='observations',
                    color_continuous_scale='Greens')
        fig.update_layout(yaxis_title="Number of Observations")
    
    st.plotly_chart(fig, use_container_width=True)

# Multi-View Analysis Page
elif page == "🔄 Multi-View Analysis":
    st.header("🔄 Multi-Dimensional Weather Analysis")
    
    available_data = [key for key, df in data.items() if df is not None and len(df) > 0]
    
    if len(available_data) < 2:
        st.warning("Need at least 2 datasets for multi-view analysis. Please check your database connections.")
        st.stop()
    
    # Combined insights
    st.subheader("📊 Cross-Dataset Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'descriptions' in available_data:
            desc_df = data['descriptions']
            st.metric("Weather Types", len(desc_df))
            top_weather = desc_df.iloc[0]['weather_description']
            st.write(f"**Most common**: {top_weather}")
    
    with col2:
        if 'hourly' in available_data:
            hourly_df = data['hourly']
            st.metric("Hourly Records", f"{len(hourly_df):,}")
            st.write(f"**Avg temp**: {hourly_df['avg_temp'].mean():.1f}°C")
    
    with col3:
        if 'daily' in available_data:
            daily_df = data['daily']
            st.metric("Days Analyzed", len(daily_df))
            st.write(f"**Temp range**: {daily_df['avg_temp'].std():.1f}°C std")
    
    # Side-by-side comparisons
    if len(available_data) >= 2:
        st.subheader("📈 Comparative Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'descriptions' in available_data:
                fig1 = px.pie(data['descriptions'].head(5), values='frequency', 
                             names='weather_description', title="Top 5 Weather Conditions")
                st.plotly_chart(fig1, use_container_width=True)
            elif 'hourly' in available_data:
                hourly_avg = data['hourly'].groupby(data['hourly']['hour'].dt.hour)['avg_temp'].mean()
                fig1 = px.line(x=hourly_avg.index, y=hourly_avg.values,
                              title="Average Temperature by Hour of Day")
                fig1.update_xaxes(title="Hour of Day")
                fig1.update_yaxes(title="Temperature (°C)")
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            if 'daily' in available_data:
                fig2 = px.line(data['daily'], x='date', y='avg_temp',
                              title="Daily Temperature Trend")
                st.plotly_chart(fig2, use_container_width=True)
            elif 'hourly' in available_data:
                fig2 = px.scatter(data['hourly'], x='avg_temp', y='avg_wind',
                                 title="Temperature vs Wind Speed")
                st.plotly_chart(fig2, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Docker Setup")
st.sidebar.markdown("""
**Current Configuration:**
- Host: postgres (container)
- Database: mydatabase
- User: user
- Schema: dev (dbt target)

**Container Network:** my-network
""")
st.sidebar.markdown("*Connected to live dbt models*")