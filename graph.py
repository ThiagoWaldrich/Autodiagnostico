import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import chardet
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import csv
from collections import defaultdict
import numpy as np
import customtkinter as ctk
from matplotlib.ticker import MultipleLocator

class ENEMAnalyzer:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.initialize_data()
        self.create_widgets()
        
    def setup_window(self):
        self.root.title("Analisador ENEM")
        self.root.geometry("600x350")
        ctk.set_appearance_mode("white") 
        ctk.set_default_color_theme("dark-blue")  
        
    def initialize_data(self):
        self.questions = []
        self.subjects = ["Física", "Matemática", "Biologia", "Química", 
                        "História", "Geografia", "Filosofia", "Sociologia", "Artes", "Literatura"]
        self.load_data()
        
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
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.register_tab = self.notebook.add("Cadastrar")
        self.charts_tab = self.notebook.add("Gráficos")
        self.subtopics_tab = self.notebook.add("Subtópicos") 
        self.data_tab = self.notebook.add("Planilha")
        
        self.create_register_tab()
        self.create_charts_tab()
        self.create_subtopics_tab()  
        self.create_data_tab()
        
    def create_register_tab(self):
        frame = self.notebook.tab("Cadastrar")

        ctk.CTkLabel(frame, text="Matéria:").grid(row=0, column=0, padx=2, pady=2, sticky='w')
        self.subject = ctk.CTkComboBox(
            frame, 
            values=self.subjects,
            width=200, 
            dropdown_font=("Arial", 12),  
            button_color="#2CC985", 
            dropdown_hover_color="lightblue",
            corner_radius=8 
        )
        self.subject.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ctk.CTkLabel(frame, text="Tópico:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.topic = ctk.CTkEntry(frame)
        self.topic.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        ctk.CTkLabel(frame, text="Subtópico:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.subtopic = ctk.CTkEntry(frame)
        self.subtopic.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        
        ctk.CTkLabel(frame, text="Descrição:").grid(row=3, column=0, padx=5, pady=5, sticky='nw')
        self.description = ctk.CTkTextbox(frame, height=100)
        self.description.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ctk.CTkLabel(frame, text="Errou por falta de:").grid(row=4, column=0, padx=5, pady=5, sticky='nw')

        self.var_conteudo = tk.BooleanVar()
        self.var_atencao = tk.BooleanVar()
        self.var_tempo = tk.BooleanVar()

        checkbox_frame = ctk.CTkFrame(frame)
        checkbox_frame.grid(row=4, column=1, sticky='w')

        ctk.CTkCheckBox(checkbox_frame, text="Conteúdo", variable=self.var_conteudo).pack(side='left', padx=5)
        ctk.CTkCheckBox(checkbox_frame, text="Atenção", variable=self.var_atencao).pack(side='left', padx=5)
        ctk.CTkCheckBox(checkbox_frame, text="Tempo", variable=self.var_tempo).pack(side='left', padx=5)
        
        ctk.CTkButton(frame, text="Adicionar", command=self.save_question).grid(row=4, column=1, pady=10, sticky='e')
        
        frame.columnconfigure(1, weight=1)
    
    def create_charts_tab(self):
        frame = self.notebook.tab("Gráficos")
        
        pie_container = ctk.CTkFrame(frame)
        pie_container.pack(fill=tk.BOTH, expand=True, padx=5)
        
        pie_frame = ctk.CTkFrame(pie_container)
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.fig_pie = plt.Figure(figsize=(5,3))
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, pie_frame)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        table_frame = ctk.CTkFrame(pie_container)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        
        self.count_table = ttk.Treeview(table_frame, columns=("Matéria", "Quantidade"), show="headings", height=5)
        self.count_table.heading("Matéria", text="Matéria")
        self.count_table.heading("Quantidade", text="Quantidade")
        self.count_table.column("Matéria", width=120)
        self.count_table.column("Quantidade", width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.count_table.yview)
        self.count_table.configure(yscrollcommand=scrollbar.set)
        
        self.count_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        
        bar_frame = ctk.CTkFrame(frame)
        bar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(22,5))
        
        self.fig_bar = plt.Figure()
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, bar_frame)
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_charts()
    
    def create_subtopics_tab(self):
        frame = self.notebook.tab("Subtópicos")
        self.subtopics_frame = ctk.CTkFrame(frame)
        self.subtopics_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        self.fig_subtopics = plt.Figure(figsize=(10, 6))
        self.canvas_subtopics = FigureCanvasTkAgg(self.fig_subtopics, self.subtopics_frame)
        self.canvas_subtopics.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_subtopics_charts()
    
    def create_data_tab(self):
        frame = self.notebook.tab("Planilha")
        
        self.tree = ttk.Treeview(frame, columns=("Matéria", "Tópico", "Subtópico", "Descrição", "Erro"), show="headings")
        self.tree.heading("Matéria", text="Matéria")
        self.tree.heading("Tópico", text="Tópico")
        self.tree.heading("Subtópico", text="Subtópico")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Erro", text="Erro")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ctk.CTkButton(btn_frame, text="Importar CSV", command=self.import_csv).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Exportar CSV", command=self.export_csv).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Excluir", command=self.delete_selected).grid(row=0, column=2, padx=5)

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        
        self.update_data_view()
    
    def save_question(self):
        if not self.subject.get() or not self.topic.get():
            messagebox.showerror("Erro", "Preencha pelo menos Matéria e Tópico!")
            return
            
        self.questions.append({
            "subject": self.subject.get(),
            "topic": self.topic.get(),
            "subtopic": self.subtopic.get(),
            "description": self.description.get("1.0", tk.END).strip(),
            "erros": {
                "conteudo": self.var_conteudo.get(),
                "atencao": self.var_atencao.get(),
                "tempo": self.var_tempo.get()
            }
        })
        
        self.save_data()
        self.clear_form()
        self.update_charts()
        self.update_subtopics_charts()
        self.update_data_view()
        messagebox.showinfo("Sucesso", "Questão salva com sucesso!")
    
    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item_values = self.tree.item(selected_item, "values")

        self.tree.delete(selected_item)

        for q in self.questions:
            if (
                q["subject"] == item_values[0]
                and q["topic"] == item_values[1]
                and q["subtopic"] == item_values[2]
                and (q["description"][:50] + "..." if len(q["description"]) > 50 else q["description"]) == item_values[3]
            ):
                self.questions.remove(q)
                break
        self.save_data()
        self.update_charts()
        self.update_subtopics_charts()
        self.update_data_view()
    
    def clear_form(self):
        self.subject.set('')
        self.topic.delete(0, tk.END)
        self.subtopic.delete(0, tk.END)
        self.description.delete("1.0", tk.END)
        self.var_conteudo.set(False)
        self.var_atencao.set(False)
        self.var_tempo.set(False)
    
    def update_charts(self):
        self.fig_pie.clear()
        counts = defaultdict(int)
        for q in self.questions:
            counts[q["subject"]] += 1
        
        ax = self.fig_pie.add_subplot(111)
        if counts:
            ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', textprops={'fontsize':7})
            ax.set_position([0.1, 0.1, 0.8, 0.8])
            self.fig_pie.tight_layout(pad=0)
        self.canvas_pie.draw()
        
        for item in self.count_table.get_children():
            self.count_table.delete(item)
        
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for subject, count in sorted_counts:
            self.count_table.insert("", tk.END, values=(subject, count))
        
        for widget in self.canvas_bar.get_tk_widget().winfo_children():
            widget.destroy()
        self.canvas_bar.get_tk_widget().pack_forget()
        
        self.fig_bar.clear()
        subject_topics = defaultdict(lambda: defaultdict(int))
        for q in self.questions:
            subject = q['subject']
            topic = q['topic']
            subject_topics[subject][topic] += 1

        num_subjects = len(subject_topics)
        cols = min(3, num_subjects)  
        rows = (num_subjects + cols - 1) // cols  

        axes = self.fig_bar.subplots(rows, cols)
        self.fig_bar.set_size_inches(6.5*cols, 4*rows) 

        if num_subjects == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = np.array([axes])

        for i, (subject, topics) in enumerate(subject_topics.items()):
            row = i // cols
            col = i % cols
            ax = axes[row, col]
            ax.yaxis.set_major_locator(MultipleLocator(1))
    
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            topic_names = [t[0] for t in sorted_topics]
            topic_counts = [t[1] for t in sorted_topics]
    
            bars = ax.bar(topic_names, topic_counts, width=0.4, color='#4a6fa5')
    
            ax.set_title(f"{subject}")
            ax.grid(axis='y', linestyle='--', alpha=1)
            ax.set_xticklabels(topic_names, ha='right', rotation=20)
            
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
        self.fig_bar.subplots_adjust(top=0.95, hspace=0.61, wspace=0.3, bottom=0.05)
        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, self.canvas_bar.get_tk_widget().master)
        self.canvas_bar.draw()
        self.canvas_bar.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_subtopics_charts(self):
        self.fig_subtopics.clear()
        
        
        subject_subtopics = defaultdict(lambda: defaultdict(int))
        for q in self.questions:
            subject = q['subject']
            subtopic = q['subtopic'] or "Sem subtópico"  
            subject_subtopics[subject][subtopic] += 1
        
        if not subject_subtopics:
            ax = self.fig_subtopics.add_subplot(111)
            ax.text(0.5, 0.5, 'Nenhum dado disponível', 
                    ha='center', va='center', fontsize=7)
            self.canvas_subtopics.draw()
            return
        

        num_subjects = len(subject_subtopics)
        cols = min(2, num_subjects) 
        rows = (num_subjects + cols - 1) // cols
        
        axes = self.fig_subtopics.subplots(rows, cols)
        self.fig_subtopics.set_size_inches(8 * cols, 4 * rows)
        
        if num_subjects == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = np.array([axes])
        
        for i, (subject, subtopics) in enumerate(subject_subtopics.items()):
            row = i // cols
            col = i % cols
            ax = axes[row, col]
            

            sorted_subtopics = sorted(subtopics.items(), key=lambda x: x[1], reverse=True)
            subtopic_names = [t[0] for t in sorted_subtopics]
            subtopic_counts = [t[1] for t in sorted_subtopics]
            

            bars = ax.bar(subtopic_names, subtopic_counts, color='#4a6fa5')
            ax.set_title(f"Subtópicos de {subject}")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            

            plt.setp(ax.get_xticklabels(), rotation=25, ha='right')
            

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
        
        self.fig_subtopics.tight_layout()
        self.canvas_subtopics.draw()
        self.fig_subtopics.subplots_adjust(top=0.95, hspace=0, wspace=0.3, bottom=0.1)
    
    def update_data_view(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for q in self.questions:
            erros = q.get("erros", {})
            erro_str = ", ".join([
                tipo.capitalize()
                for tipo, marcado in erros.items()
                if marcado
            ]) if erros else ""

            self.tree.insert("", tk.END, values=(
                q["subject"],
                q["topic"],
                q["subtopic"],
                q["description"][:50] + "..." if len(q["description"]) > 50 else q["description"],
                erro_str
            ))
    
    def import_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            with open(filepath, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding']

            with open(filepath, 'r', newline='', encoding=encoding) as csvfile:
                try:
                    dialect = csv.Sniffer().sniff(csvfile.read(1024))
                    csvfile.seek(0)
                except:
                    dialect = csv.excel_tab
                    csvfile.seek(0)
            
                reader = csv.DictReader(csvfile, dialect=dialect)
                imported_count = 0
            
                for row in reader:
                    try:
                        if not any(row.values()):
                            continue
                        
                        subject = row.get('Matéria', '').strip()
                        topic = row.get('Tópico', '').strip()
                        subtopic = row.get('Subtópico', '').strip()
                        description = row.get('Descrição', '').strip()
                        erros_str = row.get('Erros', '').strip().lower()  
                    
                        if not subject or not topic:
                            print(f"Linha ignorada - faltam Matéria ou Tópico: {row}")
                            continue
                        
                        erros_dict = {
                            "conteudo": False,
                            "atencao": False,
                            "tempo": False
                        }
                    
                        if erros_str:
                            erros_dict = {
                                "conteudo": any(p in erros_str for p in ['conteudo', 'conteúdo', 'content']),
                                "atencao": any(p in erros_str for p in ['atencao', 'atenção', 'attention']),
                                "tempo": any(p in erros_str for p in ['tempo', 'time'])
                            }
                    
                        question = {
                            "subject": subject,
                            "topic": topic,
                            "subtopic": subtopic,
                            "description": description,
                            "erros": erros_dict
                        }
                    
                        self.questions.append(question)
                        imported_count += 1
                    
                    except Exception as e:
                        print(f"Erro ao processar linha: {row}\nErro: {str(e)}")
                        continue

                self.save_data()
                self.update_charts()
                self.update_subtopics_charts()
                self.update_data_view()
            
            if imported_count > 0:
                messagebox.showinfo("Sucesso", f"{imported_count} questões importadas com sucesso!")
            else:
                messagebox.showwarning("Aviso", "Nenhuma questão foi importada. Verifique o formato do arquivo.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na importação:\n{str(e)}")

    def export_csv(self):
        if not self.questions:
            messagebox.showwarning("Aviso", "Nenhum dado para exportar!")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Matéria', 'Tópico', 'Subtópico', 'Descrição', 'Erros']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for questao in self.questions:
                    erros_str = ', '.join([k for k, v in questao['erros'].items() if v])
                    writer.writerow({
                        'Matéria': questao['subject'],
                        'Tópico': questao['topic'],
                        'Subtópico': questao['subtopic'],
                        'Descrição': questao['description'],
                        'Erros': erros_str or 'Nenhum'
                    })
            
            messagebox.showinfo("Sucesso", "Dados exportados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na exportação:\n{str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ENEMAnalyzer(root)
    root.mainloop()