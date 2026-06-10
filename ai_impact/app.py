import json
from flask import Flask, render_template
import pandas as pd
import numpy as np

# Create Flask app
app = Flask(__name__)

# Load dataset
df = pd.read_csv('data.csv')

# Helper to serialize pandas series/dataframes for templates
def to_dict_list(df_or_series):
    if isinstance(df_or_series, pd.Series):
        return [{"key": str(k), "value": float(v) if not pd.isna(v) else 0.0} for k, v in df_or_series.items()]
    elif isinstance(df_or_series, pd.DataFrame):
        return df_or_series.reset_index().to_dict(orient='records')
    return []

# Helper to convert df to styled HTML table
def to_styled_html(df_input):
    return df_input.reset_index().to_html(
        classes="table table-hover table-striped",
        index=False,
        border=0
    )

@app.route('/')
def home():
    # Overview statistics
    total_records = len(df)
    unique_jobs = df['Job_Title'].nunique()
    unique_industries = df['Industry'].nunique()
    avg_salary = df['Average_Salary_USD'].mean()
    
    # AI Risk High-level
    job_industry_replaced = df.sort_values('AI_Replacement_Risk', ascending=False)
    highest_risk_job = job_industry_replaced.iloc[0]['Job_Title']
    highest_risk_industry = job_industry_replaced.iloc[0]['Industry']
    highest_risk_val = job_industry_replaced.iloc[0]['AI_Replacement_Risk']
    
    # Future Demand High-level
    future_market = df.sort_values('Future_Demand_Score', ascending=False)
    highest_demand_job = future_market.iloc[0]['Job_Title']
    highest_demand_industry = future_market.iloc[0]['Industry']
    highest_demand_val = future_market.iloc[0]['Future_Demand_Score']

    # Overview table
    top_3_risk = job_industry_replaced.head(3)[['Job_Title', "Industry", "AI_Replacement_Risk"]]
    top_3_demand = future_market.head(3)[['Job_Title', "Industry", "Future_Demand_Score"]]

    overview_data = {
        'total_records': total_records,
        'unique_jobs': unique_jobs,
        'unique_industries': unique_industries,
        'avg_salary': round(avg_salary, 2),
        'highest_risk_job': highest_risk_job,
        'highest_risk_industry': highest_risk_industry,
        'highest_risk_val': round(highest_risk_val * 100, 1) if highest_risk_val <= 1.0 else round(highest_risk_val, 1),
        'highest_demand_job': highest_demand_job,
        'highest_demand_industry': highest_demand_industry,
        'highest_demand_val': round(highest_demand_val, 1),
        'top_3_risk_html': to_styled_html(top_3_risk),
        'top_3_demand_html': to_styled_html(top_3_demand)
    }
    
    return render_template('index.html', overview=overview_data)

@app.route('/ai_risk')
def ai_risk():
    # 1. Job Title average risk
    job_ai_risk = df.groupby('Job_Title')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 2. Industry average risk
    industry_ai_risk = df.groupby('Industry')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 3. Remote vs Office risk
    remote_ai_risk = df.groupby('Remote_Work_Possibility')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    
    # 4. Finance industry specific
    df_finance = df[df['Industry'] == 'Finance']
    finance_job_risk = df_finance.groupby('Job_Title')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    finance_country_risk = df_finance.groupby('Country')['AI_Replacement_Risk'].mean().sort_values(ascending=False)

    # Convert to HTML tables
    tables = {
        'job_ai_risk_html': to_styled_html(job_ai_risk.to_frame('Average AI Risk')),
        'industry_ai_risk_html': to_styled_html(industry_ai_risk.to_frame('Average AI Risk')),
        'finance_job_risk_html': to_styled_html(finance_job_risk.to_frame('Finance Job AI Risk')),
        'finance_country_risk_html': to_styled_html(finance_country_risk.to_frame('Finance Country AI Risk'))
    }

    # Convert to Chart Data
    chart_data = {
        'jobs_labels': list(job_ai_risk.index),
        'jobs_values': [round(float(v), 3) for v in job_ai_risk.values],
        'industries_labels': list(industry_ai_risk.index),
        'industries_values': [round(float(v), 3) for v in industry_ai_risk.values],
        'remote_labels': list(remote_ai_risk.index),
        'remote_values': [round(float(v), 3) for v in remote_ai_risk.values]
    }

    return render_template('ai_risk.html', tables=tables, chart_data=chart_data)

@app.route('/future_demand')
def future_demand():
    # 1. Job Title average future demand
    job_demand = df.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 2. Industry average future demand
    industry_demand = df.groupby('Industry')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 3. Best growing roles (Hiring_Trend_2026 == 'Growing')
    df_growing = df[df['Hiring_Trend_2026'] == 'Growing']
    growing_job_demand = df_growing.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)
    
    # 4. Software developer demand by country
    df_sd = df[df['Job_Title'] == 'Software Developer']
    sd_country_demand = df_sd.groupby('Country')['Future_Demand_Score'].mean().sort_values(ascending=False)
    
    # 5. Government demand by country
    df_gov = df[df['Industry'] == 'Government']
    gov_country_demand = df_gov.groupby('Country')['Future_Demand_Score'].mean().sort_values(ascending=False)

    tables = {
        'job_demand_html': to_styled_html(job_demand.to_frame('Average Future Demand')),
        'industry_demand_html': to_styled_html(industry_demand.to_frame('Average Future Demand')),
        'growing_job_demand_html': to_styled_html(growing_job_demand.to_frame('Growing Jobs Demand Score')),
        'sd_country_demand_html': to_styled_html(sd_country_demand.to_frame('Software Dev Demand')),
        'gov_country_demand_html': to_styled_html(gov_country_demand.to_frame('Gov Sector Demand'))
    }

    chart_data = {
        'jobs_labels': list(job_demand.index),
        'jobs_values': [round(float(v), 1) for v in job_demand.values],
        'industries_labels': list(industry_demand.index),
        'industries_values': [round(float(v), 1) for v in industry_demand.values],
        'growing_labels': list(growing_job_demand.index),
        'growing_values': [round(float(v), 1) for v in growing_job_demand.values]
    }

    return render_template('future_demand.html', tables=tables, chart_data=chart_data)

@app.route('/pakistan')
def pakistan():
    # Filter for Pakistan
    df_pak = df[df['Country'] == 'Pakistan']
    
    # 1. Job Title average risk in Pakistan
    pak_job_risk = df_pak.groupby('Job_Title')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 2. Industry average risk in Pakistan
    pak_ind_risk = df_pak.groupby('Industry')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 3. Top 3 records
    pak_top_3 = df_pak.sort_values('AI_Replacement_Risk', ascending=False).head(3)[['Job_Title', 'Industry', 'AI_Replacement_Risk']]
    
    # 4. Future demand by job title
    pak_job_demand = df_pak.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 5. Financial Analyst demand by industry in Pakistan
    df_pak_fa = df_pak[df_pak['Job_Title'] == 'Financial Analyst']
    pak_fa_demand = df_pak_fa.groupby('Industry')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 6. High demand industry overall in Pakistan
    pak_ind_demand = df_pak.groupby('Industry')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 7. Healthcare industry demand by job title in Pakistan
    df_pak_hc = df_pak[df_pak['Industry'] == 'Healthcare']
    pak_hc_demand = df_pak_hc.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)

    tables = {
        'pak_job_risk_html': to_styled_html(pak_job_risk.to_frame('AI Replacement Risk')),
        'pak_ind_risk_html': to_styled_html(pak_ind_risk.to_frame('AI Replacement Risk')),
        'pak_top_3_html': to_styled_html(pak_top_3),
        'pak_job_demand_html': to_styled_html(pak_job_demand.to_frame('Future Demand Score')),
        'pak_fa_demand_html': to_styled_html(pak_fa_demand.to_frame('Financial Analyst Demand')),
        'pak_ind_demand_html': to_styled_html(pak_ind_demand.to_frame('Future Demand Score')),
        'pak_hc_demand_html': to_styled_html(pak_hc_demand.to_frame('Healthcare Job Demand'))
    }

    chart_data = {
        'job_risk_labels': list(pak_job_risk.index),
        'job_risk_values': [round(float(v), 3) for v in pak_job_risk.values],
        'ind_risk_labels': list(pak_ind_risk.index),
        'ind_risk_values': [round(float(v), 3) for v in pak_ind_risk.values],
        'job_demand_labels': list(pak_job_demand.index),
        'job_demand_values': [round(float(v), 1) for v in pak_job_demand.values],
        'ind_demand_labels': list(pak_ind_demand.index),
        'ind_demand_values': [round(float(v), 1) for v in pak_ind_demand.values]
    }

    return render_template('pakistan.html', tables=tables, chart_data=chart_data)

@app.route('/india')
def india():
    # Filter for India
    df_ind = df[df['Country'] == 'India']
    
    # 1. Job Title average risk in India
    ind_job_risk = df_ind.groupby('Job_Title')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 2. Data Engineer job risk by industry in India
    df_ind_de = df_ind[df_ind['Job_Title'] == 'Data Engineer']
    ind_de_risk = df_ind_de.groupby('Industry')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 3. Industry risk in India
    ind_ind_risk = df_ind.groupby('Industry')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    # 4. Transportation industry jobs risk in India
    df_ind_trans = df_ind[df_ind['Industry'] == 'Transportation']
    ind_trans_job_risk = df_ind_trans.groupby('Job_Title')['AI_Replacement_Risk'].mean().sort_values(ascending=False)
    
    # 5. Future demand jobs
    ind_top_demand_raw = df_ind.sort_values('Future_Demand_Score', ascending=False).head(5)[['Job_Title', 'Industry', 'Future_Demand_Score']]
    ind_job_demand = df_ind.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 6. Product manager demand by industry in India
    df_ind_pm = df_ind[df_ind['Job_Title'] == 'Product Manager']
    ind_pm_demand = df_ind_pm.groupby('Industry')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 7. Industry demand overall in India
    ind_ind_demand = df_ind.groupby('Industry')['Future_Demand_Score'].mean().sort_values(ascending=False)
    # 8. Healthcare demand jobs in India
    df_ind_hc = df_ind[df_ind['Industry'] == 'Healthcare']
    ind_hc_demand = df_ind_hc.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)
    
    # 9. Working hours by Job Title and Industry in India
    ind_job_hours = df_ind.groupby('Job_Title')['Work_Hours_Per_Week'].mean().sort_values(ascending=False)
    ind_ind_hours = df_ind.groupby('Industry')['Work_Hours_Per_Week'].mean().sort_values(ascending=False)
    
    # 10. Remote vs Office Job Satisfaction
    ind_remote_yes = df_ind[df_ind['Remote_Work_Possibility'] == 'Yes']
    ind_remote_no = df_ind[df_ind['Remote_Work_Possibility'] == 'No']
    remote_satisfaction_sum = int(ind_remote_yes['Job_Satisfaction'].sum())
    office_satisfaction_sum = int(ind_remote_no['Job_Satisfaction'].sum())
    remote_satisfaction_avg = round(float(ind_remote_yes['Job_Satisfaction'].mean()), 2) if len(ind_remote_yes) > 0 else 0
    office_satisfaction_avg = round(float(ind_remote_no['Job_Satisfaction'].mean()), 2) if len(ind_remote_no) > 0 else 0
    
    # 11. Satisfaction by Job Title in India
    ind_job_satisfaction = df_ind.groupby('Job_Title')['Job_Satisfaction'].mean().sort_values(ascending=False)
    # 12. Growing jobs demand in India
    df_ind_growing = df_ind[df_ind['Hiring_Trend_2026'] == 'Growing']
    ind_growing_job_demand = df_ind_growing.groupby('Job_Title')['Future_Demand_Score'].mean().sort_values(ascending=False)

    tables = {
        'ind_job_risk_html': to_styled_html(ind_job_risk.to_frame('AI Replacement Risk')),
        'ind_de_risk_html': to_styled_html(ind_de_risk.to_frame('Data Engineer AI Risk')),
        'ind_ind_risk_html': to_styled_html(ind_ind_risk.to_frame('AI Replacement Risk')),
        'ind_trans_job_risk_html': to_styled_html(ind_trans_job_risk.to_frame('Transportation Job Risk')),
        'ind_top_demand_html': to_styled_html(ind_top_demand_raw),
        'ind_job_demand_html': to_styled_html(ind_job_demand.to_frame('Future Demand Score')),
        'ind_pm_demand_html': to_styled_html(ind_pm_demand.to_frame('Product Manager Demand')),
        'ind_ind_demand_html': to_styled_html(ind_ind_demand.to_frame('Future Demand Score')),
        'ind_hc_demand_html': to_styled_html(ind_hc_demand.to_frame('Healthcare Job Demand')),
        'ind_job_hours_html': to_styled_html(ind_job_hours.to_frame('Avg Hours/Week')),
        'ind_ind_hours_html': to_styled_html(ind_ind_hours.to_frame('Avg Hours/Week')),
        'ind_job_sat_html': to_styled_html(ind_job_satisfaction.to_frame('Avg Job Satisfaction')),
        'ind_growing_job_demand_html': to_styled_html(ind_growing_job_demand.to_frame('Growing Job Demand'))
    }

    chart_data = {
        'job_risk_labels': list(ind_job_risk.index),
        'job_risk_values': [round(float(v), 3) for v in ind_job_risk.values],
        'ind_risk_labels': list(ind_ind_risk.index),
        'ind_risk_values': [round(float(v), 3) for v in ind_ind_risk.values],
        'job_demand_labels': list(ind_job_demand.index),
        'job_demand_values': [round(float(v), 1) for v in ind_job_demand.values],
        'remote_satisfaction': [remote_satisfaction_sum, office_satisfaction_sum],
        'remote_satisfaction_avg': [remote_satisfaction_avg, office_satisfaction_avg],
        'job_sat_labels': list(ind_job_satisfaction.index),
        'job_sat_values': [round(float(v), 2) for v in ind_job_satisfaction.values]
    }

    return render_template('india.html', tables=tables, chart_data=chart_data)

@app.route('/column_relationship')
def column_relationship():
    # 1. Salary vs Job Satisfaction (Scatter plot)
    # To keep payload light, let's take a representative sample of up to 1000 records
    sample_size = min(1000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    scatter_data = [{"x": float(row['Average_Salary_USD']), "y": float(row['Job_Satisfaction']), "label": str(row['Job_Title'])} for _, row in df_sample.iterrows()]
    
    # 2. Upskilling Needed vs AI Tool Usage
    upskilling_yes = df[df['Upskilling_Needed'] == 'Yes']['AI_Tool_Usage'].value_counts()
    upskilling_no = df[df['Upskilling_Needed'] == 'No']['AI_Tool_Usage'].value_counts()
    
    tool_usage_categories = list(set(upskilling_yes.index).union(set(upskilling_no.index)))
    upskilling_yes_counts = [int(upskilling_yes.get(cat, 0)) for cat in tool_usage_categories]
    upskilling_no_counts = [int(upskilling_no.get(cat, 0)) for cat in tool_usage_categories]
    
    # 3. Remote vs Satisfaction / Salary in whole world
    remote_satisfaction_sum_yes = int(df[df['Remote_Work_Possibility'] == 'Yes']['Job_Satisfaction'].sum())
    remote_satisfaction_sum_no = int(df[df['Remote_Work_Possibility'] == 'No']['Job_Satisfaction'].sum())
    remote_satisfaction_avg_yes = round(float(df[df['Remote_Work_Possibility'] == 'Yes']['Job_Satisfaction'].mean()), 2)
    remote_satisfaction_avg_no = round(float(df[df['Remote_Work_Possibility'] == 'No']['Job_Satisfaction'].mean()), 2)
    
    remote_salary_avg_yes = round(float(df[df['Remote_Work_Possibility'] == 'Yes']['Average_Salary_USD'].mean()), 2)
    remote_salary_avg_no = round(float(df[df['Remote_Work_Possibility'] == 'No']['Average_Salary_USD'].mean()), 2)
    
    # 4. Work hours per week globally
    global_job_hours = df.groupby('Job_Title')['Work_Hours_Per_Week'].mean().sort_values(ascending=False)
    global_ind_hours = df.groupby('Industry')['Work_Hours_Per_Week'].mean().sort_values(ascending=False)

    tables = {
        'global_job_hours_html': to_styled_html(global_job_hours.to_frame('Avg Hours/Week')),
        'global_ind_hours_html': to_styled_html(global_ind_hours.to_frame('Avg Hours/Week'))
    }

    chart_data = {
        'scatter_points': scatter_data,
        'tool_categories': tool_usage_categories,
        'upskilling_yes': upskilling_yes_counts,
        'upskilling_no': upskilling_no_counts,
        'remote_satisfaction_sum': [remote_satisfaction_sum_yes, remote_satisfaction_sum_no],
        'remote_satisfaction_avg': [remote_satisfaction_avg_yes, remote_satisfaction_avg_no],
        'remote_salary_avg': [remote_salary_avg_yes, remote_salary_avg_no],
        'job_hours_labels': list(global_job_hours.index),
        'job_hours_values': [round(float(v), 1) for v in global_job_hours.values],
        'ind_hours_labels': list(global_ind_hours.index),
        'ind_hours_values': [round(float(v), 1) for v in global_ind_hours.values],
    }

    return render_template('column_relationship.html', tables=tables, chart_data=chart_data)

if __name__ == "__main__":
    app.run(debug=True)