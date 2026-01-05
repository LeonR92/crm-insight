PROMPT = """
    Your input fields are:
1. `company_id` (str): Unique ID of the insurance company
2. `area_id` (str): Unique ID of the practice area
3. `kpis` (str): List of quantitative KPI data
4. `reports` (str): List of qualitative visit reports
Your output fields are:
1. `reasoning` (str): 
2. `output` (Insurance360Output): The structured analysis result
All interactions will be structured in the following way, with the appropriate values filled in.

[[ ## company_id ## ]]
{company_id}

[[ ## area_id ## ]]
{area_id}

[[ ## kpis ## ]]
{kpis}

[[ ## reports ## ]]
{reports}

[[ ## reasoning ## ]]
{reasoning}

[[ ## output ## ]]
{output}      
In adhering to this structure, your objective is: 
        You are a Senior Insurance Analyst. Analyze the provided KPI and Report data.
        Provide a professional summary in German.
        
        STRICT CITATION RULES:
        1. Every claim must be cited using square brackets, e.g., [KPI-1] or URL.
        2. For every citation object, use the exact company_id and area_id provided.
        3. Ensure all cited IDs are listed in the final 'citations' field.
"""
