import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import heapq
import time
import numpy as np

class DijkstraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Алгоритм Дейкстри - Пошук найкоротшого шляху між містами України")
        self.root.geometry("1200x800")
        
        # Створення графу
        self.graph = nx.DiGraph()
        
        # Дані про міста України
        self.cities = [
            "Вінниця", "Дніпро", "Донецьк", "Житомир", "Запоріжжя", "Івано-Франківськ", 
            "Київ", "Кропивницький", "Луганськ", "Луцьк", "Львів", "Маріуполь", 
            "Мелітополь", "Миколаїв", "Одеса", "Полтава", "Рівне", "Севастополь", 
            "Сімферополь", "Суми", "Тернопіль", "Ужгород", "Харків", "Херсон", 
            "Хмельницький", "Черкаси", "Чернівці", "Чернігів", "Кривий Ріг"
        ]
        
        # Додавання міст до графу
        for city in self.cities:
            self.graph.add_node(city)
        
        # Додавання шляхів (з таблиці відстаней)
        self.routes = [
            ("Вінниця", "Житомир", 127),
            ("Вінниця", "Київ", 267),
            ("Вінниця", "Кропивницький", 320),
            ("Вінниця", "Миколаїв", 428),
            ("Вінниця", "Одеса", 423),
            ("Вінниця", "Черкаси", 341),
            ("Вінниця", "Чернівці", 276),
            ("Дніпро", "Донецьк", 248),
            ("Дніпро", "Запоріжжя", 85),
            ("Дніпро", "Кропивницький", 244),
            ("Дніпро", "Кривий Ріг", 146),
            ("Дніпро", "Полтава", 160),
            ("Дніпро", "Харків", 218),
            ("Донецьк", "Луганськ", 156),
            ("Донецьк", "Маріуполь", 113),
            ("Донецьк", "Харків", 294),
            ("Запоріжжя", "Мелітополь", 125),
            ("Івано-Франківськ", "Тернопіль", 133),
            ("Івано-Франківськ", "Ужгород", 293),
            ("Київ", "Житомир", 140),
            ("Київ", "Полтава", 340),
            ("Київ", "Суми", 333),
            ("Київ", "Черкаси", 189),
            ("Київ", "Чернігів", 148),
            ("Кропивницький", "Полтава", 246),
            ("Луганськ", "Харків", 325),
            ("Львів", "Івано-Франківськ", 134),
            ("Львів", "Луцьк", 151),
            ("Львів", "Рівне", 211),
            ("Львів", "Тернопіль", 127),
            ("Львів", "Ужгород", 268),
            ("Львів", "Чернівці", 268),
            ("Мелітополь", "Маріуполь", 192),
            ("Мелітополь", "Сімферополь", 250),
            ("Миколаїв", "Херсон", 69),
            ("Рівне", "Житомир", 188),
            ("Рівне", "Луцьк", 73),
            ("Рівне", "Тернопіль", 155),
            ("Харків", "Полтава", 143),
            ("Херсон", "Мелітополь", 231),
            ("Хмельницький", "Вінниця", 119),
            ("Хмельницький", "Житомир", 183),
            ("Хмельницький", "Рівне", 194),
            ("Хмельницький", "Тернопіль", 112),
            ("Хмельницький", "Чернівці", 187),
            ("Суми", "Харків", 184),
            ("Черкаси", "Полтава", 233),
            ("Полтава", "Суми", 175),
            ("Чернігів", "Суми", 306),
            ("Сімферополь", "Севастополь", 81),
        ]
        
        # Додавання обох напрямків для кожного маршруту (неорієнтований граф)
        for start, end, distance in self.routes:
            self.graph.add_edge(start, end, weight=distance)
            self.graph.add_edge(end, start, weight=distance)  # Додаємо зворотній напрямок
        
        # Створення елементів інтерфейсу
        self.create_widgets()
        
        # Змінна для зберігання поточного результату
        self.current_path = None
        self.current_distance = None
        
        # Відображення початкового графу
        self.draw_graph()
        
    def create_widgets(self):
        # Створення головного фрейму
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Лівий фрейм для графу
        self.graph_frame = ttk.LabelFrame(main_frame, text="Граф маршрутів між містами України")
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Правий фрейм для керування
        control_frame = ttk.LabelFrame(main_frame, text="Керування")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Вибір початкового міста
        ttk.Label(control_frame, text="Початкове місто:").pack(pady=(10, 5))
        self.start_city_var = tk.StringVar()
        self.start_city_combo = ttk.Combobox(control_frame, textvariable=self.start_city_var, values=sorted(self.cities))
        self.start_city_combo.pack(padx=10, pady=5, fill=tk.X)
        self.start_city_combo.set("Київ")
        
        # Вибір кінцевого міста
        ttk.Label(control_frame, text="Кінцеве місто:").pack(pady=(10, 5))
        self.end_city_var = tk.StringVar()
        self.end_city_combo = ttk.Combobox(control_frame, textvariable=self.end_city_var, values=sorted(self.cities))
        self.end_city_combo.pack(padx=10, pady=5, fill=tk.X)
        self.end_city_combo.set("Львів")
        
        # Кнопка пошуку шляху
        ttk.Button(control_frame, text="Знайти найкоротший шлях", command=self.find_shortest_path).pack(padx=10, pady=20, fill=tk.X)
        
        # Кнопки для модифікації графу
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(control_frame, text="Модифікація графу:").pack(pady=5)
        
        ttk.Button(control_frame, text="Додати місто (клікніть на карті)", command=self.add_city).pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Видалити місто", command=self.remove_city).pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Додати маршрут", command=self.add_route).pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Видалити маршрут", command=self.remove_route).pack(padx=10, pady=5, fill=tk.X)
        ttk.Button(control_frame, text="Скинути модифікації", command=self.reset_graph).pack(padx=10, pady=20, fill=tk.X)
        
        # Фрейм для результатів
        self.result_frame = ttk.LabelFrame(main_frame, text="Результати")
        self.result_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        self.result_text = tk.Text(self.result_frame, height=5, width=50, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.result_text.config(state=tk.DISABLED)
    
    def draw_graph(self, highlight_path=None):
        # Очищення попереднього графу
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        # Створення більшої фігури для відображення графу
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111)
        
        # Додаємо фон з картою України у кольорах прапора
        try:
            # Завантажуємо зображення України
            ukraine_img = plt.imread('1500648.png')  # Шлях до PNG файлу
            
            # Обробляємо зображення для створення маски
            if ukraine_img.ndim == 3:  # RGB або RGBA
                if ukraine_img.shape[2] == 4:  # RGBA
                    # Використовуємо альфа канал як маску
                    mask = ukraine_img[:, :, 3] > 0
                else:  # RGB
                    # Створюємо маску на основі чорного кольору
                    mask = ~np.all(ukraine_img[:, :, :3] < 0.1, axis=2)
            else:  # Grayscale
                mask = ukraine_img > 0.1
            
            # Зберігаємо маску для валідації при додаванні міста
            self.ukraine_mask = mask
            self.ukraine_extent = [-1, 1.25, -1.5, 1.25]  # Межі зображення [xmin, xmax, ymin, ymax]
            
            # Створюємо нове RGBA зображення з кольорами прапора України
            height, width = mask.shape[:2]
            ukraine_colored = np.zeros((height, width, 4))
            
            # Верхня половина - синій (для прапора України)
            ukraine_colored[:height//2, :, 0] = 0.0  # R
            ukraine_colored[:height//2, :, 1] = 0.3  # G
            ukraine_colored[:height//2, :, 2] = 0.7  # B
            
            # Нижня половина - жовтий (для прапора України)
            ukraine_colored[height//2:, :, 0] = 1.0  # R
            ukraine_colored[height//2:, :, 1] = 0.8  # G
            ukraine_colored[height//2:, :, 2] = 0.0  # B
            
            # Застосовуємо маску для прозорості
            ukraine_colored[:, :, 3] = mask.astype(float) * 0.5  # 50% прозорість
            
            # Показуємо зображення як фон
            ax.imshow(ukraine_colored, extent=self.ukraine_extent, aspect='auto', alpha=0.7)
            
        except Exception as e:
            print(f"Помилка завантаження зображення України: {e}")
            # Якщо не вдалося завантажити зображення, використовуємо простий фон
            ax.add_patch(plt.Rectangle((-1, -1.5), 2.25, 2.75, color='#0057B7', alpha=0.3))  # Синій
            ax.add_patch(plt.Rectangle((-1, 0), 2.25, 1.25, color='#FFD700', alpha=0.3))   # Жовтий
            
            # Значення за замовчуванням, якщо немає зображення
            self.ukraine_mask = None
            self.ukraine_extent = [-1, 1.25, -1.5, 1.25]
        
        # Використання фіксованих позицій для міст України
        if not hasattr(self, 'pos'):
            self.pos = {
                "Київ": (0.1, 0.3),
                "Львів": (-0.75, 0.15),
                "Луцьк": (-0.7, 0.45),
                "Рівне": (-0.5, 0.4),
                "Тернопіль": (-0.5, 0.1),
                "Івано-Франківськ": (-0.7, -0.1),
                "Ужгород": (-0.9, -0.2),
                "Чернівці": (-0.55, -0.2),
                "Житомир": (-0.2, 0.35),
                "Хмельницький": (-0.3, 0.1),
                "Вінниця": (-0.2, -0.1),
                "Одеса": (0, -0.6),
                "Миколаїв": (0.1, -0.5),
                "Херсон": (0.25, -0.6),
                "Сімферополь": (0.5, -0.9),
                "Севастополь": (0.4, -1.0),
                "Черкаси": (0.2, 0.0),
                "Кропивницький": (0.2, -0.3),
                "Чернігів": (0.2, 0.6),
                "Суми": (0.5, 0.5),
                "Полтава": (0.4, 0.2),
                "Харків": (0.7, 0.2),
                "Дніпро": (0.5, -0.2),
                "Запоріжжя": (0.5, -0.4),
                "Кривий Ріг": (0.3, -0.4),
                "Мелітополь": (0.6, -0.55),
                "Донецьк": (0.9, -0.3),
                "Луганськ": (1, 0),
                "Маріуполь": (0.8, -0.5)
            }
        
        # Перевіряємо, чи всі вузли мають координати
        for node in self.graph.nodes():
            if node not in self.pos:
                # Якщо вузол не має координат, додаємо випадкові координати
                # (бажано в межах України, але для простоти використовуємо центр карти)
                self.pos[node] = (0.0, 0.0)
                print(f"Увага: Для міста {node} не знайдено координат. Встановлено значення за замовчуванням.")
    
        # Налаштування розмірів і кольорів вершин
        node_size = 700
        node_color = "white"
        edge_color = "gray"
        
        # Відображення ребер графу
        nx.draw_networkx_edges(
            self.graph, self.pos, 
            width=1.0, 
            alpha=0.6, 
            edge_color=edge_color,
            arrows=False,
            ax=ax
        )
        
        # Відображення ваг ребер
        edge_labels = {(u, v): d["weight"] for u, v, d in self.graph.edges(data=True)}
        nx.draw_networkx_edge_labels(
            self.graph, self.pos, 
            edge_labels=edge_labels, 
            font_size=7,
            font_color="darkblue",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=1.5),
            rotate=False,
            ax=ax
        )
        
        # Якщо є шлях для підсвітки
        if highlight_path:
            # Створення списку ребер, що входять до шляху
            path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
            
            # Підсвічування ребер шляху
            nx.draw_networkx_edges(
                self.graph, self.pos, 
                edgelist=path_edges, 
                width=4, 
                alpha=1.0, 
                edge_color='red',
                arrows=True,
                arrowstyle='->',
                arrowsize=20,
                ax=ax
            )
            
            # Підсвічування вершин шляху
            path_nodes = nx.draw_networkx_nodes(
                self.graph, self.pos, 
                nodelist=highlight_path, 
                node_size=node_size*1.2, 
                node_color='red',
                edgecolors="darkred",
                linewidths=2.0,
                ax=ax
            )
            
            # Додаємо ефект тіні до підсвічених вузлів
            if hasattr(path_nodes, 'set_edgecolor'):
                path_nodes.set_edgecolor('darkred')
                path_nodes.set_linewidth(2.0)
        
        # Відображення всіх вершин графу
        nodes = nx.draw_networkx_nodes(
            self.graph, self.pos, 
            node_size=node_size, 
            node_color=node_color,
            edgecolors="black",
            linewidths=1.0,
            ax=ax
        )
        
        # Додаємо ефект тіні до вузлів
        if hasattr(nodes, 'set_edgecolor'):
            nodes.set_edgecolor('gray')
        
        # Відображення назв міст з більшим шрифтом
        nx.draw_networkx_labels(
            self.graph, self.pos, 
            font_size=9, 
            font_family="sans-serif", 
            font_weight="bold",
            ax=ax
        )
        
        # Налаштування графіку
        plt.title("Схема автомобільних маршрутів України", fontsize=16, fontweight="bold")
        plt.axis('off')  # Вимкнення відображення осей
        plt.tight_layout()  # Автоматичне налаштування відступів
        
        # Зберігаємо об'єкт осі для подальшого використання
        self.ax = ax
        self.fig = fig
        
        # Відображення графу на полотні
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        
        # Додаємо стандартну панель навігації (для масштабування, пересування та ін.)
        toolbar = NavigationToolbar2Tk(canvas, self.graph_frame)
        toolbar.update()
        
        # З'єднуємо обробник подій для додавання міст
        canvas.mpl_connect('button_press_event', self.on_click)
        
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def find_shortest_path(self):
        start_city = self.start_city_var.get()
        end_city = self.end_city_var.get()
        
        # Перевірка вхідних даних
        if start_city == end_city:
            messagebox.showwarning("Попередження", "Початкове і кінцеве місто повинні бути різними!")
            return
        
        if start_city not in self.graph.nodes or end_city not in self.graph.nodes:
            messagebox.showerror("Помилка", "Вказане місто відсутнє в графі!")
            return
        
        # Реалізація алгоритму Дейкстри з візуалізацією
        self.dijkstra_visualize(start_city, end_city)
        
    def dijkstra_visualize(self, start, end):
        # Ініціалізація
        distances = {node: float('infinity') for node in self.graph.nodes}
        distances[start] = 0
        previous = {node: None for node in self.graph.nodes}
        priority_queue = [(0, start)]
        visited = set()
        
        # Відображення початкового стану перед пошуком
        self.draw_graph()
        self.update_result(f"Початок пошуку: {start} -> {end}")
        self.root.update()
        time.sleep(0.5)
        
        # Основний цикл алгоритму Дейкстри
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # Якщо вже відвідано або знайдено коротший шлях
            if current_node in visited or current_distance > distances[current_node]:
                continue
                
            # Додаємо поточну вершину до відвіданих
            visited.add(current_node)
            
            # Якщо знайдено кінцеву вершину, закінчуємо пошук
            if current_node == end:
                break
                
            # Перебираємо всіх сусідів поточної вершини
            for neighbor, edge_data in self.graph[current_node].items():
                weight = edge_data['weight']
                
                # Якщо знайдено коротший шлях до сусіда
                if distances[current_node] + weight < distances[neighbor]:
                    distances[neighbor] = distances[current_node] + weight
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (distances[neighbor], neighbor))
            
            # Формуємо поточний шлях для візуалізації
            current_path = []
            if current_node != start:
                temp = current_node
                while temp:
                    current_path.insert(0, temp)
                    temp = previous[temp]
                current_path.insert(0, start)
                
                # Відображаємо поточний стан пошуку
                self.draw_graph(current_path)
                self.update_result(f"Обробка вершини: {current_node}\nВідстань від {start}: {distances[current_node]} км")
                self.root.update()
                time.sleep(0.3)
        
        # Відновлюємо шлях від кінця до початку
        path = []
        if distances[end] != float('infinity'):
            current = end
            while current:
                path.insert(0, current)
                current = previous[current]
                
            # Обчислюємо загальну відстань
            total_distance = distances[end]
            
            # Зберігаємо результат
            self.current_path = path
            self.current_distance = total_distance
            
            # Оновлюємо візуалізацію та результат
            self.draw_graph(path)
            self.show_result(path, total_distance)
        else:
            messagebox.showinfo("Результат", f"Шлях від {start} до {end} не знайдено!")
            self.draw_graph()
    
    def show_result(self, path, distance):
        result_text = f"Найкоротший шлях від {path[0]} до {path[-1]}:\n"
        result_text += " -> ".join(path)
        result_text += f"\n\nЗагальна відстань: {distance} км"
        
        self.update_result(result_text)
    
    def update_result(self, text):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)
    
    def add_city(self):
        """Активує режим додавання міста по кліку."""
        self.toggle_add_city_mode()

    def toggle_add_city_mode(self):
        """Перемикає режим додавання міста."""
        # Ініціалізуємо атрибут, якщо він ще не існує
        if not hasattr(self, 'add_city_mode'):
            self.add_city_mode = False
            # Додаємо статусний рядок
            self.status_var = tk.StringVar()
            self.status_var.set("Готовий")
            self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Перемикаємо режим
        self.add_city_mode = not self.add_city_mode
        
        if self.add_city_mode:
            self.status_var.set("Режим додавання міста: клікніть на карті України для додавання нового міста...")
        else:
            self.status_var.set("Готовий")
    
    def on_click(self, event):
        """Обробка кліку для додавання нового міста"""
        # Перевіряємо, що клік був на графіку
        if not event.inaxes or self.fig.canvas.toolbar.mode != "":
            return
        
        # Перевіряємо, чи активна кнопка додавання міста
        if not hasattr(self, 'add_city_mode') or not self.add_city_mode:
            return
                
        # Отримуємо координати кліку
        x, y = event.xdata, event.ydata
        
        # Перевіряємо, чи клік був в межах України
        if self.is_point_in_ukraine(x, y):
            # Запитуємо ім'я нового міста
            new_city = simpledialog.askstring("Додати місто", f"Введіть назву нового міста для точки ({x:.2f}, {y:.2f}):")
            if not new_city:
                return
                    
            if new_city in self.graph.nodes:
                messagebox.showwarning("Попередження", f"Місто {new_city} вже існує в графі!")
                return
                    
            # Додаємо місто до графу з позицією кліку
            self.graph.add_node(new_city)
            self.pos[new_city] = (x, y)
            
            # Оновлюємо список міст
            self.cities.append(new_city)
            self.start_city_combo['values'] = sorted(self.cities)
            self.end_city_combo['values'] = sorted(self.cities)
            
            # Вимикаємо режим додавання міста
            self.toggle_add_city_mode()
            
            # Запитуємо про додавання сусідів
            self.ask_for_neighbors(new_city)
            
            messagebox.showinfo("Інформація", f"Місто {new_city} успішно додано в точці ({x:.2f}, {y:.2f}).")
            self.draw_graph()
        else:
            messagebox.showwarning("Попередження", "Клік має бути в межах території України!")

    def is_point_in_ukraine(self, x, y):
        """Перевіряє, чи знаходиться точка в межах України."""
        # Базова перевірка по межах зображення
        if (x < self.ukraine_extent[0] or x > self.ukraine_extent[1] or
            y < self.ukraine_extent[2] or y > self.ukraine_extent[3]):
            return False
            
        # Якщо є маска зображення, перевіряємо по ній
        if self.ukraine_mask is not None:
            # Конвертуємо координати графіка в координати пікселя маски
            height, width = self.ukraine_mask.shape[:2]
            x_pixel = int((x - self.ukraine_extent[0]) / (self.ukraine_extent[1] - self.ukraine_extent[0]) * width)
            # Інвертуємо y координату (в зображенні y=0 це верх)
            y_pixel = int((1 - (y - self.ukraine_extent[2]) / (self.ukraine_extent[3] - self.ukraine_extent[2])) * height)
            
            # Перевіряємо, чи знаходяться координати в межах розмірів зображення
            if 0 <= x_pixel < width and 0 <= y_pixel < height:
                return self.ukraine_mask[y_pixel, x_pixel]
        
        # За замовчуванням, якщо немає маски
        return True
    def ask_for_neighbors(self, city_name):
        """Запитує у користувача про сусідні міста та відстані до них."""
        add_neighbors = messagebox.askyesno("Додати сусідів", f"Бажаєте додати сусідні міста для {city_name}?")
        
        if not add_neighbors:
            return
        
        # Створюємо вікно для додавання сусідів
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Сусіди міста {city_name}")
        dialog.geometry("500x650")  # Збільшена висота для кращого відображення елементів
        dialog.resizable(True, True)  # Дозволяємо змінювати розмір вікна
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Верхній фрейм для інструкцій
        instruction_frame = ttk.Frame(dialog, padding="10")
        instruction_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(instruction_frame, text=f"Додайте сусідні міста для {city_name}:", 
                 font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Фрейм для вибору і додавання міст
        input_frame = ttk.LabelFrame(dialog, text="Додати нового сусіда", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Компоненти для додавання сусіда
        ttk.Label(input_frame, text="Виберіть місто:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        neighbor_var = tk.StringVar()
        
        # Відфільтруємо список міст (без поточного міста)
        available_cities = [city for city in self.cities if city != city_name]
        neighbor_combo = ttk.Combobox(input_frame, textvariable=neighbor_var, values=sorted(available_cities))
        neighbor_combo.grid(row=0, column=1, padx=5, pady=5, sticky="we")
        
        ttk.Label(input_frame, text="Відстань (км):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        distance_var = tk.StringVar()
        distance_entry = ttk.Entry(input_frame, textvariable=distance_var)
        distance_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        
        # Налаштування ваг стовпців
        input_frame.columnconfigure(1, weight=1)
        
        # Список для зберігання вибраних сусідів та відстаней
        neighbors_data = []
        
        # Фрейм для списку доданих сусідів
        list_frame = ttk.LabelFrame(dialog, text="Додані сусіди", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Створення таблиці для відображення доданих сусідів
        columns = ('city', 'distance')
        neighbors_table = ttk.Treeview(list_frame, columns=columns, show='headings')
        neighbors_table.heading('city', text='Місто')
        neighbors_table.heading('distance', text='Відстань (км)')
        neighbors_table.column('city', width=200)
        neighbors_table.column('distance', width=100)
        
        # Додаємо скролбари
        xscrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=neighbors_table.xview)
        yscrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=neighbors_table.yview)
        neighbors_table.configure(xscroll=xscrollbar.set, yscroll=yscrollbar.set)
        
        # Розміщуємо скролбари і таблицю
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        neighbors_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        def add_neighbor():
            neighbor = neighbor_var.get()
            
            try:
                distance = int(distance_var.get())
                if distance <= 0:
                    raise ValueError("Відстань повинна бути додатним числом")
            except ValueError as e:
                messagebox.showerror("Помилка", f"Некоректна відстань: {e}")
                return
            
            if not neighbor or neighbor == city_name:
                messagebox.showwarning("Попередження", "Виберіть коректне сусіднє місто!")
                return
                
            if neighbor not in self.graph.nodes:
                messagebox.showerror("Помилка", f"Місто {neighbor} не існує в графі!")
                return
            
            # Перевіряємо, чи такий сусід вже доданий
            for item in neighbors_table.get_children():
                values = neighbors_table.item(item)['values']
                if values[0] == neighbor:
                    messagebox.showwarning("Попередження", f"Місто {neighbor} вже додано як сусіда!")
                    return
            
            # Додаємо до таблиці
            neighbors_table.insert('', 'end', values=(neighbor, distance))
            
            # Додаємо до списку
            neighbors_data.append((neighbor, distance))
            
            # Очищаємо поля введення
            neighbor_var.set('')
            distance_var.set('')
        
        def remove_neighbor():
            selected_item = neighbors_table.selection()
            if not selected_item:
                messagebox.showwarning("Попередження", "Виберіть сусіда для видалення!")
                return
                
            # Отримуємо дані вибраного елемента
            item = neighbors_table.item(selected_item[0])
            values = item['values']
            neighbor = values[0]
            
            # Видаляємо з таблиці
            neighbors_table.delete(selected_item)
            
            # Видаляємо зі списку
            for i, (city, distance) in enumerate(neighbors_data):
                if city == neighbor:
                    neighbors_data.pop(i)
                    break
        
        def save_neighbors():
            for neighbor, distance in neighbors_data:
                # Додаємо маршрут в обох напрямках
                self.graph.add_edge(city_name, neighbor, weight=distance)
                self.graph.add_edge(neighbor, city_name, weight=distance)
                
                # Додаємо до списку маршрутів
                self.routes.append((city_name, neighbor, distance))
                self.routes.append((neighbor, city_name, distance))  # Додаємо зворотній маршрут
            
            dialog.destroy()
            self.draw_graph()  # Перемальовуємо граф з новими сусідами
        
        # Кнопки у вхідному фреймі
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Додати сусіда", command=add_neighbor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Видалити вибраний", command=remove_neighbor).pack(side=tk.LEFT, padx=5)
        
        # Фрейм з кнопкою завершення
        bottom_frame = ttk.Frame(dialog, padding="10")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Кнопка завершення
        ttk.Button(bottom_frame, text="Зберегти всіх сусідів і закрити", 
                  command=save_neighbors, style="Accent.TButton").pack(fill=tk.X, pady=5)
        
        # Створюємо стиль для кнопки завершення
        style = ttk.Style()
        if "Accent.TButton" not in style.theme_names():  # Перевіряємо, чи існує такий стиль
            style.configure("Accent.TButton", font=("Arial", 11, "bold"))
        
        # Фокус на випадаючий список
        neighbor_combo.focus_set()
        
        # Встановлюємо мінімальний розмір вікна
        dialog.update_idletasks()  # Оновлюємо інформацію про геометрію вікна
        dialog.minsize(dialog.winfo_width(), dialog.winfo_height())
        
        # Розміщуємо вікно по центру батьківського вікна
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2,
            self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        ))
        
    def remove_route(self):
        # Створюємо діалогове вікно для видалення маршруту
        dialog = tk.Toplevel(self.root)
        dialog.title("Видалити маршрут")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Компоненти діалогового вікна
        ttk.Label(dialog, text="Початкове місто:").pack(pady=(10, 5))
        start_var = tk.StringVar()
        start_combo = ttk.Combobox(dialog, textvariable=start_var, values=sorted(self.cities))
        start_combo.pack(padx=10, pady=5, fill=tk.X)
        
        ttk.Label(dialog, text="Кінцеве місто:").pack(pady=(10, 5))
        end_var = tk.StringVar()
        end_combo = ttk.Combobox(dialog, textvariable=end_var, values=sorted(self.cities))
        end_combo.pack(padx=10, pady=5, fill=tk.X)
        
        def remove_route_confirm():
            start = start_var.get()
            end = end_var.get()
            
            if start not in self.graph.nodes or end not in self.graph.nodes:
                messagebox.showerror("Помилка", "Вказане місто відсутнє в графі!")
                return
                
            if not self.graph.has_edge(start, end):
                messagebox.showwarning("Попередження", f"Маршрут {start} - {end} не існує!")
                return
                
            # Видаляємо маршрут з графу в обох напрямках
            self.graph.remove_edge(start, end)
            self.graph.remove_edge(end, start)
            
            # Видаляємо з списку маршрутів (потрібно шукати в обох напрямках)
            for i, route in enumerate(self.routes):
                if (route[0] == start and route[1] == end) or (route[0] == end and route[1] == start):
                    self.routes.pop(i)
                    break
            
            messagebox.showinfo("Інформація", f"Маршрут {start} - {end} успішно видалено.")
            dialog.destroy()
            self.draw_graph()
        
        ttk.Button(dialog, text="Видалити", command=remove_route_confirm).pack(pady=15)
    

    def add_route(self):
            # Створюємо діалогове вікно для додавання маршруту
            dialog = tk.Toplevel(self.root)
            dialog.title("Додати маршрут")
            dialog.geometry("300x300")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Компоненти діалогового вікна
            ttk.Label(dialog, text="Початкове місто:").pack(pady=(10, 5))
            start_var = tk.StringVar()
            start_combo = ttk.Combobox(dialog, textvariable=start_var, values=sorted(self.cities))
            start_combo.pack(padx=10, pady=5, fill=tk.X)
            
            ttk.Label(dialog, text="Кінцеве місто:").pack(pady=(10, 5))
            end_var = tk.StringVar()
            end_combo = ttk.Combobox(dialog, textvariable=end_var, values=sorted(self.cities))
            end_combo.pack(padx=10, pady=5, fill=tk.X)
            
            ttk.Label(dialog, text="Відстань (км):").pack(pady=(10, 5))
            distance_var = tk.StringVar()
            distance_entry = ttk.Entry(dialog, textvariable=distance_var)
            distance_entry.pack(padx=10, pady=5, fill=tk.X)
            
            def add_route_confirm():
                start = start_var.get()
                end = end_var.get()
                
                try:
                    distance = int(distance_var.get())
                    if distance <= 0:
                        raise ValueError("Відстань повинна бути додатним числом")
                except ValueError as e:
                    messagebox.showerror("Помилка", f"Некоректна відстань: {e}")
                    return
                
                if start == end:
                    messagebox.showwarning("Попередження", "Початкове і кінцеве місто повинні бути різними!")
                    return
                    
                if start not in self.graph.nodes or end not in self.graph.nodes:
                    messagebox.showerror("Помилка", "Вказане місто відсутнє в графі!")
                    return
                    
                # Додаємо маршрут до графу в обох напрямках
                self.graph.add_edge(start, end, weight=distance)
                self.graph.add_edge(end, start, weight=distance)
                
                # Додаємо до списку маршрутів
                self.routes.append((start, end, distance))
                
                messagebox.showinfo("Інформація", f"Маршрут {start} - {end} ({distance} км) успішно додано.")
                dialog.destroy()
                self.draw_graph()
            
            ttk.Button(dialog, text="Додати", command=add_route_confirm).pack(pady=15)
    def remove_city(self):
        """Видаляє вибране місто з графу."""
        # Запитуємо користувача, яке місто видалити
        city_to_remove = simpledialog.askstring("Видалити місто", "Введіть назву міста для видалення:")
        
        if not city_to_remove:
            return
            
        if city_to_remove not in self.graph.nodes:
            messagebox.showwarning("Попередження", f"Міста {city_to_remove} немає в графі!")
            return
            
        # Видаляємо місто з графу
        self.graph.remove_node(city_to_remove)
        
        # Видаляємо місто зі списку
        if city_to_remove in self.cities:
            self.cities.remove(city_to_remove)
        
        # Видаляємо місто з координат
        if hasattr(self, 'pos') and city_to_remove in self.pos:
            del self.pos[city_to_remove]
        
        # Видаляємо пов'язані маршрути
        self.routes = [(start, end, weight) for start, end, weight in self.routes 
                    if start != city_to_remove and end != city_to_remove]
        
        # Оновлюємо випадаючі списки
        self.start_city_combo['values'] = sorted(self.cities)
        self.end_city_combo['values'] = sorted(self.cities)
        
        # Якщо видалене місто було вибране як початкове або кінцеве, змінюємо значення
        if self.start_city_var.get() == city_to_remove:
            self.start_city_var.set(self.cities[0] if self.cities else "")
        if self.end_city_var.get() == city_to_remove:
            self.end_city_var.set(self.cities[0] if self.cities else "")
        
        # Повідомляємо про успішне видалення
        messagebox.showinfo("Інформація", f"Місто {city_to_remove} було успішно видалено з графу.")
        
        # Перемальовуємо граф
        self.draw_graph()
    def reset_graph(self):
        if messagebox.askyesno("Підтвердження", "Ви впевнені, що хочете скинути всі зміни графу?"):
            # Створюємо граф заново
            self.graph = nx.DiGraph()
            
            # Відновлюємо початковий список міст
            self.cities = [
                "Вінниця", "Дніпро", "Донецьк", "Житомир", "Запоріжжя", "Івано-Франківськ", 
                "Київ", "Кропивницький", "Луганськ", "Луцьк", "Львів", "Маріуполь", 
                "Мелітополь", "Миколаїв", "Одеса", "Полтава", "Рівне", "Севастополь", 
                "Сімферополь", "Суми", "Тернопіль", "Ужгород", "Харків", "Херсон", 
                "Хмельницький", "Черкаси", "Чернівці", "Чернігів", "Кривий Ріг"
            ]
            
            # Додаємо міста до графу
            for city in self.cities:
                self.graph.add_node(city)
            
            # Відновлюємо початковий список маршрутів
            self.routes = [
                ("Вінниця", "Житомир", 127),
                ("Вінниця", "Київ", 267),
                ("Вінниця", "Кропивницький", 320),
                ("Вінниця", "Миколаїв", 428),
                ("Вінниця", "Одеса", 423),
                ("Вінниця", "Черкаси", 341),
                ("Вінниця", "Чернівці", 276),
                ("Дніпро", "Донецьк", 248),
                ("Дніпро", "Запоріжжя", 85),
                ("Дніпро", "Кропивницький", 244),
                ("Дніпро", "Кривий Ріг", 146),
                ("Дніпро", "Полтава", 160),
                ("Дніпро", "Харків", 218),
                ("Донецьк", "Луганськ", 156),
                ("Донецьк", "Маріуполь", 113),
                ("Донецьк", "Харків", 294),
                ("Запоріжжя", "Мелітополь", 125),
                ("Івано-Франківськ", "Тернопіль", 133),
                ("Івано-Франківськ", "Ужгород", 293),
                ("Київ", "Житомир", 140),
                ("Київ", "Полтава", 340),
                ("Київ", "Суми", 333),
                ("Київ", "Черкаси", 189),
                ("Київ", "Чернігів", 148),
                ("Кропивницький", "Полтава", 246),
                ("Луганськ", "Харків", 325),
                ("Львів", "Івано-Франківськ", 134),
                ("Львів", "Луцьк", 151),
                ("Львів", "Рівне", 211),
                ("Львів", "Тернопіль", 127),
                ("Львів", "Ужгород", 268),
                ("Львів", "Чернівці", 268),
                ("Мелітополь", "Маріуполь", 192),
                ("Мелітополь", "Сімферополь", 250),
                ("Миколаїв", "Херсон", 69),
                ("Рівне", "Житомир", 188),
                ("Рівне", "Луцьк", 73),
                ("Рівне", "Тернопіль", 155),
                ("Харків", "Полтава", 143),
                ("Херсон", "Мелітополь", 231),
                ("Хмельницький", "Вінниця", 119),
                ("Хмельницький", "Житомир", 183),
                ("Хмельницький", "Рівне", 194),
                ("Хмельницький", "Тернопіль", 112),
                ("Хмельницький", "Чернівці", 187),
                ("Суми", "Харків", 184),
                ("Черкаси", "Полтава", 233),
                ("Полтава", "Суми", 175),
                ("Чернігів", "Суми", 306),
                ("Сімферополь", "Севастополь", 81),
            ]
            
            # Додаємо маршрути до графу в обох напрямках
            for start, end, distance in self.routes:
                self.graph.add_edge(start, end, weight=distance)
                self.graph.add_edge(end, start, weight=distance)
            
            # Відновлюємо початкові координати міст
            self.pos = {
                "Київ": (0.1, 0.3),
                "Львів": (-0.75, 0.15),
                "Луцьк": (-0.7, 0.45),
                "Рівне": (-0.5, 0.4),
                "Тернопіль": (-0.5, 0.1),
                "Івано-Франківськ": (-0.7, -0.1),
                "Ужгород": (-0.9, -0.2),
                "Чернівці": (-0.55, -0.2),
                "Житомир": (-0.2, 0.35),
                "Хмельницький": (-0.3, 0.1),
                "Вінниця": (-0.2, -0.1),
                "Одеса": (0, -0.6),
                "Миколаїв": (0.1, -0.5),
                "Херсон": (0.25, -0.6),
                "Сімферополь": (0.5, -0.9),
                "Севастополь": (0.4, -1.0),
                "Черкаси": (0.2, 0.0),
                "Кропивницький": (0.2, -0.3),
                "Чернігів": (0.2, 0.6),
                "Суми": (0.5, 0.5),
                "Полтава": (0.4, 0.2),
                "Харків": (0.7, 0.2),
                "Дніпро": (0.5, -0.2),
                "Запоріжжя": (0.5, -0.4),
                "Кривий Ріг": (0.3, -0.4),
                "Мелітополь": (0.6, -0.55),
                "Донецьк": (0.9, -0.3),
                "Луганськ": (1, 0),
                "Маріуполь": (0.8, -0.5)
            }
            
            # Оновлюємо значення комбобоксів
            self.start_city_combo['values'] = sorted(self.cities)
            self.end_city_combo['values'] = sorted(self.cities)
            
            # Скидаємо режим додавання міста, якщо він активний
            if hasattr(self, 'add_city_mode') and self.add_city_mode:
                self.toggle_add_city_mode()
            
            # Скидаємо результати
            self.current_path = None
            self.current_distance = None
            self.update_result("")
            
            messagebox.showinfo("Інформація", "Граф успішно скинуто до початкового стану.")
            self.draw_graph()
# Запуск додатку
if __name__ == "__main__":
    root = tk.Tk()
    app = DijkstraApp(root)
    root.mainloop()