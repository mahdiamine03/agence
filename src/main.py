import customtkinter as ctk
from tkinter import messagebox, StringVar
import tkinter.ttk as ttk
from src.database import DatabaseManager
from src.auth import AuthManager
from src.pdf_generator import PDFGenerator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sys
import os

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agence de Voyage Management System Pro")
        self.geometry("1280x800")

        # Initialize Managers
        self.db = DatabaseManager()
        self.auth = AuthManager(self.db)

        # Ensure default admin exists
        if not self.db.get_user_by_username("admin"):
            self.auth.register_user("admin", "admin123", "admin")

        self.current_user = None

        # Container for frames
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        self.show_login()

    def show_login(self):
        self.clear_frames()
        login_frame = LoginFrame(self.container, self)
        login_frame.pack(fill="both", expand=True)
        self.frames['login'] = login_frame

    def show_dashboard(self):
        self.clear_frames()
        dashboard = MainLayout(self.container, self)
        dashboard.pack(fill="both", expand=True)
        self.frames['dashboard'] = dashboard

    def clear_frames(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def logout(self):
        self.current_user = None
        self.show_login()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label = ctk.CTkLabel(self.frame, text="Agency Login", font=("Roboto Medium", 24))
        self.label.pack(pady=(40, 20))

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username", width=280, height=40)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=280, height=40)
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", lambda event: self.login_event())

        self.login_button = ctk.CTkButton(self.frame, text="Login", width=280, height=40, command=self.login_event)
        self.login_button.pack(pady=30)

        self.status_label = ctk.CTkLabel(self.frame, text="", font=("Roboto", 12))
        self.status_label.pack(pady=5)

    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.controller.auth.login(username, password)
        if user:
            self.controller.db.update_last_login(username)
            self.status_label.configure(text="Connection Successful", text_color="green")
            self.controller.current_user = user
            self.after(500, self.controller.show_dashboard)
        else:
            self.status_label.configure(text="Invalid Credentials", text_color="red")
            messagebox.showerror("Login Failed", "Invalid username or password")


class MainLayout(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Travel Agency Pro", font=("Roboto Medium", 22))
        self.logo_label.pack(pady=40)

        self.create_nav_button("Dashboard", "DashboardFrame")
        self.create_nav_button("Clients", "ClientFrame")
        self.create_nav_button("Bookings", "BookingFrame")

        # Admin only registration
        if self.controller.current_user and self.controller.current_user['role'] == 'admin':
            self.btn_register = ctk.CTkButton(self.sidebar, text="Register Agent", fg_color="green", hover_color="darkgreen", command=self.open_register_window)
            self.btn_register.pack(pady=10, padx=20)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", fg_color="red", hover_color="darkred", command=self.controller.logout)
        self.btn_logout.pack(side="bottom", pady=40, padx=20)

        # Content Area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)

        self.current_frame = None
        self.show_frame("DashboardFrame")

    def create_nav_button(self, text, frame_name):
        btn = ctk.CTkButton(self.sidebar, text=text, height=40, command=lambda: self.show_frame(frame_name))
        btn.pack(pady=10, padx=20)

    def show_frame(self, frame_name):
        if self.current_frame:
            self.current_frame.destroy()

        if frame_name == "DashboardFrame":
            self.current_frame = DashboardFrame(self.content_area, self.controller)
        elif frame_name == "ClientFrame":
            self.current_frame = ClientFrame(self.content_area, self.controller)
        elif frame_name == "BookingFrame":
            self.current_frame = BookingFrame(self.content_area, self.controller)

        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def open_register_window(self):
        RegisterAgentWindow(self.controller)


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title = ctk.CTkLabel(self, text="Dashboard Overview", font=("Roboto Medium", 28))
        self.title.pack(pady=20, anchor="w")

        stats = self.controller.db.get_stats()

        # KPI Cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=20)

        self.create_kpi_card(self.cards_frame, "Total Clients", str(stats['total_clients']), 0)
        self.create_kpi_card(self.cards_frame, "Monthly Revenue", f"${stats['monthly_revenue']:,.2f}", 1)
        self.create_kpi_card(self.cards_frame, "Pending Bookings", str(stats['pending_bookings']), 2)

        # Matplotlib Chart
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, pady=20)

        self.create_chart()

    def create_kpi_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, height=140)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = ctk.CTkLabel(card, text=title, font=("Roboto", 16))
        lbl_title.pack(pady=(20, 5))

        lbl_val = ctk.CTkLabel(card, text=value, font=("Roboto Medium", 32), text_color="#3B8ED0")
        lbl_val.pack(pady=10)

    def create_chart(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        data = self.controller.db.get_monthly_revenue_stats()
        months = data['labels']
        revenue = data['values']

        ax.bar(months, revenue, color='#3B8ED0')
        ax.set_title("Revenue Trend (Last 6 Months)")
        ax.set_ylabel("Revenue ($)")

        # Styling for Dark Mode
        fig.patch.set_facecolor('#2B2B2B')
        ax.set_facecolor('#2B2B2B')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class ClientFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Split View
        self.left_pane = ctk.CTkFrame(self, width=300)
        self.left_pane.pack(side="left", fill="y", padx=(0, 10))

        self.right_pane = ctk.CTkFrame(self)
        self.right_pane.pack(side="right", fill="both", expand=True)

        # Left Pane: List & Search
        ctk.CTkLabel(self.left_pane, text="Clients", font=("Roboto Medium", 20)).pack(pady=10)

        self.search_entry = ctk.CTkEntry(self.left_pane, placeholder_text="Search...")
        self.search_entry.pack(fill="x", padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_client)

        self.client_list_frame = ctk.CTkScrollableFrame(self.left_pane)
        self.client_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.add_btn = ctk.CTkButton(self.left_pane, text="+ New Client", command=self.open_add_client_window)
        self.add_btn.pack(pady=10, padx=10)

        self.delete_btn = ctk.CTkButton(self.left_pane, text="Delete Selected", fg_color="red", hover_color="darkred", command=self.delete_client)
        self.delete_btn.pack(pady=10, padx=10)

        # Right Pane: Details (Tabs)
        self.tabview = ctk.CTkTabview(self.right_pane)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabview.add("Client Info")
        self.tabview.add("History")

        self.selected_client_id = None
        self.info_entries = {}
        self.create_info_tab()

        self.load_client_list()

    def create_info_tab(self):
        tab = self.tabview.tab("Client Info")
        fields = ["First Name", "Last Name", "Passport No", "Phone", "Email", "Nationality", "DOB"]

        for i, field in enumerate(fields):
            ctk.CTkLabel(tab, text=field).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry = ctk.CTkEntry(tab, width=300)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            self.info_entries[field] = entry

        self.save_btn = ctk.CTkButton(tab, text="Update Details", command=self.update_client_details)
        self.save_btn.grid(row=len(fields), column=1, pady=20, sticky="w")
        self.save_btn.configure(state="disabled")

    def load_client_list(self, query=""):
        for widget in self.client_list_frame.winfo_children():
            widget.destroy()

        if query:
            clients = self.controller.db.search_clients(query)
        else:
            clients = self.controller.db.get_all_clients()

        for client in clients:
            btn = ctk.CTkButton(self.client_list_frame,
                                text=f"{client['last_name']}, {client['first_name']} ({client['passport_no']})",
                                fg_color="transparent", border_width=1,
                                command=lambda c=client: self.select_client(c))
            btn.pack(fill="x", pady=2)

    def search_client(self, event):
        self.load_client_list(self.search_entry.get())

    def select_client(self, client):
        self.selected_client_id = client['id']
        self.save_btn.configure(state="normal")

        # Fill Info Tab
        mapping = {
            "First Name": client['first_name'],
            "Last Name": client['last_name'],
            "Passport No": client['passport_no'],
            "Phone": client['phone'],
            "Email": client['email'],
            "Nationality": client['nationality'],
            "DOB": client['dob']
        }
        for field, value in mapping.items():
            self.info_entries[field].delete(0, "end")
            self.info_entries[field].insert(0, value if value else "")

        # Fill History Tab
        self.load_client_history(client['id'])

    def load_client_history(self, client_id):
        tab = self.tabview.tab("History")
        for widget in tab.winfo_children():
            widget.destroy()

        bookings = self.controller.db.get_bookings_by_client(client_id)

        columns = ("ID", "Destination", "Service", "Date", "Cost", "Status")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.pack(fill="both", expand=True)

        for b in bookings:
            tree.insert("", "end", values=(b['id'], b['destination'], b['service_type'], b['start_date'], f"${b['selling_price']}", b['status']))

    def update_client_details(self):
        if not self.selected_client_id:
            return

        data = {k: v.get() for k, v in self.info_entries.items()}
        success = self.controller.db.update_client(
            self.selected_client_id, data["Passport No"], data["First Name"], data["Last Name"],
            data["Phone"], data["Email"], data["Nationality"], data["DOB"]
        )
        if success:
            messagebox.showinfo("Success", "Client details updated.")
            self.load_client_list()
        else:
            messagebox.showerror("Error", "Update failed.")

    def open_add_client_window(self):
        AddClientWindow(self.controller, self.load_client_list)

    def delete_client(self):
        if not self.selected_client_id:
            messagebox.showwarning("Warning", "Select a client first")
            return

        if messagebox.askyesno("Confirm", "Are you sure? This will delete all associated bookings."):
            self.controller.db.delete_client(self.selected_client_id)
            self.selected_client_id = None
            self.save_btn.configure(state="disabled")
            self.load_client_list()
            # Clear entries
            for entry in self.info_entries.values():
                entry.delete(0, "end")


class BookingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Left: Booking Form
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.form_frame, text="New Booking", font=("Roboto Medium", 20)).pack(pady=10)

        # Client Selector
        ctk.CTkLabel(self.form_frame, text="Client").pack(pady=5)
        self.client_var = StringVar()
        self.client_combo = ctk.CTkComboBox(self.form_frame, variable=self.client_var, values=self.get_client_options())
        self.client_combo.pack(pady=5)

        # Service Type
        ctk.CTkLabel(self.form_frame, text="Service Type").pack(pady=5)
        self.service_var = StringVar(value="Flight")
        self.radio_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.radio_frame.pack()
        ctk.CTkRadioButton(self.radio_frame, text="Flight", variable=self.service_var, value="Flight").pack(side="left", padx=5)
        ctk.CTkRadioButton(self.radio_frame, text="Hotel", variable=self.service_var, value="Hotel").pack(side="left", padx=5)

        # Fields
        self.entries = {}
        fields = ["Destination", "Provider", "Start Date", "End Date"]
        for field in fields:
            ctk.CTkLabel(self.form_frame, text=field).pack(pady=2)
            entry = ctk.CTkEntry(self.form_frame)
            entry.pack(pady=2)
            self.entries[field] = entry

        # Financials
        ctk.CTkLabel(self.form_frame, text="Net Price ($)").pack(pady=2)
        self.net_price = ctk.CTkEntry(self.form_frame)
        self.net_price.pack(pady=2)
        self.net_price.bind("<KeyRelease>", self.calc_selling_price)

        ctk.CTkLabel(self.form_frame, text="Margin ($)").pack(pady=2)
        self.margin = ctk.CTkEntry(self.form_frame)
        self.margin.pack(pady=2)
        self.margin.bind("<KeyRelease>", self.calc_selling_price)

        ctk.CTkLabel(self.form_frame, text="Selling Price ($)").pack(pady=2)
        self.selling_price = ctk.CTkEntry(self.form_frame) # Read-only ideally
        self.selling_price.pack(pady=2)

        self.create_btn = ctk.CTkButton(self.form_frame, text="Create Booking", command=self.create_booking)
        self.create_btn.pack(pady=20)

        # Right: Booking List
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(self.list_frame, columns=("ID", "Client", "Service", "Dest", "Price", "Status"), show="headings")
        for col in ("ID", "Client", "Service", "Dest", "Price", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        self.tree.pack(fill="both", expand=True)

        # Actions
        self.pdf_btn = ctk.CTkButton(self.list_frame, text="Download Invoice PDF", command=self.generate_pdf)
        self.pdf_btn.pack(pady=10)

        self.load_bookings()

    def get_client_options(self):
        clients = self.controller.db.get_all_clients()
        return [f"{c['id']} - {c['last_name']}" for c in clients]

    def calc_selling_price(self, event):
        try:
            net = float(self.net_price.get())
            margin = float(self.margin.get())
            self.selling_price.delete(0, "end")
            self.selling_price.insert(0, str(net + margin))
        except ValueError:
            pass

    def create_booking(self):
        try:
            client_str = self.client_var.get()
            if not client_str: raise ValueError("Select a client")
            client_id = client_str.split(" - ")[0]

            data = {k: v.get() for k, v in self.entries.items()}
            net = float(self.net_price.get())
            selling = float(self.selling_price.get())

            success = self.controller.db.add_booking(
                client_id, self.service_var.get(), data["Destination"], data["Provider"],
                data["Start Date"], data["End Date"], net, selling
            )

            if success:
                messagebox.showinfo("Success", "Booking created.")
                self.load_bookings()
            else:
                messagebox.showerror("Error", "Failed to create booking.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Input: {e}")

    def load_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        bookings = self.controller.db.get_all_bookings()
        for b in bookings:
            client_name = f"{b['last_name']}, {b['first_name']}"
            self.tree.insert("", "end", values=(b['id'], client_name, b['service_type'], b['destination'], f"${b['selling_price']}", b['status']))

    def generate_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a booking first.")
            return

        booking_id = self.tree.item(selected[0], "values")[0]
        booking_data = self.controller.db.get_booking_by_id(booking_id)

        if booking_data:
            path = PDFGenerator.generate_invoice(dict(booking_data))
            messagebox.showinfo("PDF Generated", f"Invoice saved at:\n{path}")
        else:
            messagebox.showerror("Error", "Could not fetch booking data.")


class AddClientWindow(ctk.CTkToplevel):
    def __init__(self, controller, callback):
        super().__init__()
        self.controller = controller
        self.callback = callback
        self.title("New Client")
        self.geometry("400x500")
        self.attributes("-topmost", True)

        self.entries = {}
        fields = ["Passport No", "First Name", "Last Name", "Phone", "Email", "Nationality", "DOB"]

        for field in fields:
            ctk.CTkLabel(self, text=field).pack(pady=2)
            entry = ctk.CTkEntry(self, width=250)
            entry.pack(pady=2)
            self.entries[field] = entry

        ctk.CTkButton(self, text="Save Client", command=self.save).pack(pady=20)

    def save(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if not data["Passport No"] or not data["Last Name"]:
            messagebox.showerror("Error", "Passport and Name are required.")
            return

        success = self.controller.db.add_client(
            data["Passport No"], data["First Name"], data["Last Name"],
            data["Phone"], data["Email"], data["Nationality"], data["DOB"]
        )

        if success:
            messagebox.showinfo("Success", "Client Added")
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Passport number already exists.")

class RegisterAgentWindow(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Register New Agent")
        self.geometry("350x400")
        self.attributes("-topmost", True)

        ctk.CTkLabel(self, text="New Agent Username").pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(self, width=250)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Password").pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self, width=250, show="*")
        self.password_entry.pack(pady=5)

        self.register_btn = ctk.CTkButton(self, text="Register", command=self.register)
        self.register_btn.pack(pady=30)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required")
            return

        success = self.controller.auth.register_user(username, password)
        if success:
            messagebox.showinfo("Success", "Agent registered successfully")
            self.destroy()
        else:
            messagebox.showerror("Error", "Username already exists")

if __name__ == "__main__":
    app = TravelApp()
    app.mainloop()
