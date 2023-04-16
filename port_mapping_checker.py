import subprocess
import tkinter as tk
import tkinter.messagebox as messagebox

# Define the list of ports to search for
ports_to_search = ["55303", "55011", "54853", "54829","6000"]

# Define the desired service
desired_service = "OneDrive.exe"

def run_port_checker():
    # Clear the output text box
    output_text.delete("1.0", tk.END)

    # Iterate over the ports to search for
    for port_to_search in ports_to_search:
        # Set a flag to keep track of whether the port is found
        port_found = False

        # Execute the netstat command and capture the output
        output = subprocess.check_output("netstat -ano", shell=True)

        # Split the output by lines and iterate over them
        for line in output.decode().split("\n"):
            # Split the line by spaces
            parts = line.split()
            # Check if the line contains the correct number of columns
            if len(parts) >= 2:
                # Check if the local address column contains the port we're looking for
                if f":{port_to_search}" in parts[1]:
                    # Extract the process ID from the line
                    process_id = parts[-1]
                    # Execute a tasklist command to get the process name and service name
                    tasklist_output = subprocess.check_output(f"tasklist /fi \"PID eq {process_id}\" /fo list", shell=True)
                    # Extract the process and service names from the tasklist output
                    process_name = None
                    service_name = None
                    for tasklist_line in tasklist_output.decode().split("\n"):
                        if tasklist_line.startswith("Image Name:"):
                            process_name = tasklist_line.split(":")[1].strip()
                        elif tasklist_line.startswith("Services:"):
                            service_name = tasklist_line.split(":")[1].strip()
                    # Check if the process name matches the desired service
                    if process_name == desired_service:
                        # Print the results, indicating that this is the desired service
                        output_text.insert(tk.END, f"Port {port_to_search} is being used by process '{process_name}' (The right one!)\n")
                        port_found = True
                    else:
                        # Print the results, indicating that this is a bad service
                        # output_text.insert(tk.END, f"Port {port_to_search} is being used by process '{process_name}' (BAD Service, kill it with FIRE, service={service_name})\n")
                        output_text.insert(tk.END, f"Port {port_to_search} is being used by process '{process_name}' (BAD Service, kill it with FIRE !!\n")
                        port_found = True

        # Check if the port was not found and print a message
        if not port_found:
            output_text.insert(tk.END, f"Port {port_to_search} is not in use\n")

def stop_service_on_ports(ports):
    ports_without_process = []
    for port in ports:
        try:
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True)
            lines = output.decode().split("\n")
            process_found = False
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and f":{port}" in parts[1]:
                    process_id = parts[-1]
                    subprocess.run(f"taskkill /F /PID {process_id}", shell=True)
                    output_text.insert(tk.END, f"Stopped service on port {port} with PID {process_id}\n")
                    process_found = True
            if not process_found:
                ports_without_process.append(port)
        except subprocess.CalledProcessError:
            ports_without_process.append(port)
    return ports_without_process


def restart_service_on_ports(ports):
    # implementation for restarting services on selected ports
    # Not used
    pass

def on_stop_service_clicked():
    selected_ports = [ports_listbox.get(idx) for idx in ports_listbox.curselection()]
    if not selected_ports:
        messagebox.showerror("Error", "You need to select a port first")
    else:
        ports_without_process = stop_service_on_ports(selected_ports)
        for port in ports_without_process:
            messagebox.showerror("Error", f"There's no active service on {port} port")



def on_restart_service_clicked():
    selected_ports = [ports_listbox.get(idx) for idx in ports_listbox.curselection()]
    restart_service_on_ports(selected_ports)

root = tk.Tk()
root.title("Array Scanner Port checker thingumy")
root.geometry("900x600")

banner_label = tk.Label(root, text="Array Scanner Port checker thingumy")
banner_label.pack()


check_ports_button = tk.Button(root, text="Check Ports", command=run_port_checker, width=24)
check_ports_button.pack(pady=10)

ports_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
ports_listbox.pack()

for port in ports_to_search:
    ports_listbox.insert(tk.END, port)

stop_service_button = tk.Button(root, text="KILL IT WITH FIRE !!", command=on_stop_service_clicked, width=24)
stop_service_button.pack(pady=10)


output_text = tk.Text(root, height=10)
output_text.pack(fill=tk.X, expand=True, padx=(root.winfo_screenwidth() * 0.05), pady=10)


root.mainloop()

