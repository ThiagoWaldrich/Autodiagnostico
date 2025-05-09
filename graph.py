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
        self.root.geometry("800x600") 
        ctk.set_appearance_mode("white") 
        ctk.set_default_color_theme("dark-blue")  
        
    def initialize_data(self):
        self.questions = []
        self.subjects = ["Física", "Matemática", "Biologia", "Química", 
                        "História", "Geografia", "Filosofia", "Sociologia", "Artes", "Literatura"]
        self.load_data()
        self.root.after(100, self.update_initial_views)
    
    def update_initial_views(self):
   
        self.update_charts()
        self.update_subtopics_charts()
        self.update_data_view()
        
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
        
        # Container superior 
        pie_container = ctk.CTkFrame(frame)
        pie_container.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Frame para o gráfico de pizza
        pie_frame = ctk.CTkFrame(pie_container)
        pie_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.fig_pie = plt.Figure(figsize=(5,3))
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, pie_frame)
        self.canvas_pie.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Frame para a tabela
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
        
        # Container com scroll para os gráficos de barras
        self.bar_scroll_frame = ctk.CTkScrollableFrame(frame, orientation="vertical")
        self.bar_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para os gráficos de barras dentro do scrollable frame
        self.bar_frame = ctk.CTkFrame(self.bar_scroll_frame)
        self.bar_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_subtopics_tab(self):
        frame = self.notebook.tab("Subtópicos")
        
        # Container com scroll para os gráficos de subtópicos
        self.subtopics_scroll_frame = ctk.CTkScrollableFrame(frame, orientation="vertical")
        self.subtopics_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        # Frame para os gráficos de subtópicos dentro do scrollable frame
        self.subtopics_frame = ctk.CTkFrame(self.subtopics_scroll_frame)
        self.subtopics_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
    
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
        # Atualiza o gráfico de pizza
        self.fig_pie.clear()
        counts = defaultdict(int)
        for q in self.questions:
            counts[q["subject"]] += 1
        
        ax = self.fig_pie.add_subplot(111)
        if counts:
            ax.pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', textprops={'fontsize':8})
            ax.set_position([0.1, 0.1, 0.8, 0.8])
            self.fig_pie.tight_layout(pad=0)
        self.canvas_pie.draw()
        
        # Atualiza a tabela de contagem
        for item in self.count_table.get_children():
            self.count_table.delete(item)
        
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        for subject, count in sorted_counts:
            self.count_table.insert("", tk.END, values=(subject, count))
        
        # Limpa o frame de gráficos de barras anterior
        for widget in self.bar_frame.winfo_children():
            widget.destroy()
        
        # Agrupa os dados por matéria e tópico
        subject_topics = defaultdict(lambda: defaultdict(int))
        for q in self.questions:
            subject = q['subject']
            topic = q['topic']
            subject_topics[subject][topic] += 1

        if not subject_topics:
            return
        
        # Para cada matéria, criar um gráfico separado
        for subject, topics in subject_topics.items():
            # Criar um frame separado para cada matéria
            subject_frame = ctk.CTkFrame(self.bar_frame)
            subject_frame.pack(fill=tk.X, expand=True, padx=10, pady=5, anchor="n")
            
            # Label para o título da matéria
            ctk.CTkLabel(subject_frame, text=f"Tópicos de {subject}", font=("Arial", 14, "bold")).pack(pady=(5, 10))
            
            # Criar o gráfico
            fig = plt.Figure(figsize=(7, max(4, len(topics) * 0.4)))
            ax = fig.add_subplot(111)
            
            # Ordenar os tópicos por contagem
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            topic_names = [t[0] for t in sorted_topics]
            topic_counts = [t[1] for t in sorted_topics]
            
            # Criar o gráfico de barras
            bars = ax.bar(topic_names, topic_counts, width=0.6, color='#4a6fa5')
            
            # Configurações do gráfico
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.set_xticklabels(topic_names, rotation=20, fontsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.set_ylim(0, max(topic_counts) * 1.2)  # Espaço extra para os valores acima das barras
            ax.yaxis.set_major_locator(MultipleLocator(1))
            
            # Adicionar valores em cima das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
            
            # Ajustar o layout
            fig.tight_layout()
            
            # Criar canvas para o gráfico
            canvas = FigureCanvasTkAgg(fig, subject_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_subtopics_charts(self):
        # Limpa o frame de gráficos de subtópicos
        for widget in self.subtopics_frame.winfo_children():
            widget.destroy()
        
        # Agrupa os dados por matéria e subtópico
        subject_subtopics = defaultdict(lambda: defaultdict(int))
        for q in self.questions:
            subject = q['subject']
            subtopic = q['subtopic'] or "Sem subtópico"
            subject_subtopics[subject][subtopic] += 1
        
        if not subject_subtopics:
            # Se não houver dados, exibe uma mensagem
            no_data_label = ctk.CTkLabel(self.subtopics_frame, text="Nenhum dado disponível")
            no_data_label.pack(expand=True, pady=45)
            return
        
        # Para cada matéria, criar um gráfico separado
        for subject, subtopics in subject_subtopics.items():
            # Criar um frame separado para cada matéria
            subject_frame = ctk.CTkFrame(self.subtopics_frame)
            subject_frame.pack(fill=tk.X, expand=True, padx=10, pady=5, anchor="n")
            
            # Label para o título da matéria
            ctk.CTkLabel(subject_frame, text=f"Subtópicos de {subject}", font=("Arial", 14, "bold")).pack(pady=(5, 10))
            
            # Criar o gráfico
            fig = plt.Figure(figsize=(7, max(4, len(subtopics) * 0.4)))
            ax = fig.add_subplot(111)
            
            # Ordenar os subtópicos por contagem
            sorted_subtopics = sorted(subtopics.items(), key=lambda x: x[1], reverse=True)
            subtopic_names = [t[0] for t in sorted_subtopics]
            subtopic_counts = [t[1] for t in sorted_subtopics]
            
            # Criar o gráfico de barras
            bars = ax.bar(subtopic_names, subtopic_counts, width=0.5, color='#4a6fa5')
            
            # Configurações do gráfico
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.set_xticklabels(subtopic_names, ha='right', rotation=45, fontsize=7)
            ax.tick_params(axis='y', labelsize=9)
            ax.set_ylim(0, max(subtopic_counts) * 1.2)  # Espaço extra para os valores acima das barras
            ax.yaxis.set_major_locator(MultipleLocator(1))
            
            # Adicionar valores em cima das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=9)
            
            # Ajustar o layout
            fig.tight_layout()
            
            # Criar canvas para o gráfico
            canvas = FigureCanvasTkAgg(fig, subject_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
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
                q["description"][:120] + "..." if len(q["description"]) >120 else q["description"],
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