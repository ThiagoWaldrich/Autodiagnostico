import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib import ticker
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv
from collections import defaultdict
import numpy as np

class ENEMAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador ENEM")
        self.root.geometry("1000x700")
        
        self.questions = []
        self.subjects = ["Física", "Matemática", "Biologia", "Química", 
                        "História", "Geografia", "Filosofia", "Sociologia"]
        
        self.load_data()
        self.create_widgets()
    
    def load_data(self):
        try:
            with open('enem_data.json', 'r') as f:
                self.questions = json.load(f)
        except:
            self.questions = []
    
    def save_data(self):
        with open('enem_data.json', 'w') as f:
            json.dump(self.questions, f, indent=2)
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.create_register_tab()
        self.create_charts_tab()
        self.create_data_tab()
    
    def create_register_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Cadastrar")
        
        # Formulário
        ttk.Label(frame, text="Matéria:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.subject = ttk.Combobox(frame, values=self.subjects, state="readonly")
        self.subject.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Tópico:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.topic = ttk.Entry(frame)
        self.topic.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Subtópico:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.subtopic = ttk.Entry(frame)
        self.subtopic.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(frame, text="Descrição:").grid(row=3, column=0, padx=5, pady=5, sticky='nw')
        self.description = tk.Text(frame, height=5, width=40)
        self.description.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Button(frame, text="Adicionar", command=self.save_question).grid(row=4, column=1, pady=10, sticky='e')
        
        frame.columnconfigure(1, weight=1)
    
    def create_charts_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Gráficos")
        
        # Gráfico de Pizza
        pie_frame = ttk.LabelFrame(frame, text="Distribuição por Matéria")
        pie_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fig_pie = plt.Figure(figsize=(6,2))
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, pie_frame)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Gráfico de Barras
        bar_frame = ttk.LabelFrame(frame, text="Tópicos por Matéria", labelanchor="n")
        bar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(20,5))
        
        
        self.fig_bar = plt.Figure(figsize=(25,10))
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, bar_frame)
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        
        self.update_charts()
    
    def create_data_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Planilha")
        
        # Treeview para exibir dados
        self.tree = ttk.Treeview(frame, columns=("Matéria", "Tópico", "Subtópico", "Descrição"), show="headings")
        self.tree.heading("Matéria", text="Matéria")
        self.tree.heading("Tópico", text="Tópico")
        self.tree.heading("Subtópico", text="Subtópico")
        self.tree.heading("Descrição", text="Descrição")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botão para importar CSV
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Importar CSV", command=self.import_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Atualizar", command=self.update_data_view).pack(side="right", padx=5)
        
        self.update_data_view()
    
    def save_question(self):
        if not self.subject.get() or not self.topic.get():
            messagebox.showerror("Erro", "Preencha pelo menos Matéria e Tópico!")
            return
            
        self.questions.append({
            "subject": self.subject.get(),
            "topic": self.topic.get(),
            "subtopic": self.subtopic.get(),
            "description": self.description.get("1.0", tk.END).strip()
        })
        
        self.save_data()
        self.clear_form()
        self.update_charts()
        self.update_data_view()
        messagebox.showinfo("Sucesso", "Questão salva com sucesso!")
    
    def clear_form(self):
        self.subject.set('')
        self.topic.delete(0, tk.END)
        self.subtopic.delete(0, tk.END)
        self.description.delete("1.0", tk.END)
    
    def update_charts(self):
        self.fig_pie.clear()
        counts = defaultdict(int)
        for q in self.questions:
            counts[q["subject"]] += 1
        
        ax = self.fig_pie.add_subplot(111)
        if counts:
            ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%')
        ax.set_title("Distribuição por Matéria")
        self.canvas_pie.draw()
        
        self.fig_bar.clear()
        subject_topics = defaultdict(lambda: defaultdict(int))
        for q in self.questions:
            subject = q['subject']
            topic = q['topic']
            subject_topics[subject][topic] += 1

        num_subjects = len(subject_topics)
        cols = min(3, num_subjects)  # Máximo de 3 colunas por linha
        rows = (num_subjects + cols - 1) // cols  # Calcula número de linhas necessário

        axes = self.fig_bar.subplots(rows, cols)
        self.fig_bar.set_size_inches(6*cols, 4*rows)  # Tamanho dinâmico

        if num_subjects == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = np.array([axes])

        for i, (subject, topics) in enumerate(subject_topics.items()):
            row = i // cols
            col = i % cols
            ax = axes[row, col]
    
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            topic_names = [t[0] for t in sorted_topics]
            topic_counts = [t[1] for t in sorted_topics]
    
            bars = ax.bar(topic_names, topic_counts, width=0.4, color='#4a6fa5')
    
            ax.set_title(f"{subject}")
            ax.set_ylabel("Quantidade")
            ax.grid(axis='y', linestyle='--', alpha=0.2)
            ax.set_xticklabels(topic_names, ha='right')
    
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height)}',
               ha='center', va='bottom')

        if num_subjects < rows * cols:
            for j in range(num_subjects, rows * cols):
                row = j // cols
                col = j % cols
            axes[row, col].axis('off')

        self.fig_bar.tight_layout()
        self.fig_bar.subplots_adjust(top=0.9, hspace=0.2, wspace=0.3)
        self.canvas_bar.draw()
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_bar.flush_events()
        self.canvas_bar.get_tk_widget().update_idletasks()

    
    def update_data_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for q in self.questions:
            self.tree.insert("", tk.END, values=(
                q["subject"],
                q["topic"],
                q["subtopic"],
                q["description"][:50] + "..." if len(q["description"]) > 50 else q["description"]
            ))
    
    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return
            
        try:
            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.questions.append({
                        "subject": row.get("Matéria", ""),
                        "topic": row.get("Tópico", ""),
                        "subtopic": row.get("Subtópico", ""),
                        "description": row.get("Descrição", "")
                    })
            
            self.save_data()
            self.update_charts()
            self.update_data_view()
            messagebox.showinfo("Sucesso", "Dados importados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar CSV:\n{str(e)}")
    
    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return
            
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Matéria", "Tópico", "Subtópico", "Descrição"])
                for q in self.questions:
                    writer.writerow([
                        q["subject"],
                        q["topic"],
                        q["subtopic"],
                        q["description"]
                    ])
            
            messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar CSV:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ENEMAnalyzer(root)
    root.mainloop()