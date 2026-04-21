import tkinter
from tkinter import ttk
from tkinter import messagebox
from api import *
from windows import *

checklogin=False
currentuser=None
token=None
base_url="http://localhost:2333"

class Client:
    def __init__(self,root):
        self.root=root
        self.root.title("数据库系统")
        self.log_in=False
        self.tokens=None
        self.users=None
        self.power=-1

        #登录注册
        self.btlr=tkinter.Frame(root)
        self.btlr.pack(anchor=tkinter.NE,padx=5,pady=20)
        self.register_bt=tkinter.Button(self.btlr,text="注册",command=self.reg)
        self.login_bt=tkinter.Button(self.btlr,text="登录",command=self.log)
        self.cpw_bt=tkinter.Button(self.btlr,text="修改密码",command=self.cgpw)
        self.delete_bt=tkinter.Button(self.btlr,text="注销账户",command=self.dlt)
        self.username_area=tkinter.Button(self.btlr,text=self.users)
        #管理员操作
        self.edit_bt=tkinter.Button(self.btlr,text="编辑")
        self.remove_bt=tkinter.Button(self.btlr,text="删除")
        self.add_bt=tkinter.Button(self.btlr,text="增加")
        self.manageuser=tkinter.Button(self.btlr,text="账户管理")

        self.refresh_buttons()

        #搜索框
        search_area=tkinter.Frame(root)
        search_area.pack(fill=tkinter.X,pady=20)
        thisarea=tkinter.Frame(search_area)
        thisarea.pack(anchor=tkinter.CENTER)
        thisarea.grid_columnconfigure(0,weight=1)
        self.searchvar=tkinter.StringVar()
        self.ssk=tkinter.Entry(thisarea,textvariable=self.searchvar,font=("",20),width=100)
        #self.ssk.pack(side=tkinter.LEFT,padx=20)
        self.ssk.grid(row=0,column=0,sticky="ew",padx=(20,20))
        self.ssk.bind("<Return>",lambda x:self.searchkw())
        b1=tkinter.Button(thisarea,text="Search by keywords",command=self.searchkw)
        b2=tkinter.Button(thisarea,text="Search by ID",command=self.searchid)
        b1.grid(row=0,column=1,padx=10)
        b2.grid(row=0,column=2,padx=10)

        self.result_box=ttk.Treeview(root,columns=("title","info"),show="headings")
        self.result_box.pack(fill=tkinter.BOTH,expand=True,padx=20,pady=20)
        self.result_box.heading("title",text="Title")
        self.result_box.column("title",anchor=tkinter.W,width=500)
        self.result_box.heading("info",text="Information")
        self.result_box.column("info",anchor=tkinter.W,width=1000)
        #self.result_listbox=tkinter.Listbox(root)
        #self.result_listbox.pack(fill=tkinter.BOTH, expand=True, padx=20, pady=20)

        download_area=tkinter.Frame(root)
        download_area.pack(fill=tkinter.X,pady=20)
        da=tkinter.Frame(download_area)
        da.pack(anchor=tkinter.CENTER)
        da.grid_columnconfigure(0,weight=1)
        self.downloadid=tkinter.StringVar()
        self.dlid=tkinter.Entry(da,textvariable=self.downloadid,font=("",20),width=100)
        self.dlid.grid(row=0,column=0,sticky="ew",padx=(20,20))
        download_bt=tkinter.Button(da,text="DOWNLOAD",command=self.download)
        download_bt.grid(row=0,column=1,padx=20)
        
    def refresh_buttons(self):
        self.register_bt.pack_forget()
        self.login_bt.pack_forget()
        self.cpw_bt.pack_forget()
        self.delete_bt.pack_forget()
        self.username_area.pack_forget()
        self.edit_bt.pack_forget()
        self.remove_bt.pack_forget()
        self.add_bt.pack_forget()
        if self.log_in:
            self.cpw_bt.pack(side=tkinter.RIGHT,padx=2)
            self.delete_bt.pack(side=tkinter.RIGHT,padx=2)
            self.username_area=tkinter.Button(self.btlr,text=self.users)
            if self.power==0:
                self.edit_bt.pack=tkinter.Button(self.btlr,padx=2)
                self.remove_bt.pack=tkinter.Button(self.btlr,padx=2)
                self.add_bt.pack=tkinter.Button(self.btlr,padx=2)
            self.username_area.pack(side=tkinter.RIGHT,padx=5)
        else:
            self.register_bt.pack(side=tkinter.RIGHT,padx=2)
            self.login_bt.pack(side=tkinter.RIGHT,padx=2)

    def searchkw(self):
        kw=self.searchvar.get().strip()
        result=search_api(kw,self.tokens)
        for item in self.result_box.get_children():
            self.result_box.delete(item)
        #self.result_box.delete(0,tkinter.END)
        if result:
            for i in result:
                self.result_box.insert("",tkinter.END,values=(i.get("title"),"ID:"+str(i.get("id"))+" Author:"+str(i.get("zuozhe"))+" 介绍:"+str(i.get("introduction"))+" 下载量:"+str(i.get("download_sum"))+" 创建时间:"+str(i.get("created_at"))))
                #self.result_listbox.insert(tkinter.END,str(i.get("title"))+" "+str(i.get("id"))+" "+str(i.get("zuozhe"))+" "+str(i.get("introduction")))
        else:
            self.result_box.insert("",tkinter.END,values=("None",None))
            #self.result_listbox.insert(tkinter.END,"None")
    def searchid(self):
        kw=self.searchvar.get().strip()
        try:
            id=int(kw)
            result=find_api(id,self.tokens)
            for item in self.result_box.get_children():
                self.result_box.delete(item)
            #self.result_listbox.delete(0,tkinter.END)
            #print(result["id"])
            if result.get("title"):
                self.result_box.insert("",tkinter.END,values=(result.get("title"),"ID:"+str(result.get("id"))+" Author:"+str(result.get("zuozhe"))+" 介绍:"+str(result.get("introduction"))+" 下载量:"+str(result.get("download_sum"))+" 创建时间:"+str(result.get("created_at"))))
                #self.result_listbox.insert(tkinter.END,str(result.get("title"))+" "+str(result.get("id"))+" "+str(result.get("zuozhe"))+" "+str(result.get("introduction")))
            else:
                self.result_box.insert("",tkinter.END,values=("None",None))
                #self.result_listbox.insert(tkinter.END,"None")
        except:
            self.result_box.insert("",tkinter.END,values=("None",None))
            #self.result_listbox.delete(0,tkinter.END)
            #self.result_listbox.insert(tkinter.END,"ENTER ID!")
    def reg(self):
        def rg(name:str,pw:str):
            result=register_api(name,pw)
            if result.get("name"):
                return {"message":"Success!"}
            else:
                return {"message":"FAILED!"}
        REGISTER(self.root,rg)
    def log(self):
        def lg_in(name:str,pw:str):
            result=login_api(name,pw)
            if result.get("token"):
                self.log_in=True
                self.tokens=result["token"]
                self.users=name
                self.power=result["power"]
                self.refresh_buttons()
                return {"message":"Success!"}
            else:
                return {"message":"FAILED!"}
        LOGIN(self.root,lg_in)
    def cgpw(self):
        def cp(op:str,np:str):
            result=changepw_api(op,np,self.tokens)
            if result.get("message")=="Success!":
                return {"message":"Success!"}
            else:
                return {"message":"FAILED!"}
        CGPW(self.root,cp)
    def dlt(self):
        self.log_in=False
        self.users=None
        self.tokens=None
        self.power=-1
        self.refresh_buttons()
    def download(self):
        id=self.downloadid.get().strip()
        try:
            id=int(id)
        except:
            messagebox.showerror("NUMBER!!!")
            return
        download_api(id,self.tokens)

if __name__ == "__main__":
    root=tkinter.Tk()
    root.geometry("1280x720")
    app=Client(root)
    #print("test")
    root.mainloop()