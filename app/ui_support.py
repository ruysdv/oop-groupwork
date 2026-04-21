import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import requests
import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, END, EW, LEFT, RIGHT, W, X, Y

from api import base_url


def _request(method, url, **kwargs):
    response = requests.request(method, url, timeout=20, **kwargs)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_message(response)) from exc
    return response


def _response_message(response):
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        return str(payload.get("detail") or payload.get("message") or payload)
    return str(payload)


def _auth_headers(token):
    return {"auth": token}


def format_resource_info(item):
    return (
        f"ID: {item.get('id')}  |  "
        f"Author: {item.get('zuozhe')}  |  "
        f"Description: {item.get('introduction')}  |  "
        f"Downloads: {item.get('download_sum')}  |  "
        f"Created At: {item.get('created_at')}"
    )


def _save_dir():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "Download")


def _filename_from_headers(response, fallback):
    disposition = response.headers.get("content-disposition", "")
    marker = "filename="
    if marker in disposition:
        return disposition.split(marker, 1)[1].strip().strip('"')
    return fallback


def download_resource(obj_id, token):
    os.makedirs(_save_dir(), exist_ok=True)
    with requests.get(
        f"{base_url}/objects/{obj_id}/download",
        headers=_auth_headers(token),
        stream=True,
        timeout=20,
    ) as response:
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(_response_message(response)) from exc

        filename = _filename_from_headers(response, f"{obj_id}.zip")
        filepath = os.path.join(_save_dir(), filename)
        with open(filepath, "wb") as file_handle:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file_handle.write(chunk)
    return filepath


def admin_add_resource(token, payload):
    if not payload["file_path"]:
        raise RuntimeError("Please choose a ZIP file before creating the resource.")
    if not payload["file_path"].lower().endswith(".zip"):
        raise RuntimeError("Only ZIP files are supported by the current backend.")

    data = {
        "obj_id": str(payload["obj_id"]),
        "t": payload["title"],
        "zz": payload["author"],
        "itd": payload["description"],
    }
    with open(payload["file_path"], "rb") as upload_file:
        files = {
            "file": (
                os.path.basename(payload["file_path"]),
                upload_file,
                "application/zip",
            )
        }
        response = _request(
            "POST",
            f"{base_url}/objects",
            headers=_auth_headers(token),
            data=data,
            files=files,
        )
    return response.json()


def admin_edit_resource(token, payload):
    data = {
        "t": payload["title"],
        "zz": payload["author"],
        "itd": payload["description"],
    }
    files = None
    file_handle = None
    if payload["file_path"]:
        if not payload["file_path"].lower().endswith(".zip"):
            raise RuntimeError("Only ZIP files are supported by the current backend.")
        file_handle = open(payload["file_path"], "rb")
        files = {
            "file": (
                os.path.basename(payload["file_path"]),
                file_handle,
                "application/zip",
            )
        }

    try:
        response = _request(
            "PUT",
            f"{base_url}/objects/{payload['obj_id']}",
            headers=_auth_headers(token),
            data=data,
            files=files,
        )
    finally:
        if file_handle is not None:
            file_handle.close()
    return response.json()


def admin_remove_resource(token, obj_id):
    response = _request(
        "DELETE",
        f"{base_url}/objects",
        headers=_auth_headers(token),
        params={"obj_id": obj_id},
    )
    return response.json()


def admin_list_users(token):
    response = _request(
        "GET",
        f"{base_url}/admin/users/list",
        headers=_auth_headers(token),
    )
    return response.json()


def admin_create_user(token, username, password, permission):
    response = _request(
        "POST",
        f"{base_url}/admin/users",
        headers=_auth_headers(token),
        params={"name": username, "pw": password, "power": permission},
    )
    return response.json()


def admin_delete_user(token, username):
    response = _request(
        "DELETE",
        f"{base_url}/admin/users/{username}",
        headers=_auth_headers(token),
        params={"name": username},
    )
    return response.json()


def admin_set_permission(token, username, permission):
    response = _request(
        "PUT",
        f"{base_url}/admin/users/{username}/permission",
        headers=_auth_headers(token),
        params={"name": username, "power": permission},
    )
    return response.json()


class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder, placeholder_color="#9aa5b1", **kwargs):
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self.default_fg = kwargs.pop("fg", "#1f2933")
        super().__init__(master, fg=self.default_fg, **kwargs)
        self.placeholder_visible = False
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._show_placeholder)
        self.reset_placeholder()

    def _clear_placeholder(self, _event=None):
        if self.placeholder_visible:
            self.delete(0, END)
            self.configure(fg=self.default_fg)
            self.placeholder_visible = False

    def _show_placeholder(self, _event=None):
        if not self.get():
            self.reset_placeholder()

    def get_value(self):
        if self.placeholder_visible:
            return ""
        return self.get()

    def reset_placeholder(self):
        self.delete(0, END)
        self.insert(0, self.placeholder)
        self.configure(fg=self.placeholder_color)
        self.placeholder_visible = True


class ResourceDialog(tb.Toplevel):
    def __init__(self, master, title, confirm_text, on_submit, initial=None, require_file=True):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.on_submit = on_submit
        self.require_file = require_file
        self.initial = initial or {}

        self.id_var = tk.StringVar(value=str(self.initial.get("id", "")))
        self.title_var = tk.StringVar(value=self.initial.get("title", ""))
        self.author_var = tk.StringVar(value=self.initial.get("zuozhe", ""))
        self.file_var = tk.StringVar(value="")

        body = tb.Frame(self, padding=18)
        body.pack(fill=BOTH, expand=True)
        body.grid_columnconfigure(1, weight=1)

        tb.Label(body, text="Resource ID", width=16).grid(row=0, column=0, sticky=W, pady=6)
        id_entry = tb.Entry(body, textvariable=self.id_var)
        id_entry.grid(row=0, column=1, sticky=EW, pady=6)
        if self.initial:
            id_entry.configure(state="readonly")

        tb.Label(body, text="Title", width=16).grid(row=1, column=0, sticky=W, pady=6)
        tb.Entry(body, textvariable=self.title_var).grid(row=1, column=1, sticky=EW, pady=6)

        tb.Label(body, text="Author", width=16).grid(row=2, column=0, sticky=W, pady=6)
        tb.Entry(body, textvariable=self.author_var).grid(row=2, column=1, sticky=EW, pady=6)

        tb.Label(body, text="Description", width=16).grid(row=3, column=0, sticky="nw", pady=6)
        self.description = tk.Text(body, height=6, wrap="word", font=("Segoe UI", 10))
        self.description.grid(row=3, column=1, sticky=EW, pady=6)
        self.description.insert("1.0", self.initial.get("introduction", ""))

        tb.Label(body, text="ZIP File", width=16).grid(row=4, column=0, sticky=W, pady=6)
        file_frame = tb.Frame(body)
        file_frame.grid(row=4, column=1, sticky=EW, pady=6)
        file_frame.grid_columnconfigure(0, weight=1)
        tb.Entry(file_frame, textvariable=self.file_var, state="readonly").grid(
            row=0, column=0, sticky=EW, padx=(0, 10)
        )
        tb.Button(
            file_frame,
            text="Browse",
            command=self._browse_file,
            bootstyle="outline-secondary",
            width=10,
        ).grid(row=0, column=1)

        footer = tb.Frame(body)
        footer.grid(row=5, column=0, columnspan=2, sticky=EW, pady=(14, 0))
        tb.Button(
            footer,
            text="Cancel",
            command=self.destroy,
            bootstyle="secondary",
            width=12,
        ).pack(side=RIGHT)
        tb.Button(
            footer,
            text=confirm_text,
            command=self._submit,
            bootstyle="primary",
            width=16,
        ).pack(side=RIGHT, padx=(0, 10))

        self.bind("<Escape>", lambda _event: self.destroy())

    def _browse_file(self):
        filename = filedialog.askopenfilename(
            title="Choose ZIP File",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        )
        if filename:
            self.file_var.set(filename)

    def _submit(self):
        raw_id = self.id_var.get().strip()
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        description = self.description.get("1.0", END).strip()
        file_path = self.file_var.get().strip()

        if not raw_id:
            messagebox.showerror("Missing Resource ID", "Resource ID is required.")
            return
        if not title:
            messagebox.showerror("Missing Title", "Title is required.")
            return
        try:
            obj_id = int(raw_id)
        except ValueError:
            messagebox.showerror("Invalid Resource ID", "Resource ID must be a number.")
            return
        if self.require_file and not file_path:
            messagebox.showerror("Missing ZIP File", "Please choose a ZIP file.")
            return

        success = self.on_submit(
            {
                "obj_id": obj_id,
                "title": title,
                "author": author,
                "description": description,
                "file_path": file_path or None,
            }
        )
        if success:
            self.destroy()


class CreateUserDialog(tb.Toplevel):
    def __init__(self, master, on_submit):
        super().__init__(master)
        self.title("Create User")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.on_submit = on_submit
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.permission_var = tk.StringVar(value="User")

        body = tb.Frame(self, padding=18)
        body.pack(fill=BOTH, expand=True)
        body.grid_columnconfigure(1, weight=1)

        tb.Label(body, text="Username", width=14).grid(row=0, column=0, sticky=W, pady=6)
        tb.Entry(body, textvariable=self.username_var).grid(row=0, column=1, sticky=EW, pady=6)

        tb.Label(body, text="Password", width=14).grid(row=1, column=0, sticky=W, pady=6)
        tb.Entry(body, textvariable=self.password_var, show="*").grid(
            row=1, column=1, sticky=EW, pady=6
        )

        tb.Label(body, text="Permission", width=14).grid(row=2, column=0, sticky=W, pady=6)
        permission_box = ttk.Combobox(
            body,
            textvariable=self.permission_var,
            values=["User", "Admin"],
            state="readonly",
        )
        permission_box.grid(row=2, column=1, sticky=EW, pady=6)

        footer = tb.Frame(body)
        footer.grid(row=3, column=0, columnspan=2, sticky=EW, pady=(14, 0))
        tb.Button(
            footer, text="Cancel", command=self.destroy, bootstyle="secondary", width=12
        ).pack(side=RIGHT)
        tb.Button(
            footer,
            text="Create User",
            command=self._submit,
            bootstyle="primary",
            width=14,
        ).pack(side=RIGHT, padx=(0, 10))

    def _submit(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        permission = 0 if self.permission_var.get() == "Admin" else 1

        if not username or not password:
            messagebox.showerror("Missing Information", "Username and password are required.")
            return

        success = self.on_submit(username, password, permission)
        if success:
            self.destroy()


class UserManagerWindow(tb.Toplevel):
    def __init__(self, master, token):
        super().__init__(master)
        self.title("User Manager")
        self.geometry("760x460")
        self.minsize(680, 420)
        self.transient(master)

        self.token = token
        self.user_rows = {}

        outer = tb.Frame(self, padding=18)
        outer.pack(fill=BOTH, expand=True)

        toolbar = tb.Frame(outer)
        toolbar.pack(fill=X, pady=(0, 12))
        tb.Button(toolbar, text="Create User", command=self.open_create_user, bootstyle="success").pack(
            side=LEFT
        )
        tb.Button(
            toolbar,
            text="Delete User",
            command=self.delete_selected_user,
            bootstyle="danger",
        ).pack(side=LEFT, padx=(10, 0))
        tb.Button(
            toolbar,
            text="Toggle Role",
            command=self.toggle_permission,
            bootstyle="warning",
        ).pack(side=LEFT, padx=(10, 0))
        tb.Button(toolbar, text="Refresh", command=self.refresh, bootstyle="info").pack(
            side=RIGHT
        )

        table_frame = tb.Frame(outer)
        table_frame.pack(fill=BOTH, expand=True)

        self.user_table = ttk.Treeview(
            table_frame,
            columns=("username", "role"),
            show="headings",
            selectmode="browse",
        )
        self.user_table.heading("username", text="Username")
        self.user_table.heading("role", text="Role")
        self.user_table.column("username", width=360, anchor=W)
        self.user_table.column("role", width=180, anchor=W)
        self.user_table.pack(side=LEFT, fill=BOTH, expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.user_table.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.user_table.configure(yscrollcommand=scroll.set)

        self.refresh()

    def refresh(self):
        try:
            users = admin_list_users(self.token)
        except Exception as exc:
            messagebox.showerror("Load Failed", str(exc))
            return

        self.user_rows.clear()
        for item in self.user_table.get_children():
            self.user_table.delete(item)

        for user in users:
            role = "Admin" if user.get("power") == 0 else "User"
            row_id = self.user_table.insert(
                "", END, values=(user.get("name"), role)
            )
            self.user_rows[row_id] = user

    def selected_user(self):
        selection = self.user_table.selection()
        if not selection:
            return None
        return self.user_rows.get(selection[0])

    def open_create_user(self):
        CreateUserDialog(self, self._submit_create_user)

    def _submit_create_user(self, username, password, permission):
        try:
            admin_create_user(self.token, username, password, permission)
        except Exception as exc:
            messagebox.showerror("Create Failed", str(exc))
            return False
        messagebox.showinfo("Success", f"User {username} created successfully.")
        self.refresh()
        return True

    def delete_selected_user(self):
        user = self.selected_user()
        if not user:
            messagebox.showwarning("Select a User", "Please select a user first.")
            return
        if not messagebox.askyesno("Delete User", f"Delete user {user['name']}?"):
            return
        try:
            admin_delete_user(self.token, user["name"])
        except Exception as exc:
            messagebox.showerror("Delete Failed", str(exc))
            return
        messagebox.showinfo("Success", f"User {user['name']} deleted successfully.")
        self.refresh()

    def toggle_permission(self):
        user = self.selected_user()
        if not user:
            messagebox.showwarning("Select a User", "Please select a user first.")
            return

        new_power = 1 if user.get("power") == 0 else 0
        new_role = "User" if new_power == 1 else "Admin"
        try:
            admin_set_permission(self.token, user["name"], new_power)
        except Exception as exc:
            messagebox.showerror("Update Failed", str(exc))
            return
        messagebox.showinfo("Success", f"{user['name']} is now {new_role}.")
        self.refresh()
