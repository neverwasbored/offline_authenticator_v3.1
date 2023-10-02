import tkinter as tk
from tkinter import ttk
import json
import pyotp
import time
import pyperclip


def copy_event():
    if actual_code.cget("text") != "":
        pyperclip.copy(actual_code.cget("text"))
        show_message()


def show_message():
    style.configure("COPY.TLabel", background="#007538")
    style.configure("LINE.TFrame", background="#007538")
    notify_label.configure(text="successful!")
    window.after(3000, hide_message)


def hide_message():
    style.configure("COPY.TLabel", background="#333333")
    style.configure("LINE.TFrame", background="#333333")
    notify_label.configure(text="")


def processing_data(event):
    notify_wind.configure(text="")
    output_search_input = search_input.get().lower()
    found_items = []
    if original_data != None:
        for dictionary in original_data:
            if "name" in dictionary and dictionary["name"].lower() == output_search_input:
                found_items.append(dictionary)
        if found_items == []:
            notify_wind.configure(
                text="Current key is not found!", background="#5E0C0C")
        else:
            notify_wind.configure(
                text=f"{found_items[0]['name']}", background="#0c5e13")
            old_radio = selected_app_var.get()
            update_otp_time(found_items[0], output_search_input, old_radio)


def update_otp_time(found_items, output_search_input, old_radio):
    new_search_input = search_input.get().lower()
    if output_search_input == new_search_input:
        key = found_items
        secret_code = key['key']
        totp = pyotp.TOTP(secret_code)
        authy_code = totp.now()
        remaining_code = round(
            totp.interval - (time.time() % totp.interval))
        actual_code.configure(text=f"{authy_code}")
        time_label.configure(text=f"{remaining_code}")
        window.after(1000, update_otp_time, found_items,
                     output_search_input, old_radio)

# you can add 2 more files like this


def bitmart_event():
    try:
        with open('pairs_bitmart.json', 'r') as json_file:
            notify_wind.configure(text="Write your email")
            original_data = json.load(json_file)
            return (original_data)
    except FileNotFoundError:
        notify_wind.configure(text="Failed Bitmart.json")


def apply_hover_style(event):
    event.widget.configure(style="HOVER.TRadiobutton")


def remove_hover_style(event):
    event.widget.configure(style="TRadiobutton")


def get_index_by_content(listbox, search_content):
    for i in range(listbox.size()):
        if listbox.get(i) == search_content:
            return i
    return None


def on_select(event, listbox):
    if listbox.curselection():
        selected_item = listbox.get(listbox.curselection())
        index = get_index_by_content(listbox, selected_item)
        if index is not None:
            selected_item_list = selected_item.split()
            search_entry.delete(0, tk.END)
            search_entry.insert(index=0, string=selected_item_list[0])
            search_by_entry(event, listbox)


def display_json_data(original_data, listbox):
    if original_data != None:
        listbox.delete(0, tk.END)
        for item in original_data:
            name = item.get('name', 'No key')
            key = item.get('key', 'No value')
            listbox.insert(tk.END, f"{name} - {key}")


def search_by_entry(event, listbox):
    listbox.selection_clear(0, tk.END)
    coincidence_list = []
    user_data = search_entry.get().lower()
    for item in listbox.get(0, tk.END):
        email_in_listbox = item.split()[0].lower()
        if user_data in email_in_listbox:
            coincidence_list.append(item)
    if len(coincidence_list) != 0:
        first_value = coincidence_list[0]
        curr_index = get_index_by_content(listbox, first_value)
        listbox.selection_set(curr_index)
        listbox.see(curr_index)
        count_coincidence.configure(text=f"Count: {len(coincidence_list)}")
        if len(coincidence_list) == 1:
            user_selected = str(coincidence_list[0]).split()[0]
            search_entry.delete(0, tk.END)
            search_entry.insert(index=0, string=f"{str(user_selected)}")
            search_entry.config(state="readonly")
            listbox.configure(selectmode="none")
            search_entry.configure(style="SUCCESS.TEntry")
            popup.after(1000, lambda: normal_mode_entry(listbox))

    else:
        search_entry.config(state="readonly")
        count_coincidence.configure(text=f"Count: {0}")
        search_entry.configure(style="FAILED.TEntry")
        listbox.configure(selectmode="none")
        popup.after(1000, lambda: normal_mode_entry(listbox))


def normal_mode_entry(listbox):
    search_entry.config(state="normal")
    search_entry.configure(style="DEFAULT.TEntry")
    listbox.configure(selectmode="browse")


def delete_item(event, listbox):
    if search_entry.get() != "":
        # permission window
        permission = tk.Toplevel(popup, background="#484848")
        permission.title("Confirm your choise")
        permission.iconbitmap("logo.ico")
        permission.geometry("350x75")

        permission.maxsize(height=75, width=350)
        permission.minsize(height=75, width=350)

        # confirm frame
        confirm_frame = ttk.Frame(permission, style="ADDFR.TFrame")
        confirm_frame.pack(side="top")

        # confirm label
        confirm_label = ttk.Label(
            confirm_frame, text="Are you sure you want to delete?", style="ADDLAB.TLabel")
        confirm_label.grid(row=0, column=1)

        # data label
        data_label = ttk.Label(
            confirm_frame, text=f"{search_entry.get()}", style="ADDLAB.TLabel")
        data_label.grid(row=1, column=1)

        # true btn
        true_btn = ttk.Button(confirm_frame, text="Yes",
                              style="ADDBTN.TButton")
        true_btn.bind("<ButtonPress-1>",
                      lambda event: true_func(event, listbox, permission))
        true_btn.grid(row=2, column=0)

        # false btn
        false_btn = ttk.Button(confirm_frame, text="No",
                               command=permission.destroy, style="ADDBTN.TButton")
        false_btn.grid(row=2, column=2)


def true_func(event, listbox, permission):
    for elem in original_data:
        if elem["name"] == search_entry.get():
            current_index = get_index_by_content(
                listbox, f"{elem['name']} - {elem['key']}")
            original_data.remove(elem)
            # here you can add 2 more files
            if selected_app_var.get() == 0:
                try:
                    with open("pairs_bitmart.json", 'w') as json_file:
                        json.dump(original_data, json_file)
                    permission.destroy()
                    search_entry.delete(0, tk.END)
                    search_entry.configure(style="SUCCESS.TEntry")
                    popup.after(1000, lambda: normal_mode_entry(listbox))
                    bitmart_event()
                    display_json_data(original_data, listbox)
                    count_coincidence.configure(
                        text=f"Count: {listbox.size()}")
                    listbox.see(current_index - 1)
                except:
                    search_entry.configure(style="FAILED.TEntry")
                    popup.after(1000, lambda: normal_mode_entry(listbox))
                    bitmart_event()
                    display_json_data(original_data, listbox)


def add_pair(event, name_entry, key_entry, add_button, listbox):
    if original_data != None:
        if name_entry.get() != "" and key_entry != "":
            name_value = name_entry.get()
            key_value = key_entry.get()
            export_dict = {
                "name": f"{name_value}",
                "key": f"{key_value}"
            }
            original_data.append(export_dict)
            # here you can add more files
            if selected_app_var.get() == 0:
                try:
                    with open("pairs_bitmart.json", 'w') as json_file:
                        json.dump(original_data, json_file)
                    name_entry.delete(0, tk.END)
                    key_entry.delete(0, tk.END)
                    add_button.configure(style="SUCCESS.TButton")
                    popup.after(1000, lambda: normal_mode_button(add_button))
                    bitmart_event()
                    display_json_data(original_data, listbox)
                    count_coincidence.configure(
                        text=f"Count: {listbox.size()}")
                    listbox.see(listbox.size() - 1)
                    listbox.select_set(listbox.size() - 1)
                except:
                    add_button.configure(style="FAILED.TButton")
                    popup.after(1000, lambda: normal_mode_button(add_button))
                    bitmart_event()
                    display_json_data(original_data, listbox)


def normal_mode_button(add_button):
    add_button.configure(style="DEFAULT.TButton")


def show_popup():
    global popup
    global search_entry
    global count_coincidence

    # popup settings
    popup = tk.Toplevel(window)
    popup.title("Add/Remove")
    popup.configure(background="#333333")
    popup.iconbitmap("logo.ico")
    popup.geometry("400x450")

    popup.maxsize(width=400, height=450)
    popup.minsize(width=400, height=450)

    # listbox of keys and values
    list_frame = ttk.Frame(popup, height=15, style="POPUP.TFrame")
    list_frame.pack(side="top")

    # add slider
    scrollbar = ttk.Scrollbar(
        list_frame, orient="vertical", style="Vertical.TScrollbar")
    scrollbar.grid(row=0, column=3, sticky="ns")

    # listbox
    listbox = tk.Listbox(list_frame, width=60, height=15)
    listbox.grid(row=0, column=0, columnspan=3)
    listbox.bind("<<ListboxSelect>>", lambda event: on_select(
        event, listbox))

    # connect listbox and slider
    scrollbar.config(command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)

    # display pairs
    if original_data != None:
        display_json_data(original_data, listbox)

    # search Entry and delete btn and count of coincidence
    search_entry = ttk.Entry(list_frame,  width=35)
    search_entry.grid(row=1, column=0, sticky="w", pady=5)

    delete_btn = ttk.Button(list_frame, style="DELETEBTN.TButton", text="Delete",
                            cursor="hand2", width=10)
    delete_btn.bind("<ButtonPress-1>",
                    lambda event: delete_item(event, listbox))
    delete_btn.grid(row=1, column=2, sticky="e", pady=5, padx=5)

    count_coincidence = ttk.Label(
        list_frame, text=f"Count: {listbox.size()}", style="COUNT.TLabel")
    count_coincidence.grid(row=1, column=1, sticky="w", pady=10)

    # bind search_entry
    search_entry.bind(
        "<KeyRelease>", lambda event: search_by_entry(event, listbox))

    # add frame
    add_frame = ttk.Frame(popup, style="ADDFR.TFrame")
    add_frame.pack(side="top", pady=10)

    # add title
    add_title = ttk.Label(add_frame, text="Add function",
                          style="ADDLAB.TLabel")
    add_title.grid(row=0,  pady=10, column=0, columnspan=3)

    # name label
    name_title = ttk.Label(add_frame, text="Name:", style="ADDLAB.TLabel")
    name_title.grid(row=1, sticky="w",  column=0,  pady=5, padx=5)

    # name entry
    name_entry = ttk.Entry(add_frame, width=30)
    name_entry.grid(row=1, sticky="w",  column=1,  pady=5, padx=5)

    # key label
    key_title = ttk.Label(add_frame, text="Key:", style="ADDLAB.TLabel")
    key_title.grid(row=2, sticky="w",  column=0,  pady=5, padx=5)

    # key entry
    key_entry = ttk.Entry(add_frame, width=30)
    key_entry.grid(row=2, sticky="w",  column=1,  pady=5, padx=5)

    # add button
    add_button = ttk.Button(add_frame, text="Add pair", style="ADDBTN.TButton")
    add_button.bind("<ButtonPress-1>",
                    lambda event: add_pair(event, name_entry, key_entry, add_button, listbox))
    add_button.grid(row=3, sticky="s", column=0, columnspan=3, pady=10)


# app settings
window = tk.Tk()
window.title("HHTNQ AUTH")
window.geometry("300x400")
window.configure(background="#333333")
window.iconbitmap("logo.ico")

window.minsize(width=300, height=400)
window.maxsize(width=300, height=400)

# styles
style = ttk.Style()
style.theme_use("clam")
style.configure("Frames.TFrame", background="#484848")
style.configure("TRadiobutton", background="#484848",
                foreground="white", borderwidth=0, font=("Inter", 12), hovercolor="#484848")
style.configure("SW.TLabel", background="#484848",
                foreground="white", font=("Inter", 12))
style.configure("HHTNQ.TLabel", background="#333333",
                foreground="white", font=("Inter", 16), padding=(0, 25))
style.configure("HOVER.TRadiobutton", foreground="black")
style.configure("REFRESH.TButton", background="#484848",
                borderwidth=0, highlightthickness=0)
style.configure("2fa.TLabel", background="#484848",
                font=("Inter", 16), foreground="white")
style.configure("COPY.TButton", background="#ffffff", foreground="black")
style.configure("EMAIL.TEntry", foreground="black")
style.configure("COPY.TLabel", background="#333333", foreground="white")
style.configure("LINE.TFrame", background="#333333")
style.configure("HHTNQ.TFrame", background="#333333")
style.configure("SUCCESS.TEntry", fieldbackground="#32a852")
style.configure("DEFAULT.TEntry", fieldbackground="white")
style.configure("FAILED.TEntry", fieldbackground="#a8313f")
style.configure("SUCCESS.TButton", background="#32a852")
style.configure("DEFAULT.TButton")
style.configure("POPUP.TFrame", background="#484848")
style.configure("DELETEBTN.TButton", padding=(0, 1),
                background="white")
style.configure("COUNT.TLabel", background="#484848",
                foreground="white")
style.configure("ADDFR.TFrame", background="#484848")
style.configure("ADDLAB.TLabel", background="#484848", foreground="white")
style.configure("ADDBTN.TButton", background="white")
style.configure("Version.TLabel", background="#333333", foreground="#666")
style.configure("FAILED.TButton", background="#a8313f")
style.configure("Vertical.TScrollbar", gripcount=0,
                troughcolor="white", bordercolor="gray")

# HHTNQ frame
hhtnq_frame = ttk.Frame(window, style="HHTNQ.TFrame")
hhtnq_frame.pack()

# HHTNQ label
logo_image = tk.PhotoImage(file="logo.png")
smaller_image = logo_image.subsample(x=12, y=12)
hhtnq_label = ttk.Label(hhtnq_frame, text="HHTNQ",
                        style="HHTNQ.TLabel")
hhtnq_image = ttk.Label(hhtnq_frame, style="HHTNQ.TLabel", image=smaller_image)
hhtnq_label.grid(row=0, column=1, padx=10)
hhtnq_image.grid(row=0, column=0, padx=10)

# main frame
frame = ttk.Frame(window, width=280, style="Frames.TFrame")
frame.pack(side="top")

# main label
main_label = ttk.Label(frame, text="Search by email", style="SW.TLabel")
main_label.grid(row=0, column=1, pady=10, padx=5)

# search input
search_input = ttk.Entry(
    frame, style="EMAIL.TEntry", width=25)
search_input.bind('<KeyRelease>', lambda event: processing_data(event))
search_input.grid(row=1, column=1, pady=10, padx=5)

# refresh btn
refresh_image = tk.PhotoImage(file="refresh.png")
refresh_btn = ttk.Button(frame, image=refresh_image,
                         cursor="hand2", style="REFRESH.TButton", command=show_message)
refresh_btn.bind('<ButtonPress-1>', lambda event: processing_data(event))
refresh_btn.grid(row=1, column=2, pady=10, padx=5)

# notification frame
notification_frame = ttk.Frame(
    frame, border=1)
notification_frame.grid(row=2, column=0, columnspan=3)

# notification window
notify_wind = ttk.Label(
    notification_frame, text="Write your email", style="SW.TLabel")
notify_wind.pack()

# row with code label and actual 2fa code and time left
code_label = ttk.Label(frame, text="Code:", style="SW.TLabel")
code_label.grid(row=3, column=0, pady=10, sticky="n", padx=5)

actual_code = ttk.Label(frame, text="", style="2fa.TLabel")
actual_code.grid(row=3, column=1, pady=10)

time_label = ttk.Label(frame, text="", style="SW.TLabel")
time_label.grid(row=3, column=2, pady=10, padx=5, sticky="n")

# copy to clipboard btn
copy_btn = ttk.Button(frame, text="Copy to clipboard",
                      cursor="hand2", style="COPY.TButton", command=copy_event)
copy_btn.grid(row=4, column=1, pady=10, padx=5)

# popup btn
add_image = tk.PhotoImage(file="add.png")
top_level_btn = ttk.Button(
    frame, cursor="hand2", style="REFRESH.TButton", command=show_popup, image=add_image)
top_level_btn.grid(row=4, column=2, pady=10, padx=5)

# switch frame
switch_frame = ttk.Frame(window, style="Frames.TFrame")
switch_frame.pack(side="bottom", fill="both")

# chose your service
selected_app_var = tk.IntVar(value=0)

bitmart_btn = ttk.Radiobutton(switch_frame, text="Bitmart",
                              style="TRadiobutton", cursor="hand2", variable=selected_app_var, value=0, command=bitmart_event)
bitmart_btn.grid(row=0, column=0, padx=17, pady=5)

free_zone = ttk.Radiobutton(switch_frame, text="Free",
                            style="TRadiobutton", cursor="hand2", variable=selected_app_var, value=1)
free_zone.grid(row=0, column=1, padx=17, pady=5)

one_more_free = ttk.Radiobutton(switch_frame, text="superx",
                                style="TRadiobutton", cursor="hand2", variable=selected_app_var, value=2)
one_more_free.grid(row=0, column=2, padx=17, pady=5)

# initalisation bitmart.json
original_data = bitmart_event()

# switch app binds
bitmart_btn.bind('<ButtonPress-1>', lambda event: processing_data(event))
free_zone.bind('<ButtonPress-1>', lambda event: processing_data(event))
one_more_free.bind('<ButtonPress-1>', lambda event: processing_data(event))

# hover
bitmart_btn.bind("<Enter>", apply_hover_style)
bitmart_btn.bind("<Leave>", remove_hover_style)
free_zone.bind("<Enter>", apply_hover_style)
free_zone.bind("<Leave>", remove_hover_style)
one_more_free.bind("<Enter>", apply_hover_style)
one_more_free.bind("<Leave>", remove_hover_style)

# notify frame
notify_frame = ttk.Frame(window, style="LINE.TFrame")
notify_frame.pack(side="bottom", fill="both")

# notify label
notify_label = ttk.Label(notify_frame, text="", style="COPY.TLabel")
notify_label.pack()

# version label
version_label = ttk.Label(window, text="Version 3.1", style="Version.TLabel")
version_label.pack(side="right")


window.mainloop()
