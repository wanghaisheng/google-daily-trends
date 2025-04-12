import pandas as pd
from pytrends.request import TrendReq
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time # To handle potential rate limits

# --- Configuration ---
load_dotenv() # Load variables from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found. Please set it in the .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# --- Parameters for Analysis ---
root_keyword = "AI resume builder"
competitor_keywords = ["Canva resume", "Zety", "Kickresume"] # Add relevant competitors
timeframe = 'today 5-y' # e.g., 'today 5-y', 'today 12-m', '2020-01-01 2023-12-31'
geo = 'US' # e.g., 'US', 'GB', '' for Worldwide
language = 'en-US'
category = 0 # 0 for all categories
gprop = '' # Search type: '', 'images', 'news', 'youtube', 'froogle' (Shopping)

# --- Helper Functions ---

def get_pytrends_data(keyword_list, timeframe, geo, cat=0, gprop='', hl='en-US'):
    """Fetches various Google Trends data points for a list of keywords."""
    pytrends = TrendReq(hl=hl, tz=360) # tz=360 for US timezone offset
    data = {}

    print(f"Fetching data for: {keyword_list}")

    try:
        # 1. Interest Over Time (handles single or multiple keywords)
        print(" -> Fetching Interest Over Time...")
        pytrends.build_payload(keyword_list, cat=cat, timeframe=timeframe, geo=geo, gprop=gprop)
        data['interest_over_time'] = pytrends.interest_over_time()
        time.sleep(1) # Be respectful of API rate limits

        # 2. Related Queries & Topics (only for the first keyword if multiple)
        root_kw = keyword_list[0]
        print(f" -> Fetching Related Queries for '{root_kw}'...")
        pytrends.build_payload([root_kw], cat=cat, timeframe=timeframe, geo=geo, gprop=gprop)
        related_queries_raw = pytrends.related_queries()
        # Check if the keyword exists in the returned dictionary
        if root_kw in related_queries_raw and related_queries_raw[root_kw]:
            data['related_queries'] = related_queries_raw[root_kw]
        else:
             data['related_queries'] = {'top': pd.DataFrame(), 'rising': pd.DataFrame()} # Empty structure
        time.sleep(1)

        print(f" -> Fetching Related Topics for '{root_kw}'...")
        # No need to rebuild payload if parameters are the same
        related_topics_raw = pytrends.related_topics()
        if root_kw in related_topics_raw and related_topics_raw[root_kw]:
             data['related_topics'] = related_topics_raw[root_kw]
        else:
            data['related_topics'] = {'top': pd.DataFrame(), 'rising': pd.DataFrame()} # Empty structure
        time.sleep(1)

    except Exception as e:
        print(f"Error fetching Pytrends data: {e}")
        # Return partial data if possible, or empty dict
        return data

    return data

def format_data_for_gemini(trends_data, root_kw, competitors):
    """Converts Pytrends data (DataFrames) into a string format for the Gemini prompt."""
    prompt_data = f"Analysis for Root Keyword: '{root_kw}'\n"
    prompt_data += f"Competitors Analyzed: {', '.join(competitors)}\n"
    prompt_data += f"Timeframe: {timeframe}, Geo: {geo}\n\n"

    # --- Interest Over Time (Root Keyword) ---
    if 'interest_over_time' in trends_data and not trends_data['interest_over_time'].empty:
        root_trend = trends_data['interest_over_time'][[root_kw]] # Select only root keyword column
        prompt_data += "--- Root Keyword Interest Over Time (Sample) ---\n"
        # Provide a summary or sample to avoid excessive length
        prompt_data += root_trend.tail().to_string() + "\n"
        prompt_data += f"(Trend data spans from {root_trend.index.min().date()} to {root_trend.index.max().date()})\n\n"
    else:
         prompt_data += "--- Root Keyword Interest Over Time ---\nNo data available.\n\n"


    # --- Related Queries ---
    prompt_data += "--- Related Queries (Especially 'Rising') ---\n"
    if 'related_queries' in trends_data:
        if not trends_data['related_queries']['rising'].empty:
            prompt_data += "**Rising Queries:**\n"
            prompt_data += trends_data['related_queries']['rising'].to_string(index=False) + "\n\n"
        else:
            prompt_data += "**Rising Queries:** None found.\n\n"
        if not trends_data['related_queries']['top'].empty:
            prompt_data += "**Top Queries:**\n"
            prompt_data += trends_data['related_queries']['top'].head().to_string(index=False) + "\n\n" # Show top few
        else:
            prompt_data += "**Top Queries:** None found.\n\n"
    else:
        prompt_data += "No related queries data available.\n\n"

    # --- Related Topics ---
    prompt_data += "--- Related Topics (Especially 'Rising') ---\n"
    if 'related_topics' in trends_data:
        if not trends_data['related_topics']['rising'].empty:
            prompt_data += "**Rising Topics:**\n"
            prompt_data += trends_data['related_topics']['rising'].to_string(index=False) + "\n\n"
        else:
            prompt_data += "**Rising Topics:** None found.\n\n"
        if not trends_data['related_topics']['top'].empty:
            prompt_data += "**Top Topics:**\n"
            prompt_data += trends_data['related_topics']['top'].head().to_string(index=False) + "\n\n" # Show top few
        else:
            prompt_data += "**Top Topics:** None found.\n\n"
    else:
        prompt_data += "No related topics data available.\n\n"

    # --- Competitor Comparison ---
    if 'interest_over_time' in trends_data and not trends_data['interest_over_time'].empty and competitors:
        comp_data = trends_data['interest_over_time'][[root_kw] + competitors]
        prompt_data += "--- Root Keyword vs. Competitor Interest Over Time (Sample) ---\n"
        prompt_data += comp_data.tail().to_string() + "\n"
        prompt_data += f"(Trend data spans from {comp_data.index.min().date()} to {comp_data.index.max().date()})\n\n"
    else:
         prompt_data += "--- Root Keyword vs. Competitor Interest Over Time ---\nNo comparison data available or no competitors specified.\n\n"


    return prompt_data

def analyze_with_gemini(prompt_text):
    """Sends the formatted data and analysis prompt to Gemini."""
    model = genai.GenerativeModel('gemini-1.5-flash') # Or other suitable model like 'gemini-pro'

    prompt = f"""
    You are an expert market analyst interpreting Google Trends data.
    Analyze the following data for the root keyword '{root_keyword}' and its competitors. Follow these steps rigorously:

    1.  **Root Keyword Trend Analysis:** Based on the 'Interest Over Time' data for '{root_keyword}', describe its overall trend. Is it growing, stable, declining, or seasonal? Mention any significant peaks or troughs.

    2.  **User Intent & Needs Analysis (Related Queries/Topics):**
        *   Examine the **'Rising' Related Queries**. What specific user needs, features (e.g., 'free', 'template', 'ATS'), pain points, or alternative tools/brands do these searches suggest? What is the underlying user intent?
        *   Examine the **'Rising' Related Topics**. What broader concepts, industries (e.g., 'Software', 'ATS'), or major competitor entities are strongly associated and currently growing in interest alongside '{root_keyword}'? How does this inform the market context?
        *   Briefly consider the 'Top' queries/topics for established, high-volume associations.

    3.  **Competitive Landscape Analysis:**
        *   Compare the 'Interest Over Time' trends of '{root_keyword}' against its competitors ({', '.join(competitor_keywords)}).
        *   Does the data suggest **Market Substitution** (i.e., '{root_keyword}' rising while competitors fall, or vice-versa)?
        *   Or does it suggest **Sector Expansion** (i.e., '{root_keyword}' and competitors generally rising together)?
        *   Comment on the relative popularity (search interest levels) between the root keyword and its main competitors based on the data.

    4.  **Synthesis & Opportunity Assessment:** Based on all the above points (trend, user intent, competition), provide a concise summary. What are the key market opportunities or potential risks for a product/service related to '{root_keyword}'? Highlight any unmet needs or potential differentiation points suggested by the data.

    **Here is the Google Trends Data:**

    {prompt_text}

    **Begin Analysis:**
    """

    print("\n--- Sending Data to Gemini for Analysis ---")
    try:
        response = model.generate_content(prompt)
        print("--- Analysis Received ---")
        # Basic check for safety flags, you might want more robust handling
        if not response.candidates:
             return "Analysis could not be generated (possibly due to safety settings or empty response)."
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"Error during Gemini analysis: {e}"

# --- Main Execution ---
if __name__ == "__main__":
    # Fetch data for root keyword and competitors together
    all_keywords = [root_keyword] + competitor_keywords
    trends_data = get_pytrends_data(all_keywords, timeframe, geo, cat=category, gprop=gprop, hl=language)

    if not trends_data:
        print("Failed to fetch sufficient data from Pytrends.")
    else:
        # Format data for the prompt
        formatted_prompt_data = format_data_for_gemini(trends_data, root_keyword, competitor_keywords)
        # print("\n--- Formatted Data for Gemini ---")
        # print(formatted_prompt_data) # Optional: print the data being sent

        # Get analysis from Gemini
        analysis_result = analyze_with_gemini(formatted_prompt_data)

        # Print the final analysis
        print("\n\n--- Google Trends Market Analysis (via Gemini) ---")
        print(f"Keyword: '{root_keyword}'")
        print(f"Competitors: {', '.join(competitor_keywords)}")
        print(f"Timeframe: {timeframe}, Geo: {geo}\n")
        print(analysis_result)
