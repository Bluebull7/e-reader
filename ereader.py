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
        self.geometry("800x600")

        # State variables
        self.pdf_doc = None
        self.current_page_index = 0
        self.total_pages = 0
        self.zoom_level = 100  # Default zoom level (in percentage)

        # Canvas to display PDF pages
        self.canvas = tk.Canvas(self, background="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Controls Frame
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

        # Bindings for Zoom
        #self.bind("<Control-minus>", self.zoom_out)
        #self.bind("<Control-plus>", self.zoom_in)
        self.bind("<Control-KeyPress-minus>", self.zoom_out)
        self.bind("<Control-KeyPress-equal>", self.zoom_in)

        # Open PDF on startup if provided; otherwise prompt for file
        if pdf_path:
            self.load_pdf(pdf_path)
        else:
            self.open_pdf_dialog()

        # Bind ESC to exit fullscreen mode or close
        self.bind("<Escape>", self.exit_fullscreen)

    def open_pdf_dialog(self):
        """Prompt user to select a PDF file to open."""
        pdf_file = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if pdf_file:
            self.load_pdf(pdf_file)
        else:
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
        # Apply zoom level (100 dpi is default, scaled by zoom level)
        zoom_matrix = fitz.Matrix(self.zoom_level / 100, self.zoom_level / 100)
        pix = page.get_pixmap(matrix=zoom_matrix)
        mode = "RGB" if pix.alpha == 0 else "RGBA"

        # Convert PyMuPDF pixmap to PIL Image
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)

        # Convert PIL image to a Tkinter image
        self.tk_img = ImageTk.PhotoImage(img)

        # Clear the canvas
        self.canvas.delete("all")

        # Center the image on the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_offset = (canvas_width - pix.width) // 2
        y_offset = (canvas_height - pix.height) // 2

        # Draw the image on the canvas
        self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=self.tk_img)

        # Update window title
        self.title(f"Distraction-Free PDF Reader - Page {page_index + 1}/{self.total_pages} - Zoom: {self.zoom_level}%")

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

    def zoom_in(self, event=None):
        """Zoom in by increasing the zoom level."""
        self.zoom_level = min(self.zoom_level + 10, 300)  # Cap at 300%
        self.show_page(self.current_page_index)

    def zoom_out(self, event=None):
        """Zoom out by decreasing the zoom level."""
        self.zoom_level = max(self.zoom_level - 10, 50)  # Cap at 50%
        self.show_page(self.current_page_index)

def main():
    import sys
    pdf_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = PDFReader(pdf_file)
    app.mainloop()

if __name__ == "__main__":
    main()
