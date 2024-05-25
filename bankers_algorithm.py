import tkinter as tk
from tkinter import messagebox, simpledialog

class BankerAlgorithm:
    def __init__(self, total_resources):
        self.total_resources = total_resources
        self.available_resources = total_resources[:]
        self.max_demand = []
        self.allocation = []
        self.need = []

    def add_process(self, max_demand):
        if any(d > t for d, t in zip(max_demand, self.total_resources)):
            messagebox.showerror("Error", "Process max demand exceeds total system resources. Process not added.")
            return False
        self.max_demand.append(max_demand)
        self.allocation.append([0] * len(max_demand))
        self.need.append(max_demand[:])
        messagebox.showinfo("Success", f"Process {len(self.max_demand) - 1} added successfully.")
        return True

    def request_resources(self, process_id, request):
        if process_id >= len(self.max_demand) or process_id < 0:
            messagebox.showerror("Error", "Invalid process ID.")
            return False
        if any(req > need for req, need in zip(request, self.need[process_id])):
            messagebox.showerror("Error", "Request exceeds declared maximum demand.")
            return False
        if any(req > avail for req, avail in zip(request, self.available_resources)):
            messagebox.showwarning("Warning", "Not enough resources available.")
            return False
        
        # Temporarily allocate requested resources
        self.execute_request(process_id, request)
        
        if not self.is_safe():
            self.rollback_request(process_id, request)
            messagebox.showerror("Error", "Unsafe state would occur. Request denied.")
            return False
        
        # Check if process's needs are fully satisfied and release resources if so
        if all(need == 0 for need in self.need[process_id]):
            self.release_process_resources(process_id)
            return "completed"
        
        messagebox.showinfo("Success", "Request granted.")
        return True

    def release_resources(self, process_id, release):
        if process_id >= len(self.allocation) or process_id < 0:
            messagebox.showerror("Error", "Invalid process ID.")
            return False
        if len(release) != len(self.allocation[process_id]):
            messagebox.showerror("Error", "Resource release length does not match allocation length.")
            return False
        if any(rel > alloc for rel, alloc in zip(release, self.allocation[process_id])):
            messagebox.showerror("Error", "Cannot release more resources than are currently allocated.")
            return False
        for i in range(len(release)):
            self.available_resources[i] += release[i]
            self.allocation[process_id][i] -= release[i]
            self.need[process_id][i] += release[i]
        messagebox.showinfo("Success", f"Resources released from process {process_id}")
        return True

    def release_process_resources(self, process_id):
        for i in range(len(self.available_resources)):
            self.available_resources[i] += self.allocation[process_id][i]
            self.allocation[process_id][i] = 0
            self.need[process_id][i] = 0
        messagebox.showinfo("Success", f"Process {process_id} has completed and its resources have been released.")

    def execute_request(self, process_id, request):
        for i in range(len(request)):
            self.available_resources[i] -= request[i]
            self.allocation[process_id][i] += request[i]
            self.need[process_id][i] -= request[i]

    def rollback_request(self, process_id, request):
        for i in range(len(request)):
            self.available_resources[i] += request[i]
            self.allocation[process_id][i] -= request[i]
            self.need[process_id][i] += request[i]

    def is_safe(self):
        work = self.available_resources[:]
        finish = [False] * len(self.max_demand)
        while True:
            found = False
            for i in range(len(finish)):
                if not finish[i] and all(self.need[i][j] <= work[j] for j in range(len(work))):
                    for k in range(len(work)):
                        work[k] += self.allocation[i][k]
                    finish[i] = True
                    found = True
                    break
            if not found:
                break
        return all(finish)

    def show_state(self, text_widget):
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "Current System State:\n")
        text_widget.insert(tk.END, f"Available resources: {self.available_resources}\n")
        text_widget.insert(tk.END, "Processes' resource allocation and needs:\n")
        for i in range(len(self.allocation)):
            text_widget.insert(tk.END, f"Process {i}: Allocation: {self.allocation[i]}, Need: {self.need[i]}, Max: {self.max_demand[i]}\n")

class BankersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Banker's Algorithm Management System")
        self.banker = None

        tk.Label(root, text="Enter total system resources (e.g., 10 5 2):").grid(row=0, column=0)
        self.resources_entry = tk.Entry(root)
        self.resources_entry.grid(row=0, column=1)

        tk.Button(root, text="Initialize System", command=self.initialize_system).grid(row=0, column=2)

        self.state_text = tk.Text(root, height=20, width=60)
        self.state_text.grid(row=1, column=0, columnspan=3)

        self.log_text = tk.Text(root, height=10, width=60)
        self.log_text.grid(row=3, column=0, columnspan=3)

        tk.Button(root, text="Add Process", command=self.add_process).grid(row=2, column=0)
        tk.Button(root, text="Request Resources", command=self.request_resources).grid(row=2, column=1)
        tk.Button(root, text="Release Resources", command=self.release_resources).grid(row=2, column=2)

    def initialize_system(self):
        resources = [int(x) for x in self.resources_entry.get().split()]
        self.banker = BankerAlgorithm(resources)
        self.banker.show_state(self.state_text)

    def add_process(self):
        if self.banker is None:
            messagebox.showerror("Error", "System not initialized. Please initialize the system first.")
            return
        demands = simpledialog.askstring("Input", f"Enter maximum resource demands for a new process (should not exceed total resources {self.banker.total_resources}):")
        if demands:
            demands = [int(x) for x in demands.split()]
            self.banker.add_process(demands)
            self.banker.show_state(self.state_text)

    def request_resources(self):
        if self.banker is None:
            messagebox.showerror("Error", "System not initialized. Please initialize the system first.")
            return
        pid = simpledialog.askinteger("Input", "Enter process ID:")
        if pid is None or pid >= len(self.banker.max_demand) or pid < 0:
            messagebox.showerror("Error", "Invalid process ID.")
            return
        reqs = simpledialog.askstring("Input", "Enter resource request (must not exceed the remaining need or available resources):")
        if reqs:
            reqs = [int(x) for x in reqs.split()]
            result = self.banker.request_resources(pid, reqs)
            if result == "completed":
                self.log_text.insert(tk.END, f"Process {pid} has completed.\n")
            self.banker.show_state(self.state_text)

    def release_resources(self):
        if self.banker is None:
            messagebox.showerror("Error", "System not initialized. Please initialize the system first.")
            return
        pid = simpledialog.askinteger("Input", "Enter process ID:")
        if pid is None or pid >= len(self.banker.max_demand) or pid < 0:
            messagebox.showerror("Error", "Invalid process ID.")
            return
        rels = simpledialog.askstring("Input", "Enter resources to release (cannot exceed the current allocation):")
        if rels:
            rels = [int(x) for x in rels.split()]
            if not self.banker.release_resources(pid, rels):
                messagebox.showerror("Error", "Release resources failed.")
            else:
                self.banker.show_state(self.state_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = BankersGUI(root)
    root.mainloop()
