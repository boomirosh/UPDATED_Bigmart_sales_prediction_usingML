import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend import predict_sales, get_feature_importances

st.set_page_config(page_title="Big Mart Sales Prediction Dashboard", page_icon="🛒", layout="wide")

current_year = dt.datetime.today().year

st.markdown("<h1 style='text-align: center; color: #003366;'>BIG MART SALES PREDICTION DASHBOARD</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 Single Item Prediction & What-If", "📂 Batch CSV Prediction"])

with tab1:
    with st.sidebar:
        st.header("Enter Outlet & Item Details")
        item_mrp = st.number_input("Item MRP (₹)", min_value=0.0, value=150.0, step=10.0)
        outlet_identifier = st.selectbox("Outlet Identifier", ["OUT010", "OUT013", "OUT017", "OUT018", "OUT019", "OUT027", "OUT035", "OUT045", "OUT046", "OUT049"])
        outlet_size = st.selectbox("Outlet Size", ["High", "Medium", "Small"])
        outlet_type = st.selectbox("Outlet Type", ["Grocery Store", "Supermarket Type1", "Supermarket Type2", "Supermarket Type3"])
        establishment_year = st.number_input("Establishment Year", min_value=1900, max_value=current_year, value=1999, step=1)
        
        st.write("---")
        st.subheader("What-If: Price / Discount")
        slider_val = st.slider("Adjust MRP percentage", min_value=-75, max_value=75, value=0, step=1)
        predict_btn = st.button("PREDICT SALES", type="primary", use_container_width=True)

    if predict_btn or 'calculated' in st.session_state:
        if predict_btn:
            current_sales, future_predictions, lower_bounds, upper_bounds, effective_mrp = predict_sales(
                item_mrp, outlet_identifier, outlet_size, outlet_type, int(establishment_year), float(slider_val)
            )
            st.session_state['data'] = (current_sales, future_predictions, lower_bounds, upper_bounds, effective_mrp, slider_val)
            st.session_state['calculated'] = True

        current_sales, future_predictions, lower_bounds, upper_bounds, effective_mrp, slider_val = st.session_state['data']

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="Effective MRP (After Slider)", value=f"₹{effective_mrp:.2f}", delta=f"{slider_val:+.0f}%")
        with col_m2:
            st.metric(label="Current Predicted Sales", value=f"₹{current_sales:.2f}")

        st.write("---")
        col_graph, col_table = st.columns([3, 2])
        year_labels = ["Current", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]

        with col_graph:
            st.subheader("5-Year Sales Trend & Confidence Bounds")
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(year_labels, future_predictions, marker="o", linewidth=2.2, color="#007BFF", label="Predicted Sales")
            ax.fill_between(year_labels, lower_bounds, upper_bounds, color="#007BFF", alpha=0.2, label="Confidence Interval")
            ax.set_xlabel("Timeline")
            ax.set_ylabel("Sales (₹)")
            ax.grid(True, linestyle="--", alpha=0.5)
            ax.legend(loc="upper left", fontsize=8)
            fig.tight_layout()
            st.pyplot(fig)

        with col_table:
            st.subheader("Year-wise Breakdown")
            df_breakdown = pd.DataFrame({"Timeline": year_labels, "Predicted Sales (₹)": [f"₹{p:.2f}" for p in future_predictions]})
            st.dataframe(df_breakdown, hide_index=True, use_container_width=True)

            total_sales = sum(future_predictions)
            avg_sales = total_sales / len(future_predictions)
            max_sales = max(future_predictions)
            min_sales = min(future_predictions)
            peak_year = year_labels[future_predictions.index(max_sales)]

            st.subheader("Export Reports (Includes Summary Paragraph)")
            col_dl1, col_dl2 = st.columns(2)

            with col_dl1:
                csv_buffer = io.StringIO()
                pd.DataFrame({
                    "Timeline": year_labels,
                    "Predicted Sales (INR)": future_predictions,
                    "Lower Bound (INR)": lower_bounds,
                    "Upper Bound (INR)": upper_bounds
                }).to_csv(csv_buffer, index=False)
                
                csv_buffer.write("\n---,SIMPLE SUMMARY & OVERVIEW,---\n")
                csv_buffer.write(
                    f"\"Over the next 5 years, this item is projected to bring in a total of about INR {total_sales:,.2f} in sales, "
                    f"averaging around INR {avg_sales:,.2f} each year. Sales are expected to reach their highest point during {peak_year} "
                    f"with approximately INR {max_sales:,.2f}, while the lowest projected sales point is around INR {min_sales:,.2f}.\"\n"
                )
                
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv_buffer.getvalue().encode('utf-8'),
                    file_name="bigmart_sales_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_dl2:
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
                story = []
                styles = getSampleStyleSheet()

                title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=4, alignment=1)
                subtitle_style = ParagraphStyle('ReportSubtitle', parent=styles['Normal'], fontSize=9, textColor=colors.gray, spaceAfter=10, alignment=1)
                heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#004080'), spaceBefore=8, spaceAfter=4)
                body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#333333'), leading=12, spaceBefore=2)

                story.append(Paragraph("BIG MART SALES PREDICTION REPORT", title_style))
                story.append(Paragraph(f"Generated on: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))

                story.append(Paragraph("<b>5-Year Sales Trajectory Breakdown</b>", heading_style))
                table_data = [["Timeline", "Predicted Sales (₹)", "Lower Bound (₹)", "Upper Bound (₹)"]]
                for lbl, pred, lb, ub in zip(year_labels, future_predictions, lower_bounds, upper_bounds):
                    table_data.append([lbl, f"₹{pred:.2f}", f"₹{lb:.2f}", f"₹{ub:.2f}"])

                projection_table = Table(table_data, colWidths=[100, 110, 100, 110])
                projection_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004080')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,-1), 8),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc'))
                ]))
                story.append(projection_table)
                story.append(Spacer(1, 10))

                pdf_summary_text = (
                    f"<b>Simple Summary & Overview:</b> Over the next 5 years, this item is projected to bring in a total "
                    f"of about <b>₹{total_sales:,.2f}</b> in sales, averaging around <b>₹{avg_sales:,.2f}</b> each year. "
                    f"Sales are expected to reach their highest point during <b>{peak_year}</b> with approximately <b>₹{max_sales:,.2f}</b>, "
                    f"while the lowest projected sales point is around <b>₹{min_sales:,.2f}</b>."
                )
                story.append(Paragraph("<b>Data Summary</b>", heading_style))
                story.append(Paragraph(pdf_summary_text, body_style))

                doc.build(story)
                pdf_data = buffer.getvalue()
                buffer.close()

                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name="bigmart_sales_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    else:
        st.info("👈 Fill out the details in the sidebar and click **PREDICT SALES** to see your forecast.")

with tab2:
    st.subheader("Batch Sales Prediction via CSV Upload")
    st.write("Upload a CSV file containing columns for Item MRP, Outlet Identifier, Outlet Size, Outlet Type, and Establishment Year.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        
        # Clean column names (strip whitespace and convert to lowercase for flexible matching)
        batch_df.columns = batch_df.columns.str.strip()
        col_map = {col.lower(): col for col in batch_df.columns}
        
        st.write("Uploaded Data Preview:", batch_df.head())
        
        if st.button("Run Batch Prediction"):
            results = []
            for _, row in batch_df.iterrows():
                # Flexible column name lookup
                mrp_key = next((col_map[c] for c in col_map if 'mrp' in c), None)
                id_key = next((col_map[c] for c in col_map if 'identifier' in c or 'outlet_id' in c or c == 'outlet'), None)
                size_key = next((col_map[c] for c in col_map if 'size' in c), None)
                type_key = next((col_map[c] for c in col_map if 'type' in c), None)
                year_key = next((col_map[c] for c in col_map if 'year' in c or 'establishment' in c), None)
                
                mrp = float(row[mrp_key]) if mrp_key and pd.notna(row[mrp_key]) else 150.0
                out_id = str(row[id_key]) if id_key and pd.notna(row[id_key]) else "OUT013"
                out_size = str(row[size_key]) if size_key and pd.notna(row[size_key]) else "Medium"
                out_type = str(row[type_key]) if type_key and pd.notna(row[type_key]) else "Supermarket Type1"
                est_yr = int(row[year_key]) if year_key and pd.notna(row[year_key]) else 1999
                
                curr, _, _, _, eff = predict_sales(mrp, out_id, out_size, out_type, est_yr, 0.0)
                results.append({
                    "Item_MRP": mrp, 
                    "Outlet": out_id, 
                    "Outlet_Type": out_type, 
                    "Effective_MRP": eff, 
                    "Predicted_Sales": curr
                })
            
            res_df = pd.DataFrame(results)
            st.success("Batch Prediction Complete!")
            st.dataframe(res_df, use_container_width=True)

st.write("---")
with st.expander("📊 View Model Feature Importance Analysis"):
    names, values = get_feature_importances()
    fig_feat, ax_feat = plt.subplots(figsize=(8, 3.5))
    sorted_pairs = sorted(zip(names, values), key=lambda x: x[1])
    sorted_names, sorted_vals = zip(*sorted_pairs)
    ax_feat.barh(sorted_names, sorted_vals, color="#17a2b8")
    ax_feat.set_title("Feature Importance Ranking", fontsize=11, fontweight="bold")
    ax_feat.set_xlabel("Importance Scale", fontsize=9)
    ax_feat.set_xticks([0.1, 0.2, 0.3, 0.4, 0.5])
    ax_feat.set_xticklabels(['1', '2', '3', '4', '5'])
    fig_feat.tight_layout()
    st.pyplot(fig_feat)