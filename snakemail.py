import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import imaplib, smtplib, json, os, email, threading, mimetypes, base64
from email.message import EmailMessage

CONFIG_FILE = ".snakemail.config.json"

class SnakeMail:
    def __init__(self, root):
        self.root = root
        self.root.title("SnakeMail v1.3 - Secure Terminal")
        self.root.geometry("1000x680") 
        self.current_user = None
        self.current_pass = None
        self.mail = None
        self.attachment_paths = [] # Keeps track of attached files ready to send
        self.emails_data = [] # Stores full email data for the popup windows

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        self.show_login_screen()

    def load_credentials(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("user", ""), data.get("pass", "")
            except: pass
        return "", ""

    def show_login_screen(self):
        self.clear_frame()
        saved_user, saved_pass = self.load_credentials()
        
        login_f = tk.Frame(self.container)
        login_f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(login_f, text="SNAKEMAIL LOGIN", font=("Courier", 14, "bold")).pack(pady=10)
        
        self.email_entry = tk.Entry(login_f, width=30)
        self.email_entry.insert(0, saved_user)
        self.email_entry.pack(pady=5)
        
        self.pass_entry = tk.Entry(login_f, width=30, show="*")
        self.pass_entry.insert(0, saved_pass)
        self.pass_entry.pack(pady=5)
        
        def toggle_pass():
            self.pass_entry.config(show="" if show_var.get() else "*")

        show_var = tk.BooleanVar()
        tk.Checkbutton(login_f, text="Show Password", variable=show_var, command=toggle_pass).pack()

        self.rem_var = tk.BooleanVar(value=True if saved_user else False)
        tk.Checkbutton(login_f, text="Remember Credentials", variable=self.rem_var).pack()
        
        tk.Button(login_f, text="INITIALIZE CONSOLE", command=self.validate_login).pack(pady=10)

    def validate_login(self):
        u = self.email_entry.get().strip()
        p = self.pass_entry.get() 
        
        try:
            self.mail = imaplib.IMAP4_SSL("mail.cock.li", 993, timeout=10)
            
            if not u or not p:
                raise ValueError("Email or Password cannot be empty")
            
            self.mail.login(u, p)
            
            if self.rem_var.get():
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"user": u, "pass": p}, f)
            else:
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            
            self.current_user, self.current_pass = u, p
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Auth Error", str(e))

    def show_dashboard(self):
        self.clear_frame()
        # --- LEFT: THE READER ---
        left_frame = tk.Frame(self.container, padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_frame, text="INBOX FEED (Click to Expand)", font=("Courier", 12, "bold")).pack(anchor="w")
        
        self.inbox_list = tk.Listbox(left_frame, bg="#f8f8f8", font=("Courier", 10))
        self.inbox_list.pack(fill="both", expand=True)
        self.inbox_list.bind("<<ListboxSelect>>", self.open_email_window)
        
        btn_f = tk.Frame(left_frame)
        btn_f.pack(pady=5)
        
        self.fetch_btn = tk.Button(btn_f, text="FETCH LATEST LOGS", command=self.start_fetch_thread)
        self.fetch_btn.pack(side="left", padx=5)
        
        self.recon_btn = tk.Button(btn_f, text="RECONNECT SERVER", command=self.start_reconnect_thread)
        self.recon_btn.pack(side="left", padx=5)

        tk.Button(btn_f, text="CLEAR CONSOLE", command=self.clear_console).pack(side="left", padx=5)

        # --- RIGHT: STATUS, COMPOSER & LOGS ---
        right_frame = tk.Frame(self.container, width=350, padx=10, pady=10, bg="#efefef")
        right_frame.pack(side="right", fill="both")

        status_box = tk.LabelFrame(right_frame, text="System Identity", bg="#efefef")
        status_box.pack(fill="x", pady=(0, 10))
        tk.Label(status_box, text=f"ID: {self.current_user}", bg="#efefef", font=("Courier", 9)).pack(anchor="w", padx=5)
        tk.Label(status_box, text="STATUS: LOGGED IN", fg="green", bg="#efefef", font=("Courier", 9, "bold")).pack(anchor="w", padx=5)

        send_box = tk.LabelFrame(right_frame, text="Dispatch Message", bg="#efefef")
        send_box.pack(fill="both", expand=True)

        tk.Label(send_box, text="To:", bg="#efefef").pack(anchor="w")
        self.to_entry = tk.Entry(send_box)
        self.to_entry.pack(fill="x", padx=5)

        tk.Label(send_box, text="Subject:", bg="#efefef").pack(anchor="w")
        self.sub_entry = tk.Entry(send_box)
        self.sub_entry.pack(fill="x", padx=5)

        tk.Label(send_box, text="Message:", bg="#efefef").pack(anchor="w")
        self.msg_text = tk.Text(send_box, height=6, font=("Arial", 10))
        self.msg_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.attach_label = tk.Label(send_box, text="No attachments", bg="#efefef", fg="gray", font=("Arial", 8))
        self.attach_label.pack(pady=(0, 2))
        
        btn_row = tk.Frame(send_box, bg="#efefef")
        btn_row.pack(pady=5)
        
        self.attach_btn = tk.Button(btn_row, text="ATTACH FILE", command=self.attach_file)
        self.attach_btn.pack(side="left", padx=5)

        self.send_btn = tk.Button(btn_row, text="SEND EMAIL", bg="#2e2e2e", fg="white", command=self.send_mail)
        self.send_btn.pack(side="left", padx=5)

        log_box = tk.LabelFrame(right_frame, text="Live System Log", bg="#efefef")
        log_box.pack(fill="both", expand=True, pady=(5, 0))
        self.sys_log = scrolledtext.ScrolledText(log_box, height=5, bg="black", fg="lime", font=("Courier", 8), state='disabled')
        self.sys_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        tk.Button(right_frame, text="LOGOUT", command=self.perform_logout).pack(side="bottom", pady=5)
        self.log_event("Console Initialized.")

    def open_email_window(self, event):
        selection = self.inbox_list.curselection()
        if not selection: return
        
        index = selection[0]
        if index >= len(self.emails_data): return 
            
        email_info = self.emails_data[index]

        top = tk.Toplevel(self.root)
        top.title(f"Reading: {email_info['subject']}")
        top.geometry("650x600") 
        
        # Keep reference to images so they don't disappear
        top.image_refs = []

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Courier", 10), bg="#fdfdfd", height=15)
        text_area.pack(fill="both", expand=True, padx=10, pady=10)

        full_text = f"SENDER: {email_info['sender']}\nSUBJECT: {email_info['subject']}\n{'-'*50}\n\n{email_info['body']}"
        text_area.insert("1.0", full_text)
        text_area.config(state="disabled")

        # NATIVE IMAGE RENDERER (NO PILLOW)
        if email_info.get('attachments'):
            attach_frame = tk.Frame(top, bg="#efefef", pady=5)
            attach_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(attach_frame, text="Secured Attachments:", bg="#efefef", font=("Arial", 10, "bold")).pack(anchor="w")
            
            gallery = tk.Frame(attach_frame, bg="#efefef")
            gallery.pack(fill="x")

            for filename, data in email_info['attachments']:
                # Natively render PNG and GIF in memory
                if filename.lower().endswith(('.png', '.gif')):
                    try:
                        b64_data = base64.b64encode(data)
                        photo = tk.PhotoImage(data=b64_data)
                        top.image_refs.append(photo) # Save reference
                        
                        lbl = tk.Label(gallery, image=photo, text=filename, compound=tk.TOP, bg="#efefef")
                        lbl.pack(side="left", padx=5)
                    except Exception as e:
                        tk.Label(gallery, text=f"[Preview Error: {filename}]", fg="red").pack(side="left")
                else:
                    # Provide a save button for JPGs, PDFs, etc.
                    btn_f = tk.Frame(gallery, bg="#efefef")
                    btn_f.pack(side="left", padx=5)
                    
                    tk.Label(btn_f, text=f"{filename}", bg="#efefef", fg="blue").pack()
                    
                    def save_file(fname=filename, fdata=data):
                        save_path = filedialog.asksaveasfilename(initialfile=fname, title="Save Secured File")
                        if save_path:
                            with open(save_path, "wb") as f:
                                f.write(fdata)
                            messagebox.showinfo("Saved", f"File safely extracted to {save_path}")
                            
                    tk.Button(btn_f, text="SAVE TO DISK", command=save_file).pack()

    def attach_file(self):
        filepaths = filedialog.askopenfilenames(title="Select Files to Attach")
        if filepaths:
            self.attachment_paths.extend(filepaths)
            names = [os.path.basename(p) for p in self.attachment_paths]
            self.attach_label.config(text=", ".join(names), fg="blue")
            self.log_event(f"Attached {len(filepaths)} file(s).")

    def log_event(self, msg):
        def update():
            if hasattr(self, 'sys_log') and self.sys_log.winfo_exists():
                self.sys_log.config(state='normal')
                self.sys_log.insert(tk.END, f"> {msg}\n")
                self.sys_log.see(tk.END)
                self.sys_log.config(state='disabled')
        self.root.after(0, update)

    def start_fetch_thread(self):
        self.fetch_btn.config(state='disabled', text="CONNECTING...")
        self.log_event("Fetching latest logs from server...")
        threading.Thread(target=self.fetch_emails, daemon=True).start()

    def fetch_emails(self):
        try:
            self.mail.select("inbox")
            _, data = self.mail.search(None, "ALL")
            if not data or not data[0]:
                self.root.after(0, lambda: self.update_inbox_ui(["[Inbox Empty]"]))
                self.log_event("Inbox empty.")
                return

            ids = data[0].split()
            fetched_emails = []
            
            # Fetch the last 10 emails
            for i in ids[-10:]:
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
                                    body = p.decode(errors='ignore') if p else "[No Content]"
                                
                                if part.get_content_disposition() == 'attachment':
                                    filename = part.get_filename()
                                    if filename:
                                        attachments_list.append((filename, part.get_payload(decode=True)))
                        else:
                            p = msg.get_payload(decode=True)
                            body = p.decode(errors='ignore') if p else "[No Content]"
                        
                        sender = msg['from'] if msg['from'] else "Unknown"
                        subject = msg['subject'] if msg['subject'] else "No Subject"
                        clean_body = body.replace('\n', ' ').replace('\r', '').strip()
                        
                        preview = (clean_body[:50] + "...") if len(clean_body) > 50 else clean_body
                        summary_str = f"[{sender[:25]}] {subject[:20]} | {preview}"
                        
                        fetched_emails.append({
                            'summary': summary_str,
                            'sender': sender,
                            'subject': subject,
                            'body': body,
                            'attachments': attachments_list
                        })
            
            fetched_emails.reverse()
            self.root.after(0, self.update_inbox_ui, fetched_emails)
            self.log_event(f"Successfully fetched {min(10, len(ids))} messages.")
        except Exception as e:
            self.root.after(0, lambda e=e: messagebox.showerror("Fetch Error", str(e)))
            self.log_event(f"ERROR fetching: {str(e)}")
        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state='normal', text="FETCH LATEST LOGS"))

    def update_inbox_ui(self, emails_list):
        self.inbox_list.delete(0, tk.END)
        self.emails_data = []
        
        if isinstance(emails_list[0], str):
            self.inbox_list.insert(tk.END, emails_list[0])
        else:
            for em in emails_list:
                self.inbox_list.insert(tk.END, em['summary'])
                self.emails_data.append(em)

    def start_reconnect_thread(self):
        self.recon_btn.config(state='disabled', text="CONNECTING...")
        self.log_event("Attempting to re-establish server connection...")
        threading.Thread(target=self.reconnect_server, daemon=True).start()

    def reconnect_server(self):
        try:
            if self.mail:
                try:
                    self.mail.logout()
                except:
                    pass 

            self.mail = imaplib.IMAP4_SSL("mail.cock.li", 993, timeout=15)
            self.mail.login(self.current_user, self.current_pass)
            
            self.log_event("SUCCESS: Server connection re-established.")
            self.root.after(0, lambda: messagebox.showinfo("Reconnected", "Successfully reconnected to mail.cock.li"))
            
        except Exception as e:
            self.log_event(f"RECONNECT FAILED: {str(e)}")
            self.root.after(0, lambda e=e: messagebox.showerror("Connection Error", f"Failed to reconnect:\n{str(e)}"))
            
        finally:
            self.root.after(0, lambda: self.recon_btn.config(state='normal', text="RECONNECT SERVER"))

    def send_mail(self):
        recipient = self.to_entry.get().strip()
        if not recipient:
            messagebox.showwarning("Warning", "Recipient required.")
            return
        self.send_btn.config(state='disabled', text="SENDING...")
        self.log_event(f"Dispatching message to {recipient}...")
        
        def task():
            try:
                msg = EmailMessage()
                msg.set_content(self.msg_text.get("1.0", tk.END))
                msg['Subject'] = self.sub_entry.get()
                msg['From'] = self.current_user
                msg['To'] = recipient
                
                for filepath in self.attachment_paths:
                    ctype, encoding = mimetypes.guess_type(filepath)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    
                    with open(filepath, 'rb') as f:
                        file_data = f.read()
                    
                    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(filepath))

                with smtplib.SMTP_SSL("mail.cock.li", 465) as smtp:
                    smtp.login(self.current_user, self.current_pass)
                    smtp.send_message(msg)
                
                self.root.after(0, lambda: messagebox.showinfo("Success", "Sent!"))
                self.root.after(0, self.reset_composer)
                self.log_event("Dispatch successful.")
            except Exception as e:
                self.root.after(0, lambda e=e: messagebox.showerror("Send Error", str(e)))
                self.log_event(f"ERROR sending: {str(e)}")
            finally:
                self.root.after(0, lambda: self.send_btn.config(state='normal', text="SEND EMAIL"))
        threading.Thread(target=task, daemon=True).start()

    def reset_composer(self):
        self.msg_text.delete("1.0", tk.END)
        self.sub_entry.delete(0, tk.END)
        self.to_entry.delete(0, tk.END)
        self.attachment_paths = []
        if hasattr(self, 'attach_label'):
            self.attach_label.config(text="No attachments", fg="gray")

    def clear_console(self):
        self.inbox_list.delete(0, tk.END)
        self.emails_data = []
        self.log_event("Inbox view cleared.")

    def perform_logout(self):
        self.log_event("Disconnecting from IMAP server...")
        try:
            if self.mail:
                self.mail.logout()
        except:
            pass
        self.current_user = None
        self.current_pass = None
        self.show_login_screen()

    def clear_frame(self):
        for w in self.container.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeMail(root)
    root.mainloop()
