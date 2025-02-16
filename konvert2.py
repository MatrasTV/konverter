import os
from PIL import Image, ImageEnhance
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox, StringVar, Scale, HORIZONTAL, Checkbutton, IntVar, Menu
from tkinter import ttk

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter by MatrasTV")
        self.root.resizable(False, False)  # Disable window resizing

        self.filename = ""
        self.output_folder = ""
        self.replace_black = IntVar()  # Variable to track the state of the checkbox

        # Menu Bar
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        # Adding "File" menu
        file_menu = Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.load_image)
        file_menu.add_command(label="Выбрать папку", command=self.select_output_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        self.menu.add_cascade(label="Файл", menu=file_menu)

        # Adding "Help" menu
        help_menu = Menu(self.menu, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about_info)
        self.menu.add_cascade(label="Справка", menu=help_menu)

        # UI Elements
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="NSEW")

        ttk.Label(main_frame, text="Выберите изображение:").grid(row=0, column=0, padx=10, pady=10, sticky="W")
        ttk.Button(main_frame, text="Открыть файл", command=self.load_image).grid(row=0, column=1, padx=10, pady=10)

        self.file_label = ttk.Label(main_frame, text="Файл не выбран")
        self.file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="W")

        ttk.Label(main_frame, text="Резкость:").grid(row=2, column=0, padx=10, pady=10, sticky="W")
        self.sharpness_value = ttk.Label(main_frame, text="1.0")
        self.sharpness_value.grid(row=2, column=1, padx=10, pady=10, sticky="E")

        self.sharpness_scale = ttk.Scale(main_frame, from_=0.1, to=5.0, orient=HORIZONTAL, command=self.update_sharpness_value)
        self.sharpness_scale.set(1.0)
        self.sharpness_scale.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="EW")

        ttk.Checkbutton(main_frame, text="Заменить черный цвет на 1", variable=self.replace_black).grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="W")

        ttk.Label(main_frame, text="Название выходного файла:").grid(row=5, column=0, padx=10, pady=10, sticky="W")
        self.output_name = StringVar()
        ttk.Entry(main_frame, textvariable=self.output_name).grid(row=5, column=1, padx=10, pady=10, sticky="EW")

        ttk.Label(main_frame, text="Выбрать папку сохранения:").grid(row=6, column=0, padx=10, pady=10, sticky="W")
        ttk.Button(main_frame, text="Выбрать папку", command=self.select_output_folder).grid(row=6, column=1, padx=10, pady=10)

        self.folder_label = ttk.Label(main_frame, text="Папка не выбрана", anchor="w")
        self.folder_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="EW")
        self.folder_label.bind("<Configure>", self.truncate_folder_label)

        ttk.Button(main_frame, text="Преобразовать", command=self.convert_image).grid(row=8, column=0, columnspan=2, padx=10, pady=10)

        # Configure weights for better scaling
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def truncate_folder_label(self, event=None):
        text = self.output_folder if self.output_folder else "Папка не выбрана"
        width = self.folder_label.winfo_width()
        if width > 0:
            while self.folder_label.winfo_reqwidth() > width:
                text = text[:-4] + "..."
                self.folder_label.config(text=text)

    def update_sharpness_value(self, value):
        self.sharpness_value.config(text=f"{float(value):.1f}")

    def load_image(self):
        self.filename = filedialog.askopenfilename(title="Выберите изображение", filetypes=[("Изображения", "*.png;*.jpg;*.jpeg"), ("Все файлы", "*.*")])
        if self.filename:
            self.file_label.config(text=f"Файл выбран: {os.path.basename(self.filename)}")
        else:
            self.file_label.config(text="Файл не выбран")

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Выберите папку для сохранения")
        if self.output_folder:
            self.folder_label.config(text=f"Папка: {self.output_folder}")
            self.truncate_folder_label()
        else:
            self.folder_label.config(text="Папка не выбрана")

    def convert_image(self):
        if not self.filename:
            messagebox.showerror("Ошибка", "Сначала выберите изображение")
            return

        if not self.output_folder:
            messagebox.showerror("Ошибка", "Выберите папку для сохранения файла")
            return

        output_name = self.output_name.get().strip()
        if not output_name:
            messagebox.showerror("Ошибка", "Введите название выходного файла")
            return

        try:
            colors = 256  # Жестко заданное ограничение по цветам
            factor = self.sharpness_scale.get()
            with Image.open(self.filename) as img:
                img = img.resize((64, 64))
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(factor)

                # Проверяем режим изображения
                if img.mode == "RGBA":
                    img = img.convert("RGB")  # Убираем альфа-канал, если он есть

                # Применяем ограничение цветов
                img = img.quantize(colors=colors, method=2)  # Используем Fast Octree

                # Конвертация обратно в RGB для корректной обработки
                img = img.convert("RGB")

                # Конвертация изображения в текстовый формат
                otvet = "{"  # JSON-подобная структура
                for x in range(64):
                    otvet += f"\"{x}\":{{"
                    for y in range(64):
                        pix = img.getpixel((x, y))
                        pixel_value = int(f"{pix[0]:02x}{pix[1]:02x}{pix[2]:02x}", 16)

                        # Замена черного цвета на 1, если включен чекбокс
                        if self.replace_black.get() == 1 and pixel_value == 0:
                            pixel_value = 1

                        otvet += f"\"{y}\":{pixel_value}.0"
                        if y != 63:
                            otvet += ","
                    otvet += "}"
                    if x != 63:
                        otvet += ","
                otvet += "}"

                # Сохранение в текстовый файл
                output_path = os.path.join(self.output_folder, output_name + ".txt")
                with open(output_path, "w") as text_file:
                    text_file.write(otvet)

            messagebox.showinfo("Успех", f"Изображение успешно преобразовано и сохранено в {output_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось преобразовать изображение: {e}")

    def show_about_info(self):
        messagebox.showinfo("О программе", "Image Converter v1.0\nАвтор: MatrasTV\nПрограмма для преобразования изображений в текстовый формат.")

if __name__ == "__main__":
    root = Tk()
    app = ImageConverterApp(root)
    root.mainloop()