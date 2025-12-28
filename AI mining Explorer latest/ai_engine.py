import google.generativeai as genai

genai.configure(api_key="AIzaSyBKLjcytiYCosL0ZTePQSuwUjB0XL-DtDo")
model = genai.GenerativeModel("models/gemini-2.5-flash")

def generate_code(prompt, df_columns):
    system_prompt = (
        f"You are an assistant converting Excel-related natural language tasks into Python pandas code.\n"
        f"The dataframe is named 'df' and has these columns: {', '.join(df_columns)}.\n"
        
        f"Save any result in a variable called 'result'. "
        f"If plotting, use matplotlib and save the chart as 'chart.png'."
    )
    response = model.generate_content(f"{system_prompt}\n\nTask: {prompt}")
    code = response.text.strip()
    return code

