import os
import platform
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CONFIG_FILE = "config.txt"


def get_default_wsjtx_log():
  """Automatically detects the standard WSJT-X log path based on OS."""
  home = os.path.expanduser("~")
  system = platform.system()
  if system == "Windows":
    return os.path.join(home, "AppData", "Local", "WSJT-X", "wsjtx_log.adi")
  elif system == "Darwin":  # macOS
    return os.path.join(
        home, "Library", "Application Support", "WSJT-X", "wsjtx_log.adi"
    )
  else:  # Linux
    return os.path.join(home, ".local", "share", "WSJT-X", "wsjtx_log.adi")


def load_config_path():
  """Reads config.txt if it exists to check for a custom log path."""
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        path = f.read().strip()
        if path and os.path.exists(path):
          return path
    except Exception:
      pass
  return get_default_wsjtx_log()


def save_config_path(path):
  """Saves the custom log path to config.txt."""
  try:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      f.write(path)
  except Exception as e:
    print(f"Error saving config: {e}")


class POTALoggerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("POTA FT-8/FT-4 Companion Logger")
    self.root.geometry("880x580")
    self.root.configure(bg="#1e1e2e")

    # Modern Dark Theme Styling using TTK
    self.style = ttk.Style()
    self.style.theme_use("clam")
    self.style.configure(
        "Treeview",
        background="#252538",
        foreground="#cdd6f4",
        fieldbackground="#252538",
        borderwidth=0,
        rowheight=26,
    )
    self.style.configure(
        "Treeview.Heading",
        background="#313244",
        foreground="#cdd6f4",
        font=("Segoe UI", 10, "bold"),
    )
    self.style.map("Treeview", background=[("selected", "#45475a")])

    self.contacts = []
    self.last_file_size = 0
    self.activation_alert_shown = False
    self.current_log_path = load_config_path()

    self.create_widgets()
    self.start_file_watcher()

  def create_widgets(self):
    # Top Header Frame
    top_frame = tk.Frame(self.root, bg="#1e1e2e", padx=15, pady=15)
    top_frame.pack(fill=tk.X)

    title_label = tk.Label(
        top_frame,
        text="🌲 WSJTX POTA Companion Logger",
        font=("Segoe UI", 16, "bold"),
        fg="#89b4fa",
        bg="#1e1e2e",
    )
    title_label.pack(side=tk.LEFT)

    # Export Button (Red background, Yellow text)
    export_btn = tk.Button(
        top_frame,
        text="📤 Export POTA ADIF",
        font=("Segoe UI", 11, "bold"),
        bg="#504c4c",
        fg="#e90d0d",
        activebackground="#504c4c",
        activeforeground="#e90d0d",
        relief=tk.FLAT,
        padx=10,
        pady=5,
        cursor="hand2",
        command=self.export_pota_adif,
    )
    export_btn.pack(side=tk.RIGHT, padx=(10, 0))

    # Progress Counter Badge
    self.counter_var = tk.StringVar(value="Contacts: 0 / 10")
    self.counter_label = tk.Label(
        top_frame,
        textvariable=self.counter_var,
        font=("Segoe UI", 11, "bold"),
        fg="#a6e3a1",
        bg="#313244",
        padx=10,
        pady=5,
    )
    self.counter_label.pack(side=tk.RIGHT)

    # Middle Control Frame (My Park & Mode selection)
    info_frame = tk.Frame(self.root, bg="#1e1e2e", padx=15, pady=5)
    info_frame.pack(fill=tk.X)

    tk.Label(
        info_frame,
        text="My Park:",
        font=("Segoe UI", 10, "bold"),
        fg="#cdd6f4",
        bg="#1e1e2e",
    ).pack(side=tk.LEFT, padx=(0, 8))

    self.park_entry = tk.Entry(
        info_frame,
        font=("Segoe UI", 10),
        bg="#313244",
        fg="#cdd6f4",
        insertbackground="white",
        relief=tk.FLAT,
        width=10,
    )
    self.park_entry.insert(0, "K-1234")
    self.park_entry.pack(side=tk.LEFT, ipady=4, ipadx=4, padx=(0, 20))

    tk.Label(
        info_frame,
        text="Mode:",
        font=("Segoe UI", 10, "bold"),
        fg="#cdd6f4",
        bg="#1e1e2e",
    ).pack(side=tk.LEFT, padx=(0, 8))

    self.mode_combobox = ttk.Combobox(
        info_frame,
        values=["FT-8", "FT-4"],
        font=("Segoe UI", 10),
        state="readonly",
        width=8,
    )
    self.mode_combobox.set("FT-8")
    self.mode_combobox.pack(side=tk.LEFT, ipady=2)

    # Table / Contact List Frame
    table_frame = tk.Frame(self.root, bg="#1e1e2e", padx=15, pady=10)
    table_frame.pack(fill=tk.BOTH, expand=True)

    columns = (
        "Callsign",
        "Band",
        "Mode",
        "Time UTC",
        "Sent",
        "Rcvd",
        "Park",
    )
    self.tree = ttk.Treeview(
        table_frame, columns=columns, show="headings", selectmode="browse"
    )

    column_widths = {
        "Callsign": 120,
        "Band": 80,
        "Mode": 80,
        "Time UTC": 140,
        "Sent": 70,
        "Rcvd": 70,
        "Park": 110,
    }
    for col in columns:
      self.tree.heading(col, text=col)
      self.tree.column(
          col, width=column_widths.get(col, 100), anchor=tk.CENTER
      )

    scrollbar = ttk.Scrollbar(
        table_frame, orient=tk.VERTICAL, command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Status Bar Footer with File Locator Button
    footer_frame = tk.Frame(self.root, bg="#1e1e2e", padx=15, pady=10)
    footer_frame.pack(fill=tk.X)

    self.status_var = tk.StringVar()
    self.update_status_text()

    status_label = tk.Label(
        footer_frame,
        textvariable=self.status_var,
        font=("Segoe UI", 12, "italic"),
        fg="#ccee0c",
        bg="#1e1e2e",
        anchor="w",
    )
    status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Locate Log Button (Red background, Yellow text)
    browse_btn = tk.Button(
        footer_frame,
        text="📁 Locate Log File",
        font=("Segoe UI", 11, "bold"),
        bg="#504c4c",
        fg="#e90d0d",
        activebackground="#504c4c",
        activeforeground="#e90d0d",
        relief=tk.FLAT,
        padx=10,
        pady=5,
        cursor="hand2",
        command=self.browse_log_file,
    )
    browse_btn.pack(side=tk.RIGHT)

  def update_status_text(self):
    self.status_var.set(f"Status: Listening to {self.current_log_path}")

  def browse_log_file(self):
    """Allows user to manually pick wsjtx_log.adif if stored elsewhere."""
    filename = filedialog.askopenfilename(
        title="Select WSJT-X ADIF Log File",
        filetypes=[("ADIF files", "*.adif;*.adi"), ("All files", "*.*")],
    )
    if filename:
      self.current_log_path = filename
      save_config_path(filename)
      self.update_status_text()
      self.last_file_size = 0
      self.contacts.clear()
      for item in self.tree.get_children():
        self.tree.delete(item)
      self.counter_var.set("Contacts: 0 / 10")
      self.activation_alert_shown = False
      messagebox.showinfo(
          "Log Path Updated",
          f"Successfully targeted custom log file:\n{filename}",
      )

  def parse_adif_record(self, record_text):
    """Parses individual ADIF records including TX and RX signal reports."""

    def get_field(field_name):
      match = re.search(
          rf"<{field_name}:(\d+)>([^<]+)", record_text, re.IGNORECASE
      )
      if match:
        length = int(match.group(1))
        return match.group(2)[:length].strip()
      return ""

    call = get_field("CALL")
    band = get_field("BAND")
    qso_date = get_field("QSO_DATE")
    time_on = get_field("TIME_ON")
    stx = get_field("STX") or get_field("RST_SENT") or "-10"
    srx = get_field("SRX") or get_field("RST_RCVD") or "-10"

    if call:
      formatted_time = "N/A"
      if len(qso_date) == 8 and len(time_on) >= 4:
        formatted_time = (
            f"{qso_date[:4]}-{qso_date[4:6]}-{qso_date[6:]}"
            f" {time_on[:2]}:{time_on[2:4]}"
        )
      return {
          "call": call,
          "band": band,
          "qso_date": qso_date,
          "time_on": time_on,
          "time_display": formatted_time,
          "stx": stx,
          "srx": srx,
      }
    return None

  def check_log_file(self):
    """Checks the WSJT-X log file size and reads newly appended contacts."""
    log_path = self.current_log_path
    if os.path.exists(log_path):
      try:
        current_size = os.path.getsize(log_path)
        if current_size > self.last_file_size:
          with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(self.last_file_size)
            new_content = f.read()
            self.last_file_size = current_size

          records = new_content.split("<EOR>")
          for record in records:
            parsed = self.parse_adif_record(record)
            if parsed:
              park = self.park_entry.get().strip()
              mode = self.mode_combobox.get().strip()
              parsed["park"] = park
              parsed["mode"] = mode
              self.contacts.append(parsed)
              self.tree.insert(
                  "",
                  0,
                  values=(
                      parsed["call"],
                      parsed["band"],
                      mode,
                      parsed["time_display"],
                      parsed["stx"],
                      parsed["srx"],
                      park,
                  ),
              )

              # Update counter display
              count = len(self.contacts)
              self.counter_var.set(f"Contacts: {count} / 10")

              # Trigger activation success notification at 10 contacts
              if count >= 10 and not self.activation_alert_shown:
                self.activation_alert_shown = True
                messagebox.showinfo(
                    "🎉 Activation Successful!",
                    "Fantastic job! You have logged 10 contacts and"
                    " successfully completed your POTA activation requirement!",
                )
      except Exception as e:
        self.status_var.set(f"Error reading log file: {str(e)}")

    # Poll every 2 seconds for updates
    self.root.after(2000, self.check_log_file)

  def start_file_watcher(self):
    log_path = self.current_log_path
    if os.path.exists(log_path):
      self.last_file_size = os.path.getsize(log_path)
    else:
      self.last_file_size = 0
    self.root.after(2000, self.check_log_file)

  def export_pota_adif(self):
    """Exports logged contacts into a POTA-ready ADIF file named ft8_data.adif."""
    if not self.contacts:
      messagebox.showwarning(
          "No Contacts", "There are no contacts logged yet to export."
      )
      return

    filename = filedialog.asksaveasfilename(
        defaultextension=".adif",
        initialfile="ft8_data.adif",
        filetypes=[("ADIF files", "*.adif"), ("All files", "*.*")],
    )

    if filename:
      try:
        park_ref = self.park_entry.get().strip()
        adif_lines = [
            "POTA Companion Logger Export",
            "<ADIF_VER:5>3.1.4",
            "<EOH>\n",
        ]

        for c in self.contacts:
          record = (
              f"<CALL:{len(c['call'])}>{c['call']} "
              f"<BAND:{len(c['band'])}>{c['band']} "
              f"<MODE:{len(c['mode'])}>{c['mode']} "
              f"<QSO_DATE:8>{c['qso_date']} "
              f"<TIME_ON:6>{c['time_on']} "
              f"<STX:{len(c['stx'])}>{c['stx']} "
              f"<SRX:{len(c['srx'])}>{c['srx']} "
              f"<MY_SIG:4>POTA "
              f"<MY_SIG_INFO:{len(park_ref)}>{park_ref} "
              f"<EOR>"
          )
          adif_lines.append(record)

        with open(filename, "w", encoding="utf-8") as f:
          f.write("\n".join(adif_lines))

        messagebox.showinfo(
            "Export Successful",
            f"Successfully exported {len(self.contacts)} contacts to:\n{filename}",
        )
      except Exception as e:
        messagebox.showerror(
            "Export Error", f"Failed to save POTA ADIF file:\n{str(e)}"
        )


if __name__ == "__main__":
  root = tk.Tk()
  app = POTALoggerApp(root)
  root.mainloop()