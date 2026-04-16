"""
Flask Backend Server for UrbanSpot AI
Fixed version with proper paths and email integration
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.orchestrator import run_analysis
from tools.email_service import send_analysis_email
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Store analysis results temporarily
analysis_cache = {}


@app.route('/')
def index():
    """Serve the main HTML page"""
    html_path = Path(__file__).parent / 'templates' / 'index.html'
    if html_path.exists():
        with open(html_path, 'r') as f:
            return f.read()
    return "Frontend not found. Please ensure index.html is in app/templates/"


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Run business location analysis"""
    try:
        data = request.json
        
        # Build user input
        user_input = {
            'business_type': data.get('business_type', 'coffee_shop'),
            'borough_filter': data.get('borough_filter'),
            'weight_demand': data.get('weights', {}).get('demand', 0.20),
            'weight_foot_traffic': data.get('weights', {}).get('foot_traffic', 0.20),
            'weight_income': data.get('weights', {}).get('income', 0.20),
            'weight_competition': data.get('weights', {}).get('competition', 0.20),
            'weight_rent': data.get('weights', {}).get('rent', 0.20)
        }
        
        print(f"\n{'='*50}")
        print("RUNNING ANALYSIS")
        print(f"{'='*50}")
        print(f"Business Type: {user_input['business_type']}")
        print(f"Boroughs: {user_input['borough_filter']}")
        print(f"Weights: {user_input['weight_demand']}, {user_input['weight_foot_traffic']}, {user_input['weight_income']}, {user_input['weight_competition']}, {user_input['weight_rent']}")
        
        # Run analysis
        result = run_analysis(user_input)
        
        # Cache result
        analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_cache[analysis_id] = result
        
        print(f"\n✅ Analysis Complete - ID: {analysis_id}")
        
        # Extract data
        recommendation = result.get('recommendation', {})
        artifacts = result.get('artifacts', {})
        critic_feedback = result.get('critic_feedback', {})
        
        # Process charts
        charts = []
        if 'figures' in artifacts:
            for fig in artifacts['figures']:
                try:
                    charts.append(fig.to_json())
                except:
                    charts.append(json.dumps(fig) if not isinstance(fig, str) else fig)
        
        # Return structured response
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'recommendation': {
                'best_location': recommendation.get('best_location', 'N/A'),
                'borough': recommendation.get('borough', 'N/A'),
                'score': recommendation.get('score', 0),
                'confidence': recommendation.get('confidence', 'medium'),
                'reasoning': recommendation.get('reasoning', []),
                'trade_offs': recommendation.get('trade_offs', []),
                'top_alternatives': recommendation.get('top_alternatives', []),
                'key_insights': recommendation.get('key_insights', '')
            },
            'explanation': result.get('explanation', 'No explanation available'),
            'critic_feedback': {
                'approved': critic_feedback.get('approved', False),
                'issues': critic_feedback.get('issues', []),
                'suggestions': critic_feedback.get('suggestions', []),
                'missing_considerations': critic_feedback.get('missing_considerations', []),
                'alternative_perspective': critic_feedback.get('alternative_perspective', '')
            },
            'iterations': result.get('iterations', 1),
            'charts': charts,
            'artifacts': {
                'csv_path': str(artifacts.get('csv', '')),
                'report_path': str(artifacts.get('report', ''))
            }
        })
        
    except Exception as e:
        print(f"\n❌ Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/email-report', methods=['POST'])
def email_report():
    """Email analysis report"""
    try:
        data = request.json
        analysis_id = data.get('analysis_id')
        email = data.get('email')
        include_charts = data.get('include_charts', True)
        
        if analysis_id not in analysis_cache:
            return jsonify({
                'success': False,
                'error': 'Analysis not found'
            }), 404
        
        result = analysis_cache[analysis_id]
        
        print(f"\n📧 Sending email to: {email}")
        
        # Send email
        success = send_analysis_email(
            to_email=email,
            result=result,
            include_charts=include_charts
        )
        
        if success:
            print(f"✅ Email sent successfully")
            return jsonify({
                'success': True,
                'message': f'Report sent to {email}'
            })
        else:
            print(f"❌ Email failed to send")
            return jsonify({
                'success': False,
                'error': 'Failed to send email. Please check SMTP settings in .env file.'
            }), 500
            
    except Exception as e:
        print(f"\n❌ Email Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Email error: {str(e)}'
        }), 500


@app.route('/api/download-report/<analysis_id>')
def download_report(analysis_id):
    """Download analysis report as CSV"""
    try:
        if analysis_id not in analysis_cache:
            return jsonify({'error': 'Analysis not found'}), 404
        
        result = analysis_cache[analysis_id]
        artifacts = result.get('artifacts', {})
        
        # Get CSV path from artifacts
        csv_path = artifacts.get('csv')
        
        if not csv_path:
            return jsonify({'error': 'CSV file not generated'}), 404
        
        # Convert to Path object
        csv_file = Path(csv_path)
        
        # Check if file exists
        if not csv_file.exists():
            # Try alternative paths
            possible_paths = [
                csv_file,
                Path(project_root) / csv_path,
                Path(project_root) / 'data' / 'outputs' / 'neighborhood_scores.csv',
                Path.cwd() / 'data' / 'outputs' / 'neighborhood_scores.csv'
            ]
            
            for path in possible_paths:
                if path.exists():
                    csv_file = path
                    break
            else:
                return jsonify({
                    'error': f'CSV file not found. Searched paths: {[str(p) for p in possible_paths]}'
                }), 404
        
        print(f"📥 Downloading CSV from: {csv_file}")
        
        return send_file(
            str(csv_file),
            as_attachment=True,
            download_name=f'urbanspot_analysis_{analysis_id}.csv',
            mimetype='text/csv'
        )
            
    except Exception as e:
        print(f"❌ Download error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cached_analyses': len(analysis_cache),
        'project_root': str(project_root)
    })


if __name__ == '__main__':
    print(f"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           🏙️  UrbanSpot AI Server                    ║
    ║                                                       ║
    ║  Multi-Agent NYC Business Location Intelligence      ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    
    🚀 Server starting on http://localhost:5000
    📊 Open your browser to access the web interface
    📁 Project root: {project_root}
    
    """)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )