import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import bcrypt
import json

class userclass:
    users = {}

    def __init__(self, name, password, user_id=None, hashed=False):
        self.name = name
        self.tasks = []
        self.user_id = user_id if user_id else self.generate_unique_user_id()

        if hashed:  # If password is already hashed (when loading from file)
            self.__password_hash = password
        else:  # If creating a new user
            self.__password_hash = self.hash_password(password)

        userclass.users[self.user_id] = self
        self.save_account()

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def Verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.__password_hash.encode('utf-8'))

    def generate_unique_user_id(self):
        while True:
            user_id = random.randint(1, 1000)
            if user_id not in userclass.users:
                return user_id

    def save_account(self):
        data = {
            str(acc): [acc_obj.name, acc_obj.__password_hash, acc_obj.tasks]
            for acc, acc_obj in userclass.users.items()
        }
        with open("listusers.json", "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_users():
        try:
            with open("listusers.json", "r") as f:
                data = json.load(f)
                for user_id, details in data.items():
                    name, password_hash, tasks = details
                    acc = userclass(name, password_hash, int(user_id), hashed=True)
                    acc.tasks = tasks  # Load tasks correctly
                    userclass.users[int(user_id)] = acc
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    @staticmethod
    def login(uid, password):
        if uid in userclass.users and userclass.users[uid].Verify_password(password):
            return userclass.users[uid]
        return None

    def showtasks(self):
        return self.tasks

    def addtask(self, task, status="Incomplete"):
        self.tasks.append([task, status])
        self.save_account()
        return "Task added successfully!!"

    def changestatus(self, task_number, status="Incomplete"):
        try:
            self.tasks[int(task_number) - 1][1] = status
            self.save_account()
            return 1
        except (IndexError, ValueError):
            return 0

    def delete_task(self, task_number):
        try:
            del self.tasks[int(task_number) - 1]
            self.save_account()
            return 1
        except (IndexError, ValueError):
            return 0

class todolistapp:
    def __init__(self, root):
        self.root = root
        self.root.title("My To-Do List")
        self.root.geometry("400x500")
        self.create_login_screen()
        userclass.load_users()

    def create_login_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="USER ID").pack()
        self.user_entry = tk.Entry(self.root)
        self.user_entry.pack()
        tk.Label(self.root, text="PASSWORD").pack()
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack()
        tk.Button(self.root, text="Login", command=self.login).pack()
        tk.Button(self.root, text="Register", command=self.create_register_screen).pack()

    def create_register_screen(self):
        self.clear_screen()
        tk.Label(self.root, text="Name").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()
        tk.Label(self.root, text="PASSWORD").pack()
        self.pass_entry = tk.Entry(self.root, show="*")
        self.pass_entry.pack()
        tk.Button(self.root, text="Create Account", command=self.register).pack()
        tk.Button(self.root, text="Go Back", command=self.create_login_screen).pack()

    def register(self):
        name = self.name_entry.get()
        password = self.pass_entry.get()

        if len(password) < 8 or password.isalnum():
            messagebox.showerror("UNSAFE", "Password must be 8+ characters with a special character.")
            return

        user = userclass(name, password)
        messagebox.showinfo("Success", f"Account created! User ID: {user.user_id}")
        self.create_login_screen()

    def login(self):
        try:
            uid = int(self.user_entry.get())
            password = self.pass_entry.get()
            self.user = userclass.login(uid, password)

            if self.user:
                self.create_dashboard()
            else:
                messagebox.showerror("ERROR", "Invalid Credentials")
        except ValueError:
            messagebox.showerror("Value Error", "Enter a Valid User ID")

    def create_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Welcome, {self.user.name}!").pack()
        tk.Button(self.root, text="View Tasks", command=self.taskscreen).pack()
        tk.Button(self.root, text="Logout", command=self.create_login_screen).pack()

    def taskscreen(self):
        self.clear_screen()
        tk.Label(self.root, text="Your Tasks:").pack()

        for idx, task in enumerate(self.user.showtasks(), start=1):
            tk.Label(self.root, text=f"{idx}. {task[0]} - {task[1]}").pack()

        tk.Button(self.root, text="Add Task", command=self.addtsk).pack()
        tk.Button(self.root, text="Change Task Status", command=self.changestatus).pack()
        tk.Button(self.root, text="Remove a Task", command=self.deletetask).pack()
        tk.Button(self.root, text="Go Back", command=self.create_dashboard).pack()

    def addtsk(self):
        task = simpledialog.askstring("ADD TASK", "Enter the task")
        if task:
            messagebox.showinfo("Success", self.user.addtask(task))
        self.taskscreen()

    def changestatus(self):
        tasknum = simpledialog.askstring("Change Task Status", "Enter the task number")
        status = simpledialog.askstring("Change Task Status", "Enter the new status")

        if tasknum and status:
            if self.user.changestatus(tasknum, status):
                messagebox.showinfo("Success", f"Task {tasknum} status changed!")
            else:
                messagebox.showerror("Error", "Invalid task number.")
        self.taskscreen()

    def deletetask(self):
        tasknum = simpledialog.askstring("Delete Task", "Enter the task number")
        if tasknum and self.user.delete_task(tasknum):
            messagebox.showinfo("Success", f"Task {tasknum} deleted.")
        else:
            messagebox.showerror("Error", "Invalid task number.")
        self.taskscreen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = todolistapp(root)
    root.mainloop()
