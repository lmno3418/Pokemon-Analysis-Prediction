"""
Interactive Pokémon Dashboard using Dash
Provides modern KPIs, advanced visualizations, and interactive filters
"""

import pandas as pd
import json
import os
from dash import Dash, dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

# Modern color palette
COLORS = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'info': '#06b6d4',
    'light': '#f8fafc',
    'dark': '#1e293b',
    'border': '#e2e8f0'
}

# Load Pokemon data
def load_pokemon_dataframe():
    """Load Pokemon data from JSON and convert to DataFrame"""
    data_path = os.path.join(os.path.dirname(__file__), "static/data/PokemonData2.json")
    try:
        with open(data_path, "r") as f:
            raw_data = json.load(f)
        
        df = pd.DataFrame(raw_data)
        df = df.rename(columns={'#': 'id'})
        
        # Ensure numeric columns are numeric
        numeric_cols = ['id', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 
                       'Generation', 'height', 'weight', 'base_experience']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate total stats
        if all(col in df.columns for col in ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']):
            df['Total_Stats'] = df[['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']].sum(axis=1)
        
        return df
    except Exception as e:
        print(f"Error loading Pokemon data: {e}")
        return pd.DataFrame()

def create_dashboard(server, pokemon_df):
    """Create and configure Dash app with modern UI"""
    
    app = Dash(__name__, server=server, url_base_pathname='/dashboard/')
    
    # Get unique values for filters
    types = sorted(pokemon_df['Type 1'].unique())
    generations = sorted(pokemon_df['Generation'].dropna().unique())
    
    # Modern CSS styling
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                * {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                }
                body {
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                    margin: 0;
                    padding: 0;
                }
                .main-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 20px;
                    margin-bottom: 40px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                }
                .header-title {
                    font-size: 48px;
                    font-weight: 700;
                    margin: 0;
                    background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                .header-subtitle {
                    font-size: 16px;
                    opacity: 0.95;
                    margin: 8px 0 0 0;
                }
                .filters-card {
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                    margin-bottom: 30px;
                    border: 1px solid #e2e8f0;
                }
                .filter-group {
                    margin-bottom: 20px;
                }
                .filter-label {
                    font-weight: 600;
                    color: #1e293b;
                    margin-bottom: 8px;
                    display: block;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .kpi-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin-bottom: 30px;
                }
                .kpi-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .kpi-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
                }
                .kpi-icon {
                    font-size: 32px;
                    margin-bottom: 12px;
                }
                .kpi-value {
                    font-size: 28px;
                    font-weight: 700;
                    color: #667eea;
                    margin: 8px 0;
                }
                .kpi-label {
                    font-size: 13px;
                    color: #64748b;
                    font-weight: 500;
                }
                .chart-container {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                    margin-bottom: 20px;
                }
                .charts-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .full-width {
                    grid-column: 1 / -1;
                }
                .tabs-container {
                    margin-bottom: 30px;
                }
                .data-table-container {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
                    border: 1px solid #e2e8f0;
                    overflow-x: auto;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 14px;
                }
                table thead {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    font-weight: 600;
                }
                table th {
                    padding: 14px;
                    text-align: left;
                }
                table td {
                    padding: 12px 14px;
                    border-bottom: 1px solid #e2e8f0;
                }
                table tbody tr:hover {
                    background-color: #f8fafc;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Define layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("📊 Pokémon Analytics Hub", className='header-title'),
            html.P("Advanced analytics and interactive visualizations", className='header-subtitle')
        ], className='main-container'),
        
        # Main content container
        html.Div([
            # Filters Section
            html.Div([
                html.H3("🔍 Filters & Controls", style={'marginBottom': 20, 'color': '#1e293b', 'fontWeight': '600'}),
                html.Div([
                    html.Div([
                        html.Label("Type 1:", className='filter-label'),
                        dcc.Dropdown(
                            id='type-filter',
                            options=[{'label': 'All Types', 'value': 'all'}] + [{'label': t, 'value': t} for t in types],
                            value='all',
                            style={'width': '100%'},
                            clearable=False
                        )
                    ], className='filter-group', style={'flex': '1'}),
                    
                    html.Div([
                        html.Label("Generation:", className='filter-label'),
                        dcc.Dropdown(
                            id='generation-filter',
                            options=[{'label': 'All Generations', 'value': 'all'}] + [{'label': f"Gen {int(g)}", 'value': g} for g in generations],
                            value='all',
                            style={'width': '100%'},
                            clearable=False
                        )
                    ], className='filter-group', style={'flex': '1'}),
                    
                    html.Div([
                        html.Label("Legendary Status:", className='filter-label'),
                        dcc.Dropdown(
                            id='legendary-filter',
                            options=[
                                {'label': 'All', 'value': 'all'},
                                {'label': '⭐ Legendary Only', 'value': True},
                                {'label': '🌟 Non-Legendary', 'value': False}
                            ],
                            value='all',
                            style={'width': '100%'},
                            clearable=False
                        )
                    ], className='filter-group', style={'flex': '1'}),
                ], style={'display': 'flex', 'gap': '16px', 'marginBottom': '20px', 'flexWrap': 'wrap'}),
                
                html.Div([
                    html.Label("Top N Pokémon (for rankings):", className='filter-label'),
                    dcc.Slider(
                        id='top-n-slider',
                        min=5,
                        max=25,
                        step=5,
                        value=10,
                        marks={5: '5', 10: '10', 15: '15', 20: '20', 25: '25'},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className='filter-label'
                    )
                ], style={'marginBottom': '0'})
            ], className='filters-card'),
            
            # KPI Cards
            html.Div(id='kpi-container', className='kpi-grid'),
            
            # Charts Grid - Row 1
            html.Div([
                html.Div([
                    dcc.Loading(dcc.Graph(id='scatter-plot'), type="default")
                ], className='chart-container'),
                
                html.Div([
                    dcc.Loading(dcc.Graph(id='top-bar-chart'), type="default")
                ], className='chart-container'),
            ], className='charts-grid'),
            
            # Charts Grid - Row 2
            html.Div([
                html.Div([
                    dcc.Loading(dcc.Graph(id='box-plot'), type="default")
                ], className='chart-container'),
                
                html.Div([
                    dcc.Loading(dcc.Graph(id='violin-plot'), type="default")
                ], className='chart-container'),
            ], className='charts-grid'),
            
            # Charts Grid - Row 3
            html.Div([
                html.Div([
                    dcc.Loading(dcc.Graph(id='type-distribution'), type="default")
                ], className='chart-container'),
                
                html.Div([
                    dcc.Loading(dcc.Graph(id='stat-area-chart'), type="default")
                ], className='chart-container'),
            ], className='charts-grid'),
            
            # Full Width Charts
            html.Div([
                html.Div([
                    dcc.Loading(dcc.Graph(id='correlation-heatmap'), type="default")
                ], className='chart-container full-width'),
                
                html.Div([
                    dcc.Loading(dcc.Graph(id='pca-plot'), type="default")
                ], className='chart-container full-width'),
                
                html.Div([
                    dcc.Loading(dcc.Graph(id='distribution-chart'), type="default")
                ], className='chart-container full-width'),
            ], className='charts-grid'),
            
            # Data Table
            html.Div([
                html.H3("📋 Pokémon Database", style={'marginBottom': 20, 'color': '#1e293b', 'fontWeight': '600'}),
                html.Div(id='data-table-container', className='data-table-container')
            ], className='chart-container', style={'marginTop': '30px'})
        ], style={'maxWidth': '1600px', 'margin': '0 auto', 'padding': '20px'})
    ], style={'minHeight': '100vh', 'backgroundColor': '#f5f7fa'})
    
    # Callback to update all visualizations
    @app.callback(
        [Output('kpi-container', 'children'),
         Output('scatter-plot', 'figure'),
         Output('top-bar-chart', 'figure'),
         Output('box-plot', 'figure'),
         Output('violin-plot', 'figure'),
         Output('type-distribution', 'figure'),
         Output('stat-area-chart', 'figure'),
         Output('correlation-heatmap', 'figure'),
         Output('pca-plot', 'figure'),
         Output('distribution-chart', 'figure'),
         Output('data-table-container', 'children')],
        [Input('type-filter', 'value'),
         Input('generation-filter', 'value'),
         Input('legendary-filter', 'value'),
         Input('top-n-slider', 'value')]
    )
    def update_dashboard(type_filter, gen_filter, legendary_filter, top_n):
        """Update all dashboard visualizations"""
        
        # Filter data
        df_filtered = pokemon_df.copy()
        
        if type_filter != 'all':
            df_filtered = df_filtered[df_filtered['Type 1'] == type_filter]
        if gen_filter != 'all':
            df_filtered = df_filtered[df_filtered['Generation'] == gen_filter]
        if legendary_filter != 'all':
            df_filtered = df_filtered[df_filtered['Legendary'] == legendary_filter]
        
        df_filtered = df_filtered.dropna(subset=['Name', 'HP', 'Attack', 'Defense'])
        
        # 1. KPI Cards
        kpi_cards = html.Div([
            kpi_card("Total Pokémon", str(len(df_filtered)), "👾", "#667eea"),
            kpi_card("Avg HP", f"{df_filtered['HP'].mean():.1f}", "❤️", "#ef4444"),
            kpi_card("Avg Attack", f"{df_filtered['Attack'].mean():.1f}", "⚔️", "#f59e0b"),
            kpi_card("Avg Defense", f"{df_filtered['Defense'].mean():.1f}", "🛡️", "#06b6d4"),
            kpi_card("Avg Base XP", f"{df_filtered['base_experience'].mean():.1f}", "⭐", "#10b981"),
            kpi_card("% Legendary", f"{(df_filtered['Legendary'].sum() / len(df_filtered) * 100):.1f}%", "🏆", "#764ba2")
        ], style={'display': 'contents'})
        
        # 2. Scatter Plot: Attack vs Defense
        scatter_fig = go.Figure()
        for gen in sorted(df_filtered['Generation'].unique()):
            df_gen = df_filtered[df_filtered['Generation'] == gen]
            scatter_fig.add_trace(go.Scatter(
                x=df_gen['Attack'],
                y=df_gen['Defense'],
                mode='markers',
                name=f'Gen {int(gen)}',
                marker=dict(
                    size=df_gen['HP'] / 3,
                    opacity=0.7,
                    line=dict(width=1.5, color='white')
                ),
                text=df_gen['Name'],
                hovertemplate='<b>%{text}</b><br>Attack: %{x}<br>Defense: %{y}<extra></extra>'
            ))
        scatter_fig.update_layout(
            title='<b>Attack vs Defense Analysis</b><sub>Bubble size = HP</sub>',
            xaxis_title='Attack', yaxis_title='Defense',
            hovermode='closest', height=400,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 3. Top N Bar Chart
        top_pokemon = df_filtered.nlargest(top_n, 'Attack')[['Name', 'Attack']].sort_values('Attack')
        bar_fig = go.Figure(data=[
            go.Bar(x=top_pokemon['Attack'], y=top_pokemon['Name'], orientation='h',
                   marker=dict(color=top_pokemon['Attack'], colorscale='Viridis', line=dict(color='white', width=1)))
        ])
        bar_fig.update_layout(
            title=f'<b>Top {top_n} Pokémon by Attack</b>',
            xaxis_title='Attack', yaxis_title='',
            height=400, showlegend=False,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 4. Box Plot by Type
        box_fig = go.Figure()
        for ptype in sorted(df_filtered['Type 1'].unique())[:8]:
            df_type = df_filtered[df_filtered['Type 1'] == ptype]
            box_fig.add_trace(go.Box(y=df_type['Attack'], name=ptype, marker_color='#667eea'))
        box_fig.update_layout(
            title='<b>Attack Distribution by Type</b>',
            yaxis_title='Attack',
            height=400,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 5. Violin Plot
        violin_fig = go.Figure()
        for ptype in sorted(df_filtered['Type 1'].unique())[:8]:
            df_type = df_filtered[df_filtered['Type 1'] == ptype]
            violin_fig.add_trace(go.Violin(y=df_type['Defense'], name=ptype, box_visible=True, meanline_visible=True))
        violin_fig.update_layout(
            title='<b>Defense Distribution by Type</b>',
            yaxis_title='Defense',
            height=400,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 6. Type Distribution
        type_counts = df_filtered['Type 1'].value_counts().head(12)
        type_fig = go.Figure(data=[
            go.Bar(x=type_counts.index, y=type_counts.values,
                   marker=dict(color=type_counts.values, colorscale='Turbo', line=dict(color='white', width=1)))
        ])
        type_fig.update_layout(
            title='<b>Pokémon Count by Type</b>',
            xaxis_title='Type', yaxis_title='Count',
            height=400, showlegend=False,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 7. Area Chart - Avg Stats by Generation
        gen_stats = df_filtered.groupby('Generation')[['HP', 'Attack', 'Defense', 'Speed']].mean()
        area_fig = go.Figure()
        for stat in ['HP', 'Attack', 'Defense', 'Speed']:
            area_fig.add_trace(go.Scatter(
                x=gen_stats.index, y=gen_stats[stat],
                mode='lines', name=stat,
                fill='tonexty' if stat != 'HP' else 'tozeroy'
            ))
        area_fig.update_layout(
            title='<b>Average Stats by Generation</b>',
            xaxis_title='Generation', yaxis_title='Average Stat Value',
            height=400,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 8. Correlation Heatmap
        stat_cols = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 'base_experience']
        corr_matrix = df_filtered[stat_cols].corr()
        heatmap_fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=stat_cols, y=stat_cols,
            colorscale='RdBu', zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text:.2f}', textfont={"size": 10}
        ))
        heatmap_fig.update_layout(
            title='<b>Stat Correlation Matrix</b>',
            height=500,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 9. PCA Plot with Clustering
        stat_cols_numeric = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        df_pca = df_filtered[stat_cols_numeric].dropna()
        
        if len(df_pca) > 10:
            scaler = StandardScaler()
            df_scaled = scaler.fit_transform(df_pca)
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(df_scaled)
            
            # K-means clustering
            kmeans = KMeans(n_clusters=4, random_state=42)
            clusters = kmeans.fit_predict(df_scaled)
            
            pca_fig = go.Figure(data=[
                go.Scatter(
                    x=pca_result[:, 0], y=pca_result[:, 1],
                    mode='markers',
                    marker=dict(
                        size=6, color=clusters, colorscale='Plasma',
                        line=dict(color='white', width=1)
                    ),
                    text=df_filtered.iloc[df_pca.index]['Name'],
                    hovertemplate='<b>%{text}</b><extra></extra>'
                )
            ])
            pca_fig.update_layout(
                title=f'<b>PCA Clustering</b><sub>PC1: {pca.explained_variance_ratio_[0]:.1%} | PC2: {pca.explained_variance_ratio_[1]:.1%}</sub>',
                xaxis_title='PC1', yaxis_title='PC2',
                height=500,
                template='plotly_white',
                paper_bgcolor='white'
            )
        else:
            pca_fig = go.Figure().add_annotation(text="Insufficient data for PCA")
            pca_fig.update_layout(height=500)
        
        # 10. Distribution Chart (Multi-stat)
        dist_fig = go.Figure()
        for stat in ['HP', 'Attack', 'Defense']:
            dist_fig.add_trace(go.Histogram(x=df_filtered[stat], name=stat, opacity=0.6, nbinsx=20))
        dist_fig.update_layout(
            title='<b>Stats Distribution</b>',
            xaxis_title='Stat Value', yaxis_title='Frequency',
            barmode='overlay', height=400,
            template='plotly_white',
            paper_bgcolor='white'
        )
        
        # 11. Data Table
        table_df = df_filtered[['Name', 'Type 1', 'Type 2', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Generation']].head(50)
        table = html.Table([
            html.Thead(html.Tr([html.Th(col, style={'textAlign': 'left'}) for col in table_df.columns])),
            html.Tbody([
                html.Tr([html.Td(f"{table_df.iloc[i][col]}", style={'color': '#1e293b'}) for col in table_df.columns])
                for i in range(len(table_df))
            ])
        ])
        
        return kpi_cards, scatter_fig, bar_fig, box_fig, violin_fig, type_fig, area_fig, heatmap_fig, pca_fig, dist_fig, table
    
    return app

def kpi_card(title, value, icon, color):
    """Create a modern KPI card"""
    return html.Div([
        html.Div(icon, style={'fontSize': '36px', 'marginBottom': '12px'}),
        html.Div(value, style={'fontSize': '28px', 'fontWeight': '700', 'color': color, 'marginBottom': '4px'}),
        html.Div(title, style={'fontSize': '13px', 'color': '#64748b', 'fontWeight': '500'})
    ], className='kpi-card')
