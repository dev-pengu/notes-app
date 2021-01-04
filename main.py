try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    from ttk import *
import os, platform
from tkinter.messagebox import showinfo, askyesnocancel
from tkinter.filedialog import asksaveasfilename, askopenfilename
from time import ctime, sleep

from src.print_helper import PrintHelper
import win32print

#TODO: compile


class NoteWindow(tk.Frame):

    _file = None
    _width = 300
    _height = 300
    _changes = False
    _created_date = ctime()

    def __init__(self, **kwargs):
        '''Sets up the window and widgets'''
        try:
            self._file = kwargs['file']
        except KeyError:
            pass
        try:
            self._width = kwargs['width']
        except KeyError:
            pass
        try:
            self._height = kwargs['height']
        except KeyError:
            pass

        tk.Frame.__init__(self)
        try:
            self.master.iconbitmap('.\\assets\\favicon.ico')
        except:
            pass

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        left = (screen_width / 2) - (self._width / 2)
        top = (screen_height / 2) - (self._height / 2)

        self.pack(fill=tk.BOTH, expand=True)
        self.master.geometry('%dx%d+%d+%d' % (self._width, self._height, left, top))
        self.master.protocol('WM_DELETE_WINDOW', self._quitApp)
        self._gui_init()
        if self._file != None:
            self.master.title(os.path.basename(self._file) + " - Notes")
        else:
            self.master.title('Untitled - Notes')

    def _gui_init(self):
        '''Builds the gui window'''

        self._menu = tk.Menu(self)
        self.master.config(menu=self._menu)
        self._file_menu = tk.Menu(self._menu, tearoff=0)
        self._menu.add_cascade(label='File', menu=self._file_menu)
        self._file_menu.add_command(label='New', command=self._new_file, accelerator='Ctrl+N')
        self._file_menu.add_command(label='Open...', command=self._open_file, accelerator='Ctrl+O')
        self._file_menu.add_command(label='Save', command=self._save_file, accelerator='Ctrl+S')
        self._file_menu.add_command(label='Save As...', command=self._save_file_as, accelerator='Ctrl+Shift+S')
        self._file_menu.add_separator()
        self._file_menu.add_command(label='Print', command=self._print, accelerator='Ctrl+P')
        self._file_menu.add_separator()
        self._file_menu.add_command(label='Exit', command=self._quitApp)

        self._edit_menu = tk.Menu(self._menu, tearoff=0)
        self._menu.add_cascade(label='Edit', menu=self._edit_menu)
        self._edit_menu.add_command(label='Undo', command=self._undo, accelerator='Ctrl+Z')
        self._edit_menu.add_command(label='Redo', command=self._redo, accelerator='Ctrl+Y')
        self._edit_menu.add_separator()
        self._edit_menu.add_command(label='Cut', command=self._cut, accelerator='Ctrl+X')
        self._edit_menu.add_command(label='Copy', command=self._copy, accelerator='Ctrl+C')
        self._edit_menu.add_command(label='Paste', command=self._paste, accelerator='Ctrl+V')

        self._help_menu = tk.Menu(self._menu, tearoff=0)
        self._menu.add_cascade(label='Help', menu=self._help_menu)
        self._help_menu.add_command(label = 'About Notes', command=self._about_app)
        
        self._statusBar = tk.Frame(self, height=20, relief=tk.SUNKEN, bd=1)
        self._statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        self._resize = ttk.Sizegrip(self._statusBar)
        self._resize.pack(side=tk.RIGHT, anchor=tk.S+tk.E)
        self._date_label = tk.Label(self._statusBar, text=self._created_date, padx=10)
        self._date_label.pack(side=tk.RIGHT, anchor=tk.E)
        self._print_label = tk.Label(self._statusBar, text="", padx=10)
        self._print_label.pack(side=tk.LEFT, anchor=tk.W)
        self._scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._text_area = tk.Text(self, undo=True)
        self._text_area.pack(expand=True, fill=tk.BOTH)
        self._scrollbar['command'] = self._text_area.yview
        self._text_area['yscrollcommand'] = self._scrollbar.set
        self._text_area.bind('<Key>', self._updated)
        self._text_area.focus_set()

        self._create_binding_keys()

    def _updated(self, event=None):
        '''Tracks when changes are made to the contents of the text area'''
        self._print_label['text'] = ""
        if self._changes == False:
            self._changes = True
            filename = 'Untitled'
            if self._file != None:
                filename = os.path.basename(self._file)
            self.master.title("*" + filename + " - Notepad")

    def _quitApp(self):
        '''Exit Handler to take care of saving if changes have been made'''
        if self._text_area.compare('end-1c', '==', '1.0') or self._changes == False:
            self.master.destroy()
        else:
            result = self._prompt_for_save()
            if result:
                self._save()
            elif result == None:
                return
            self.master.destroy()

    def _new_file(self, event=None):
        '''Creates a new unsaved empty note'''
        self._print_label['text'] = ""
        if self._text_area.compare('end-1c', '==', '1.0') or self._changes == False:
            self.master.title('Untitled - Notes')
            self._file = None
            self._text_area.delete(1.0, tk.END)
        else:
            result = self._prompt_for_save()
            if result:
                self._save()
            elif result == None:
                pass
            else:
                self.master.title('Untitled - Notes')
                self._file = None
                self._text_area.delete(1.0, tk.END)

    def _prompt_for_save(self):
        '''Prompts user for save confirmation'''
        filename = 'Untitled'
        if self._file != None:
            filename = os.path.basename(self._file)
        return askyesnocancel(title='Notes', message="Do you want to save changes to {0}".format(filename))

    def _save(self, event=None):
        '''Save handler for exiting application or creating a new file'''
        if self._file == None:
            self._save_file_as()
        else:
            self._save_file()

    def _open_file(self, event=None):
        '''Prompts user for file using filedialog and opens the file'''
        self._print_label['text'] = ""
        self._file = askopenfilename(defaultextension='.txt',
                                     filetypes=[('All Files','*.*'),
                                                ('Text Documents','*.txt')])
        if self._file == "":
            self._file = None
        else:
            self.master.title(os.path.basename(self._file) + ' - Notes')
            self._text_area.delete(1.0, tk.END)
            file = open(self._file, 'r')
            self._text_area.insert(1.0, file.read())
            self._created_date = ctime(os.path.getctime(self._file))
            self._date_label['text'] = self._created_date
            file.close()

    def _save_file(self, event=None):
        '''Saves the file, if it has not already been saved, will ask user for filepath using
            filedialog. Otherwise, will save using previous path.'''
        self._print_label['text'] = ""
        if self._file == None:
            self._file = asksaveasfilename(initialfile='Untitled.txt',
                                           defaultextension='.txt',
                                           filetypes=[('Text Documents','*.txt'),
                                                    ('All Files','*.*')])
            if self._file == "":
                self._file == None
            else:
                file = open(self._file,'w')
                file.write(self._text_area.get(1.0, tk.END))
                file.close()
                self._changes = False
                self.master.title(os.path.basename(self._file) + " - Notepad")
                self._print_label['text'] = "File saved to: " + self._file
        else:
            file = open(self._file, 'w')
            file.write(self._text_area.get(1.0, tk.END))
            file.close()
            self._changes = False
            self.master.title(os.path.basename(self._file) + " - Notepad")
            self._print_label['text'] = "File saved..."

    def _save_file_as(self, event=None):
        '''Prompts user for a save path using filedialog and saves using resulting path.'''
        self._print_label['text'] = ""
        self._file = asksaveasfilename(initialfile='Untitled.txt',
                                        defaultextension='.txt',
                                        filetypes=[('Text Documents','*.txt'),
                                                    ('All Files','*.*')])
        if self._file == "":
            self._file == None
        else:
            file = open(self._file,'w')
            file.write(self._text_area.get(1.0, tk.END))
            file.close()
            self._changes = False
            self.master.title(os.path.basename(self._file) + " - Notepad")
            self._print_label['text'] = "File saved to: " + self._file

    def _print(self, event=None):
        '''Prints contents of text area to default printer. If a default printer is not set up,
            nothing will happen'''
        try:
            if platform.system() == 'Windows':
                self._print_label['text'] = "Printing to: " + win32print.GetDefaultPrinter()
            print_obj = PrintHelper(data=self._text_area.get(1.0, tk.END))
            print_obj.print()
        except:
            pass

    def _undo(self, event=None):
        '''Undo previous change to text'''
        self._text_area.edit_undo()

    def _redo(self, event=None):
        '''Redo previous change to text'''
        self._text_area.edit_redo()

    def _cut(self, event=None):
        '''Cut event handler'''
        self._text_area.event_generate("<<Cut>>")

    def _copy(self, event=None):
        '''Copy event handler'''
        self._text_area.event_generate("<<Copy>>")
        self._updated()

    def _paste(self, event=None):
        '''Paste event handler'''
        self._text_area.event_generate("<<Paste>>")
        self._updated()

    def _about_app(self):
        '''Shows an dialog with information about author'''
        aboutInfo = '''Programming Pengu\n© 2020 Matt Lippelman. All rights reserved.'''
        showinfo(title="About Notes", message=aboutInfo)

    def _select_all(self, event=None):
        '''Selects all text in the text area'''
        self._text_area.tag_add('sel', '1.0', tk.END)
        return

    def _deselect_all(self, event=None):
        '''Deselects all text in the text area'''
        self._text_area.tag_remove('sel', '1.0', tk.END)
        return

    def _create_binding_keys(self):
        '''Creates key bindings for keyboard shortcuts'''
        for key in ["<Control-a>", "<Control-A>"]:
            self._text_area.bind(key, self._select_all)
        for key in ["<Button-1>", "<Return>"]:
            self._text_area.bind(key, self._deselect_all)
        for key in ["<Control-y>", "<Control-Y>"]:
            self._text_area.bind(key, self._redo)
        for key in ["<Control-z>", "<Control-Z>"]:
            self._text_area.bind(key, self._undo)
        self._text_area.bind("<Control-n>", self._new_file)
        self._text_area.bind("<Control-o>", self._open_file)
        self._text_area.bind("<Control-s>", self._save_file)
        self._text_area.bind("<Control-S>", self._save_file_as)
        self._text_area.bind("<Control-p>", self._print)
        return


def main():
    NoteWindow(width=850, height=850).mainloop()


main()