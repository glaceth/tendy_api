import os
import openai
from typing import Dict, Any, Optional

def analyze_token_with_gpt(summary: str, evolution_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Analyze token data using GPT with optional evolution comparison.
    
    Args:
        summary: Current token data summary
        evolution_data: Dictionary containing evolution metrics between current and previous data
    
    Returns:
        GPT analysis string
    """
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return "⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=api_key)
        
        # Build the prompt with evolution data if available
        prompt = f"""
Analyze this cryptocurrency token based on the following data:

{summary}
"""
        
        if evolution_data:
            prompt += f"""

EVOLUTION DATA (Changes since last analysis):
"""
            for key, value in evolution_data.items():
                prompt += f"- {key}: {value}\n"
        
        prompt += """

Please provide a comprehensive analysis including:
1. Current market sentiment and outlook
2. Risk assessment based on the data
3. Key metrics analysis (market cap, holders, rugscore, etc.)
4. Evolution trends if provided
5. Investment recommendation (high risk, medium risk, low risk)

Keep the analysis concise but informative for Telegram messaging.
"""
        
        # Call GPT API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a cryptocurrency analyst expert. Provide clear, actionable analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"⚠️ Error analyzing token with GPT: {str(e)}"

def format_evolution_data(current_data: Dict[str, Any], previous_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format evolution data for GPT prompt.
    
    Args:
        current_data: Current token data
        previous_data: Previous token data
    
    Returns:
        Dictionary with formatted evolution strings
    """
    evolution = {}
    
    # Market Cap evolution
    if 'mc' in current_data and 'mc' in previous_data:
        try:
            current_mc = float(current_data['mc'])
            previous_mc = float(previous_data['mc'])
            change = current_mc - previous_mc
            change_pct = (change / previous_mc) * 100 if previous_mc > 0 else 0
            evolution['Market Cap'] = f"${previous_mc:,.0f} → ${current_mc:,.0f} ({change_pct:+.1f}%)"
        except (ValueError, TypeError):
            evolution['Market Cap'] = "Data parsing error"
    
    # Holders evolution
    if 'holders' in current_data and 'holders' in previous_data:
        try:
            current_holders = int(current_data['holders'])
            previous_holders = int(previous_data['holders'])
            change = current_holders - previous_holders
            change_pct = (change / previous_holders) * 100 if previous_holders > 0 else 0
            evolution['Holders'] = f"{previous_holders:,} → {current_holders:,} ({change_pct:+.1f}%)"
        except (ValueError, TypeError):
            evolution['Holders'] = "Data parsing error"
    
    # Rugscore evolution
    if 'rugscore' in current_data and 'rugscore' in previous_data:
        try:
            current_score = float(current_data['rugscore'])
            previous_score = float(previous_data['rugscore'])
            change = current_score - previous_score
            evolution['Rug Score'] = f"{previous_score:.1f} → {current_score:.1f} ({change:+.1f})"
        except (ValueError, TypeError):
            evolution['Rug Score'] = "Data parsing error"
    
    # Time elapsed
    if 'timestamp' in current_data and 'timestamp' in previous_data:
        try:
            current_time = current_data['timestamp']
            previous_time = previous_data['timestamp']
            evolution['Time Elapsed'] = f"Last update: {previous_time} → Current: {current_time}"
        except (ValueError, TypeError):
            evolution['Time Elapsed'] = "Timestamp parsing error"
    
    return evolution