import tkinter as tk
from tkinter import ttk
from main import get_response

LARGE_FONT = ('Verdana', 16)
NORMAL_FONT = ('Verdana', 12)
SMALL_FONT = ('Verdana', 10)
BG_GRAY = "#ABB2B9"
BG_COLOR = "#03547C"
DIVIDER_BG_COLOR = "#899499"
TEXT_COLOR = "#EAECEE"


class EvaluatorApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        tk.Tk.wm_title(self, "User Story Evaluator")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, minsize=600, weight=1)
        container.grid_columnconfigure(0, minsize=500, weight=1)

        ttk.Style().configure("TButton", padding=6, relief="flat",
                              background=BG_COLOR)

        self.frames = {}

        for F in (StartPage, AutomaticEvaluator, PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_COLOR)

        label = tk.Label(self, text='User Story Evaluator', font=LARGE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        label.place(relx=0.28, rely=0.015)

        divider = tk.Frame(self, bg=DIVIDER_BG_COLOR, height=1, bd=0)
        divider.place(relx=0, rely=0.08, relheight=0.01, relwidth=1)

        button1 = ttk.Button(self, text='Automatic User Story Evaluator',
                             command=lambda: controller.show_frame(AutomaticEvaluator))
        button1.place(relx=0.32, rely=0.2)

        button2 = ttk.Button(self, text='Manual User Story Evaluator',
                             command=lambda: controller.show_frame(PageTwo))
        button2.place(relx=0.333, rely=0.3)


class AutomaticEvaluator(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg=BG_COLOR)

        label = tk.Label(self, text='Automatic Evaluator', font=LARGE_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        label.place(relx=0.28, rely=0.015)

        divider = tk.Frame(self, bg=DIVIDER_BG_COLOR, height=1, bd=0)
        divider.place(relx=0, rely=0.08, relheight=0.01, relwidth=1)

        entered_user_story_label = tk.Label(self, text="Your User Story", font=NORMAL_FONT, bg=BG_COLOR, fg=TEXT_COLOR)
        entered_user_story_label.place(relx=0.32, rely=0.15)

        self.entered_user_story_text = tk.Text(self, wrap="word")
        self.entered_user_story_text.place(relx=0.055, rely=0.20, relheight=0.15, relwidth=0.89)
        self.entered_user_story_text.insert('insert', "The User Story entered for evaluation will be displayed here.")
        self.entered_user_story_text.configure(cursor="arrow", state='disabled')

        evaluation_results_label = tk.Label(self, text="Evaluation result", font=NORMAL_FONT,
                                            bg=BG_COLOR, fg=TEXT_COLOR)
        evaluation_results_label.place(relx=0.32, rely=0.38)

        self.evaluation_results_text = tk.Text(self, wrap="word")
        self.evaluation_results_text.place(relx=0.055, rely=0.43, relheight=0.07, relwidth=0.89)
        self.evaluation_results_text.insert('insert',
                                            "The results of evaluating given user story will be displayed here.")
        self.evaluation_results_text.configure(cursor="arrow", state='disabled')

        submit_field_label = tk.Label(self, text="Enter your User Story here", font=NORMAL_FONT,
                                      bg=BG_COLOR, fg=TEXT_COLOR)
        submit_field_label.place(relx=0.24, rely=0.55)

        self.submit_field_text = tk.Text(self, wrap="word")
        self.submit_field_text.place(relx=0.055, rely=0.60, relheight=0.15, relwidth=0.89)
        self.submit_field_text.focus()
        self.submit_field_text.bind("<Return>", self._on_enter_pressed)

        submit_button = ttk.Button(self, text="Submit", width=20, command=lambda: self._on_enter_pressed(None))
        submit_button.place(relx=0.055, rely=0.78, relheight=0.15, relwidth=0.89)

    def _on_enter_pressed(self, event):
        user_story = self.submit_field_text.get(1.0, 'end')
        self._insert_message(user_story)

    def _insert_message(self, user_story):
        if not user_story:
            return

        self.submit_field_text.delete(1.0, 'end')

        self.entered_user_story_text.configure(state='normal')
        self.entered_user_story_text.delete(1.0, 'end')
        self.entered_user_story_text.insert(1.0, user_story)
        self.entered_user_story_text.configure(cursor="arrow", state='disabled')

        self.evaluation_results_text.configure(state='normal')
        self.evaluation_results_text.delete(1.0, 'end')
        self.evaluation_results_text.insert(1.0, get_response(user_story))
        self.evaluation_results_text.configure(cursor="arrow", state='disabled')


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        head_label = tk.Label(self, bg=BG_COLOR, fg=TEXT_COLOR, text="Welcome", font=LARGE_FONT, pady=10)
        head_label.place(relwidth=1)

        # tiny divider
        line = tk.Label(self, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.7, relheight=0.012)

        # text area
        self.text_area = tk.Text(self, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR, font=NORMAL_FONT)
        self.text_area.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_area.configure(cursor="arrow", state='disabled')

        # text widget
        self.text_widget = tk.Text(self.text_area, bg=BG_COLOR, fg=TEXT_COLOR, font=NORMAL_FONT, padx=10, pady=5)
        self.text_widget.place(relheight=1, relwidth=1)
        self.text_widget.configure(cursor="arrow", state='disabled')

        # scroll bar
        scrollbar = ttk.Scrollbar(self.text_area)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)

        # bottom label
        bottom_label = tk.Label(self, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)

        # message entry box
        self.msg_entry = tk.Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=NORMAL_FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()

        # send button
        send_button = ttk.Button(bottom_label, text="Send", width=20,
                                 command=lambda: controller.show_frame(StartPage))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)


if __name__ == "__main__":
    app = EvaluatorApp()
    app.mainloop()
