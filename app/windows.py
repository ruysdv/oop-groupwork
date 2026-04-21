import tkinter
from tkinter import messagebox
class LOGIN:
    def __init__(self,ft,lg):
        self.window=tkinter.Toplevel(ft)
        self.window.title("LOGIN")
        self.lg=lg
        tkinter.Label(self.window,text="USERNAME:").grid(row=0,column=0)
        self.name=tkinter.Entry(self.window)
        self.name.grid(row=0,column=1)
        tkinter.Label(self.window,text="PASSWORD:").grid(row=1,column=0)
        self.pw=tkinter.Entry(self.window,show="*")
        self.pw.grid(row=1,column=1)
        self.pw.bind("<Return>",lambda x:self.lg_in())
        tkinter.Button(self.window,text="LOGIN",command=self.lg_in).grid(row=2,columnspan=2)
    def lg_in(self):
        result=self.lg(str(self.name.get()),str(self.pw.get()))
        if result.get("message")=="Success!":
            self.window.destroy()
        else:
            messagebox.showerror("FAILED","WRONG NAME OR PASSWORD")

class REGISTER:
    def __init__(self,ft,rg):
        self.window=tkinter.Toplevel(ft)
        self.window.title("REGISTER")
        self.rg=rg
        tkinter.Label(self.window,text="USERNAME:").grid(row=0,column=0)
        self.name=tkinter.Entry(self.window)
        self.name.grid(row=0,column=1)
        tkinter.Label(self.window,text="PASSWORD:").grid(row=1,column=0)
        self.pw=tkinter.Entry(self.window,show="*")
        self.pw.grid(row=1,column=1)
        self.pw.bind("<Return>",lambda x:self.rg_in())
        tkinter.Button(self.window,text="REGISTER",command=self.rg_in).grid(row=2,columnspan=2)
    def rg_in(self):
        result=self.rg(str(self.name.get()),str(self.pw.get()))
        if result.get("message")=="Success!":
            self.window.destroy()
        else:
            messagebox.showerror("FAILED","THIS USER EXEISTS!")

class CGPW:
    def __init__(self,ft,cp):
        self.window=tkinter.Toplevel(ft)
        self.window.title("Change Password")
        self.cp=cp
        tkinter.Label(self.window,text="OLD PASSWORD:").grid(row=0,column=0)
        self.name=tkinter.Entry(self.window)
        self.name.grid(row=0,column=1)
        tkinter.Label(self.window,text="NEW PASSWORD:").grid(row=1,column=0)
        self.pw=tkinter.Entry(self.window,show="*")
        self.pw.grid(row=1,column=1)
        self.pw.bind("<Return>",lambda x:self.cp_in())
        tkinter.Button(self.window,text="CHANGE",command=self.cp_in).grid(row=2,columnspan=2)
    def cp_in(self):
        result=self.cp(str(self.name.get()),str(self.pw.get()))
        if result.get("message")=="Success!":
            self.window.destroy()
        else:
            messagebox.showerror("FAILED","WRONG PASSWORD")