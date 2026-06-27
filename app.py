import pandas as pd
import io
from shiny import App, render, ui, reactive

# 1. Structural UI Definition (3 Metric Cards + Chart beneath)
app_ui = ui.page_fluid(
    ui.tags.style(
        """
        body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; padding: 24px; }
        .card-bg { background-color: #1e293b; border: 1px solid #334155; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
        .metric-title { font-size: 0.85rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; letter-spacing: 0.05em; margin: 0; }
        .metric-value { font-size: 2.25rem; font-weight: 700; margin-top: 8px; margin-bottom: 0; }
        .text-white { color: #ffffff; }
        .text-slate-400 { color: #94a3b8; }
        .mb-4 { margin-bottom: 16px; }
        .px-4 { padding-left: 16px; padding-right: 16px; }
        """
    ),
    ui.div(
        ui.h2("Commercial Cleaning Performance Dashboard", class_="text-white font-bold"),
        ui.p("Operational Analytics Portfolio | January 2026", class_="text-slate-400 mb-4"),
    ),
    
    # Information Hierarchy Layout: 3 Metric Cards Block
    ui.layout_column_wrap(
        ui.div(
            ui.p("Total Revenue", class_="metric-title"),
            ui.output_text("render_revenue", class_="metric-value text-emerald-400"),
            class_="card-bg"
        ),
        ui.div(
            ui.p("Total Hours Logged", class_="metric-title"),
            ui.output_text("render_hours", class_="metric-value text-sky-400"),
            class_="card-bg"
        ),
        ui.div(
            ui.p("Hourly Yield Rate", class_="metric-title"),
            ui.output_text("render_yield", class_="metric-value text-amber-400"),
            class_="card-bg"
        ),
        width=1/3,
        gap="24px",
        class_="mb-4"
    ),
    
    # Chart Canvas Positioned Directly Beneath Cards
    ui.div(
        ui.div(
            ui.h3("Revenue Breakdown by Asset Location", class_="text-white text-base font-semibold mb-4"),
            ui.output_plot("render_performance_chart"),
            class_="card-bg"
        )
    )
)

# 2. Server Processing Engine (Reactive Execution)
def server(input, output, session):
    
    # Reactive calculation engine reading the data asset file
    @reactive.calc
    def processed_data():
        try:
            df = pd.read_csv("data_jan_2026.csv")
            df['Hours_Worked'] = pd.to_numeric(df['Hours_Worked'], errors='coerce')
            df['Revenue_Generated'] = pd.to_numeric(df['Revenue_Generated'], errors='coerce')
            return df.dropna(subset=['Hours_Worked', 'Revenue_Generated'])
        except Exception as e:
            # Fallback to an empty schema if data generation hasn't run yet
            return pd.DataFrame(columns=['Client_Site', 'Hours_Worked', 'Revenue_Generated'])

    @output
    @render.text
    def render_revenue():
        df = processed_data()
        if df.empty: return "£0.00"
        return f"£{df['Revenue_Generated'].sum():,.2f}"

    @output
    @render.text
    def render_hours():
        df = processed_data()
        if df.empty: return "0.0 hrs"
        return f"{df['Hours_Worked'].sum():.1f} hrs"

    @output
    @render.text
    def render_yield():
        df = processed_data()
        if df.empty: return "£0.00 / hr"
        total_rev = df['Revenue_Generated'].sum()
        total_hrs = df['Hours_Worked'].sum()
        rate = total_rev / total_hrs if total_hrs > 0 else 0
        return f"£{rate:.2f} / hr"

    @output
    @render.plot
    def render_performance_chart():
        df = processed_data()
        if df.empty:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            return fig
            
        # Structural aggregation by customer profile site
        site_perf = df.groupby('Client_Site')['Revenue_Generated'].sum().sort_values(ascending=True)
        
        # Plotting layout logic matching dark theme aesthetics
        ax = site_perf.plot(kind='barh', color=['#fbbf24', '#60a5fa', '#34d399'], figsize=(10, 4))
        ax.set_facecolor('#1e293b')
        ax.figure.patch.set_facecolor('#1e293b')
        
        # Strip borders for professional scannability
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#475569')
        ax.spines['bottom'].set_color('#475569')
        
        ax.tick_params(colors='#94a3b8', labelsize=11)
        ax.set_xlabel("Revenue Generated (£)", color='#94a3b8', fontsize=11, labelpad=10)
        ax.set_ylabel("", color='#94a3b8')
        ax.grid(axis='x', color='#334155', linestyle='--', alpha=0.7)
        
        return ax.figure

app = App(app_ui, server)
