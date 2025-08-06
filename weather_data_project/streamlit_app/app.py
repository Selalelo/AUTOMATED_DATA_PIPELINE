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

# Load environment variables from .env file

# Try to import statsmodels for trendlines (optional)
try:
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

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

# Refresh data button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Database connection configuration
st.sidebar.header("🔗 Database Connection")

# Get database configuration from environment variables
def get_db_config():
    """Get database configuration from Streamlit secrets"""
    return {
        'host': st.secrets["database"]["host"],
        'port': st.secrets["database"]["port"],
        'database': st.secrets["database"]["dbname"],
        'username': st.secrets["database"]["user"],
        'password': st.secrets["database"]["password"],
        'schema': st.secrets["database"]["schema"]
    }


# Load configuration
config = get_db_config()

# Show connection status in sidebar (without sensitive info)
with st.sidebar.expander("Database Settings", expanded=False):
    st.write(f"**Host:** {config['host']}")
    st.write(f"**Port:** {config['port']}")
    st.write(f"**Database:** {config['database']}")
    st.write(f"**Username:** {config['username']}")
    st.write(f"**Schema:** {config['schema']}")
    st.write("**Password:** " + ("✅ Loaded from .env" if config['password'] else "❌ Not found in .env"))
    
    # Option to override connection settings (for development)
    # st.markdown("---")
    # override_settings = st.checkbox("Override with manual settings", value=False)
    
    if override_settings:
        st.warning("⚠️ Manual override enabled - not recommended for production!")
        config['host'] = st.text_input("Host", value=config['host'])
        config['port'] = st.text_input("Port", value=config['port'])
        config['database'] = st.text_input("Database", value=config['database'])
        config['username'] = st.text_input("Username", value=config['username'])
        config['password'] = st.text_input("Password", value="", type="password")
        config['schema'] = st.text_input("Schema", value=config['schema'])

# Table name configuration (also from environment variables)
st.sidebar.subheader("📋 dbt Model Names")

def get_table_config():
    """Get table names from environment variables with fallbacks"""
    return {
        'descriptions': os.getenv('TABLE_WEATHER_DESCRIPTIONS', 'weather_condition_frequency'),
        'hourly': os.getenv('TABLE_HOURLY_TRENDS', 'fct_hourly_weather_trend'),
        'daily': os.getenv('TABLE_DAILY_SUMMARY', 'fct_daily_weather_summary')
    }

table_names = get_table_config()

# Show table configuration with option to override
with st.sidebar.expander("Table Configuration", expanded=False):
    st.write(f"**Weather Descriptions:** {table_names['descriptions']}")
    st.write(f"**Hourly Trends:** {table_names['hourly']}")
    st.write(f"**Daily Summary:** {table_names['daily']}")
    
    override_tables = st.checkbox("Override table names", value=False)
    if override_tables:
        table_names['descriptions'] = st.text_input("Weather Descriptions Table", value=table_names['descriptions'])
        table_names['hourly'] = st.text_input("Hourly Trends Table", value=table_names['hourly'])
        table_names['daily'] = st.text_input("Daily Summary Table", value=table_names['daily'])

# Database connection function
@st.cache_resource
def get_database_connection():
    """Create database connection using environment variables"""
    try:
        # Check if required environment variables are set
        if not config['password']:
            st.error("❌ Database password not found in environment variables!")
            st.info("Please check your .env file contains DB_PASSWORD")
            return None
        
        connection_string = f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        engine = create_engine(connection_string)
        
        # Test the connection
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Consume the result
        
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

# Environment status check
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Environment Status")

# Check if .env file exists
required_vars = ['host', 'user', 'password', 'dbname']
missing_vars = [var for var in required_vars if var not in st.secrets["database"]]

if missing_vars:
    st.error(f"Missing required secrets: {', '.join(missing_vars)}")

# Connection status and data loading
use_sample_data = st.sidebar.checkbox("Use Sample Data (Demo Mode)", value=bool(missing_vars))

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
                            data[key] = load_weather_descriptions(engine, table_name, config['schema'])
                        elif key == 'hourly':
                            data[key] = load_hourly_data(engine, table_name, config['schema'])
                        elif key == 'daily':
                            data[key] = load_daily_data(engine, table_name, config['schema'])
                        
                        if data[key] is not None and len(data[key]) > 0:
                            st.sidebar.success(f"✅ {key.title()} data loaded: {len(data[key])} records")
                        else:
                            st.sidebar.warning(f"⚠️ {key.title()} table empty or not found")
                    except Exception as e:
                        st.sidebar.error(f"❌ Error loading {key}: {str(e)}")
    else:
        st.sidebar.error("❌ Database connection failed")
        st.warning("Please check your .env file configuration or enable 'Use Sample Data' to see the dashboard.")
        st.stop()

# Navigation
st.sidebar.markdown("---")
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.selectbox(
    "Select Analysis View:",
    ["🏠 Overview", "☁️ Weather Descriptions", "⏰ Hourly Trends", "📅 Daily Summaries", "🔄 Multi-View Analysis"]
)


# Overview Page
if page == "🏠 Overview":
    st.header("Dashboard Overview")
    
    # Environment configuration info
    with st.expander("🔧 Environment Configuration", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Database Configuration:**")
            st.code(f"""
DB_HOST={config['host']}
DB_PORT={config['port']}
DB_NAME={config['database']}
DB_USER={config['username']}
DB_PASSWORD={"***" if config['password'] else "NOT SET"}
DB_SCHEMA={config['schema']}
            """, language="bash")
        
        with col2:
            st.markdown("**Table Configuration:**")
            st.code(f"""
TABLE_WEATHER_DESCRIPTIONS={table_names['descriptions']}
TABLE_HOURLY_TRENDS={table_names['hourly']}
TABLE_DAILY_SUMMARY={table_names['daily']}
            """, language="bash")
    
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
        - Secure environment variable configuration
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
        max_n = min(10, len(df))
        min_n = min(5, len(df))
        if len(df) > 1:
            top_n = st.slider("Show Top N:", min_n, len(df), max_n)
        else:
            top_n = 1
            st.write(f"Showing: {top_n} record(s)")
    
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
        
        # Create scatter plot with optional trendline
        if STATSMODELS_AVAILABLE:
            fig = px.scatter(df, x='avg_temp', y='avg_wind',
                            title=f"Temperature vs Wind Speed (Correlation: {correlation:.3f})",
                            labels={'avg_temp': 'Temperature (°C)', 'avg_wind': 'Wind Speed (m/s)'},
                            trendline="ols")
        else:
            fig = px.scatter(df, x='avg_temp', y='avg_wind',
                            title=f"Temperature vs Wind Speed (Correlation: {correlation:.3f})",
                            labels={'avg_temp': 'Temperature (°C)', 'avg_wind': 'Wind Speed (m/s)'})
            st.info("💡 Install 'statsmodels' package to see trendlines: `pip install statsmodels`")
    
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
st.sidebar.markdown("### 🗄️ Database Info")
st.sidebar.markdown(f"""
**Current Configuration:**
- Host: {config['host']}
- Database: {config['database']}
- Schema: {config['schema']}
- Connection: {'✅ Active' if 'engine' in locals() and engine is not None else '❌ Inactive'}
""")
st.sidebar.markdown("*Using secure environment variable configuration*")
