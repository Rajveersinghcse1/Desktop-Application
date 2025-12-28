import tkinter as tk
from tkinter import messagebox, ttk

class Robot:
    def survived_robots_healths(self, positions, healths, directions):
        n = len(positions)
        indices = list(range(n))
        result = []
        stack = []

        # Sorting indices based on positions
        indices.sort(key=lambda x: positions[x])

        for current_index in indices:
            # Add right-moving robots to the stack
            if directions[current_index] == 'R':
                stack.append(current_index)
            else:
                while stack and healths[current_index] > 0:
                    # Pop the top robot from the stack for collision check
                    top_index = stack.pop()

                    # Top robot survives, current robot is destroyed
                    if healths[top_index] > healths[current_index]:
                        healths[top_index] -= 1
                        healths[current_index] = 0
                        stack.append(top_index)
                    elif healths[top_index] < healths[current_index]:
                        # Current robot survives, top robot is destroyed
                        healths[current_index] -= 1
                        healths[top_index] = 0
                    else:
                        # Both robots are destroyed
                        healths[current_index] = 0
                        healths[top_index] = 0

        # Collect surviving robots
        for index in range(n):
            if healths[index] > 0:
                result.append(healths[index])

        return result

class RobotUI:
    def __init__(self, master):
        self.master = master
        master.title("Robot Collision Simulation")
        master.geometry("850x650")
        master.configure(bg="#F0F0F0")

        # Main title
        self.title_label = tk.Label(master, text="Robot Collision Simulation", font=("Helvetica", 18), bg="#F0F0F0")
        self.title_label.pack(pady=10)

        # Input section
        self.input_frame = tk.Frame(master, bg="#F0F0F0")
        self.input_frame.pack(pady=10)

        self.positions_label = tk.Label(self.input_frame, text="Positions (space-separated):", bg="#F0F0F0")
        self.positions_label.grid(row=0, column=0, padx=5, pady=5)
        self.positions_entry = tk.Entry(self.input_frame, width=40)
        self.positions_entry.grid(row=0, column=1, padx=5, pady=5)

        self.directions_label = tk.Label(self.input_frame, text="Directions (L/R):", bg="#F0F0F0")
        self.directions_label.grid(row=1, column=0, padx=5, pady=5)
        self.directions_entry = tk.Entry(self.input_frame, width=40)
        self.directions_entry.grid(row=1, column=1, padx=5, pady=5)

        self.healths_label = tk.Label(self.input_frame, text="Healths (space-separated):", bg="#F0F0F0")
        self.healths_label.grid(row=2, column=0, padx=5, pady=5)
        self.healths_entry = tk.Entry(self.input_frame, width=40)
        self.healths_entry.grid(row=2, column=1, padx=5, pady=5)

        # Control buttons
        self.button_frame = tk.Frame(master, bg="#F0F0F0")
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="Start Simulation", command=self.run_simulation, width=20, bg="#4CAF50", fg="white")
        self.submit_button.grid(row=0, column=0, padx=10)

        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset_simulation, width=20, bg="#F44336", fg="white")
        self.reset_button.grid(row=0, column=1, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_simulation, width=20, bg="#FFC107", fg="black", state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=10)

        # Label to display collision messages
        self.collision_label = tk.Label(master, text="", font=("Helvetica", 14), fg="red", bg="#F0F0F0")
        self.collision_label.pack(pady=10)

        # Canvas for robot visualization
        self.canvas = tk.Canvas(master, width=800, height=400, bg='white', bd=2, relief="sunken")
        self.canvas.pack(pady=20)

        self.robot = Robot()
        self.timer = None
        self.positions = []
        self.directions = []
        self.healths = []

    def run_simulation(self):
        try:
            positions = list(map(int, self.positions_entry.get().split()))
            directions = list(self.directions_entry.get())  # Convert directions to a list
            healths = list(map(int, self.healths_entry.get().split()))

            if len(positions) != len(directions) or len(positions) != len(healths):
                messagebox.showerror("Input Error", "The number of positions, directions, and healths must be the same.")
                return

            self.positions = positions
            self.directions = directions
            self.healths = healths

            self.stop_button.config(state=tk.NORMAL)  # Enable stop button
            self.submit_button.config(state=tk.DISABLED)  # Disable submit button during simulation
            self.collision_label.config(text="")  # Clear any previous collision message

            # Start the animation of robots
            self.animate_robots(positions, healths, directions)

        except ValueError:
            messagebox.showerror("Input Error", "Please ensure all fields are filled in correctly.")

    def animate_robots(self, positions, healths, directions):
        self.canvas.delete("all")  # Clear previous drawings

        def move_robots():
            collision_detected = False
            for i in range(len(positions)):
                if healths[i] <= 0:  # Skip dead robots
                    continue

                # Update positions based on directions
                if directions[i] == 'R':
                    positions[i] += 1  # Move right
                elif directions[i] == 'L':
                    positions[i] -= 1  # Move left

            # Clear previous drawings
            self.canvas.delete("all")

            # Draw robots and detect collisions
            for i in range(len(positions)):
                if healths[i] <= 0:  # Skip dead robots
                    continue

                x = positions[i] * 10  # Scale position for better visibility
                y = 200  # Fixed height for robots
                color = self.get_health_color(healths[i])

                # Draw robot body
                self.canvas.create_rectangle(x, y, x + 30, y + 40, fill=color, outline="black")

                # Draw robot eyes
                self.canvas.create_oval(x + 5, y + 5, x + 10, y + 10, fill="black")  # Left eye
                self.canvas.create_oval(x + 20, y + 5, x + 25, y + 10, fill="black")  # Right eye

                # Draw health
                self.canvas.create_text(x + 15, y + 20, text=str(healths[i]), fill="black")

                # Draw robot direction indicator
                if directions[i] == 'R':
                    self.canvas.create_text(x + 15, y + 50, text="→", fill="black")
                else:
                    self.canvas.create_text(x + 15, y + 50, text="←", fill="black")

                # Check for collision with other robots
                for j in range(i + 1, len(positions)):
                    if healths[j] > 0:  # Check only if both robots are alive
                        # Check if robots are moving towards each other
                        if directions[i] == 'R' and directions[j] == 'L' and positions[i] < positions[j]:
                            if abs(positions[i] - positions[j]) <= 5:  # Collision threshold
                                collision_detected = True
                                self.resolve_collision(i, j, healths, directions)
                                self.display_collision_message(i, j)  # Display collision message

            # Schedule next move if there are robots still moving
            if not collision_detected and any(health > 0 for health in healths):
                self.timer = self.canvas.after(100, move_robots)
            else:
                self.submit_button.config(state=tk.NORMAL)  # Enable submit button when done

        move_robots()

    def resolve_collision(self, i, j, healths, directions):
        """Handle the collision between robot i and robot j."""
        if healths[i] > healths[j]:
            healths[i] -= 1
            healths[j] = 0
            directions[j] = 'S'
        elif healths[j] > healths[i]:
            healths[j] -= 1
            healths[i] = 0
            directions[i] = 'S'
        else:
            healths[i] = 0
            healths[j] = 0
            directions[i] = 'S'
            directions[j] = 'S'

    def display_collision_message(self, i, j):
        """Display a message on the GUI when a collision occurs."""
        collision_text = f"Collision detected between robot {i + 1} and robot {j + 1}!"
        self.collision_label.config(text=collision_text)

    def get_health_color(self, health):
        # Color mapping based on health
        if health <= 0:
            return "gray"
        elif health < 25:
            return "red"
        elif health < 50:
            return "yellow"
        else:
            return "green"

    def reset_simulation(self):
        """Reset the simulation."""
        self.canvas.delete("all")
        self.positions_entry.delete(0, tk.END)
        self.directions_entry.delete(0, tk.END)
        self.healths_entry.delete(0, tk.END)
        self.submit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.collision_label.config(text="")
        if self.timer:
            self.canvas.after_cancel(self.timer)

    def stop_simulation(self):
        """Stop the animation."""
        if self.timer:
            self.canvas.after_cancel(self.timer)
        self.submit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    robot_ui = RobotUI(root)
    root.mainloop()
