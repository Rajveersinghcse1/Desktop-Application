import matplotlib.pyplot as plt

def run_generated_code(df, code):
    if code.startswith("```") and code.endswith("```"):
        code = "\n".join(code.split("\n")[1:-1])

    local_vars = {"df": df.copy(), "plt": plt, "result": None}
    try:
        exec(code, {}, local_vars)
        return local_vars.get("result", "⚠️ No result variable assigned.")
    except Exception as e:
        return f"❌ Error: {e}"
