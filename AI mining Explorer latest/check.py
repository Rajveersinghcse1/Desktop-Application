import streamlit as st
import pandas as pd
import numpy as np
import re
from io import BytesIO
import base64
from typing import Optional, Union, Dict, Any

# Configure page
st.set_page_config(
    page_title="💡 AI Excel Assistant", 
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4361ee;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .error-message {
        background-color: #ffebee;
        border-left-color: #f44336;
        color: #c62828;
    }
    
    
    
    .dataframe-container {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .highlight-info {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

class ExcelAssistantApp:
    def __init__(self):
        """Initialize the Excel Assistant application."""
        self.predefined_prompts = [
            "Show Data",
            "Show all rows where Salary > 50000",
            "Highlight rows where Age > 30",
            "Show rows where Department equals 'Engineering'",
            "Find all rows where values are above average",
            "Identify and highlight outliers in the data",
            "Highlight duplicate records",
            "Show rows with missing values",
            "Highlight top 10 records by value",
            "Compare different groups and highlight differences",
            "Highlight rows where multiple conditions are met"
        ]
        
        # Initialize session state
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'df' not in st.session_state:
            st.session_state.df = None
        if 'styled_df' not in st.session_state:
            st.session_state.styled_df = None
        if 'last_highlight_info' not in st.session_state:
            st.session_state.last_highlight_info = ""

    def add_to_chat(self, message: str, message_type: str = "normal"):
        """Add message to chat history."""
        st.session_state.chat_history.append({
            'message': message,
            'type': message_type
        })

    def display_chat_history(self):
        """Display chat history with proper styling."""
        if st.session_state.chat_history:
            st.subheader("💬 Conversation History")
            for chat in st.session_state.chat_history:
                css_class = f"chat-message {chat['type']}-message" if chat['type'] != "normal" else "chat-message"
                st.markdown(f'<div class="{css_class}">{chat["message"]}</div>', unsafe_allow_html=True)

    def load_excel_file(self, uploaded_file) -> Optional[pd.DataFrame]:
        """Load Excel file and return DataFrame."""
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.xls'):
                df = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                raise ValueError("Unsupported file format")
            
            self.add_to_chat(f"✅ Excel file '{uploaded_file.name}' loaded successfully.", "success")
            self.add_to_chat(f"📊 Data shape: {df.shape[0]} rows, {df.shape[1]} columns", "success")
            return df
        except Exception as e:
            self.add_to_chat(f"❌ Error loading file: {str(e)}", "error")
            return None

    def generate_code_from_prompt(self, prompt: str, columns: list) -> str:
        """Generate pandas code based on user prompt."""
        prompt_lower = prompt.lower()
        
        # Basic show data
        if "show data" in prompt_lower:
            return "df.head(20)"
        
        # Handle highlighting conditions
        highlight_patterns = [
            (r"highlight.*where\s+(.*)", "highlight_condition"),
            (r"highlight.*rows.*where\s+(.*)", "highlight_condition"),
            (r"highlight.*(top|bottom)\s+(\d+)", "highlight_top_bottom"),
            (r"highlight.*outlier", "highlight_outliers"),
            (r"highlight.*duplicate", "highlight_duplicates"),
            (r"highlight.*missing", "highlight_missing"),
            (r"highlight.*above.*average", "highlight_above_average")
        ]
        
        for pattern, action_type in highlight_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                if action_type == "highlight_condition":
                    condition = match.group(1).strip()
                    return f"highlight_condition(df, '{condition}')"
                elif action_type == "highlight_top_bottom":
                    direction = match.group(1)
                    n = match.group(2)
                    return f"highlight_top_n(df, {n}, ascending={'True' if direction == 'bottom' else 'False'})"
                elif action_type == "highlight_outliers":
                    return "highlight_outliers(df)"
                elif action_type == "highlight_duplicates":
                    return "highlight_duplicates(df)"
                elif action_type == "highlight_missing":
                    return "highlight_missing_values(df)"
                elif action_type == "highlight_above_average":
                    return "highlight_above_average(df)"
        
        # Handle show/filter conditions
        show_patterns = [
            (r"show.*where\s+(.*)", "filter_condition"),
            (r"find.*where\s+(.*)", "filter_condition"),
            (r"filter.*where\s+(.*)", "filter_condition")
        ]
        
        for pattern, action_type in show_patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                condition = match.group(1).strip()
                return f"filter_dataframe(df, '{condition}')"
        
        # Default case
        return "df.head(10)"

    def highlight_condition(self, df: pd.DataFrame, condition: str) -> pd.DataFrame.style:
        """Highlight rows based on condition."""
        try:
            # Parse common conditions
            condition = condition.replace(" equals ", " == ").replace(" equal ", " == ")
            condition = condition.replace(" greater than ", " > ").replace(" less than ", " < ")
            condition = condition.replace(" >= ", " >= ").replace(" <= ", " <= ")
            
            # Handle string conditions
            if "==" in condition and not condition.count("'") >= 2:
                parts = condition.split("==")
                if len(parts) == 2:
                    col_name = parts[0].strip()
                    value = parts[1].strip()
                    if not (value.startswith("'") and value.endswith("'")):
                        condition = f"{col_name} == '{value}'"
            
            # Create boolean mask
            mask = df.eval(condition)
            highlight_count = mask.sum()
            
            st.session_state.last_highlight_info = f"🎯 Highlighted {highlight_count} rows matching condition: {condition}"
            
            def highlight_rows(row):
                return ['background-color: #ffeb3b; color: #000;' if mask[row.name] else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error in condition: {str(e)}")
            return df.style

    def highlight_top_n(self, df: pd.DataFrame, n: int, ascending: bool = False) -> pd.DataFrame.style:
        """Highlight top/bottom N rows."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                st.warning("No numeric columns found for ranking")
                return df.style
            
            # Use first numeric column for ranking
            sort_col = numeric_cols[0]
            sorted_indices = df[sort_col].nlargest(n).index if not ascending else df[sort_col].nsmallest(n).index
            
            direction = "bottom" if ascending else "top"
            st.session_state.last_highlight_info = f"🎯 Highlighted {direction} {n} rows by {sort_col}"
            
            def highlight_rows(row):
                return ['background-color: #4caf50; color: white;' if row.name in sorted_indices else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error highlighting top/bottom rows: {str(e)}")
            return df.style

    def highlight_outliers(self, df: pd.DataFrame) -> pd.DataFrame.style:
        """Highlight outlier rows using IQR method."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                st.warning("No numeric columns found for outlier detection")
                return df.style
            
            outlier_mask = pd.Series(False, index=df.index)
            
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask |= (df[col] < lower_bound) | (df[col] > upper_bound)
            
            outlier_count = outlier_mask.sum()
            st.session_state.last_highlight_info = f"🎯 Highlighted {outlier_count} outlier rows"
            
            def highlight_rows(row):
                return ['background-color: #f44336; color: white;' if outlier_mask[row.name] else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error detecting outliers: {str(e)}")
            return df.style

    def highlight_duplicates(self, df: pd.DataFrame) -> pd.DataFrame.style:
        """Highlight duplicate rows."""
        try:
            duplicate_mask = df.duplicated(keep=False)
            duplicate_count = duplicate_mask.sum()
            
            st.session_state.last_highlight_info = f"🎯 Highlighted {duplicate_count} duplicate rows"
            
            def highlight_rows(row):
                return ['background-color: #ff9800; color: white;' if duplicate_mask[row.name] else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error highlighting duplicates: {str(e)}")
            return df.style

    def highlight_missing_values(self, df: pd.DataFrame) -> pd.DataFrame.style:
        """Highlight rows with missing values."""
        try:
            missing_mask = df.isnull().any(axis=1)
            missing_count = missing_mask.sum()
            
            st.session_state.last_highlight_info = f"🎯 Highlighted {missing_count} rows with missing values"
            
            def highlight_rows(row):
                return ['background-color: #9c27b0; color: white;' if missing_mask[row.name] else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error highlighting missing values: {str(e)}")
            return df.style

    def highlight_above_average(self, df: pd.DataFrame) -> pd.DataFrame.style:
        """Highlight rows where numeric values are above average."""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                st.warning("No numeric columns found")
                return df.style
            
            above_avg_mask = pd.Series(False, index=df.index)
            
            for col in numeric_cols:
                avg_val = df[col].mean()
                above_avg_mask |= df[col] > avg_val
            
            above_avg_count = above_avg_mask.sum()
            st.session_state.last_highlight_info = f"🎯 Highlighted {above_avg_count} rows with above-average values"
            
            def highlight_rows(row):
                return ['background-color: #2196f3; color: white;' if above_avg_mask[row.name] else '' for _ in row]
            
            return df.style.apply(highlight_rows, axis=1)
            
        except Exception as e:
            st.error(f"Error highlighting above average: {str(e)}")
            return df.style

    def filter_dataframe(self, df: pd.DataFrame, condition: str) -> pd.DataFrame:
        """Filter dataframe based on condition."""
        try:
            # Parse common conditions
            condition = condition.replace(" equals ", " == ").replace(" equal ", " == ")
            condition = condition.replace(" greater than ", " > ").replace(" less than ", " < ")
            
            # Handle string conditions
            if "==" in condition and not condition.count("'") >= 2:
                parts = condition.split("==")
                if len(parts) == 2:
                    col_name = parts[0].strip()
                    value = parts[1].strip()
                    if not (value.startswith("'") and value.endswith("'")):
                        condition = f"{col_name} == '{value}'"
            
            filtered_df = df.query(condition)
            st.session_state.last_highlight_info = f"📊 Filtered to {len(filtered_df)} rows matching: {condition}"
            return filtered_df
            
        except Exception as e:
            st.error(f"Error filtering data: {str(e)}")
            return df

    def execute_generated_code(self, df: pd.DataFrame, code: str) -> Union[pd.DataFrame, pd.DataFrame.style]:
        """Execute generated code safely."""
        try:
            # Create safe execution environment
            safe_globals = {
                'df': df,
                'pd': pd,
                'np': np,
                'highlight_condition': self.highlight_condition,
                'highlight_top_n': self.highlight_top_n,
                'highlight_outliers': self.highlight_outliers,
                'highlight_duplicates': self.highlight_duplicates,
                'highlight_missing_values': self.highlight_missing_values,
                'highlight_above_average': self.highlight_above_average,
                'filter_dataframe': self.filter_dataframe
            }
            
            result = eval(code, safe_globals)
            return result
            
        except Exception as e:
            st.error(f"Execution error: {str(e)}")
            return df

    def download_dataframe(self, df: pd.DataFrame, filename: str = "data.xlsx"):
        """Create download link for DataFrame."""
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        b64 = base64.b64encode(output.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">📥 Download Excel File</a>'
        return href

    def run(self):
        """Main application logic."""
        # Header
        st.markdown('<h1 class="main-header">💡 AI Excel Assistant</h1>', unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.header("📂 File Upload")
            uploaded_file = st.file_uploader(
                "Choose an Excel file",
                type=['xlsx', 'xls'],
                help="Upload your Excel file to get started"
            )
            
            if uploaded_file is not None:
                st.session_state.df = self.load_excel_file(uploaded_file)
            
            st.markdown("---")
            
            # Predefined prompts
            st.header("📋 Quick Prompts")
            selected_prompt = st.selectbox(
                "Choose a predefined prompt:",
                [""] + self.predefined_prompts,
                help="Select a common prompt or create your own"
            )
            
            if st.button("Use Selected Prompt") and selected_prompt:
                st.session_state.user_input = selected_prompt
            
            st.markdown("---")
            
            # Help section
            with st.expander("💡 Help & Examples"):
                st.markdown("""
                **Highlighting Examples:**
                - `Highlight rows where Age > 30`
                - `Highlight top 10 records`
                - `Highlight outliers in the data`
                - `Highlight duplicate records`
                - `Highlight rows with missing values`
                
                **Filtering Examples:**
                - `Show rows where Salary > 50000`
                - `Find rows where Department equals Engineering`
                - `Filter where Status == Active`
                """)

        # Main content area
        if st.session_state.df is not None:
            # Data overview
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Rows", st.session_state.df.shape[0])
            with col2:
                st.metric("📋 Total Columns", st.session_state.df.shape[1])
            with col3:
                st.metric("💾 Data Size", f"{st.session_state.df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            st.markdown("---")
            
            # Input area
            st.subheader("💬 Ask a Question")
            user_input = st.text_input(
                "Enter your prompt:",
                key="user_input",
                placeholder="e.g., 'Highlight rows where Salary > 50000'"
            )
            
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🚀 Send", type="primary"):
                    if user_input:
                        self.process_prompt(user_input)
            
            # Display chat history
            self.display_chat_history()
            
            # Display results
            if st.session_state.styled_df is not None:
                st.markdown("---")
                st.subheader("📊 Results")
                
                # Show highlight info if available
                if st.session_state.last_highlight_info:
                    st.markdown(f'<div class="highlight-info">{st.session_state.last_highlight_info}</div>', 
                              unsafe_allow_html=True)
                
                # Display styled dataframe
                st.dataframe(st.session_state.styled_df, use_container_width=True, height=400)
                
                # Download button
                if hasattr(st.session_state.styled_df, 'data'):
                    download_link = self.download_dataframe(st.session_state.styled_df.data)
                    st.markdown(download_link, unsafe_allow_html=True)
        else:
            # Welcome message
            st.info("👋 Welcome! Please upload an Excel file to get started.")
            
            # Sample data for demo
            if st.button("🎲 Try with Sample Data"):
                sample_data = {
                    'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
                    'Age': [25, 30, 35, 28, 32],
                    'Salary': [50000, 60000, 75000, 55000, 70000],
                    'Department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'Marketing']
                }
                st.session_state.df = pd.DataFrame(sample_data)
                self.add_to_chat("✅ Sample data loaded successfully.", "success")
                st.rerun()

    def process_prompt(self, prompt: str):
        """Process user prompt and generate results."""
        self.add_to_chat(f">>> {prompt}", "user")
        
        try:
            # Generate code from prompt
            code = self.generate_code_from_prompt(prompt, st.session_state.df.columns.tolist())
            
            # Execute code
            result = self.execute_generated_code(st.session_state.df, code)
            
            if isinstance(result, pd.DataFrame):
                st.session_state.styled_df = result.style
                self.add_to_chat(f"💬 Showing {len(result)} rows", "success")
            elif hasattr(result, 'data'):  # Styled DataFrame
                st.session_state.styled_df = result
                self.add_to_chat("💬 Data highlighted based on your criteria", "success")
            else:
                st.session_state.styled_df = pd.DataFrame([{"Result": str(result)}]).style
                self.add_to_chat(f"💬 Result: {result}", "success")
                
        except Exception as e:
            self.add_to_chat(f"❌ Error: {str(e)}", "error")


# Initialize and run the app
if __name__ == "__main__":
    app = ExcelAssistantApp()
    app.run()