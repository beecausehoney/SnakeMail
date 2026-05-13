import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import imaplib, smtplib, json, os, email, threading, mimetypes, base64, time
from email.message import EmailMessage

CONFIG_FILE = ".snakemail.config.json"
THEME_BG = "#0a0a0a"
THEME_FG = "#00ff41" # Matrix Lime
THEME_ACCENT = "#ffb000" # Amber

class SnakeMail:
    def __init__(self, root):
        self.root = root
        self.root.title("SnakeMail v1.4 - Cyber-Link Terminal")
        self.root.geometry("1100x720")
        self.root.configure(bg=THEME_BG)
        
        self.current_user = None
        self.current_pass = None
        self.mail = None
        self.attachment_paths = []
        self.emails_data = []
        self.sync_active = False

        # Custom Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TLabel", background=THEME_BG, foreground=THEME_FG, font=("Courier", 10))
        
        self.container = tk.Frame(self.root, bg=THEME_BG)
        self.container.pack(fill="both", expand=True)
        self.show_login_screen()

    def obfuscate(self, data):
        return base64.b64encode(data.encode()).decode()

    def deobfuscate(self, data):
        return base64.b64decode(data.encode()).decode()

    def load_credentials(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    u = data.get("user", "")
                    p = self.deobfuscate(data.get("pass", ""))
                    return u, p
            except: pass
        return "", ""

    def show_login_screen(self):
        self.clear_frame()
        saved_user, saved_pass = self.load_credentials()
        
        login_f = tk.Frame(self.container, bg=THEME_BG, highlightbackground=THEME_FG, highlightthickness=1)
        login_f.place(relx=0.5, rely=0.5, anchor="center", ipadx=20, ipady=20)
        
        tk.Label(login_f, text="--- SNAKEMAIL v1.4 ACCESS ---", bg=THEME_BG, fg=THEME_ACCENT, font=("Courier", 14, "bold")).pack(pady=15)
        
        tk.Label(login_f, text="OPERATOR ID:", bg=THEME_BG, fg=THEME_FG).pack(anchor="w")
        self.email_entry = tk.Entry(login_f, width=35, bg="#1a1a1a", fg=THEME_FG, insertbackground=THEME_FG, border=0)
        self.email_entry.insert(0, saved_user)
        self.email_entry.pack(pady=5)
        
        tk.Label(login_f, text="ACCESS KEY:", bg=THEME_BG, fg=THEME_FG).pack(anchor="w")
        self.pass_entry = tk.Entry(login_f, width=35, show="*", bg="#1a1a1a", fg=THEME_FG, insertbackground=THEME_FG, border=0)
        self.pass_entry.insert(0, saved_pass)
        self.pass_entry.pack(pady=5)
        
        self.rem_var = tk.BooleanVar(value=True if saved_user else False)
        tk.Checkbutton(login_f, text="STAY LOGGED IN", variable=self.rem_var, bg=THEME_BG, fg=THEME_FG, selectcolor="black", activebackground=THEME_BG, activeforeground=THEME_FG).pack()
        
        tk.Button(login_f, text="[ INITIALIZE UPLINK ]", command=self.validate_login, bg=THEME_BG, fg=THEME_ACCENT, activebackground=THEME_ACCENT, borderwidth=1).pack(pady=20)

    def validate_login(self):
        u = self.email_entry.get().strip()
        p = self.pass_entry.get() 
        try:
            self.mail = imaplib.IMAP4_SSL("mail.cock.li", 993, timeout=10)
            self.mail.login(u, p)
            
            if self.rem_var.get():
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"user": u, "pass": self.obfuscate(p)}, f)
            else:
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            
            self.current_user, self.current_pass = u, p
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Auth Error", f"CONNECTION REFUSED: {str(e)}")

    def show_dashboard(self):
        self.clear_frame()
        # --- LEFT: TERMINAL FEED ---
        left_frame = tk.Frame(self.container, padx=10, pady=10, bg=THEME_BG)
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_frame, text=">> INCOMING DATA PACKETS", bg=THEME_BG, fg=THEME_ACCENT, font=("Courier", 12, "bold")).pack(anchor="w")
        
        self.inbox_list = tk.Listbox(left_frame, bg="#050505", fg=THEME_FG, font=("Courier", 10), border=0, selectbackground=THEME_ACCENT)
        self.inbox_list.pack(fill="both", expand=True, pady=10)
        self.inbox_list.bind("<<ListboxSelect>>", self.open_email_window)
        
        btn_f = tk.Frame(left_frame, bg=THEME_BG)
        btn_f.pack(pady=5, fill="x")
        
        self.fetch_btn = tk.Button(btn_f, text="SYNC NOW", command=self.start_fetch_thread, bg="#111", fg=THEME_FG)
        self.fetch_btn.pack(side="left", padx=5)
        
        self.auto_sync_btn = tk.Button(btn_f, text="AUTO-SYNC: OFF", command=self.toggle_sync, bg="#111", fg="red")
        self.auto_sync_btn.pack(side="left", padx=5)

        # --- RIGHT: SYSTEM PANEL ---
        right_frame = tk.Frame(self.container, width=380, padx=10, pady=10, bg="#0d0d0d")
        right_frame.pack(side="right", fill="both")

        # Identity
        status_box = tk.LabelFrame(right_frame, text=" IDENTITY ", bg="#0d0d0d", fg=THEME_ACCENT, font=("Courier", 9))
        status_box.pack(fill="x", pady=(0, 10))
        tk.Label(status_box, text=f"USR: {self.current_user}", bg="#0d0d0d", fg=THEME_FG).pack(anchor="w", padx=5)
        tk.Label(status_box, text="SYS: ONLINE", bg="#0d0d0d", fg=THEME_FG).pack(anchor="w", padx=5)

        # Composer
        send_box = tk.LabelFrame(right_frame, text=" DISPATCH ", bg="#0d0d0d", fg=THEME_ACCENT, font=("Courier", 9))
        send_box.pack(fill="both", expand=True)

        tk.Label(send_box, text="TO:", bg="#0d0d0d", fg=THEME_FG).pack(anchor="w")
        self.to_entry = tk.Entry(send_box, bg="#1a1a1a", fg=THEME_FG, border=0)
        self.to_entry.pack(fill="x", padx=5)

        tk.Label(send_box, text="SUB:", bg="#0d0d0d", fg=THEME_FG).pack(anchor="w")
        self.sub_entry = tk.Entry(send_box, bg="#1a1a1a", fg=THEME_FG, border=0)
        self.sub_entry.pack(fill="x", padx=5)

        tk.Label(send_box, text="DATA:", bg="#0d0d0d", fg=THEME_FG).pack(anchor="w")
        self.msg_text = tk.Text(send_box, height=8, bg="#1a1a1a", fg=THEME_FG, font=("Courier", 10), border=0)
        self.msg_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.attach_label = tk.Label(send_box, text="No cargo attached", bg="#0d0d0d", fg="gray", font=("Courier", 8))
        self.attach_label.pack()
        self.attach_label.bind("<Button-3>", lambda e: self.reset_attachments()) # Right click to clear
        
        btn_row = tk.Frame(send_box, bg="#0d0d0d")
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="ADD CARGO", command=self.attach_file, bg="#222", fg=THEME_FG).pack(side="left", padx=5)
        self.send_btn = tk.Button(btn_row, text="SEND PACKET", command=self.send_mail, bg=THEME_FG, fg="black", font=("Courier", 9, "bold")).pack(side="left", padx=5)

        # Logs
        log_box = tk.LabelFrame(right_frame, text=" SYSTEM LOGS ", bg="#0d0d0d", fg=THEME_ACCENT, font=("Courier", 9))
        log_box.pack(fill="both", expand=True, pady=(5, 0))
        self.sys_log = scrolledtext.ScrolledText(log_box, height=6, bg="black", fg=THEME_FG, font=("Courier", 8), state='disabled', border=0)
        self.sys_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Button(right_frame, text="TERMINATE SESSION", command=self.perform_logout, bg="#330000", fg="white").pack(side="bottom", pady=5)
        self.log_event("Connection Stabilized. SnakeMail Ready.")

    def toggle_sync(self):
        self.sync_active = not self.sync_active
        if self.sync_active:
            self.auto_sync_btn.config(text="AUTO-SYNC: ON", fg=THEME_FG)
            self.log_event("Auto-sync background daemon started.")
            threading.Thread(target=self.sync_loop, daemon=True).start()
        else:
            self.auto_sync_btn.config(text="AUTO-SYNC: OFF", fg="red")
            self.log_event("Auto-sync background daemon stopped.")

    def sync_loop(self):
        while self.sync_active:
            self.start_fetch_thread()
            time.sleep(60) # Sync every minute

    def reset_attachments(self):
        self.attachment_paths = []
        self.attach_label.config(text="No cargo attached", fg="gray")
        self.log_event("Cargo queue cleared.")

    def open_email_window(self, event):
        selection = self.inbox_list.curselection()
        if not selection: return
        index = selection[0]
        if index >= len(self.emails_data): return 
            
        email_info = self.emails_data[index]
        top = tk.Toplevel(self.root, bg=THEME_BG)
        top.title(f"DECRYPTED: {email_info['subject']}")
        top.geometry("700x600") 
        top.image_refs = []

        header = tk.Frame(top, bg="#111", padx=10, pady=10)
        header.pack(fill="x")
        tk.Label(header, text=f"FROM: {email_info['sender']}", bg="#111", fg=THEME_ACCENT).pack(anchor="w")
        tk.Label(header, text=f"SUBJ: {email_info['subject']}", bg="#111", fg=THEME_FG).pack(anchor="w")

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Courier", 10), bg=THEME_BG, fg=THEME_FG, border=0)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", email_info['body'])
        text_area.config(state="disabled")

        if email_info.get('attachments'):
            af = tk.Frame(top, bg="#0d0d0d")
            af.pack(fill="x", padx=10, pady=5)
            for filename, data in email_info['attachments']:
                btn = tk.Button(af, text=f"EXTRACT: {filename}", command=lambda f=filename, d=data: self.save_attachment(f, d), bg="#222", fg=THEME_ACCENT)
                btn.pack(side="left", padx=2)

    def save_attachment(self, filename, data):
        path = filedialog.asksaveasfilename(initialfile=filename)
        if path:
            with open(path, "wb") as f:
                f.write(data)
            messagebox.showinfo("Success", "File extracted to disk.")

    def log_event(self, msg):
        def update():
            if hasattr(self, 'sys_log') and self.sys_log.winfo_exists():
                self.sys_log.config(state='normal')
                self.sys_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
                self.sys_log.see(tk.END)
                self.sys_log.config(state='disabled')
        self.root.after(0, update)

    def start_fetch_thread(self):
        self.fetch_btn.config(state='disabled')
        threading.Thread(target=self.fetch_emails, daemon=True).start()

    def fetch_emails(self):
        try:
            self.mail.select("inbox")
            _, data = self.mail.search(None, "ALL")
            if not data or not data[0]:
                self.log_event("No data found in inbox.")
                return

            ids = data[0].split()
            fetched_emails = []
            for i in ids[-15:]: # Increased to 15
                _, msg_data = self.mail.fetch(i, "(RFC822)")
                for resp in msg_data:
                    if isinstance(resp, tuple):
                        msg = email.message_from_bytes(resp[1])
                        body = ""
                        attachments_list = []
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    p = part.get_payload(decode=True)
                                    body = p.decode(errors='ignore') if p else ""
                                if part.get_content_disposition() == 'attachment':
                                    filename = part.get_filename()
                                    if filename: attachments_list.append((filename, part.get_payload(decode=True)))
                        else:
                            p = msg.get_payload(decode=True)
                            body = p.decode(errors='ignore') if p else ""
                        
                        sender = msg['from'] or "Unknown"
                        subject = msg['subject'] or "No Subject"
                        summary = f" {sender[:20]} | {subject[:30]}"
                        fetched_emails.append({'summary': summary, 'sender': sender, 'subject': subject, 'body': body, 'attachments': attachments_list})
            
            fetched_emails.reverse()
            self.root.after(0, self.update_inbox_ui, fetched_emails)
            self.log_event(f"Uplink successful: {len(fetched_emails)} packets received.")
        except Exception as e:
            self.log_event(f"SYNC ERROR: {str(e)}")
        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state='normal'))

    def update_inbox_ui(self, emails_list):
        self.inbox_list.delete(0, tk.END)
        self.emails_data = emails_list
        for em in emails_list:
            self.inbox_list.insert(tk.END, em['summary'])

    def attach_file(self):
        filepaths = filedialog.askopenfilenames()
        if filepaths:
            self.attachment_paths.extend(filepaths)
            self.attach_label.config(text=f"{len(self.attachment_paths)} files queued", fg=THEME_ACCENT)
            self.log_event(f"Cargo loaded: {len(filepaths)} files.")

    def send_mail(self):
        recipient = self.to_entry.get().strip()
        if not recipient: return
        self.log_event(f"Attempting dispatch to {recipient}...")
        
        def task():
            try:
                msg = EmailMessage()
                msg.set_content(self.msg_text.get("1.0", tk.END))
                msg['Subject'] = self.sub_entry.get()
                msg['From'] = self.current_user
                msg['To'] = recipient
                for path in self.attachment_paths:
                    ctype, _ = mimetypes.guess_type(path)
                    maintype, subtype = (ctype or 'application/octet-stream').split('/', 1)
                    with open(path, 'rb') as f:
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))

                with smtplib.SMTP_SSL("mail.cock.li", 465) as smtp:
                    smtp.login(self.current_user, self.current_pass)
                    smtp.send_message(msg)
                
                self.log_event("Dispatch successful. Connection closed.")
                self.root.after(0, self.reset_composer)
            except Exception as e:
                self.log_event(f"DISPATCH FAILED: {str(e)}")
        threading.Thread(target=task, daemon=True).start()

    def reset_composer(self):
        self.msg_text.delete("1.0", tk.END)
        self.sub_entry.delete(0, tk.END)
        self.to_entry.delete(0, tk.END)
        self.reset_attachments()

    def perform_logout(self):
        self.sync_active = False
        try: self.mail.logout()
        except: pass
        self.show_login_screen()

    def clear_frame(self):
        for w in self.container.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeMail(root)
    root.mainloop()
