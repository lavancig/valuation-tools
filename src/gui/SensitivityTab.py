#!/usr/bin/env python3
"""
Sensitivity Analysis Tab for Monte Carlo Simulation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class SensitivityTab:
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.simulation_results = None
        self.is_running = False
        
        # Create the main frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the interface
        self._create_interface()
        
    def _create_interface(self):
        """Create the sensitivity analysis interface"""
        
        # Title
        title_label = ttk.Label(self.frame, text="Sensitivity Analysis - Monte Carlo Simulation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(self.frame, text="Simulation Parameters", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Number of scenarios
        scenarios_frame = ttk.Frame(control_frame)
        scenarios_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(scenarios_frame, text="Number of Scenarios:").pack(side=tk.LEFT)
        self.scenarios_var = tk.StringVar(value="1000")
        scenarios_spinbox = ttk.Spinbox(scenarios_frame, from_=100, to=10000, 
                                       textvariable=self.scenarios_var, width=10)
        scenarios_spinbox.pack(side=tk.LEFT, padx=(10, 0))
        
        # Run button
        self.run_button = ttk.Button(scenarios_frame, text="Run Monte Carlo Simulation", 
                                   command=self._run_simulation, state='disabled')
        self.run_button.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(control_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_label = ttk.Label(control_frame, text="Ready to run simulation")
        self.progress_label.pack(pady=(5, 0))
        
        # Status indicator
        self.status_label = ttk.Label(control_frame, text="⚠ Run a valuation first to enable simulation", 
                                     foreground="red")
        self.status_label.pack(pady=(5, 0))
        
        # Parameter ranges section
        params_frame = ttk.LabelFrame(self.frame, text="Parameter Ranges", padding=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create parameter controls
        self._create_parameter_controls(params_frame)
        
        # Results section
        results_frame = ttk.LabelFrame(self.frame, text="Simulation Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics frame
        stats_frame = ttk.Frame(results_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statistics labels
        self.stats_labels = {}
        stats_info = [
            ("Mean", "Mean Fair Value:"),
            ("Median", "Median Fair Value:"),
            ("Std", "Standard Deviation:"),
            ("Min", "Minimum Value:"),
            ("Max", "Maximum Value:"),
            ("P5", "5th Percentile:"),
            ("P95", "95th Percentile:")
        ]
        
        for i, (key, label) in enumerate(stats_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(stats_frame, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_frame, text="N/A", font=('Arial', 9, 'bold'))
            self.stats_labels[key].grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20))
        
        # Plot frame
        plot_frame = ttk.Frame(results_frame)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty plot
        self.ax.set_title("Fair Value Distribution (Monte Carlo Simulation)")
        self.ax.set_xlabel("Fair Value ($)")
        self.ax.set_ylabel("Frequency")
        self.ax.text(0.5, 0.5, "Run simulation to see results", 
                    transform=self.ax.transAxes, ha='center', va='center', 
                    fontsize=14, alpha=0.5)
        
    def _create_parameter_controls(self, parent):
        """Create parameter range controls"""
        
        # Parameter definitions
        self.parameters = {
            'discount_rate': {
                'name': 'Discount Rate (Cost of Equity)',
                'base': 0.075,
                'range': 0.015,  # ±1.5%
                'unit': '%',
                'var': tk.StringVar(value="1.5")
            },
            'perpetual_growth': {
                'name': 'Perpetual Growth Rate',
                'base': 0.029,
                'range': 0.01,  # ±1.0%
                'unit': '%',
                'var': tk.StringVar(value="1.0")
            },
            'prediction_window_growth': {
                'name': 'Prediction Window Growth Rate',
                'base': 0.05,
                'range': 0.03,  # ±3.0%
                'unit': '%',
                'var': tk.StringVar(value="3.0")
            },
            'profitability': {
                'name': 'Profitability (Net Income Margin)',
                'base': 0.25,
                'range': 0.03,  # ±3%
                'unit': '%',
                'var': tk.StringVar(value="3.0")
            },
            'capex': {
                'name': 'CapEx Variation',
                'base': 1.0,
                'range': 0.2,  # ±20%
                'unit': '%',
                'var': tk.StringVar(value="20.0")
            },
            'working_capital': {
                'name': 'Working Capital Variation',
                'base': 1.0,
                'range': 0.15,  # ±15%
                'unit': '%',
                'var': tk.StringVar(value="15.0")
            },
            'net_borrowings': {
                'name': 'Net Borrowings Variation',
                'base': 1.0,
                'range': 0.3,  # ±30%
                'unit': '%',
                'var': tk.StringVar(value="30.0")
            }
        }
        
        # Create parameter controls
        for i, (key, param) in enumerate(self.parameters.items()):
            param_frame = ttk.Frame(parent)
            param_frame.pack(fill=tk.X, pady=2)
            
            # Parameter name
            ttk.Label(param_frame, text=param['name'], width=30).pack(side=tk.LEFT)
            
            # Base value
            ttk.Label(param_frame, text=f"Base: {param['base']*100:.1f}{param['unit']}").pack(side=tk.LEFT, padx=(10, 5))
            
            # Range input
            ttk.Label(param_frame, text="±").pack(side=tk.LEFT)
            range_spinbox = ttk.Spinbox(param_frame, from_=0.1, to=50.0, 
                                       textvariable=param['var'], width=8, format="%.1f")
            range_spinbox.pack(side=tk.LEFT, padx=(2, 5))
            ttk.Label(param_frame, text=param['unit']).pack(side=tk.LEFT)
    
    def _check_valuation_ready(self, show_errors=True):
        """Check if valuation model is ready for sensitivity analysis"""
        if self.controller is None:
            if show_errors:
                messagebox.showerror("No Controller", "Controller not available. Please restart the application.")
            return False
        
        if not hasattr(self.controller, '_modelObj'):
            if show_errors:
                messagebox.showerror("No Model", "Valuation model not found. Please run a valuation first.")
            return False
        
        if self.controller._modelObj is None:
            if show_errors:
                messagebox.showerror("Model Not Initialized", "Valuation model is not initialized. Please run a valuation first.")
            return False
        
        valuation_model = self.controller._modelObj
        if not hasattr(valuation_model, '_valuationObj'):
            if show_errors:
                messagebox.showerror("DCF Model Missing", "DCF valuation object not found. Please run a valuation first.")
            return False
        
        dcf_model = valuation_model._valuationObj
        if not hasattr(dcf_model, '_successful') or not dcf_model._successful:
            if show_errors:
                messagebox.showerror("Model Not Ready", "Valuation model is not properly initialized. Please run a valuation first.")
            return False
        
        return True
    
    def update_status(self):
        """Update the status indicator based on valuation readiness"""
        if self._check_valuation_ready(show_errors=False):
            self.status_label.config(text="✓ Valuation ready - Simulation available", 
                                   foreground="green")
            self.run_button.config(state='normal')
        else:
            self.status_label.config(text="⚠ Run a valuation first to enable simulation", 
                                   foreground="red")
            self.run_button.config(state='disabled')
    
    def refresh_status(self):
        """Refresh the status indicator - can be called externally"""
        try:
            if hasattr(self, 'status_label') and self.status_label is not None:
                self.update_status()
        except Exception as e:
            # Silently ignore errors during initialization
            pass
            
    def _run_simulation(self):
        """Run the Monte Carlo simulation"""
        if self.is_running:
            messagebox.showwarning("Simulation Running", "A simulation is already running. Please wait.")
            return
        
        # Check if valuation is ready
        if not self._check_valuation_ready():
            return
            
        try:
            num_scenarios = int(self.scenarios_var.get())
            if num_scenarios < 100 or num_scenarios > 10000:
                messagebox.showerror("Invalid Input", "Number of scenarios must be between 100 and 10,000")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number of scenarios")
            return
        
        # Start simulation in a separate thread
        self.is_running = True
        self.run_button.config(state='disabled', text="Running...")
        self.progress_var.set(0)
        self.progress_label.config(text="Starting simulation...")
        
        # Run simulation in background thread
        thread = threading.Thread(target=self._run_monte_carlo, args=(num_scenarios,))
        thread.daemon = True
        thread.start()
        
    def _run_monte_carlo(self, num_scenarios):
        """Run the Monte Carlo simulation"""
        try:
            # Get current valuation model (already checked in _check_valuation_ready)
            valuation_model = self.controller._modelObj
            dcf_model = valuation_model._valuationObj
            
            # Generate parameter samples
            self.progress_label.config(text="Generating parameter samples...")
            self.progress_var.set(10)
            
            samples = self._generate_parameter_samples(num_scenarios)
            
            # Run simulations
            self.progress_label.config(text="Running simulations...")
            self.progress_var.set(20)
            
            results = []
            batch_size = max(1, num_scenarios // 100)  # Update progress every 1%
            
            for i in range(0, num_scenarios, batch_size):
                batch_end = min(i + batch_size, num_scenarios)
                batch_samples = samples[i:batch_end]
                
                # Run batch of simulations
                batch_results = self._run_batch_simulations(dcf_model, batch_samples)
                results.extend(batch_results)
                
                # Update progress
                progress = 20 + (i / num_scenarios) * 70
                self.progress_var.set(progress)
                self.progress_label.config(text=f"Running simulations... {len(results)}/{num_scenarios}")
            
            # Store results
            self.simulation_results = np.array(results)
            
            # Update UI
            self.progress_var.set(100)
            self.progress_label.config(text="Simulation completed!")
            
            # Update statistics and plot
            self._update_results()
            
        except Exception as e:
            self._simulation_error(f"Simulation failed: {str(e)}")
        finally:
            self.is_running = False
            self.run_button.config(state='normal', text="Run Monte Carlo Simulation")
    
    def _generate_parameter_samples(self, num_scenarios):
        """Generate random parameter samples for Monte Carlo simulation"""
        samples = []
        
        for _ in range(num_scenarios):
            sample = {}
            
            # Discount rate: centered at 0 ± range
            discount_range = float(self.parameters['discount_rate']['var'].get()) / 100
            discount_std = discount_range / 3  # Use 1/3 of range as std dev for normal distribution
            sample['discount_rate'] = np.random.normal(0, discount_std)
            # Clamp to 5 standard deviations in either direction
            sample['discount_rate'] = max(-5 * discount_std, min(5 * discount_std, sample['discount_rate']))
            
            # Perpetual growth rate: centered at 0 ± range
            perpetual_growth_range = float(self.parameters['perpetual_growth']['var'].get()) / 100
            perpetual_growth_std = perpetual_growth_range / 3
            sample['perpetual_growth'] = np.random.normal(0, perpetual_growth_std)
            # Clamp to 5 standard deviations in either direction
            sample['perpetual_growth'] = max(-5 * perpetual_growth_std, min(5 * perpetual_growth_std, sample['perpetual_growth']))
            
            # Prediction window growth rate: centered at 0 ± range
            prediction_growth_range = float(self.parameters['prediction_window_growth']['var'].get()) / 100
            prediction_growth_std = prediction_growth_range / 3
            sample['prediction_window_growth'] = np.random.normal(0, prediction_growth_std)
            # Clamp to 5 standard deviations in either direction
            sample['prediction_window_growth'] = max(-5 * prediction_growth_std, min(5 * prediction_growth_std, sample['prediction_window_growth']))
            
            # Profitability: centered at 0 ± range
            profit_range = float(self.parameters['profitability']['var'].get()) / 100
            profit_std = profit_range / 3
            sample['profitability'] = np.random.normal(0, profit_std)
            # Clamp to 5 standard deviations in either direction
            sample['profitability'] = max(-5 * profit_std, min(5 * profit_std, sample['profitability']))
            
            # CapEx variation: centered at 0 ± range
            capex_range = float(self.parameters['capex']['var'].get()) / 100
            capex_std = capex_range / 3
            sample['capex_multiplier'] = np.random.normal(0, capex_std)
            # Clamp to 5 standard deviations in either direction
            sample['capex_multiplier'] = max(-5 * capex_std, min(5 * capex_std, sample['capex_multiplier']))
            
            # Working capital variation: centered at 0 ± range
            wc_range = float(self.parameters['working_capital']['var'].get()) / 100
            wc_std = wc_range / 3
            sample['wc_multiplier'] = np.random.normal(0, wc_std)
            # Clamp to 5 standard deviations in either direction
            sample['wc_multiplier'] = max(-5 * wc_std, min(5 * wc_std, sample['wc_multiplier']))
            
            # Net borrowings variation: centered at 0 ± range
            borrow_range = float(self.parameters['net_borrowings']['var'].get()) / 100
            borrow_std = borrow_range / 3
            sample['borrowings_multiplier'] = np.random.normal(0, borrow_std)
            # Clamp to 5 standard deviations in either direction
            sample['borrowings_multiplier'] = max(-5 * borrow_std, min(5 * borrow_std, sample['borrowings_multiplier']))
            
            samples.append(sample)
        
        return samples
    
    def _run_batch_simulations(self, dcf_model, samples):
        """Run a batch of simulations with different parameters"""
        results = []
        
        for sample in samples:
            try:
                # Convert sample to parameter weights format
                # The sample now contains percentage changes (centered at 0), so we can use them directly
                parameter_weights = {}
                
                # Direct percentage changes (already centered at 0)
                if 'discount_rate' in sample:
                    parameter_weights['discount_rate'] = sample['discount_rate']
                
                if 'perpetual_growth' in sample:
                    parameter_weights['perpetual_growth'] = sample['perpetual_growth']
                
                if 'prediction_window_growth' in sample:
                    parameter_weights['prediction_window_growth'] = sample['prediction_window_growth']
                
                if 'profitability' in sample:
                    parameter_weights['profitability'] = sample['profitability']
                
                # For multipliers, the values are already percentage changes from 1.0
                if 'capex_multiplier' in sample:
                    parameter_weights['capex'] = sample['capex_multiplier']
                
                if 'wc_multiplier' in sample:
                    parameter_weights['nwc'] = sample['wc_multiplier']
                
                if 'borrowings_multiplier' in sample:
                    parameter_weights['net_borrowings'] = sample['borrowings_multiplier']
                
                # Run valuation with parameter weights
                fair_value, _ = dcf_model.calculateFairValue(5, parameter_weights, storeResults=False)
                
                if fair_value is not None and not np.isnan(fair_value):
                    results.append(float(fair_value))
                
            except Exception as e:
                # If simulation fails, skip this sample
                print(f"Simulation failed for sample: {e}")
                continue
        
        return results
    
    
    def _update_results(self):
        """Update the results display with simulation results"""
        if self.simulation_results is None or len(self.simulation_results) == 0:
            return
        
        # Calculate statistics
        mean_val = np.mean(self.simulation_results)
        median_val = np.median(self.simulation_results)
        std_val = np.std(self.simulation_results)
        min_val = np.min(self.simulation_results)
        max_val = np.max(self.simulation_results)
        p5_val = np.percentile(self.simulation_results, 5)
        p95_val = np.percentile(self.simulation_results, 95)
        
        # Update statistics labels
        self.stats_labels['Mean'].config(text=f"${mean_val:.2f}")
        self.stats_labels['Median'].config(text=f"${median_val:.2f}")
        self.stats_labels['Std'].config(text=f"${std_val:.2f}")
        self.stats_labels['Min'].config(text=f"${min_val:.2f}")
        self.stats_labels['Max'].config(text=f"${max_val:.2f}")
        self.stats_labels['P5'].config(text=f"${p5_val:.2f}")
        self.stats_labels['P95'].config(text=f"${p95_val:.2f}")
        
        # Update histogram
        self.ax.clear()
        self.ax.hist(self.simulation_results, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        self.ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_val:.2f}')
        self.ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: ${median_val:.2f}')
        self.ax.axvline(p5_val, color='orange', linestyle=':', linewidth=2, label=f'5th %ile: ${p5_val:.2f}')
        self.ax.axvline(p95_val, color='orange', linestyle=':', linewidth=2, label=f'95th %ile: ${p95_val:.2f}')
        
        # Check if bounds are broken and set x-axis limits only if necessary
        max_value = np.max(self.simulation_results)
        upper_bound = 3 * median_val
        if max_value > upper_bound:
            # Set x-axis limits from 0 to 3x the median value only if there are outliers
            self.ax.set_xlim(0, upper_bound)
        
        self.ax.set_title(f"Fair Value Distribution (Monte Carlo Simulation - {len(self.simulation_results)} scenarios)")
        self.ax.set_xlabel("Fair Value ($)")
        self.ax.set_ylabel("Frequency")
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
    
    def _simulation_error(self, message):
        """Handle simulation errors"""
        self.progress_label.config(text="Simulation failed")
        self.progress_var.set(0)
        messagebox.showerror("Simulation Error", message)
