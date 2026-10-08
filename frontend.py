import datetime as dt
import csv
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend import predict_sales, get_feature_importances

current_year = dt.datetime.today().year

last_export_data = []
last_inputs = {}
is_predicted_once = False

master = Tk()
master.title("Big Mart Sales Prediction Dashboard")
master.geometry("1350x850")
master.resizable(False, False)

Label(
    master,
    text="BIG MART SALES PREDICTION",
    bg="black",
    fg="white",
    font=("Arial", 16, "bold"),
    pady=10
).pack(fill="x")

main_container = Frame(master)
main_container.pack(fill="both", expand=True, padx=15, pady=15)

# Left Panel Inputs
left_panel = Frame(main_container, bd=2, relief="groove", padx=15, pady=15)
left_panel.pack(side=LEFT, fill="y", padx=(0, 10))

Label(left_panel, text="Enter Outlet & Item Details", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 10))

input_frame = Frame(left_panel)
input_frame.pack()

Label(input_frame, text="Item MRP (₹)", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=6)
e1 = Entry(input_frame, width=20, font=("Arial", 11))
e1.grid(row=0, column=1, padx=10)

Label(input_frame, text="Outlet Identifier", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=6)
clicked = StringVar(value="")
outlet_options = ["OUT010", "OUT013", "OUT017", "OUT018", "OUT019", "OUT027", "OUT035", "OUT045", "OUT046", "OUT049"]
e2 = OptionMenu(input_frame, clicked, *outlet_options)
e2.config(width=16, font=("Arial", 10))
e2.grid(row=1, column=1, padx=10)

Label(input_frame, text="Outlet Size", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=6)
clicked0 = StringVar(value="")
size_options = ["High", "Medium", "Small"]
e3 = OptionMenu(input_frame, clicked0, *size_options)
e3.config(width=16, font=("Arial", 10))
e3.grid(row=2, column=1, padx=10)

Label(input_frame, text="Outlet Type", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=6)
clicked1 = StringVar(value="")
type_options = ["Grocery Store", "Supermarket Type1", "Supermarket Type2", "Supermarket Type3"]
e4 = OptionMenu(input_frame, clicked1, *type_options)
e4.config(width=16, font=("Arial", 10))
e4.grid(row=3, column=1, padx=10)

Label(input_frame, text="Establishment Year", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=6)
e5 = Entry(input_frame, width=20, font=("Arial", 11))
e5.grid(row=4, column=1, padx=10)

# Slider Section
slider_frame = Frame(left_panel, bd=1, relief="solid", padx=10, pady=8)
slider_frame.pack(fill="x", pady=15)

Label(slider_frame, text="What-If: Price / Discount Slider", font=("Arial", 11, "bold"), fg="#0056b3").pack(anchor="w")
Label(slider_frame, text="Adjust MRP percentage (-75% to +75%):", font=("Arial", 9), fg="gray").pack(anchor="w", pady=(2, 5))

mrp_slider = Scale(slider_frame, from_=-75, to=75, orient=HORIZONTAL, resolution=1, font=("Arial", 10), command=lambda val: on_slider_change())
mrp_slider.set(0)
mrp_slider.pack(fill="x", padx=5)

adjusted_mrp_label = Label(slider_frame, text="Effective MRP: ₹0.00", font=("Arial", 10, "italic"), fg="#333")
adjusted_mrp_label.pack(anchor="w", pady=(5, 0))

button_frame = Frame(left_panel)
button_frame.pack(pady=5)

# Right Panel Results & Visuals
right_panel = Frame(main_container, bd=2, relief="groove", padx=10, pady=10)
right_panel.pack(side=RIGHT, fill="both", expand=True)

sales_result_label = Label(right_panel, text="Current Predicted Sales: ₹0.00", font=("Arial", 13, "bold"), fg="#0056b3")
sales_result_label.pack(pady=(0, 5))

viz_container = Frame(right_panel)
viz_container.pack(fill="both", expand=True)

graph_frame = Frame(viz_container)
graph_frame.pack(side=LEFT, fill="both", expand=True)

figure = plt.Figure(figsize=(4.8, 4.4), dpi=100)
ax = figure.add_subplot(111)
canvas = FigureCanvasTkAgg(figure, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

# Right Stacked Container (Table -> Export Buttons)
right_stack_frame = Frame(viz_container, padx=10)
right_stack_frame.pack(side=RIGHT, fill="y", padx=5)

# 1. Year-wise Breakdown Table
Label(right_stack_frame, text="Year-wise Breakdown", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
columns = ("Timeline", "Predicted Sales (₹)")
tree = ttk.Treeview(right_stack_frame, columns=columns, show="headings", height=5)
tree.heading("Timeline", text="Timeline")
tree.heading("Predicted Sales (₹)", text="Predicted Sales (₹)")
tree.column("Timeline", width=85, anchor="center")
tree.column("Predicted Sales (₹)", width=135, anchor="center")
tree.pack(fill="x", pady=(0, 4))

# 2. Export Reports Section (Immediately below the table)
export_section_frame = Frame(right_stack_frame, bd=1, relief="groove", padx=8, pady=5)
export_section_frame.pack(fill="x", pady=(2, 6))

Label(export_section_frame, text="Export Reports (Includes Summary Paragraph)", font=("Arial", 9, "bold"), fg="#333").pack(anchor="w", pady=(0, 3))

def export_to_csv():
    if not last_export_data:
        messagebox.showwarning("No Data", "Please generate predictions first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Timeline", "Predicted Sales (INR)", "Lower Bound (INR)", "Upper Bound (INR)"])
            writer.writerows(last_export_data)
            
            pred_values = [row[1] for row in last_export_data]
            total_sales = sum(pred_values)
            avg_sales = total_sales / len(pred_values)
            max_sales = max(pred_values)
            min_sales = min(pred_values)
            
            writer.writerow([])
            writer.writerow(["--- SIMPLE SUMMARY & OVERVIEW ---"])
            writer.writerow([
                f"Over the next 5 years, this item is projected to generate a total of about INR {total_sales:,.2f}, "
                f"with an average annual sales of INR {avg_sales:,.2f}. The highest sales are expected to reach INR {max_sales:,.2f}, "
                f"and the lowest projected sales will be around INR {min_sales:,.2f}."
            ])

        messagebox.showinfo("Success", "Report and Paragraph Summary exported to CSV successfully!")

def export_to_pdf():
    if not last_export_data:
        messagebox.showwarning("No Data", "Please generate predictions first.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#004080'), spaceBefore=6, spaceAfter=3)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333333'), leading=12, spaceBefore=2)
        
        story = [
            Paragraph("BIG MART SALES PREDICTION REPORT", ParagraphStyle('Title', fontSize=15, textColor=colors.HexColor('#003366'), alignment=1)),
            Paragraph(f"Generated on: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ParagraphStyle('Sub', fontSize=8, textColor=colors.gray, alignment=1, spaceAfter=8)),
            Paragraph("<b>5-Year Projections Table</b>", heading_style)
        ]
        
        table_data = [["Timeline", "Predicted Sales (₹)", "Lower Bound (₹)", "Upper Bound (₹)"]]
        for row in last_export_data:
            table_data.append([row[0], f"₹{row[1]:.2f}", f"₹{row[2]:.2f}", f"₹{row[3]:.2f}"])
            
        proj_table = Table(table_data, colWidths=[110, 130, 110, 130])
        proj_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004080')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc'))
        ]))
        story.append(proj_table)
        story.append(Spacer(1, 8))
        
        pred_values = [row[1] for row in last_export_data]
        total_sales = sum(pred_values)
        avg_sales = total_sales / len(pred_values)
        max_sales = max(pred_values)
        min_sales = min(pred_values)
        
        summary_paragraph = (
            f"<b>Simple Summary & Overview:</b> Over the next 5 years, this item is projected to generate a total "
            f"of about <b>₹{total_sales:,.2f}</b> in sales, averaging around <b>₹{avg_sales:,.2f}</b> each year. "
            f"Sales are expected to reach a peak of approximately <b>₹{max_sales:,.2f}</b>, with the lowest "
            f"projected sales dropping to around <b>₹{min_sales:,.2f}</b>."
        )
        
        story.append(Paragraph("<b>Data Summary</b>", heading_style))
        story.append(Paragraph(summary_paragraph, body_style))

        doc.build(story)
        messagebox.showinfo("Success", "PDF Report with Simple Summary successfully generated!")

btn_row_frame = Frame(export_section_frame)
btn_row_frame.pack(fill="x", pady=2)

Button(btn_row_frame, text="📥 Download CSV Report", command=export_to_csv, font=("Arial", 9, "bold"), bg="#28a745", fg="white", width=19, pady=2).pack(side=LEFT, padx=2)
Button(btn_row_frame, text="📄 Download PDF Report", command=export_to_pdf, font=("Arial", 9, "bold"), bg="#dc3545", fg="white", width=19, pady=2).pack(side=RIGHT, padx=2)

def show_feature_importance_window():
    feat_window = Toplevel(master)
    feat_window.title("Model Feature Importance Analysis")
    feat_window.geometry("550x420")
    feat_window.resizable(False, False)

    Label(feat_window, text="What Drives Model Predictions?", font=("Arial", 12, "bold"), pady=8).pack()

    fig_feat = plt.Figure(figsize=(5, 3.5), dpi=100)
    ax_feat = fig_feat.add_subplot(111)

    names, values = get_feature_importances()
    sorted_pairs = sorted(zip(names, values), key=lambda x: x[1])
    sorted_names, sorted_vals = zip(*sorted_pairs)

    ax_feat.barh(sorted_names, sorted_vals, color="#17a2b8")
    ax_feat.set_title("Feature Importance Ranking", fontsize=10, fontweight="bold")
    ax_feat.set_xlabel("Importance Scale", fontsize=9)
    ax_feat.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5])
    ax_feat.set_xticklabels(['1', '2', '3', '4', '5'])
    fig_feat.tight_layout()

    canvas_feat = FigureCanvasTkAgg(fig_feat, master=feat_window)
    canvas_feat.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

def run_prediction_logic(is_from_slider=False):
    global last_export_data, last_inputs, is_predicted_once
    try:
        if e1.get().strip() == "" or clicked.get() == "" or clicked0.get() == "" or clicked1.get() == "" or e5.get().strip() == "":
            if not is_from_slider:
                messagebox.showerror("Missing Input", "Please fill in all required fields.")
            return

        item_mrp = float(e1.get())
        establishment_year = int(e5.get())
        slider_val = float(mrp_slider.get())

        current_sales, future_predictions, lower_bounds, upper_bounds, effective_mrp = predict_sales(
            item_mrp, clicked.get(), clicked0.get(), clicked1.get(), establishment_year, slider_val
        )

        last_inputs = {
            "mrp": item_mrp, "outlet": clicked.get(), "size": clicked0.get(),
            "type": clicked1.get(), "year": establishment_year, "slider": slider_val,
            "effective_mrp": effective_mrp, "current_sales": current_sales
        }

        adjusted_mrp_label.config(text=f"Effective MRP: ₹{effective_mrp:.2f} ({slider_val:+.0f}%)")
        sales_result_label.config(text=f"Current Predicted Sales: ₹{current_sales:.2f}")

        year_labels = ["Current", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
        last_export_data = list(zip(year_labels, future_predictions, lower_bounds, upper_bounds))

        ax.clear()
        ax.plot(year_labels, future_predictions, marker="o", linewidth=2.2, color="#007BFF", label="Predicted Sales")
        ax.fill_between(year_labels, lower_bounds, upper_bounds, color="#007BFF", alpha=0.2, label="Confidence Interval")
        ax.set_title(f"5-Year Trend (MRP Slider: {slider_val:+.0f}%)", fontsize=10, fontweight="bold", pad=6)
        ax.set_xlabel("Timeline", fontsize=8)
        ax.set_ylabel("Sales (₹)", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left", fontsize=7)
        figure.tight_layout()
        canvas.draw()

        for row in tree.get_children():
            tree.delete(row)

        for label, val in zip(year_labels, future_predictions):
            tree.insert("", "end", values=(label, f"₹{val:.2f}"))

        is_predicted_once = True
    except ValueError:
        if not is_from_slider:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")

def show_prediction():
    run_prediction_logic(is_from_slider=False)

def on_slider_change():
    if is_predicted_once:
        run_prediction_logic(is_from_slider=True)

def clear_inputs():
    global last_export_data, last_inputs, is_predicted_once
    last_export_data, last_inputs, is_predicted_once = [], {}, False
    e1.delete(0, END)
    e5.delete(0, END)
    clicked.set("")
    clicked0.set("")
    clicked1.set("")
    mrp_slider.set(0)
    adjusted_mrp_label.config(text="Effective MRP: ₹0.00")
    sales_result_label.config(text="Current Predicted Sales: ₹0.00")
    ax.clear()
    canvas.draw()
    for row in tree.get_children(): tree.delete(row)

Button(button_frame, text="PREDICT SALES", command=show_prediction, font=("Arial", 11, "bold"), bg="#007BFF", fg="white", width=18, pady=4).grid(row=0, column=0, pady=3)
Button(button_frame, text="FEATURE IMPORTANCE", command=show_feature_importance_window, font=("Arial", 10, "bold"), bg="#17a2b8", fg="white", width=18, pady=4).grid(row=1, column=0, pady=3)
Button(button_frame, text="CLEAR", command=clear_inputs, font=("Arial", 10), width=18, pady=4).grid(row=2, column=0, pady=3)
Button(button_frame, text="EXIT", command=master.destroy, font=("Arial", 10), width=18, pady=4).grid(row=3, column=0, pady=3)

mainloop()