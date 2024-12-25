#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class PDFReader(tk.Tk):
    def __init__(self, pdf_path=None):
        super().__init__()

        # Application title and geometry
        self.title("Distraction-Free PDF Reader")
        self.geometry("800x600")  # Feel free to change the default size

        # State variables
        self.pdf_doc = None
        self.current_page_index = 0
        self.total_pages = 0

        # Canvas to display PDF pages
        self.canvas = tk.Canvas(self, background="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Controls Frame (only visible if you hover or move the mouse, if you want)
        self.controls_frame = tk.Frame(self, bg="gray")
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Previous Page Button
        self.prev_button = tk.Button(self.controls_frame, text="<< Prev", command=self.show_previous_page)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Next Page Button
        self.next_button = tk.Button(self.controls_frame, text="Next >>", command=self.show_next_page)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Go to Page
        self.page_label = tk.Label(self.controls_frame, text="Go to Page:")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.page_entry = tk.Entry(self.controls_frame, width=5)
        self.page_entry.pack(side=tk.LEFT, padx=5)
        self.page_entry.bind("<Return>", self.go_to_page)

        # Fullscreen toggle button
        self.fullscreen_btn = tk.Button(self.controls_frame, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Open PDF on startup if provided; otherwise prompt for file
        if pdf_path:
            self.load_pdf(pdf_path)
        else:
            self.open_pdf_dialog()

        # Bind ESC to exit fullscreen mode or close
        self.bind("<Escape>", self.exit_fullscreen)
        
        # Optional: Hide controls after some period of inactivity (for pure distraction-free)
        # You could implement a mouse motion binding that shows/hides the controls.

    def open_pdf_dialog(self):
        """Prompt user to select a PDF file to open."""
        pdf_file = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if pdf_file:
            self.load_pdf(pdf_file)
        else:
            # If user cancels, close the app or handle differently
            self.destroy()

    def load_pdf(self, pdf_file):
        """Load the given PDF file using PyMuPDF."""
        try:
            self.pdf_doc = fitz.open(pdf_file)
            self.current_page_index = 0
            self.total_pages = len(self.pdf_doc)
            self.show_page(self.current_page_index)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")
            self.destroy()

    def show_page(self, page_index):
        """Render and display the specified page index."""
        if not self.pdf_doc:
            return
        if page_index < 0 or page_index >= self.total_pages:
            return

        page = self.pdf_doc[page_index]
        pix = page.get_pixmap(dpi=100)  # Increase DPI if you need higher quality
        mode = "RGB" if pix.alpha == 0 else "RGBA"

        # Convert PyMuPDF pixmap to PIL Image
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        # Optional: You can resize the image to fit the window:
        # img = img.resize((new_width, new_height), Image.ANTIALIAS)

        # Convert PIL image to a Tkinter image
        self.tk_img = ImageTk.PhotoImage(img)
        
        # Clear the canvas
        self.canvas.delete("all")

        # Center the image on the canvas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()
        self.image_width = img.width
        self.image_height = img.height

        x_offset = (self.canvas_width - self.image_width) // 2
        y_offset = (self.canvas_height - self.image_height) // 2

        # Draw the image on the canvas
        self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.tk_img)

        # Update window title
        self.title(f"Distraction-Free PDF Reader - Page {page_index + 1}/{self.total_pages}")

    def show_next_page(self):
        """Show the next page if available."""
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.show_page(self.current_page_index)

    def show_previous_page(self):
        """Show the previous page if available."""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.show_page(self.current_page_index)

    def go_to_page(self, event=None):
        """Jump to a specific page based on user input."""
        try:
            page_num = int(self.page_entry.get()) - 1
            if 0 <= page_num < self.total_pages:
                self.current_page_index = page_num
                self.show_page(self.current_page_index)
            else:
                messagebox.showwarning("Invalid Page", "Page out of range.")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number.")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        is_fullscreen = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not is_fullscreen)

    def exit_fullscreen(self, event=None):
        """Exit fullscreen if in fullscreen mode, else close app."""
        if self.attributes("-fullscreen"):
            self.attributes("-fullscreen", False)
        else:
            self.destroy()

    def on_resize(self, event):
        """If you want to scale the page automatically on window resize, implement it here."""
        pass

def main():
    import sys
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = PDFReader(pdf_file)
    app.mainloop()

if __name__ == "__main__":
    main()
