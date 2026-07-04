# ==========================================================
# Event Management System — Tkinter GUI Version
# B.Tech CSE (Data Science) Project
# ==========================================================

import json
import csv
import os
import sys
import datetime
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ──────────────────────────────────────────────────────────
# DECORATOR
# ──────────────────────────────────────────────────────────
def log_action(action_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(f"[LOG SUCCESS] Completed action: {action_type}")
            return result
        return wrapper
    return decorator

# ──────────────────────────────────────────────────────────
# MODEL CLASSES  (unchanged from original)
# ──────────────────────────────────────────────────────────
class Person(ABC):
    def __init__(self, person_id, name, email, mobile_number):
        self._person_id = person_id
        self._name = name
        self._email = email
        self._mobile_number = mobile_number

    @abstractmethod
    def display_details(self):
        pass

    def update_details(self, name=None, email=None, mobile_number=None):
        if name: self._name = name
        if email: self._email = email
        if mobile_number: self._mobile_number = mobile_number


class Participant(Person):
    def __init__(self, person_id, name, email, mobile_number, participant_id):
        super().__init__(person_id, name, email, mobile_number)
        self.participant_id = participant_id
        self.registered_events = []

    def register_event(self, event_id):
        if event_id not in self.registered_events:
            self.registered_events.append(event_id)

    def view_events(self):
        return self.registered_events

    def display_details(self):
        return f"[Participant] ID: {self.participant_id}, Name: {self._name}, Email: {self._email}"


class Organizer(Person):
    def __init__(self, person_id, name, email, mobile_number, organizer_id):
        super().__init__(person_id, name, email, mobile_number)
        self.organizer_id = organizer_id
        self.assigned_events = []

    def display_details(self):
        return f"[Organizer] ID: {self.organizer_id}, Name: {self._name}, Role: Event Coordinator"


class Venue:
    def __init__(self, venue_id, venue_name, capacity, availability_status=True):
        self.venue_id = venue_id
        self.venue_name = venue_name
        self.capacity = capacity
        self.availability_status = availability_status

    @staticmethod
    def check_capacity_utility(capacity, required_slots):
        return capacity >= required_slots


class Event:
    def __init__(self, event_id, event_name, category, date_str, venue_obj, registration_fee):
        self.event_id = event_id
        self.event_name = event_name
        self.category = category
        self.date = date_str
        self.venue = venue_obj
        self.registration_fee = float(registration_fee)

    def __str__(self):
        return f"Event: {self.event_name} ({self.category}) on {self.date} at {self.venue}"

    def __repr__(self):
        return f"Event('{self.event_id}', '{self.event_name}')"


class Registration:
    def __init__(self, registration_id, participant_id, event_id):
        self.registration_id = registration_id
        self.participant_id = participant_id
        self.event_id = event_id
        self.registration_date = str(datetime.date.today())


class Payment:
    def __init__(self, payment_id, amount, payment_status="Pending"):
        self.payment_id = payment_id
        self._amount = float(amount)
        self.payment_status = payment_status
        self.payment_date = str(datetime.date.today())

    def process_payment(self):
        self.payment_status = "Completed"

    def generate_receipt(self):
        return (f"--- RECEIPT ---\n"
                f"ID: {self.payment_id}\n"
                f"Amount: ₹{self._amount:.2f}\n"
                f"Status: {self.payment_status}\n"
                f"Date: {self.payment_date}")


class Schedule:
    def __init__(self, schedule_id):
        self.schedule_id = schedule_id
        self.event_sessions = []

    def create_schedule(self, session_details):
        self.event_sessions.append(session_details)


class Certificate:
    def __init__(self, certificate_id, participant_name, event_name):
        self.certificate_id = certificate_id
        self.participant_name = participant_name
        self.event_name = event_name

    def generate_certificate(self):
        return (f"╔══════════════════════════════════════════╗\n"
                f"       CERTIFICATE OF PARTICIPATION        \n"
                f"╚══════════════════════════════════════════╝\n\n"
                f"  This certifies that\n\n"
                f"       {self.participant_name}\n\n"
                f"  successfully attended\n\n"
                f"       {self.event_name}\n\n"
                f"  Certificate ID : {self.certificate_id}\n"
                f"  Issued on      : {datetime.date.today()}\n")


# ──────────────────────────────────────────────────────────
# BACKEND SYSTEM CLASS  (unchanged logic)
# ──────────────────────────────────────────────────────────
class EventManagementSystem:
    def __init__(self):
        self.participants  = {}
        self.organizers    = {}
        self.events        = {}
        self.venues        = {}
        self.registrations = []
        self.payments      = []
        self.categories    = set()

    def __len__(self):
        return len(self.events)

    def validate_event_id(self, event_id):
        if event_id not in self.events:
            raise KeyError(f"Event ID '{event_id}' does not exist.")

    def generate_report_records(self, record_list):
        for record in record_list:
            yield record

    @log_action("Participant Registration")
    def register_participant(self, p_id, name, email, mobile, part_id):
        if part_id in self.participants:
            raise ValueError("Duplicate Participant ID.")
        new_part = Participant(p_id, name, email, mobile, part_id)
        self.participants[part_id] = new_part
        return new_part

    @log_action("Event Creation")
    def create_event(self, event_id, name, category, date_str, venue_name, fee):
        if event_id in self.events:
            raise ValueError("Event ID already exists.")
        new_event = Event(event_id, name, category, date_str, venue_name, fee)
        self.events[event_id] = new_event
        self.categories.add(category)
        return new_event

    @log_action("Payment Processing")
    def process_payment(self, pay_id, amount):
        if float(amount) <= 0:
            raise ValueError("Invalid Payment Amount.")
        pay = Payment(pay_id, amount)
        pay.process_payment()
        self.payments.append(pay)
        return pay

    def search_event_recursive(self, event_ids_list, target_id, index=0):
        if index >= len(event_ids_list):
            return None
        if event_ids_list[index] == target_id:
            return self.events[target_id]
        return self.search_event_recursive(event_ids_list, target_id, index + 1)

    def get_events_sorted_by_date(self):
        return sorted(self.events.values(), key=lambda x: x.date)

    def get_upcoming_events(self):
        return [ev for ev in self.events.values()]

    def get_system_statistics(self):
        total_revenue = sum(p._amount for p in self.payments if p.payment_status == "Completed")
        return {
            "Total Events": len(self),
            "Total Registered Participants": len(self.participants),
            "Total Financial Revenue (₹)": total_revenue
        }

    def save_data(self, directory="data"):
        if not os.path.exists(directory):
            os.makedirs(directory)
        data_dump = {
            "participants": {
                k: {"name": v._name, "email": v._email,
                    "mobile": v._mobile_number, "p_id": v._person_id,
                    "evs": v.registered_events}
                for k, v in self.participants.items()
            },
            "events": {
                k: {"name": v.event_name, "category": v.category,
                    "date": v.date, "venue": v.venue, "fee": v.registration_fee}
                for k, v in self.events.items()
            }
        }
        with open(os.path.join(directory, "system_data.json"), "w") as f:
            json.dump(data_dump, f, indent=4)

    def load_data(self, directory="data"):
        filepath = os.path.join(directory, "system_data.json")
        if not os.path.exists(filepath):
            return False
        with open(filepath, "r") as f:
            data = json.load(f)
            for k, v in data.get("participants", {}).items():
                p = Participant(v["p_id"], v["name"], v["email"], v["mobile"], k)
                p.registered_events = v["evs"]
                self.participants[k] = p
            for k, v in data.get("events", {}).items():
                self.events[k] = Event(k, v["name"], v["category"],
                                       v["date"], v["venue"], v["fee"])
                self.categories.add(v["category"])
        return True

    def export_summary_csv(self, filename="event_summary_report.csv"):
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Event ID", "Event Name", "Category",
                             "Scheduled Date", "Registration Cost"])
            for ev in self.events.values():
                writer.writerow([ev.event_id, ev.event_name,
                                 ev.category, ev.date, ev.registration_fee])
        return filename


# ══════════════════════════════════════════════════════════
#  TKINTER GUI APPLICATION
# ══════════════════════════════════════════════════════════
BG        = "#1e1e2e"   # dark navy background
PANEL     = "#2a2a3e"   # slightly lighter panel
ACCENT    = "#7c6af7"   # purple accent
ACCENT2   = "#56d4a0"   # teal/green for success
TEXT      = "#cdd6f4"   # soft white text
SUBTEXT   = "#a6adc8"   # muted text
ENTRY_BG  = "#313244"   # entry field background
BTN_FG    = "#ffffff"
DANGER    = "#f38ba8"   # red for errors
FONT_HEAD = ("Segoe UI", 15, "bold")
FONT_SUB  = ("Segoe UI", 10)
FONT_BTN  = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 10)


def styled_button(parent, text, command, color=ACCENT, **kw):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=BTN_FG, activebackground=color,
        font=FONT_BTN, relief="flat", cursor="hand2",
        padx=12, pady=6, **kw
    )
    return btn


def form_label(parent, text):
    return tk.Label(parent, text=text, bg=PANEL, fg=SUBTEXT, font=FONT_SUB, anchor="w")


def form_entry(parent, width=28):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 font=FONT_SUB, relief="flat", width=width, bd=4)
    return e


def section_title(parent, text):
    return tk.Label(parent, text=text, bg=PANEL, fg=ACCENT,
                    font=("Segoe UI", 12, "bold"), anchor="w")


class EMSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.ems = EventManagementSystem()
        self.title("Event Management System")
        self.geometry("1050x680")
        self.resizable(True, True)
        self.configure(bg=BG)
        self._build_layout()
        self._auto_load()

    # ── LAYOUT ────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ──
        sidebar = tk.Frame(self, bg=PANEL, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🗓 EMS", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(pady=(24, 4))
        tk.Label(sidebar, text="Event Management System", bg=PANEL,
                 fg=SUBTEXT, font=("Segoe UI", 8)).pack(pady=(0, 24))

        self.pages = {}
        nav_items = [
            ("👤  Register Participant", "register"),
            ("🎉  Create Event",         "create_event"),
            ("📋  View Events",          "view_events"),
            ("🔍  Search Event",         "search"),
            ("🔗  Link Participant",     "link"),
            ("💳  Process Payment",      "payment"),
            ("🏅  Issue Certificate",    "certificate"),
            ("📊  Analytics & CSV",      "analytics"),
            ("💾  Save / Load",          "saveload"),
        ]
        for label, key in nav_items:
            btn = tk.Button(
                sidebar, text=label, command=lambda k=key: self._show_page(k),
                bg=PANEL, fg=TEXT, activebackground=ACCENT,
                font=("Segoe UI", 10), relief="flat", anchor="w",
                padx=16, pady=8, cursor="hand2"
            )
            btn.pack(fill="x")

        # ── Main area ──
        self.main_area = tk.Frame(self, bg=BG)
        self.main_area.pack(side="left", fill="both", expand=True)

        # Build all page frames
        self._build_register_page()
        self._build_create_event_page()
        self._build_view_events_page()
        self._build_search_page()
        self._build_link_page()
        self._build_payment_page()
        self._build_certificate_page()
        self._build_analytics_page()
        self._build_saveload_page()

        self._show_page("register")

    def _show_page(self, key):
        for k, frame in self.pages.items():
            frame.place_forget()
        self.pages[key].place(relx=0, rely=0, relwidth=1, relheight=1)

    # ── STATUS BAR helper ──────────────────────────────────
    def _status_bar(self, parent):
        bar = tk.Label(parent, text="", bg=BG, fg=ACCENT2,
                       font=("Segoe UI", 9), anchor="w")
        bar.pack(fill="x", padx=20, pady=(4, 0))
        return bar

    def _set_status(self, bar, msg, ok=True):
        bar.config(text=msg, fg=ACCENT2 if ok else DANGER)

    # ── OUTPUT BOX helper ──────────────────────────────────
    def _output_box(self, parent, height=10):
        box = scrolledtext.ScrolledText(
            parent, bg=ENTRY_BG, fg=TEXT, font=FONT_MONO,
            relief="flat", height=height, state="disabled",
            insertbackground=TEXT
        )
        box.pack(fill="both", expand=True, padx=20, pady=8)
        return box

    def _write_output(self, box, text):
        box.config(state="normal")
        box.delete("1.0", "end")
        box.insert("end", text)
        box.config(state="disabled")

    # ══ PAGE 1 — REGISTER PARTICIPANT ═════════════════════
    def _build_register_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["register"] = f

        tk.Label(f, text="Register Participant", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))
        tk.Label(f, text="Add a new participant to the system.",
                 bg=BG, fg=SUBTEXT, font=FONT_SUB).pack(anchor="w", padx=20)

        panel = tk.Frame(f, bg=PANEL, bd=0)
        panel.pack(fill="x", padx=20, pady=12)

        fields = [
            ("National ID", "rp_pid"),
            ("Full Name",   "rp_name"),
            ("Email",       "rp_email"),
            ("Mobile",      "rp_mobile"),
            ("Participant ID", "rp_partid"),
        ]
        self._entries = getattr(self, "_entries", {})
        for i, (lbl, key) in enumerate(fields):
            form_label(panel, lbl).grid(row=i, column=0, sticky="w", padx=16, pady=6)
            e = form_entry(panel)
            e.grid(row=i, column=1, padx=16, pady=6)
            self._entries[key] = e

        status = self._status_bar(f)
        styled_button(f, "Register Participant",
                      lambda: self._do_register(status)).pack(anchor="w", padx=20, pady=4)

    def _do_register(self, status):
        e = self._entries
        try:
            self.ems.register_participant(
                e["rp_pid"].get(), e["rp_name"].get(),
                e["rp_email"].get(), e["rp_mobile"].get(),
                e["rp_partid"].get()
            )
            self._set_status(status, f"✔ Participant '{e['rp_partid'].get()}' registered successfully.")
            for k in ["rp_pid","rp_name","rp_email","rp_mobile","rp_partid"]:
                e[k].delete(0, "end")
        except Exception as ex:
            self._set_status(status, f"✘ {ex}", ok=False)

    # ══ PAGE 2 — CREATE EVENT ═════════════════════════════
    def _build_create_event_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["create_event"] = f

        tk.Label(f, text="Create Event", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        panel = tk.Frame(f, bg=PANEL)
        panel.pack(fill="x", padx=20, pady=12)

        fields = [
            ("Event ID",     "ce_id"),
            ("Event Name",   "ce_name"),
            ("Category",     "ce_cat"),
            ("Date (YYYY-MM-DD)", "ce_date"),
            ("Venue",        "ce_venue"),
            ("Fee (₹)",      "ce_fee"),
        ]
        self._entries = getattr(self, "_entries", {})
        for i, (lbl, key) in enumerate(fields):
            form_label(panel, lbl).grid(row=i, column=0, sticky="w", padx=16, pady=6)
            e = form_entry(panel)
            e.grid(row=i, column=1, padx=16, pady=6)
            self._entries[key] = e

        status = self._status_bar(f)
        styled_button(f, "Create Event",
                      lambda: self._do_create_event(status)).pack(anchor="w", padx=20, pady=4)

    def _do_create_event(self, status):
        e = self._entries
        try:
            self.ems.create_event(
                e["ce_id"].get(), e["ce_name"].get(), e["ce_cat"].get(),
                e["ce_date"].get(), e["ce_venue"].get(), e["ce_fee"].get()
            )
            self._set_status(status, f"✔ Event '{e['ce_id'].get()}' created.")
            for k in ["ce_id","ce_name","ce_cat","ce_date","ce_venue","ce_fee"]:
                e[k].delete(0, "end")
        except Exception as ex:
            self._set_status(status, f"✘ {ex}", ok=False)

    # ══ PAGE 3 — VIEW EVENTS ══════════════════════════════
    def _build_view_events_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["view_events"] = f

        header = tk.Frame(f, bg=BG)
        header.pack(fill="x", padx=20, pady=(20, 8))
        tk.Label(header, text="All Events", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(side="left")
        styled_button(header, "↻ Refresh",
                      lambda: self._do_view_events(tree)).pack(side="right")

        cols = ("ID", "Name", "Category", "Date", "Venue", "Fee (₹)")
        tree = ttk.Treeview(f, columns=cols, show="headings", height=18)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=ENTRY_BG, foreground=TEXT,
                        fieldbackground=ENTRY_BG, font=FONT_SUB, rowheight=26)
        style.configure("Treeview.Heading",
                        background=PANEL, foreground=ACCENT,
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=130)
        tree.pack(fill="both", expand=True, padx=20, pady=4)
        self._event_tree = tree

    def _do_view_events(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        for ev in self.ems.get_events_sorted_by_date():
            tree.insert("", "end", values=(
                ev.event_id, ev.event_name, ev.category,
                ev.date, ev.venue, f"₹{ev.registration_fee:.2f}"
            ))

    # ══ PAGE 4 — SEARCH EVENT ═════════════════════════════
    def _build_search_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["search"] = f

        tk.Label(f, text="Search Event (Recursive)", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        row = tk.Frame(f, bg=BG)
        row.pack(anchor="w", padx=20, pady=8)
        form_label(row, "Event ID:").grid(row=0, column=0, padx=(0, 8))
        self._entries = getattr(self, "_entries", {})
        se = form_entry(row, width=20)
        se.grid(row=0, column=1, padx=4)
        self._entries["search_id"] = se

        out = self._output_box(f, height=6)
        styled_button(f, "Search",
                      lambda: self._do_search(out)).pack(anchor="w", padx=20)

    def _do_search(self, out):
        target = self._entries["search_id"].get().strip()
        keys = list(self.ems.events.keys())
        match = self.ems.search_event_recursive(keys, target)
        if match:
            self._write_output(out,
                f"✔ Event Found!\n\n"
                f"  ID       : {match.event_id}\n"
                f"  Name     : {match.event_name}\n"
                f"  Category : {match.category}\n"
                f"  Date     : {match.date}\n"
                f"  Venue    : {match.venue}\n"
                f"  Fee      : ₹{match.registration_fee:.2f}")
        else:
            self._write_output(out, f"✘ No event found with ID: '{target}'")

    # ══ PAGE 5 — LINK PARTICIPANT TO EVENT ════════════════
    def _build_link_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["link"] = f

        tk.Label(f, text="Register Participant to Event", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        panel = tk.Frame(f, bg=PANEL)
        panel.pack(fill="x", padx=20, pady=12)

        self._entries = getattr(self, "_entries", {})
        form_label(panel, "Participant ID").grid(row=0, column=0, sticky="w", padx=16, pady=8)
        lpe = form_entry(panel)
        lpe.grid(row=0, column=1, padx=16, pady=8)
        self._entries["link_pid"] = lpe

        form_label(panel, "Event ID").grid(row=1, column=0, sticky="w", padx=16, pady=8)
        lee = form_entry(panel)
        lee.grid(row=1, column=1, padx=16, pady=8)
        self._entries["link_eid"] = lee

        status = self._status_bar(f)
        styled_button(f, "Link Participant → Event",
                      lambda: self._do_link(status)).pack(anchor="w", padx=20, pady=4)

    def _do_link(self, status):
        pid = self._entries["link_pid"].get().strip()
        eid = self._entries["link_eid"].get().strip()
        try:
            if pid not in self.ems.participants:
                raise KeyError(f"Participant ID '{pid}' not found.")
            self.ems.validate_event_id(eid)
            self.ems.participants[pid].register_event(eid)
            self._set_status(status, f"✔ Participant '{pid}' linked to event '{eid}'.")
        except Exception as ex:
            self._set_status(status, f"✘ {ex}", ok=False)

    # ══ PAGE 6 — PROCESS PAYMENT ══════════════════════════
    def _build_payment_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["payment"] = f

        tk.Label(f, text="Process Payment", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        panel = tk.Frame(f, bg=PANEL)
        panel.pack(fill="x", padx=20, pady=12)

        self._entries = getattr(self, "_entries", {})
        form_label(panel, "Transaction ID").grid(row=0, column=0, sticky="w", padx=16, pady=8)
        pte = form_entry(panel)
        pte.grid(row=0, column=1, padx=16, pady=8)
        self._entries["pay_id"] = pte

        form_label(panel, "Amount (₹)").grid(row=1, column=0, sticky="w", padx=16, pady=8)
        pae = form_entry(panel)
        pae.grid(row=1, column=1, padx=16, pady=8)
        self._entries["pay_amt"] = pae

        out = self._output_box(f, height=8)
        styled_button(f, "Process Payment",
                      lambda: self._do_payment(out)).pack(anchor="w", padx=20, pady=4)

    def _do_payment(self, out):
        try:
            pay = self.ems.process_payment(
                self._entries["pay_id"].get(),
                self._entries["pay_amt"].get()
            )
            self._write_output(out, pay.generate_receipt())
            self._entries["pay_id"].delete(0, "end")
            self._entries["pay_amt"].delete(0, "end")
        except Exception as ex:
            self._write_output(out, f"✘ {ex}")

    # ══ PAGE 7 — CERTIFICATE ══════════════════════════════
    def _build_certificate_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["certificate"] = f

        tk.Label(f, text="Issue Certificate", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        panel = tk.Frame(f, bg=PANEL)
        panel.pack(fill="x", padx=20, pady=12)

        self._entries = getattr(self, "_entries", {})
        form_label(panel, "Participant Name").grid(row=0, column=0, sticky="w", padx=16, pady=8)
        cne = form_entry(panel)
        cne.grid(row=0, column=1, padx=16, pady=8)
        self._entries["cert_name"] = cne

        form_label(panel, "Event Name").grid(row=1, column=0, sticky="w", padx=16, pady=8)
        cee = form_entry(panel)
        cee.grid(row=1, column=1, padx=16, pady=8)
        self._entries["cert_event"] = cee

        out = self._output_box(f, height=12)
        styled_button(f, "Generate Certificate",
                      lambda: self._do_certificate(out)).pack(anchor="w", padx=20, pady=4)

    def _do_certificate(self, out):
        name  = self._entries["cert_name"].get().strip()
        event = self._entries["cert_event"].get().strip()
        if not name or not event:
            self._write_output(out, "✘ Please enter both participant name and event name.")
            return
        cert = Certificate("CERT-101", name, event)
        self._write_output(out, cert.generate_certificate())

    # ══ PAGE 8 — ANALYTICS ════════════════════════════════
    def _build_analytics_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["analytics"] = f

        tk.Label(f, text="Analytics & Reports", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(anchor="w", padx=20, pady=8)

        out = self._output_box(f, height=14)

        styled_button(btn_row, "📊 Show Statistics",
                      lambda: self._do_stats(out)).pack(side="left", padx=4)
        styled_button(btn_row, "📄 Export CSV",
                      lambda: self._do_csv(out), color="#56d4a0").pack(side="left", padx=4)

    def _do_stats(self, out):
        stats = self.ems.get_system_statistics()
        lines = ["─── System Statistics ───\n"]
        for k, v in stats.items():
            lines.append(f"  {k:<38}: {v}")
        lines.append("\n─── Event Categories ───")
        for cat in sorted(self.ems.categories):
            lines.append(f"  • {cat}")
        self._write_output(out, "\n".join(lines))

    def _do_csv(self, out):
        try:
            fname = self.ems.export_summary_csv()
            self._write_output(out, f"✔ CSV exported → {os.path.abspath(fname)}")
        except Exception as ex:
            self._write_output(out, f"✘ {ex}")

    # ══ PAGE 9 — SAVE / LOAD ══════════════════════════════
    def _build_saveload_page(self):
        f = tk.Frame(self.main_area, bg=BG)
        self.pages["saveload"] = f

        tk.Label(f, text="Save / Load Data", bg=BG,
                 fg=TEXT, font=FONT_HEAD).pack(anchor="w", padx=20, pady=(20, 4))

        out = self._output_box(f, height=10)

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(anchor="w", padx=20, pady=8)

        styled_button(btn_row, "💾  Save Data",
                      lambda: self._do_save(out)).pack(side="left", padx=6)
        styled_button(btn_row, "📂  Load Data",
                      lambda: self._do_load(out), color=ACCENT2).pack(side="left", padx=6)

    def _do_save(self, out):
        try:
            self.ems.save_data()
            self._write_output(out, "✔ Data saved to data/system_data.json")
        except Exception as ex:
            self._write_output(out, f"✘ {ex}")

    def _do_load(self, out):
        try:
            ok = self.ems.load_data()
            if ok:
                self._write_output(out,
                    f"✔ Data loaded.\n"
                    f"  Participants : {len(self.ems.participants)}\n"
                    f"  Events       : {len(self.ems.events)}")
            else:
                self._write_output(out, "ℹ No saved data found. Starting fresh.")
        except Exception as ex:
            self._write_output(out, f"✘ {ex}")

    # ── Auto-load on startup ───────────────────────────────
    def _auto_load(self):
        self.ems.load_data()


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = EMSApp()
    app.mainloop()
