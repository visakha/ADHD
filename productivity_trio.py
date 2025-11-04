"""
ADHD Productivity Trio - Main Application
A three-way team productivity system with AI agents
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import anthropic
import sqlite3
import json
import os
from datetime import datetime
from threading import Thread
from pathlib import Path
import sys

# Constants
APP_VERSION = "1.0.0"
APP_NAME = "ADHD Productivity Trio"
DB_NAME = "productivity_trio.db"
CONFIG_FILE = "config.json"

class ProductivityTrioApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1400x900")
        
        # Initialize database
        self.init_database()
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize Claude client
        self.client = None
        self.init_claude_client()
        
        # Current project
        self.current_project_id = None
        
        # Agent definitions
        self.agents = {
            "spark": {
                "name": "Spark ✨",
                "color": "#FF6B6B",
                "role": "Motivator",
                "system_prompt": """You are Spark, an ADHD-friendly motivational coach and emotional support agent.

Your personality:
- Warm, enthusiastic, but never overwhelming
- Deeply understands ADHD patterns and challenges
- Celebrates all wins, especially tiny ones
- Non-judgmental about abandonment or restarts
- Asks powerful "why" questions to capture meaning

Your core responsibilities:
1. Keep enthusiasm alive during projects
2. Break overwhelming ideas into dopamine-generating micro-tasks
3. Remind about the "why" behind projects (without guilt)
4. Notice abandonment patterns early and gently check in
5. Capture context and meaning before they vanish
6. Create emotional safety for experimentation

Communication style:
- Short, energizing messages (ADHD-friendly)
- Use emojis sparingly but meaningfully
- Acknowledge feelings before suggesting actions
- Frame challenges as adventures, not failures
- End with hope and possibility

Remember: You're not here to fix them. You're here to champion them."""
            },
            "proto": {
                "name": "Proto 🎯",
                "color": "#4ECDC4",
                "role": "Executor",
                "system_prompt": """You are Proto, a strategic executor and implementation specialist who understands ADHD.

Your personality:
- Pragmatic, clear, and action-oriented
- Patient with context switching and restarts
- Systematic but flexible
- Tracks progress without judgment
- Creates structure that supports, not constrains

Your core responsibilities:
1. Transform vague ideas into concrete, tiny actionable steps
2. Create perfect "resume points" for when context switches happen
3. Track what's been accomplished (celebrate progress)
4. Suggest THE SINGLE most important next action
5. Adapt plans when priorities or energy levels change
6. Notice when someone is stuck and suggest alternatives

Communication style:
- Ultra-clear, numbered steps
- One primary action at a time (avoid overwhelm)
- Include time estimates (be realistic)
- Provide "exit points" (places to pause guilt-free)
- Use "we" language (you're on the team)
- Always include "where we are" context

Remember: Done is better than perfect. Momentum beats perfection."""
            }
        }
        
        # Setup UI
        self.setup_ui()
        
        # Load or create initial project
        self.load_initial_state()
        
    def init_database(self):
        """Initialize SQLite database with schema"""
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        
        # Projects table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                initial_enthusiasm INTEGER DEFAULT 10,
                abandonment_count INTEGER DEFAULT 0
            )
        ''')
        
        # Conversations table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                agent TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_snapshot TEXT,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Tasks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                description TEXT NOT NULL,
                size TEXT DEFAULT 'tiny',
                completed BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                dopamine_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # Insights table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        self.conn.commit()
        
    def load_config(self):
        """Load or create configuration"""
        default_config = {
            "anthropic_api_key": "",
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 1024,
            "theme": "light"
        }
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**default_config, **json.load(f)}
        else:
            # Create default config
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def init_claude_client(self):
        """Initialize Claude API client"""
        api_key = self.config.get("anthropic_api_key", "")
        if api_key and api_key != "":
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                messagebox.showerror("API Error", f"Failed to initialize Claude client: {str(e)}")
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.create_new_project)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="All Projects", command=self.show_all_projects)
        view_menu.add_command(label="Insights", command=self.show_insights)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar - Project info and quick actions
        left_panel = ttk.Frame(main_container, width=300)
        main_container.add(left_panel, weight=1)
        
        # Project info section
        project_frame = ttk.LabelFrame(left_panel, text="Current Project", padding=10)
        project_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        self.project_title_label = ttk.Label(project_frame, text="No project selected", 
                                             font=("Arial", 12, "bold"), wraplength=250)
        self.project_title_label.pack(anchor=tk.W, pady=5)
        
        self.project_status_label = ttk.Label(project_frame, text="", foreground="gray")
        self.project_status_label.pack(anchor=tk.W)
        
        # Quick actions
        ttk.Button(project_frame, text="🎯 Quick Capture", 
                  command=self.quick_capture).pack(fill=tk.X, pady=2)
        ttk.Button(project_frame, text="❓ What Was I Doing?", 
                  command=self.context_recovery).pack(fill=tk.X, pady=2)
        ttk.Button(project_frame, text="🎉 Complete Task", 
                  command=self.complete_task).pack(fill=tk.X, pady=2)
        
        # Tasks section
        tasks_frame = ttk.LabelFrame(left_panel, text="Active Tasks", padding=10)
        tasks_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tasks_listbox = tk.Listbox(tasks_frame, height=10)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.tasks_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_listbox.config(yscrollcommand=scrollbar.set)
        
        # Center panel - Agent conversations
        center_panel = ttk.Frame(main_container)
        main_container.add(center_panel, weight=3)
        
        # Notebook for agents
        self.notebook = ttk.Notebook(center_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each agent
        self.agent_tabs = {}
        for agent_id, agent_info in self.agents.items():
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=agent_info["name"])
            
            # Chat display
            chat_display = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, 
                                                     state=tk.DISABLED, height=20)
            chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Configure tags for colored text
            chat_display.tag_config("user", foreground="#2E86AB", font=("Arial", 10, "bold"))
            chat_display.tag_config("agent", foreground=agent_info["color"], 
                                   font=("Arial", 10, "bold"))
            chat_display.tag_config("system", foreground="gray", font=("Arial", 9, "italic"))
            
            # Input frame
            input_frame = ttk.Frame(tab_frame)
            input_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Message input
            message_input = ttk.Entry(input_frame)
            message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            # Send button
            send_button = ttk.Button(input_frame, text="Send", 
                                    command=lambda aid=agent_id: self.send_message(aid))
            send_button.pack(side=tk.RIGHT)
            
            # Bind Enter key
            message_input.bind("<Return>", lambda e, aid=agent_id: self.send_message(aid))
            
            self.agent_tabs[agent_id] = {
                "frame": tab_frame,
                "display": chat_display,
                "input": message_input,
                "button": send_button
            }
        
        # Add a team discussion tab
        team_frame = ttk.Frame(self.notebook)
        self.notebook.add(team_frame, text="🤝 Team Discussion")
        
        team_display = scrolledtext.ScrolledText(team_frame, wrap=tk.WORD, 
                                                state=tk.DISABLED, height=20)
        team_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        team_display.tag_config("user", foreground="#2E86AB", font=("Arial", 10, "bold"))
        team_display.tag_config("spark", foreground="#FF6B6B", font=("Arial", 10, "bold"))
        team_display.tag_config("proto", foreground="#4ECDC4", font=("Arial", 10, "bold"))
        
        team_input_frame = ttk.Frame(team_frame)
        team_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        team_input = ttk.Entry(team_input_frame)
        team_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        team_button = ttk.Button(team_input_frame, text="Ask Team", 
                                command=self.ask_team)
        team_button.pack(side=tk.RIGHT)
        
        team_input.bind("<Return>", lambda e: self.ask_team())
        
        self.agent_tabs["team"] = {
            "frame": team_frame,
            "display": team_display,
            "input": team_input,
            "button": team_button
        }
        
        # Right panel - Stats and insights
        right_panel = ttk.Frame(main_container, width=250)
        main_container.add(right_panel, weight=1)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(right_panel, text="Team Stats", padding=10)
        stats_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Loading stats...", 
                                     justify=tk.LEFT, wraplength=220)
        self.stats_label.pack(anchor=tk.W)
        
        # Recent insights
        insights_frame = ttk.LabelFrame(right_panel, text="Recent Insights", padding=10)
        insights_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.insights_display = scrolledtext.ScrolledText(insights_frame, wrap=tk.WORD, 
                                                          height=15, state=tk.DISABLED)
        self.insights_display.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_new_project(self):
        """Create a new project"""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Project")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Project Title:", font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=10, anchor=tk.W)
        title_entry = ttk.Entry(dialog, width=60)
        title_entry.pack(padx=10, fill=tk.X)
        title_entry.focus()
        
        ttk.Label(dialog, text="Description (What excites you about this?):", 
                 font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=10, anchor=tk.W)
        desc_text = scrolledtext.ScrolledText(dialog, width=60, height=8)
        desc_text.pack(padx=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(dialog, text="Initial Enthusiasm (1-10):", 
                 font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=10, anchor=tk.W)
        enthusiasm_var = tk.IntVar(value=10)
        enthusiasm_scale = ttk.Scale(dialog, from_=1, to=10, orient=tk.HORIZONTAL, 
                                    variable=enthusiasm_var)
        enthusiasm_scale.pack(padx=10, fill=tk.X)
        
        enthusiasm_label = ttk.Label(dialog, text="10")
        enthusiasm_label.pack()
        
        def update_enthusiasm_label(*args):
            enthusiasm_label.config(text=str(int(enthusiasm_var.get())))
        
        enthusiasm_var.trace_add("write", update_enthusiasm_label)
        
        def save_project():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            enthusiasm = int(enthusiasm_var.get())
            
            if not title:
                messagebox.showwarning("Validation", "Please enter a project title.")
                return
            
            self.cursor.execute('''
                INSERT INTO projects (title, description, initial_enthusiasm)
                VALUES (?, ?, ?)
            ''', (title, description, enthusiasm))
            self.conn.commit()
            
            project_id = self.cursor.lastrowid
            self.current_project_id = project_id
            
            # Add initial conversation with both agents
            welcome_msg = f"New project started: {title}"
            self.save_conversation(project_id, "system", welcome_msg)
            
            # Send intro to Spark
            spark_intro = f"""A new project has started! 

Title: {title}
Description: {description}
Initial enthusiasm: {enthusiasm}/10

Say hello and help capture the excitement and 'why' behind this project!"""
            
            self.send_to_agent("spark", spark_intro, auto=True)
            
            # Send intro to Proto
            proto_intro = f"""New project initiated:

Title: {title}
Description: {description}

Help break this down into the first tiny actionable steps."""
            
            self.send_to_agent("proto", proto_intro, auto=True)
            
            self.load_project_info()
            self.update_stats()
            dialog.destroy()
            
            messagebox.showinfo("Success", f"Project '{title}' created! Your agents are ready to help.")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Create Project", command=save_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def send_message(self, agent_id):
        """Send message to specific agent"""
        if not self.current_project_id:
            messagebox.showwarning("No Project", "Please create or select a project first.")
            return
        
        if not self.client:
            messagebox.showerror("API Error", "Claude API client not initialized. Please check your API key in settings.")
            return
        
        message = self.agent_tabs[agent_id]["input"].get().strip()
        if not message:
            return
        
        # Clear input
        self.agent_tabs[agent_id]["input"].delete(0, tk.END)
        
        # Display user message
        self.display_message(agent_id, "You", message, "user")
        
        # Save to database
        self.save_conversation(self.current_project_id, "user", message)
        
        # Update last activity
        self.update_project_activity()
        
        # Send to Claude in background thread
        Thread(target=self.send_to_agent, args=(agent_id, message), daemon=True).start()
    
    def send_to_agent(self, agent_id, message, auto=False):
        """Send message to agent and get response"""
        try:
            # Get agent info
            agent = self.agents[agent_id]
            
            # Get conversation history for context
            history = self.get_conversation_history(self.current_project_id, agent_id, limit=10)
            
            # Build messages array
            messages = []
            for msg in history:
                role = "user" if msg[1] == "user" else "assistant"
                messages.append({"role": role, "content": msg[2]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Update status
            self.update_status(f"Asking {agent['name']}...")
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.config["model"],
                max_tokens=self.config["max_tokens"],
                system=agent["system_prompt"],
                messages=messages
            )
            
            # Extract response text
            response_text = response.content[0].text
            
            # Display agent response
            if not auto:
                self.display_message(agent_id, agent["name"], response_text, "agent")
            
            # Save to database
            self.save_conversation(self.current_project_id, agent_id, response_text)
            
            # Update status
            self.update_status("Ready")
            
        except Exception as e:
            error_msg = f"Error communicating with {agent['name']}: {str(e)}"
            messagebox.showerror("API Error", error_msg)
            self.update_status("Error - Check your API key")
    
    def ask_team(self):
        """Send message to both agents for team discussion"""
        if not self.current_project_id:
            messagebox.showwarning("No Project", "Please create or select a project first.")
            return
        
        if not self.client:
            messagebox.showerror("API Error", "Claude API client not initialized.")
            return
        
        message = self.agent_tabs["team"]["input"].get().strip()
        if not message:
            return
        
        # Clear input
        self.agent_tabs["team"]["input"].delete(0, tk.END)
        
        # Display user message in team chat
        self.display_message("team", "You", message, "user")
        
        # Save to database
        self.save_conversation(self.current_project_id, "user", f"[TEAM] {message}")
        
        # Ask both agents in sequence
        Thread(target=self.team_discussion, args=(message,), daemon=True).start()
    
    def team_discussion(self, message):
        """Facilitate team discussion between agents"""
        try:
            # Ask Spark first
            self.update_status("Asking Spark...")
            spark_response = self.get_agent_response("spark", 
                f"In a team discussion, the user asked: {message}\n\nProvide your perspective as the Motivator.")
            
            self.display_message("team", "Spark ✨", spark_response, "spark")
            self.save_conversation(self.current_project_id, "spark", f"[TEAM] {spark_response}")
            
            # Then ask Proto
            self.update_status("Asking Proto...")
            proto_response = self.get_agent_response("proto", 
                f"In a team discussion, the user asked: {message}\n\nSpark's perspective: {spark_response}\n\nProvide your perspective as the Executor.")
            
            self.display_message("team", "Proto 🎯", proto_response, "proto")
            self.save_conversation(self.current_project_id, "proto", f"[TEAM] {proto_response}")
            
            self.update_status("Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Team discussion error: {str(e)}")
            self.update_status("Error")
    
    def get_agent_response(self, agent_id, message):
        """Get response from agent (helper method)"""
        agent = self.agents[agent_id]
        
        response = self.client.messages.create(
            model=self.config["model"],
            max_tokens=self.config["max_tokens"],
            system=agent["system_prompt"],
            messages=[{"role": "user", "content": message}]
        )
        
        return response.content[0].text
    
    def display_message(self, agent_id, sender, message, tag):
        """Display message in chat window"""
        display = self.agent_tabs[agent_id]["display"]
        display.config(state=tk.NORMAL)
        
        timestamp = datetime.now().strftime("%H:%M")
        display.insert(tk.END, f"{sender} ({timestamp})\n", tag)
        display.insert(tk.END, f"{message}\n\n")
        
        display.see(tk.END)
        display.config(state=tk.DISABLED)
    
    def quick_capture(self):
        """Quick capture current state"""
        if not self.current_project_id:
            messagebox.showwarning("No Project", "Please create or select a project first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Quick Capture")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="What are you working on right now?", 
                 font=("Arial", 11, "bold")).pack(pady=10, padx=10, anchor=tk.W)
        
        capture_text = scrolledtext.ScrolledText(dialog, width=60, height=15)
        capture_text.pack(padx=10, fill=tk.BOTH, expand=True)
        capture_text.focus()
        
        def save_capture():
            content = capture_text.get("1.0", tk.END).strip()
            if content:
                # Save as insight
                self.cursor.execute('''
                    INSERT INTO insights (project_id, insight_type, content)
                    VALUES (?, ?, ?)
                ''', (self.current_project_id, "capture", content))
                self.conn.commit()
                
                # Send to Spark for processing
                self.send_to_agent("spark", f"Quick capture: {content}", auto=True)
                
                self.update_insights_display()
                messagebox.showinfo("Saved", "Your thoughts have been captured!")
                dialog.destroy()
        
        ttk.Button(dialog, text="Capture", command=save_capture).pack(pady=10)
    
    def context_recovery(self):
        """Help recover context when returning to project"""
        if not self.current_project_id:
            messagebox.showwarning("No Project", "Please create or select a project first.")
            return
        
        # Ask Proto for a summary
        self.send_to_agent("proto", 
            "I'm returning to this project. Can you give me a quick summary of where we are and what the single most important next action is?",
            auto=False)
        
        self.notebook.select(1)  # Switch to Proto's tab
    
    def complete_task(self):
        """Mark a task as complete"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a task to complete.")
            return
        
        task_text = self.tasks_listbox.get(selection[0])
        
        # Simple dopamine celebration
        dialog = tk.Toplevel(self.root)
        dialog.title("🎉 Task Complete!")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Awesome! You completed:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        ttk.Label(dialog, text=task_text, wraplength=350).pack(pady=5)
        
        ttk.Label(dialog, text="How good does it feel? (1-10)", 
                 font=("Arial", 10, "bold")).pack(pady=10)
        
        dopamine_var = tk.IntVar(value=8)
        dopamine_scale = ttk.Scale(dialog, from_=1, to=10, orient=tk.HORIZONTAL, 
                                  variable=dopamine_var)
        dopamine_scale.pack(padx=20, fill=tk.X)
        
        dopamine_label = ttk.Label(dialog, text="8")
        dopamine_label.pack()
        
        def update_label(*args):
            dopamine_label.config(text=str(int(dopamine_var.get())))
        
        dopamine_var.trace_add("write", update_label)
        
        def save_completion():
            score = int(dopamine_var.get())
            # Here you would update the task in database
            # For MVP, just remove from list
            self.tasks_listbox.delete(selection[0])
            
            # Notify Spark
            self.send_to_agent("spark", 
                f"I just completed a task: {task_text}. Dopamine score: {score}/10. Celebrate with me!",
                auto=True)
            
            dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_completion).pack(pady=15)
    
    def save_conversation(self, project_id, agent, message):
        """Save conversation to database"""
        self.cursor.execute('''
            INSERT INTO conversations (project_id, agent, message)
            VALUES (?, ?, ?)
        ''', (project_id, agent, message))
        self.conn.commit()
    
    def get_conversation_history(self, project_id, agent_id, limit=10):
        """Get conversation history"""
        self.cursor.execute('''
            SELECT timestamp, agent, message 
            FROM conversations 
            WHERE project_id = ? AND (agent = ? OR agent = 'user')
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (project_id, agent_id, limit))
        
        return list(reversed(self.cursor.fetchall()))
    
    def update_project_activity(self):
        """Update last activity timestamp"""
        if self.current_project_id:
            self.cursor.execute('''
                UPDATE projects 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (self.current_project_id,))
            self.conn.commit()
    
    def load_project_info(self):
        """Load and display current project info"""
        if not self.current_project_id:
            self.project_title_label.config(text="No project selected")
            self.project_status_label.config(text="")
            return
        
        self.cursor.execute('''
            SELECT title, created_at, last_activity, status 
            FROM projects 
            WHERE id = ?
        ''', (self.current_project_id,))
        
        result = self.cursor.fetchone()
        if result:
            title, created, last_activity, status = result
            self.project_title_label.config(text=title)
            self.project_status_label.config(text=f"Status: {status.title()}")
    
    def update_stats(self):
        """Update statistics display"""
        if not self.current_project_id:
            return
        
        # Get project count
        self.cursor.execute('SELECT COUNT(*) FROM projects')
        project_count = self.cursor.fetchone()[0]
        
        # Get message count for current project
        self.cursor.execute('''
            SELECT COUNT(*) FROM conversations WHERE project_id = ?
        ''', (self.current_project_id,))
        message_count = self.cursor.fetchone()[0]
        
        # Get task count
        self.cursor.execute('''
            SELECT COUNT(*) FROM tasks WHERE project_id = ? AND completed = 0
        ''', (self.current_project_id,))
        task_count = self.cursor.fetchone()[0]
        
        stats_text = f"""Total Projects: {project_count}
Messages: {message_count}
Active Tasks: {task_count}

Team formed: {datetime.now().strftime('%Y-%m-%d')}
"""
        
        self.stats_label.config(text=stats_text)
    
    def update_insights_display(self):
        """Update insights display"""
        self.insights_display.config(state=tk.NORMAL)
        self.insights_display.delete("1.0", tk.END)
        
        if self.current_project_id:
            self.cursor.execute('''
                SELECT content, timestamp FROM insights 
                WHERE project_id = ?
                ORDER BY timestamp DESC LIMIT 5
            ''', (self.current_project_id,))
            
            insights = self.cursor.fetchall()
            for content, timestamp in insights:
                time_str = datetime.fromisoformat(timestamp).strftime("%m/%d %H:%M")
                self.insights_display.insert(tk.END, f"[{time_str}]\n{content}\n\n")
        
        self.insights_display.config(state=tk.DISABLED)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def load_initial_state(self):
        """Load initial state on app start"""
        # Check if there are any projects
        self.cursor.execute('SELECT id FROM projects ORDER BY last_activity DESC LIMIT 1')
        result = self.cursor.fetchone()
        
        if result:
            self.current_project_id = result[0]
            self.load_project_info()
            self.update_stats()
            self.update_insights_display()
        else:
            # Welcome message
            if self.client:
                messagebox.showinfo("Welcome!", 
                    "Welcome to ADHD Productivity Trio!\n\n" +
                    "Let's create your first project and meet your AI team members:\n" +
                    "✨ Spark (Motivator) and 🎯 Proto (Executor)\n\n" +
                    "Together, the three of you will build something amazing!")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Anthropic API Key:", 
                 font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        api_key_entry = ttk.Entry(dialog, width=60, show="*")
        api_key_entry.pack(padx=10, fill=tk.X)
        api_key_entry.insert(0, self.config.get("anthropic_api_key", ""))
        
        ttk.Label(dialog, text="Get your API key from: https://console.anthropic.com", 
                 foreground="blue").pack(pady=5, padx=10, anchor=tk.W)
        
        ttk.Label(dialog, text="Model:", 
                 font=("Arial", 10, "bold")).pack(pady=(10, 5), padx=10, anchor=tk.W)
        
        model_var = tk.StringVar(value=self.config.get("model", "claude-sonnet-4-5-20250929"))
        model_combo = ttk.Combobox(dialog, textvariable=model_var, width=57, 
                                   values=["claude-sonnet-4-5-20250929", "claude-opus-4-5-20250929"])
        model_combo.pack(padx=10, fill=tk.X)
        
        def save_settings():
            api_key = api_key_entry.get().strip()
            model = model_var.get()
            
            self.config["anthropic_api_key"] = api_key
            self.config["model"] = model
            self.save_config()
            
            # Reinitialize client
            self.init_claude_client()
            
            messagebox.showinfo("Success", "Settings saved! Please restart the app for changes to take full effect.")
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_all_projects(self):
        """Show all projects window"""
        dialog = tk.Toplevel(self.root)
        dialog.title("All Projects")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        
        # Create treeview
        tree = ttk.Treeview(dialog, columns=("Title", "Status", "Created", "Last Activity"), 
                           show="headings")
        tree.heading("Title", text="Title")
        tree.heading("Status", text="Status")
        tree.heading("Created", text="Created")
        tree.heading("Last Activity", text="Last Activity")
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load projects
        self.cursor.execute('''
            SELECT id, title, status, created_at, last_activity 
            FROM projects 
            ORDER BY last_activity DESC
        ''')
        
        for row in self.cursor.fetchall():
            pid, title, status, created, last_activity = row
            tree.insert("", tk.END, values=(title, status, created[:10], last_activity[:10]))
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_insights(self):
        """Show insights window"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Insights")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        
        text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load all insights
        self.cursor.execute('''
            SELECT content, timestamp, insight_type 
            FROM insights 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        
        for content, timestamp, itype in self.cursor.fetchall():
            time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
            text.insert(tk.END, f"[{time_str}] ({itype})\n{content}\n\n")
        
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
    
    def show_user_guide(self):
        """Show user guide"""
        messagebox.showinfo("User Guide", 
            "User Guide:\n\n" +
            "1. Create a new project to start\n" +
            "2. Chat with Spark ✨ for motivation and enthusiasm\n" +
            "3. Chat with Proto 🎯 for execution and planning\n" +
            "4. Use Team Discussion when you need both perspectives\n" +
            "5. Quick Capture to save your thoughts\n" +
            "6. Use 'What Was I Doing?' when you return\n\n" +
            "Check the full user-guide.md file for detailed instructions!")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
            f"{APP_NAME} v{APP_VERSION}\n\n" +
            "A three-way team productivity system designed for ADHD minds.\n\n" +
            "Your AI teammates:\n" +
            "✨ Spark - The Motivator\n" +
            "🎯 Proto - The Executor\n\n" +
            "Together, you build amazing things.\n\n" +
            "Powered by Claude API from Anthropic")
    
    def on_closing(self):
        """Handle app closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.conn.close()
            self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ProductivityTrioApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
