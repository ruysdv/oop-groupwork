import tkinter as tk
from tkinter import messagebox, ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, END, EW, LEFT, RIGHT, W, X, Y

from api import changepw_api, login_api, register_api, search_api, find_api
from ui_support import (
    PlaceholderEntry,
    ResourceDialog,
    UserManagerWindow,
    admin_add_resource,
    admin_edit_resource,
    admin_remove_resource,
    download_resource,
    format_resource_info,
)
from windows import CGPW, LOGIN, REGISTER


class Client:
    def __init__(self, root):
        self.root = root
        self.root.title("Resource Download System")
        self.root.geometry("1360x820")
        self.root.minsize(1120, 720)

        self.log_in = False
        self.tokens = None
        self.users = None
        self.power = -1
        self.resource_rows = {}

        self._configure_style()
        self._build_ui()
        self.refresh_buttons()

    def _configure_style(self):
        style = tb.Style()
        style.theme_use("flatly")
        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

    def _build_ui(self):
        self.outer = tb.Frame(self.root, padding=20)
        self.outer.pack(fill=BOTH, expand=True)

        self.header = tb.Frame(self.outer, padding=18, bootstyle="light")
        self.header.pack(fill=X, pady=(0, 16))

        branding = tb.Frame(self.header)
        branding.pack(side=LEFT, fill=X, expand=True)
        tb.Label(
            branding,
            text="Resource Download System",
            font=("Segoe UI", 24, "bold"),
            bootstyle="dark",
        ).pack(anchor=W)
        tb.Label(
            branding,
            text="Browse, manage, and download shared project resources.",
            font=("Segoe UI", 10),
            bootstyle="secondary",
        ).pack(anchor=W, pady=(4, 0))

        self.top_actions = tb.Frame(self.header)
        self.top_actions.pack(side=RIGHT, anchor="ne")

        self.account_actions = tb.Frame(self.top_actions)
        self.account_actions.pack(anchor="e")

        self.username_badge = tb.Label(
            self.account_actions,
            text="Guest",
            padding=(12, 8),
            bootstyle="inverse-primary",
            font=("Segoe UI", 10, "bold"),
        )
        self.register_bt = tb.Button(
            self.account_actions,
            text="Register",
            command=self.reg,
            bootstyle="outline-primary",
            width=16,
        )
        self.login_bt = tb.Button(
            self.account_actions,
            text="Login",
            command=self.log,
            bootstyle="primary",
            width=14,
        )
        self.cpw_bt = tb.Button(
            self.account_actions,
            text="Change Password",
            command=self.cgpw,
            bootstyle="outline-secondary",
            width=18,
        )
        self.logout_bt = tb.Button(
            self.account_actions,
            text="Log Out",
            command=self.dlt,
            bootstyle="outline-danger",
            width=12,
        )

        self.admin_actions = tb.Frame(self.top_actions)
        self.admin_actions.pack(anchor="e", pady=(10, 0))
        self.add_bt = tb.Button(
            self.admin_actions,
            text="Add Resource",
            command=self.open_add_dialog,
            bootstyle="success",
            width=16,
        )
        self.edit_bt = tb.Button(
            self.admin_actions,
            text="Edit Resource",
            command=self.open_edit_dialog,
            bootstyle="warning",
            width=16,
        )
        self.remove_bt = tb.Button(
            self.admin_actions,
            text="Remove Resource",
            command=self.remove_selected_resource,
            bootstyle="danger",
            width=16,
        )
        self.manageuser = tb.Button(
            self.admin_actions,
            text="Manage Users",
            command=self.open_user_manager,
            bootstyle="info",
            width=15,
        )

        self.search_card = tb.Labelframe(
            self.outer, text="Search Resources", padding=18, bootstyle="primary"
        )
        self.search_card.pack(fill=X, pady=(0, 16))
        self.search_card.grid_columnconfigure(0, weight=1)

        self.searchvar = tk.StringVar()
        self.search_entry = tb.Entry(
            self.search_card,
            textvariable=self.searchvar,
            font=("Segoe UI", 14),
        )
        self.search_entry.grid(row=0, column=0, sticky=EW, padx=(0, 14))
        self.search_entry.bind("<Return>", lambda _event: self.searchkw())
        tb.Button(
            self.search_card,
            text="Search Keywords",
            command=self.searchkw,
            bootstyle="primary",
            width=18,
        ).grid(row=0, column=1, padx=(0, 10))
        tb.Button(
            self.search_card,
            text="Search ID",
            command=self.searchid,
            bootstyle="outline-primary",
            width=14,
        ).grid(row=0, column=2)

        self.result_card = tb.Labelframe(
            self.outer, text="Resource Catalog", padding=14, bootstyle="secondary"
        )
        self.result_card.pack(fill=BOTH, expand=True)

        tree_frame = tb.Frame(self.result_card)
        tree_frame.pack(fill=BOTH, expand=True)

        self.result_box = ttk.Treeview(
            tree_frame,
            columns=("title", "info"),
            show="headings",
            selectmode="browse",
        )
        self.result_box.heading("title", text="Title")
        self.result_box.heading("info", text="Information")
        self.result_box.column("title", width=280, anchor=W)
        self.result_box.column("info", width=860, anchor=W)
        self.result_box.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.result_box.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.result_box.configure(yscrollcommand=scrollbar.set)

        self.result_box.bind("<Double-1>", lambda _event: self.open_edit_dialog())

        self.download_card = tb.Labelframe(
            self.outer, text="Download Resource", padding=18, bootstyle="success"
        )
        self.download_card.pack(fill=X, pady=(16, 0))
        self.download_card.grid_columnconfigure(0, weight=1)

        self.download_entry = PlaceholderEntry(
            self.download_card,
            placeholder="Please enter the resource ID:",
            font=("Segoe UI", 14),
        )
        self.download_entry.grid(row=0, column=0, sticky=EW, padx=(0, 14))
        tb.Button(
            self.download_card,
            text="Download",
            command=self.download,
            bootstyle="success",
            width=14,
        ).grid(row=0, column=1)

    def refresh_buttons(self):
        for widget in (
            self.username_badge,
            self.register_bt,
            self.login_bt,
            self.cpw_bt,
            self.logout_bt,
            self.add_bt,
            self.edit_bt,
            self.remove_bt,
            self.manageuser,
        ):
            widget.pack_forget()

        if self.log_in:
            self.username_badge.configure(text=self.users or "User")
            self.username_badge.pack(side=RIGHT, padx=(8, 0))
            self.logout_bt.pack(side=RIGHT, padx=(8, 0))
            self.cpw_bt.pack(side=RIGHT, padx=(8, 0))

            if self.power == 0:
                self.manageuser.pack(side=RIGHT, padx=(8, 0))
                self.remove_bt.pack(side=RIGHT, padx=(8, 0))
                self.edit_bt.pack(side=RIGHT, padx=(8, 0))
                self.add_bt.pack(side=RIGHT)
        else:
            self.register_bt.pack(side=RIGHT, padx=(8, 0))
            self.login_bt.pack(side=RIGHT)

    def _require_login(self):
        if self.tokens:
            return True
        messagebox.showwarning("Login Required", "Please log in before using this feature.")
        return False

    def _clear_results(self):
        self.resource_rows.clear()
        for item in self.result_box.get_children():
            self.result_box.delete(item)

    def _populate_results(self, results):
        self._clear_results()
        if not results:
            self.result_box.insert("", END, values=("No results", ""))
            return

        for resource in results:
            row_id = self.result_box.insert(
                "",
                END,
                values=(resource.get("title"), format_resource_info(resource)),
            )
            self.resource_rows[row_id] = resource

    def _selected_resource(self):
        selection = self.result_box.selection()
        if not selection:
            return None
        return self.resource_rows.get(selection[0])

    def searchkw(self):
        if not self._require_login():
            return

        keyword = self.searchvar.get().strip()
        try:
            results = search_api(keyword, self.tokens)
        except Exception as exc:
            messagebox.showerror("Search Failed", str(exc))
            return
        self._populate_results(results)

    def searchid(self):
        if not self._require_login():
            return

        raw_id = self.searchvar.get().strip()
        if not raw_id:
            messagebox.showwarning("Missing Resource ID", "Please enter a resource ID.")
            return

        try:
            obj_id = int(raw_id)
            result = find_api(obj_id, self.tokens)
        except ValueError:
            messagebox.showerror("Invalid Resource ID", "Resource ID must be a number.")
            return
        except Exception as exc:
            messagebox.showerror("Search Failed", str(exc))
            return

        if result.get("title"):
            self._populate_results([result])
        else:
            self._populate_results([])

    def reg(self):
        def register_user(name, password):
            result = register_api(name, password)
            if result.get("name"):
                return {"message": "Success!"}
            return {"message": "FAILED!"}

        REGISTER(self.root, register_user)

    def log(self):
        def login_user(name, password):
            result = login_api(name, password)
            if result.get("token"):
                self.log_in = True
                self.tokens = result["token"]
                self.users = name
                self.power = result["power"]
                self.refresh_buttons()
                self.searchkw()
                return {"message": "Success!"}
            return {"message": "FAILED!"}

        LOGIN(self.root, login_user)

    def cgpw(self):
        if not self._require_login():
            return

        def change_password(old_password, new_password):
            result = changepw_api(old_password, new_password, self.tokens)
            if result.get("message") == "Success!":
                return {"message": "Success!"}
            return {"message": "FAILED!"}

        CGPW(self.root, change_password)

    def dlt(self):
        self.log_in = False
        self.users = None
        self.tokens = None
        self.power = -1
        self.searchvar.set("")
        self.download_entry.reset_placeholder()
        self._clear_results()
        self.refresh_buttons()

    def download(self):
        if not self._require_login():
            return

        raw_id = self.download_entry.get_value().strip()
        if not raw_id:
            messagebox.showwarning("Missing Resource ID", "Please enter a resource ID.")
            return

        try:
            obj_id = int(raw_id)
        except ValueError:
            messagebox.showerror("Invalid Resource ID", "Resource ID must be a number.")
            return

        try:
            download_path = download_resource(obj_id, self.tokens)
        except Exception as exc:
            messagebox.showerror("Download Failed", str(exc))
            return

        messagebox.showinfo("Download Complete", f"Saved to:\n{download_path}")
        self.searchkw()

    def open_add_dialog(self):
        if not self._require_login() or self.power != 0:
            return
        ResourceDialog(
            self.root,
            title="Add Resource",
            confirm_text="Create Resource",
            on_submit=self._submit_add_resource,
        )

    def _submit_add_resource(self, payload):
        try:
            admin_add_resource(self.tokens, payload)
        except Exception as exc:
            messagebox.showerror("Create Failed", str(exc))
            return False

        messagebox.showinfo("Success", "Resource created successfully.")
        self.searchvar.set(str(payload["obj_id"]))
        self.searchid()
        return True

    def open_edit_dialog(self):
        if not self._require_login() or self.power != 0:
            return

        resource = self._selected_resource()
        if not resource:
            messagebox.showwarning(
                "Select a Resource",
                "Please select a resource from the table before editing.",
            )
            return

        ResourceDialog(
            self.root,
            title="Edit Resource",
            confirm_text="Save Changes",
            on_submit=self._submit_edit_resource,
            initial=resource,
            require_file=False,
        )

    def _submit_edit_resource(self, payload):
        try:
            admin_edit_resource(self.tokens, payload)
        except Exception as exc:
            messagebox.showerror("Update Failed", str(exc))
            return False

        messagebox.showinfo("Success", "Resource updated successfully.")
        self.searchvar.set(str(payload["obj_id"]))
        self.searchid()
        return True

    def remove_selected_resource(self):
        if not self._require_login() or self.power != 0:
            return

        resource = self._selected_resource()
        if not resource:
            messagebox.showwarning(
                "Select a Resource",
                "Please select a resource from the table before deleting it.",
            )
            return

        should_delete = messagebox.askyesno(
            "Delete Resource",
            f"Delete resource {resource['id']} - {resource['title']}?",
        )
        if not should_delete:
            return

        try:
            admin_remove_resource(self.tokens, int(resource["id"]))
        except Exception as exc:
            messagebox.showerror("Delete Failed", str(exc))
            return

        messagebox.showinfo("Success", "Resource removed successfully.")
        self.searchkw()

    def open_user_manager(self):
        if not self._require_login() or self.power != 0:
            return
        UserManagerWindow(self.root, self.tokens)


if __name__ == "__main__":
    app_root = tb.Window(themename="flatly")
    client = Client(app_root)
    app_root.mainloop()
