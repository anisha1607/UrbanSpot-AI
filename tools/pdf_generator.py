import os
import threading
import time
from fpdf import FPDF
from typing import Dict, Any, List
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt

class PDFGenerator:
    def __init__(self, output_dir: str = "data/outputs"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _write_image_with_timeout(self, fig, path, timeout=10):
        """Attempts to save a plotly figure as an image with direct Matplotlib fallback."""
        try:
            def target():
                try:
                    fig.write_image(path, engine="kaleido", scale=1)
                except: pass
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout)
            if not thread.is_alive() and os.path.exists(path):
                return True
        except: pass

        # FALLBACK: Matplotlib
        print(f"Kaleido failed or timed out for {path}. Using Matplotlib fallback...")
        try:
            return self._plot_matplotlib_fallback(fig, path)
        except Exception as e:
            print(f"Matplotlib fallback also failed: {e}")
            return False

    def _plot_matplotlib_fallback(self, fig, path):
        """Refined fallback that extracts data and labels from Plotly figure."""
        plt.figure(figsize=(10, 6))
        
        try:
            # Extract basic layout info
            title = fig.layout.title.text if fig.layout.title and hasattr(fig.layout.title, 'text') else "Analysis Chart"
            xlabel = fig.layout.xaxis.title.text if fig.layout.xaxis and fig.layout.xaxis.title and hasattr(fig.layout.xaxis.title, 'text') else ""
            ylabel = fig.layout.yaxis.title.text if fig.layout.yaxis and fig.layout.yaxis.title and hasattr(fig.layout.yaxis.title, 'text') else ""
            
            plt.title(title, fontsize=14, fontweight='bold', pad=20)
            if xlabel: plt.xlabel(xlabel, fontsize=11)
            if ylabel: plt.ylabel(ylabel, fontsize=11)
            
            for trace in fig.data:
                label = trace.name if trace.name else ""
                if trace.type == 'bar':
                    # Fix: Handle case where x might be categorical or numeric
                    plt.bar(trace.x, trace.y, label=label, alpha=0.8)
                elif trace.type == 'scatter':
                    plt.plot(trace.x, trace.y, marker='o', label=label, linewidth=2)
                elif trace.type == 'histogram':
                    plt.hist(trace.x, bins=30, label=label, alpha=0.7)
            
            # Improvement: Rotate labels and adjust size to prevent overlap
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.6, axis='y')
            
            if any(trace.name for trace in fig.data):
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                
            plt.tight_layout()
            plt.savefig(path, dpi=120, bbox_inches='tight')
            plt.close()
            return True
        except Exception as e:
            print(f"Internal fallback error: {e}")
            plt.close()
            return False

    def generate_report(self, result: Dict[str, Any], filename: str) -> str:
        """
        Generates a comprehensive PDF report including Recommendations, Critic feedback, and Visualizations.
        """
        start_time = time.time()
        filename = os.path.basename(filename)
        filepath = os.path.join(self.output_dir, filename).replace('\\', '/')
        
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(15, 20, 15)
        pdf.add_page()
        
        # --- HEADER ---
        pdf.set_fill_color(0, 51, 102) 
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("helvetica", "B", 24)
        pdf.set_y(12)
        pdf.cell(0, 15, "UrbanSpot-AI", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Comprehensive Business Location Report", align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_y(45)
        pdf.set_text_color(100, 100, 100)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 10, f"EXPORT DATE | {datetime.now().strftime('%B %d, %Y')}", align='R', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # --- RECOMMENDATION SECTION ---
        recs = result.get('recommendation', {})
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(240, 245, 255)
        pdf.rect(15, pdf.get_y(), 180, 25, 'F')
        
        pdf.set_font("helvetica", "B", 16)
        pdf.set_x(20)
        pdf.cell(0, 12, f"Target: {recs.get('best_location', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", "B", 12)
        pdf.set_x(20)
        score_val = recs.get('score', 0)
        pdf.cell(0, 8, f"Borough: {recs.get('borough', 'N/A')} | Opportunity Score: {min(100.0, score_val * 100):.1f}/100", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Reasonings
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, "Strategic Reasoning", new_x="LMARGIN", new_y="NEXT")
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("helvetica", "", 11)
        reasoning = recs.get('reasoning', [])
        for reason in (reasoning if reasoning else ["No specific reasoning provided."]):
            pdf.set_x(20)
            pdf.multi_cell(170, 7, f"- {str(reason)}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # --- CRITIC FEEDBACK SECTION ---
        critic = result.get('critic_feedback', {})
        if critic:
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 10, "AI Critic Review", new_x="LMARGIN", new_y="NEXT")
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(3)
            
            # Status
            pdf.set_font("helvetica", "B", 11)
            status = "APPROVED" if critic.get('approved') else "REFINEMENT SUGGESTED"
            pdf.set_text_color(0, 100, 0) if critic.get('approved') else pdf.set_text_color(150, 0, 0)
            pdf.cell(0, 7, f"Status: {status}", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)

            # Issues & Suggestions
            pdf.set_font("helvetica", "B", 11)
            pdf.cell(0, 7, "Key Considerations:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 10)
            all_feedback = critic.get('issues', []) + critic.get('suggestions', []) + critic.get('missing_considerations', [])
            for item in (all_feedback if all_feedback else ["No specific issues identified."]):
                pdf.set_x(20)
                pdf.multi_cell(170, 6, f"* {str(item)}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # Perspective
            if critic.get('alternative_perspective'):
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 7, "Alternative Perspective:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "I", 10)
                pdf.set_x(20)
                pdf.multi_cell(170, 6, critic['alternative_perspective'], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)

        # --- VISUALIZATIONS ---
        if 'artifacts' in result and 'figures' in result['artifacts']:
            figs = result['artifacts']['figures']
            if figs:
                pdf.add_page()
                pdf.set_font("helvetica", "B", 16)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 15, "Market Visualizations", align='C', new_x="LMARGIN", new_y="NEXT")
                pdf.ln(5)
                for i, fig in enumerate(figs):
                    img_path = os.path.join(self.output_dir, f"temp_chart_{i}.png")
                    if self._write_image_with_timeout(fig, img_path):
                        # Calculate available width (210 - 30 margin = 180)
                        pdf.image(img_path, x=15, w=180)
                        pdf.ln(10)
                        try: os.remove(img_path)
                        except: pass
                    if i < len(figs) - 1 and pdf.get_y() > 180:
                        pdf.add_page()

        # Footer
        pdf.set_y(-15)
        pdf.set_font("helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"UrbanSpot-AI Analysis Dashboard | Tool Version 2.1", align='C')

        pdf.output(filepath)
        print(f"PDF successfully saved at {filepath}")
        return filepath

def generate_pdf_report(result: Dict[str, Any], filename: str, output_dir: str = "data/outputs") -> str:
    generator = PDFGenerator(output_dir)
    return generator.generate_report(result, filename)
