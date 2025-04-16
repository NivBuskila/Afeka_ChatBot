#!/usr/bin/env python
"""
ממשק צ'אט פשוט עם חיבור ל-Gemini API
מבוסס על tkinter

הפעלה: python simple_chat.py
"""
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from google import genai

# הגדרת הסגנון
BG_COLOR = "#343541"
TEXT_COLOR = "#FFFFFF"
GEMINI_COLOR = "#10a37f"
USER_COLOR = "#4169E1"
INPUT_BG = "#40414f"
BUTTON_BG = "#10a37f"
BUTTON_FG = "#FFFFFF"
FONT = ("Segoe UI", 10)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chat Bot")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("700x600")
        
        # קבלת מפתח ה-API
        self.api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyBBw-VlqWekqnd_vPXCS7LSuKfrkbOro7s')
        
        # יצירת מופע Client
        try:
            self.genai_client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-2.0-flash"
        except Exception as e:
            messagebox.showerror("שגיאת התחברות", f"שגיאה ביצירת חיבור ל-Gemini: {str(e)}")
            root.destroy()
            return
            
        # יצירת הרכיבים הגרפיים
        self.create_widgets()
        
        # בדיקת חיבור ראשונית
        self.check_connection()
    
    def create_widgets(self):
        # מסך הצ'אט
        self.chat_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.chat_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # כותרת
        self.title_label = tk.Label(
            self.chat_frame, 
            text="שיחה עם ג'מיני", 
            font=("Segoe UI", 16, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        self.title_label.pack(pady=(0, 10))
        
        # אזור הודעות
        self.chat_history = scrolledtext.ScrolledText(
            self.chat_frame,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=FONT,
            wrap=tk.WORD,
            state="disabled"
        )
        self.chat_history.pack(padx=10, pady=10, fill="both", expand=True)
        self.chat_history.tag_configure("user", foreground=USER_COLOR)
        self.chat_history.tag_configure("gemini", foreground=GEMINI_COLOR)
        
        # אזור הקלט
        self.input_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.input_frame.pack(padx=10, pady=(0, 10), fill="x")
        
        self.message_input = tk.Text(
            self.input_frame,
            height=3,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            font=FONT,
            wrap=tk.WORD
        )
        self.message_input.pack(side=tk.LEFT, padx=(0, 5), fill="x", expand=True)
        self.message_input.bind("<Return>", self.on_enter)
        self.message_input.bind("<Shift-Return>", lambda e: None)  # מאפשר מעבר שורה עם Shift+Enter
        
        self.send_button = tk.Button(
            self.input_frame,
            text="שלח",
            command=self.send_message,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            font=FONT,
            relief=tk.FLAT,
            padx=15
        )
        self.send_button.pack(side=tk.RIGHT)
        
    def check_connection(self):
        """בדיקת חיבור ראשונית ל-Gemini API"""
        self.add_message("מערכת", "בודק חיבור ל-Gemini API...")
        
        try:
            threading.Thread(target=self._async_check_connection).start()
        except Exception as e:
            self.add_message("מערכת", f"שגיאה בחיבור: {str(e)}", "gemini")

    def _async_check_connection(self):
        """בדיקת חיבור אסינכרונית כדי לא לתקוע את הממשק"""
        try:
            response = self.genai_client.models.generate_content(
                model=self.model_name,
                contents="הצג את עצמך בקצרה בעברית"
            )
            
            self.root.after(0, lambda: self.add_message("ג'מיני", response.text, "gemini"))
            self.root.after(0, lambda: self.add_message("מערכת", "החיבור הצליח! אפשר להתחיל לשוחח.", "gemini"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message("מערכת", f"שגיאה בחיבור: {str(e)}", "gemini"))

    def on_enter(self, event):
        """טיפול בלחיצה על Enter"""
        if not event.state & 0x1:  # בדיקה האם Shift לחוץ
            self.send_message()
            return "break"  # מניעת הוספת שורה חדשה
        return None  # המשך התנהגות רגילה עם Shift+Enter
            
    def send_message(self):
        """שליחת הודעה לג'מיני וקבלת תשובה"""
        message = self.message_input.get("1.0", "end-1c").strip()
        if not message:
            return
            
        # הצגת הודעת המשתמש
        self.add_message("אתה", message, "user")
        
        # ניקוי תיבת הטקסט
        self.message_input.delete("1.0", tk.END)
        
        # הצגת הודעת המתנה
        processing_id = self.add_message("ג'מיני", "חושב...", "gemini")
        
        # שליחת הבקשה באופן אסינכרוני
        threading.Thread(target=self._async_get_response, args=(message, processing_id)).start()
    
    def _async_get_response(self, message, processing_id):
        """קבלת תשובה מג'מיני באופן אסינכרוני"""
        try:
            response = self.genai_client.models.generate_content(
                model=self.model_name,
                contents=message
            )
            
            # עדכון הממשק הגרפי - חייב להיעשות בתהליך הראשי
            self.root.after(0, lambda: self.update_message(processing_id, response.text))
        except Exception as e:
            # עדכון הודעת שגיאה
            self.root.after(0, lambda: self.update_message(processing_id, f"שגיאה: {str(e)}"))
    
    def add_message(self, sender, message, tag=None):
        """הוספת הודעה לחלון הצ'אט"""
        self.chat_history.config(state="normal")
        
        # הוספת מזהה להודעה
        message_id = f"message_{len(self.chat_history.get('1.0', tk.END).split('נשלח:'))}"
        
        # הוספת רווח לפני הודעות חדשות (אחרי ההודעה הראשונה)
        if self.chat_history.get("1.0", "end-1c"):
            self.chat_history.insert(tk.END, "\n\n")
            
        # הוספת כותרת וההודעה עצמה
        self.chat_history.insert(tk.END, f"{sender} נשלח:", tag)
        self.chat_history.insert(tk.END, f"\n{message}", tag)
        
        # שמירת מיקום תחילת ההודעה
        start_pos = self.chat_history.search(f"{sender} נשלח:", "1.0", tk.END)
        
        # הוספת תג מזהה להודעה
        self.chat_history.tag_add(message_id, start_pos, tk.END)
        
        self.chat_history.config(state="disabled")
        
        # גלילה לסוף הצ'אט
        self.chat_history.see(tk.END)
        
        return message_id
    
    def update_message(self, message_id, new_text):
        """עדכון הודעה קיימת"""
        self.chat_history.config(state="normal")
        
        # חיפוש תחילת ההודעה
        start_pos = self.chat_history.tag_ranges(message_id)[0]
        
        # חיפוש תחילת הטקסט (אחרי הכותרת)
        text_start = self.chat_history.search("\n", start_pos, tk.END)
        
        # מחיקת הטקסט הקודם
        self.chat_history.delete(f"{text_start}+1c", f"{text_start} lineend+1c")
        
        # הוספת הטקסט החדש
        self.chat_history.insert(f"{text_start}+1c", new_text, "gemini")
        
        self.chat_history.config(state="disabled")
        
        # גלילה לסוף הצ'אט
        self.chat_history.see(tk.END)

def main():
    # בדיקה אם tkinter זמין
    try:
        root = tk.Tk()
        app = ChatApp(root)
        root.mainloop()
    except ImportError:
        print("שגיאה: לא ניתן לטעון את ספריית Tkinter.")
        print("אנא התקן את הספרייה או השתמש בגרסת הטרמינל של הצ'אט.")
    except Exception as e:
        print(f"שגיאה: {str(e)}")

if __name__ == "__main__":
    main() 