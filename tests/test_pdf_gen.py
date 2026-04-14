import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables for kaleido if needed, or handle plotly
import plotly.graph_objects as go
from tools.pdf_generator import generate_pdf_report

def test_pdf_generation():
    print("Testing PDF Generation...")
    
    # Mock data
    result = {
        'recommendation': {
            'best_location': 'Test Neighborhood',
            'borough': 'Brooklyn',
            'score': 85.5,
            'reasoning': [
                'High foot traffic from local residents.',
                'Low competition in the immediate vicinity.',
                'Affordable commercial rent prices.'
            ]
        },
        'critic_feedback': {
            'approved': False,
            'issues': ['Potential saturation in the 5-block radius.'],
            'suggestions': ['Consider a smaller footprint to reduce rent.'],
            'alternative_perspective': 'Long Island City might offer better tax incentives.'
        },
        'iterations': 2,
        'artifacts': {
            'figures': [
                go.Figure(
                    data=[go.Bar(x=['Manhattan - 10001', 'Brooklyn - 11201', 'Queens - 11101'], y=[10, 20, 15], name='Test Bar')],
                    layout=go.Layout(
                        title=go.layout.Title(text='Market Comparison'),
                        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text='Neighborhood')),
                        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text='Score'))
                    )
                )
            ]
        }
    }
    
    # Ensure output dir exists
    os.makedirs("data/outputs", exist_ok=True)
    
    try:
        pdf_path = generate_pdf_report(result, "test_report.pdf", "data/outputs")
        print(f"Success! PDF generated at: {pdf_path}")
        if os.path.exists(pdf_path):
            print("File exists verification: PASS")
        else:
            print("File exists verification: FAIL")
    except Exception as e:
        print(f"PDF Generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
