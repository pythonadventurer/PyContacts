"""
PyContacts - a contact manager.
Copyright (C) 2023  Robert T. Fowler IV

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
# TODO Use event bindings to refresh the main window when record form is closed.
# TODO Fix entry widths in record form
# TODO Search feature
# TODO Sort feature
# TODO Show-hide columns feature

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path
from config import *
from database import *

class App:
    def __init__(self,root):
        root.title("PyContacts")
        root.geometry("1200x800")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=0)

        mnuMain = MainMenu(root)
        root.config(menu=mnuMain)
        table = TableFrame(root,varDatabase,"contacts")
        table.grid(row=0,column=0)

class MainMenu(Menu):
    def __init__(self,root):
        Menu.__init__ (self,root)

        mnuFile = Menu(self,tearoff=0)
        self.add_cascade(label="File",menu=mnuFile)
        mnuFile.add_command(label="Import from CSV")
        mnuFile.add_command(label="Quit",command=root.quit)

        mnuEdit = Menu(self,tearoff=0)
        self.add_cascade(label="Edit",menu=mnuEdit)
        mnuEdit.add_command(label="New Record")
        mnuEdit.add_command(label="Show/Hide Columns")
        mnuEdit.add_command(label="Preferences",command=PreferencesWindow)

        mnuHelp = Menu(self,tearoff=0)
        self.add_cascade(label="Help",menu=mnuHelp)
        mnuHelp.add_command(label="About",command=AboutWindow)

class PreferencesWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__ (self)

        self.title("Preferences")

class AboutWindow(Toplevel):
    def __init__(self):
        Toplevel.__init__ (self)

        self.title("About")
        lblAppName = Label(self,text="Contacts",font=("Helvetica",12,"bold"))
        lblVersion = Label(self,text="Version:",font=("Helvetica",10))
        lblVersionNum = Label(self,text=varAppVersion,font=("Helvetica",10))
        lblAppName.grid(row=0,column=0,columnspan=2,sticky=(W,E),padx=75)
        lblVersion.grid(row=1,column=0,padx=5,pady=5,sticky=E)
        lblVersionNum.grid(row=1,column=1,padx=5,pady=5,sticky=W)

class TableFrame(Frame):
    """
    includes a table interface and its scrollbars.
    """
    def __init__(self,parent,db,table_name):
        Frame.__init__ (self)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.db = db
        self.table_name = table_name
        self.columns = get_table_columns(self.db, self.table_name)

        def refresh():
            # clear the treeview
            treTable.delete(*treTable.get_children())

            table_data = query_all(self.db, self.table_name)
            count = 0
            for record in table_data:
                if count % 2 == 0:
                    treTable.insert(parent='', index='end', iid=count, text='', 
                        values = record, tags=('evenrow',))  
                else:
                    treTable.insert(parent='', index='end', iid=count, text='', 
                        values = record, tags=('oddrow',))  
                count += 1

        def open_record_form(e):
            selection = treTable.focus()
            item = treTable.item(selection)
            record_id = item['values'][0]
            f = RecordForm(varDatabase,"contacts",record_id)

        # frame to hold top row of buttons and search options
        fraToolbar = Frame(self)

        lblSearchCol = Label(fraToolbar,text="Search By:",font=("Helvetica",10))      
        varSearchColumn = StringVar()
        cboSearch = ttk.Combobox(fraToolbar,textvariable=varSearchColumn,font=("Helvetica",10))
        cboSearch['values'] = tuple(self.columns.keys())
        btnSearch = Button(fraToolbar,text="Search",width=10)

        lblSearchCol.grid(row=0,column=0,padx=5,pady=5)
        cboSearch.grid(row=0,column=1,padx=5,pady=5)
        btnSearch.grid(row=0,column=2,padx=5,pady=5)
        btnSort = Button(fraToolbar,text="Sort",width=10)
        btnSort.grid(row=0,column=3,padx=5,pady=5)

        fraToolbar.grid(row=0,column=0,sticky=W)

        # build the table widget
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica",10,"bold"))
        style.configure("Treeview",rowheight=25)

        scrHorizontal = ttk.Scrollbar(self,orient=HORIZONTAL)
        scrHorizontal.grid(row=2,column=0,sticky=(E,W))

        scrVertical = ttk.Scrollbar(self,orient=VERTICAL)
        scrVertical.grid(row=1,column=1,sticky=(N,S))

        treTable = ttk.Treeview(self, 
                                columns=tuple(self.columns.keys()),
                                show="headings",
                                height=25,
                                xscrollcommand=scrHorizontal.set,
                                yscrollcommand=scrVertical.set)

        # # Create Striped Row Tags
        treTable.tag_configure('oddrow', background=varPrimaryColor,font=("Helvetica",12))
        treTable.tag_configure('evenrow', background=varSecondaryColor,font=("Helvetica",12))

        treTable.grid(row=1,column=0,sticky=(N,S,E,W))

        # trick for making the horizontal scrollbar work.
        for col in treTable['columns']:
            treTable.heading(col, text=f"{col}", anchor=CENTER)
            treTable.column(col, anchor=CENTER, width=40) # initially smaller size

        treTable.update()

        for col in treTable['columns']:
            treTable.column(col, width=self.columns[col] * 10,stretch=0) 

        # hide the ID column
        # treTable.column('ID',width=0,stretch=NO)

        refresh()

        # connect the scrollbars to the treeview
        scrHorizontal['command'] = treTable.xview
        scrVertical['command'] = treTable.yview

        treTable.bind("<Double-1>",open_record_form)


class RecordForm(Toplevel):
    def __init__(self,db,table_name,record_id):
        Toplevel.__init__ (self)
        self.title("Record")
        col_names = list(get_table_columns(db, table_name).keys())

        def get_child_widgets(object):
            return [child for child in object.children.keys()]

        def get_entry_widgets():
            return [child for child in fraMain.children.keys() if "entry" in child]

        def insert_data():
            """
            Get the data from the selected record and display it in the form.
            """
            # get the list of entry boxes
            entry_widgets = get_entry_widgets()

            data = query_record(db, table_name, record_id)
            for n in range(0,len(entry_widgets)):
                fraMain.children[entry_widgets[n]].insert(0,data[n])

        def clear_form():
            # make id editable so can be cleared
            fraMain.children['!entry'].configure(state='normal')
            entry_widgets = get_entry_widgets()
            for n in range(0,len(entry_widgets)):
                fraMain.children[entry_widgets[n]].delete(0,END)

            # disable ID so user can't enter anything in it
            fraMain.children['!entry'].configure(state='disabled')

        def new_record():
            clear_form()

        def save_record():
            response = messagebox.askquestion("Confirm","Save this record?")
            print(f"Response: {response}")

            if response == "no":
                return

            # get the values from the entry widgets
            data = []
            entry_widgets = get_entry_widgets()
            for n in range(0,len(entry_widgets)):
                data.append(fraMain.children[entry_widgets[n]].get())

            # data includes the ID, tuple omits it for entry/updating.
            data_tuple = tuple(data[1:])

            if data[0] == '':  # no id means it's a new record.
                insert_records(db, table_name, col_names[1:], data_tuple)
            else:  # has ID so update existing.
                update_record(db, table_name, record_id, data_tuple) 

            messagebox.showinfo("Change Successful","Record has been updated.")
           
            exit()

        def delete_record():
            response = messagebox.askquestion("Confirm","Delete this record?")
            print(f"Response: {response}")

            if response == "no":
                return

            delete_record(db,table_name,record_id)

            messagebox.showinfo("He's Dead, Jim","Record has been deleted.")
            exit()

        def exit():
            self.destroy()

        # toolbar to hold the buttons
        fraToolbar = Frame(self)

        btnNew = Button(fraToolbar,text="New",width=8,command=new_record)
        btnSave = Button(fraToolbar,text="Save",width=8,command=save_record)
        btnDelete = Button(fraToolbar,text="Delete",width=8,command=delete_record)
        btnNew.grid(row=0,column=1,padx=5,pady=5,sticky=(W,E))
        btnSave.grid(row=0,column=2,padx=5,pady=5,sticky=(W,E))
        btnDelete.grid(row=0,column=3,padx=5,pady=5,sticky=(W,E))
        fraToolbar.grid(row=0,column=0)

        fraMain = Frame(self)

        for n in range(0,len(col_names)):
            Label(fraMain,text=col_names[n],font=("Helvetica",10,"bold")).grid(row=n,column=0,padx=5,pady=5,sticky=E)
            Entry(fraMain,font=("Helvetica",10)).grid(row=n,column=1,padx=10,pady=5,sticky=(E,W))    

        fraMain.grid(row=1,column=0)
        insert_data()

        # make ID field read-only
        fraMain.children['!entry'].configure(state='disabled')