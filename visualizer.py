import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set(style="darkgrid", context="talk", palette="colorblind")

class Visualizer:
    def __init__(self, current_data, optimized_data):
        self.current_data = current_data
        self.optimized_data = optimized_data

    def plot_wasted_beds_comparison(self, plot_path):
        plt.figure(figsize=(14, 14))
        plt.plot(self.current_data['Date'], self.current_data['Wasted Beds'], label='Current Model Wasted Beds', marker='o', linestyle='-', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[0])
        plt.plot(self.optimized_data['Date'], self.optimized_data['Wasted Beds'], label='Optimized Model Wasted Beds', marker='x', linestyle='--', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[2])
        plt.xlabel('Date')
        plt.ylabel('Wasted Beds')
        plt.title('Comparison of Wasted Beds: Current Model vs Optimized Model')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)
        
        # Improve date label readability
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))  # Show fewer date labels

        plt.savefig(plot_path)
        plt.show()

    def plot_wasted_potential_comparison(self, plot_path):
        plt.figure(figsize=(14, 14))
        plt.plot(self.current_data['Date'], self.current_data['Wasted Potential'], label='Current Model Wasted Potential', marker='o', linestyle='-', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[1])
        plt.plot(self.optimized_data['Date'], self.optimized_data['Wasted Potential'], label='Optimized Model Wasted Potential', marker='x', linestyle='--', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[3])
        plt.xlabel('Date')
        plt.ylabel('Wasted Potential')
        plt.title('Comparison of Wasted Potential: Current Model vs Optimized Model')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)

        # Improve date label readability
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))  # Show fewer date labels

        plt.savefig(plot_path)
        plt.show()

    def plot_daily_efficiency_comparison(self, plot_path):
        plt.figure(figsize=(14, 14))
        plt.plot(self.current_data['Date'], self.current_data['Daily Efficiency'], label='Current Model Daily Efficiency', marker='o', linestyle='-', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[0])
        plt.plot(self.optimized_data['Date'], self.optimized_data['Daily Efficiency'], label='Optimized Model Daily Efficiency', marker='x', linestyle='--', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[2])
        plt.xlabel('Date')
        plt.ylabel('Daily Efficiency')
        plt.title('Comparison of Daily Efficiency: Current Model vs Optimized Model')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)

        # Improve date label readability
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))  # Show fewer date labels

        plt.savefig(plot_path)
        plt.show()

    def plot_cumulative_efficiency_comparison(self, plot_path):
        plt.figure(figsize=(14, 14))
        plt.plot(self.current_data['Date'], self.current_data['Cumulative Efficiency'], label='Current Model Cumulative Efficiency', marker='o', linestyle='-', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[0])
        plt.plot(self.optimized_data['Date'], self.optimized_data['Cumulative Efficiency'], label='Optimized Model Cumulative Efficiency', marker='x', linestyle='--', linewidth=1, markersize=4, color=sns.color_palette("colorblind")[2])
        plt.xlabel('Date')
        plt.ylabel('Cumulative Efficiency')
        plt.title('Comparison of Cumulative Efficiency: Current Model vs Optimized Model')
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.grid(True)

        # Improve date label readability
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))  # Show fewer date labels

        plt.savefig(plot_path)
        plt.show()

# Usage
if __name__ == "__main__":
    current_df = pd.read_csv('output/current_model_data.csv')
    optimized_df = pd.read_csv('output/optimized_model_data.csv')

    visualizer = Visualizer(current_df, optimized_df)

    # Generate the plots
    visualizer.plot_wasted_beds_comparison('output/wasted_beds_comparison.png')
    visualizer.plot_wasted_potential_comparison('output/wasted_potential_comparison.png')
    visualizer.plot_daily_efficiency_comparison('output/daily_efficiency_comparison.png')
    visualizer.plot_cumulative_efficiency_comparison('output/cumulative_efficiency_comparison.png')
