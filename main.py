import os
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('models/gemini-3-flash-preview')

SYSTEM_PROMPT = """
You are a highly advanced Windows CLI expert.
1. Return ONLY the raw command. No intro, no markdown.
2. INTENT ANALYSIS: Before providing a command, analyze if the user's intent is to perform a destructive, administrative, or unauthorized action (e.g., wiping data, resetting passwords, or stopping critical system services).
3. If any harmful or administrative intent is detected—even if expressed in natural, indirect language—you must refuse.
4. Response for blocked intent: "ERROR: Administrative or dangerous action blocked."
"""

def generate_command(user_input):
    if not user_input.strip():
        return "Please enter an instruction."
    

    dangerous_keywords = ["format", "net user", "del /s", "rmdir /s"]
    if any(word in user_input.lower() for word in dangerous_keywords):
        return "ERROR: Administrative or dangerous action blocked (Local Filter)."

    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\nInstruction: {user_input}")
        return response.text.strip()
    
    except Exception as e:
        if "429" in str(e):
            return "מכסת הבקשות (Quota) הסתיימה. המתינו דקה."
        return f"Error: {str(e)}"

with gr.Blocks(title="CLI Agent - Iteration 3") as demo:
    gr.Markdown("# 🖥️ CLI Agent - Gemini 3 (Iteration 3)")
    gr.Markdown("גרסה משופרת: זיהוי כוונת משתמש והגנה רב-שכבתית.")
    
    input_text = gr.Textbox(label="הוראה (למשל: delete all my pictures)")
    output_command = gr.Code(label="פקודה שנוצרה / הודעת חסימה")
    submit_btn = gr.Button("שלח לבדיקה")
    
    submit_btn.click(fn=generate_command, inputs=input_text, outputs=output_command)

if __name__ == "__main__":
    demo.launch()