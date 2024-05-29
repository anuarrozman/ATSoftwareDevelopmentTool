import tkinter as tk

def create_gui(version):
    root = tk.Tk()
    root.title("My Application")

    # Main frame
    main_frame = tk.Frame(root, width=400, height=300)
    main_frame.pack_propagate(False)  # Prevent frame from resizing to widgets
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Version label
    version_label = tk.Label(main_frame, text=f"Version: {version}", anchor='se')
    version_label.pack(side=tk.BOTTOM, anchor='se', padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    version_number = "1.0.0"
    create_gui(version_number)
