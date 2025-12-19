import customtkinter as ctk
from tkinter import messagebox, StringVar
from src.database import DatabaseManager
from src.auth import AuthManager
import sys

# Configure appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TravelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agence de Voyage Management System")
        self.geometry("1100x700")

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

        self.frame = ctk.CTkFrame(self, width=350, height=400, corner_radius=15)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label = ctk.CTkLabel(self.frame, text="Agency Login", font=("Roboto Medium", 24))
        self.label.pack(pady=30)

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self.frame, text="Login", width=250, command=self.login_event)
        self.login_button.pack(pady=20)

    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.controller.auth.login(username, password)
        if user:
            self.controller.current_user = user
            self.controller.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")


class MainLayout(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Travel Agency", font=("Roboto Medium", 20))
        self.logo_label.pack(pady=30)

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_frame("DashboardFrame"))
        self.btn_dashboard.pack(pady=10, padx=20)

        self.btn_clients = ctk.CTkButton(self.sidebar, text="Clients", command=lambda: self.show_frame("ClientFrame"))
        self.btn_clients.pack(pady=10, padx=20)

        self.btn_bookings = ctk.CTkButton(self.sidebar, text="Bookings", command=lambda: self.show_frame("BookingFrame"))
        self.btn_bookings.pack(pady=10, padx=20)

        # Admin only registration button (simplified check, usually check role)
        if self.controller.current_user and self.controller.current_user['role'] == 'admin':
            self.btn_register = ctk.CTkButton(self.sidebar, text="Register Agent", fg_color="green", hover_color="darkgreen", command=self.open_register_window)
            self.btn_register.pack(pady=10, padx=20)

        self.btn_logout = ctk.CTkButton(self.sidebar, text="Logout", fg_color="red", hover_color="darkred", command=self.controller.logout)
        self.btn_logout.pack(side="bottom", pady=30, padx=20)

    def open_register_window(self):
        RegisterAgentWindow(self.controller)

        # Content Area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_area.pack(side="right", fill="both", expand=True)

        self.current_frame = None
        self.show_frame("DashboardFrame")

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


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title = ctk.CTkLabel(self, text="Dashboard Overview", font=("Roboto Medium", 24))
        self.title.pack(pady=20, anchor="w")

        stats = self.controller.db.get_stats()

        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", pady=20)

        self.create_stat_card(self.stats_frame, "Total Clients", str(stats['clients']), 0)
        self.create_stat_card(self.stats_frame, "Active Bookings", str(stats['bookings']), 1)

    def create_stat_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, height=150)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = ctk.CTkLabel(card, text=title, font=("Roboto", 16))
        lbl_title.pack(pady=(20, 5))

        lbl_val = ctk.CTkLabel(card, text=value, font=("Roboto Medium", 32))
        lbl_val.pack(pady=10)


class ClientFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=10)

        self.title = ctk.CTkLabel(self.header_frame, text="Client Management", font=("Roboto Medium", 24))
        self.title.pack(side="left")

        self.add_btn = ctk.CTkButton(self.header_frame, text="+ Add Client", command=self.open_add_client_window)
        self.add_btn.pack(side="right")

        # Search
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search client...")
        self.search_entry.pack(fill="x", pady=10)
        self.search_entry.bind("<Return>", self.search_client)

        # List Area (Using ScrollableFrame as basic list, since CTk doesn't have native Treeview)
        # Ideally we'd use CTkTable or standard Treeview styled. Let's use standard Treeview with style.
        import tkinter.ttk as ttk
        import tkinter as tk

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white", rowheight=25)
        style.configure("Treeview.Heading", background="#333333", foreground="white", relief="flat")
        style.map("Treeview", background=[("selected", "#1f538d")])

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Passport", "Phone", "Email"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Full Name")
        self.tree.heading("Passport", text="Passport")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")

        self.tree.column("ID", width=30)
        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.bind("<Double-1>", self.on_client_double_click)

        # Buttons
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=10)
        self.refresh_btn = ctk.CTkButton(self.action_frame, text="Refresh", command=self.load_clients)
        self.refresh_btn.pack(side="left")

        self.delete_btn = ctk.CTkButton(self.action_frame, text="Delete Selected", fg_color="red", command=self.delete_client)
        self.delete_btn.pack(side="right")

        self.load_clients()

    def load_clients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        clients = self.controller.db.get_all_clients()
        for client in clients:
            self.tree.insert("", "end", values=(client['id'], client['full_name'], client['passport_number'], client['phone'], client['email']))

    def search_client(self, event=None):
        query = self.search_entry.get()
        if not query:
            self.load_clients()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        clients = self.controller.db.search_clients(query)
        for client in clients:
            self.tree.insert("", "end", values=(client['id'], client['full_name'], client['passport_number'], client['phone'], client['email']))

    def open_add_client_window(self):
        AddClientWindow(self.controller, self.load_clients)

    def on_client_double_click(self, event):
        item = self.tree.selection()[0]
        client_values = self.tree.item(item, "values")
        if client_values:
            EditClientWindow(self.controller, self.load_clients, client_values)

    def delete_client(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        client_id = self.tree.item(selected_item[0], "values")[0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this client?"):
            self.controller.db.delete_client(client_id)
            self.load_clients()


class AddClientWindow(ctk.CTkToplevel):
    def __init__(self, controller, callback):
        super().__init__()
        self.controller = controller
        self.callback = callback
        self.title("Add New Client")
        self.geometry("400x500")

        self.attributes("-topmost", True)

        self.entries = {}
        fields = ["Full Name", "Passport Number", "Phone", "Email", "Address", "Notes"]

        for field in fields:
            lbl = ctk.CTkLabel(self, text=field)
            lbl.pack(pady=(10, 0))
            entry = ctk.CTkEntry(self, width=300)
            entry.pack(pady=(5, 5))
            self.entries[field] = entry

        btn = ctk.CTkButton(self, text="Save Client", command=self.save_client)
        btn.pack(pady=20)

    def save_client(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if not data["Full Name"] or not data["Passport Number"]:
            messagebox.showerror("Error", "Name and Passport are required.")
            return

        success = self.controller.db.add_client(
            data["Full Name"], data["Passport Number"], data["Phone"],
            data["Email"], data["Address"], data["Notes"]
        )

        if success:
            messagebox.showinfo("Success", "Client added successfully.")
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to add client. Passport may be duplicate.")


class EditClientWindow(ctk.CTkToplevel):
    def __init__(self, controller, callback, client_data):
        super().__init__()
        self.controller = controller
        self.callback = callback
        self.client_id = client_data[0]
        self.title("Edit Client")
        self.geometry("400x500")

        self.attributes("-topmost", True)

        self.entries = {}
        fields = ["Full Name", "Passport Number", "Phone", "Email", "Address", "Notes"]

        # Fetch full client details from DB to ensure no data loss
        client = self.controller.db.get_client_by_id(self.client_id)

        defaults = {
            "Full Name": client['full_name'],
            "Passport Number": client['passport_number'],
            "Phone": client['phone'],
            "Email": client['email'],
            "Address": client['address'],
            "Notes": client['notes']
        }

        for field in fields:
            lbl = ctk.CTkLabel(self, text=field)
            lbl.pack(pady=(10, 0))
            entry = ctk.CTkEntry(self, width=300)
            entry.insert(0, defaults[field])
            entry.pack(pady=(5, 5))
            self.entries[field] = entry

        btn = ctk.CTkButton(self, text="Update Client", command=self.update_client)
        btn.pack(pady=20)

    def update_client(self):
        data = {k: v.get() for k, v in self.entries.items()}
        if not data["Full Name"] or not data["Passport Number"]:
            messagebox.showerror("Error", "Name and Passport are required.")
            return

        success = self.controller.db.update_client(
            self.client_id,
            data["Full Name"], data["Passport Number"], data["Phone"],
            data["Email"], data["Address"], data["Notes"]
        )

        if success:
            messagebox.showinfo("Success", "Client updated successfully.")
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to update client.")


class BookingFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title = ctk.CTkLabel(self, text="Booking Management", font=("Roboto Medium", 24))
        self.title.pack(pady=10, anchor="w")

        self.add_btn = ctk.CTkButton(self, text="+ New Booking", command=self.open_add_booking)
        self.add_btn.pack(pady=10, anchor="w")

        # Treeview for bookings
        import tkinter.ttk as ttk

        self.tree = ttk.Treeview(self, columns=("ID", "Client", "Destination", "Date", "Status"), show="headings", height=15)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Client", text="Client")
        self.tree.heading("Destination", text="Destination")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=30)
        self.tree.pack(fill="both", expand=True, pady=10)

        self.load_bookings()

    def load_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        bookings = self.controller.db.get_all_bookings()
        for b in bookings:
            self.tree.insert("", "end", values=(b['id'], b['full_name'], b['destination'], b['travel_date'], b['status']))

    def open_add_booking(self):
        AddBookingWindow(self.controller, self.load_bookings)


class AddBookingWindow(ctk.CTkToplevel):
    def __init__(self, controller, callback):
        super().__init__()
        self.controller = controller
        self.callback = callback
        self.title("New Booking")
        self.geometry("450x600")
        self.attributes("-topmost", True)

        # Client Selection
        ctk.CTkLabel(self, text="Select Client (ID)").pack(pady=(10,0))
        self.client_var = StringVar()
        self.client_combo = ctk.CTkComboBox(self, variable=self.client_var, values=self.get_client_options(), width=300)
        self.client_combo.pack(pady=5)

        self.entries = {}
        fields = ["Destination", "Hotel", "Flight Details", "Travel Date (YYYY-MM-DD)", "Return Date (YYYY-MM-DD)", "Price", "Status"]

        for field in fields:
            ctk.CTkLabel(self, text=field).pack(pady=(5,0))
            entry = ctk.CTkEntry(self, width=300)
            entry.pack(pady=5)
            self.entries[field] = entry

        btn = ctk.CTkButton(self, text="Create Booking", command=self.save_booking)
        btn.pack(pady=20)

    def get_client_options(self):
        clients = self.controller.db.get_all_clients()
        return [f"{c['id']} - {c['full_name']}" for c in clients]

    def save_booking(self):
        client_str = self.client_var.get()
        if not client_str:
            messagebox.showerror("Error", "Please select a client")
            return

        client_id = client_str.split(" - ")[0]
        data = {k: v.get() for k, v in self.entries.items()}

        # Basic validation
        if not data["Destination"] or not data["Price"]:
            messagebox.showerror("Error", "Destination and Price are required.")
            return

        success = self.controller.db.add_booking(
            client_id, data["Destination"], data["Hotel"], data["Flight Details"],
            data["Travel Date (YYYY-MM-DD)"], data["Return Date (YYYY-MM-DD)"],
            data["Price"], data["Status"]
        )

        if success:
            messagebox.showinfo("Success", "Booking created.")
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to create booking.")

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
