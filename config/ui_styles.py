# config/ui_styles.py
"""CSS styles and theming for the application."""

def get_custom_css() -> str:
    """Return the complete CSS styling for the application."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .main { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        
        .ai-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .executive-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .executive-subtitle {
            font-size: 1.2rem;
            font-weight: 400;
            opacity: 0.9;
            margin-bottom: 0;
        }
        
        .thinking-process {
            background: linear-gradient(145deg, #f8f9ff, #e8ecff);
            border-left: 5px solid #4f46e5;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.1);
        }
        
        .thinking-step {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            border-left: 3px solid #10b981;
        }
        
        .calculation-detail {
            background: #f8fafc;
            padding: 0.75rem;
            border-radius: 4px;
            font-family: 'Monaco', monospace;
            font-size: 0.9rem;
            margin: 0.5rem 0;
            border: 1px solid #e2e8f0;
        }
        
        .result-summary-enhanced {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
        }
        
        .missing-info-prompt {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
        }
        
        .data-quality-alert {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            color: #92400e;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .step-reasoning {
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 6px;
        }
        
        .formula-breakdown {
            background: #f3f4f6;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Monaco', monospace;
            margin: 0.5rem 0;
            border: 1px solid #d1d5db;
        }
        
        .ai-response {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        
        .user-query {
            background: #ffffff;
            border: 2px solid #667eea;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .ai-insight {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            border: 1px solid #f0a068;
        }
        
        .calc-step {
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            border-left: 4px solid #3282b8;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .step-number {
            background: #3282b8;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 1rem;
        }
        
        .step-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #0f4c75;
            margin-bottom: 0.5rem;
        }
        
        .step-formula {
            background: #fff;
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid #dee2e6;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 1rem 0;
        }
        
        .result-highlight {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            box-shadow: 0 8px 32px rgba(40,167,69,0.3);
            margin: 2rem 0;
        }
        
        .connection-status {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            font-weight: 600;
        }
        
        .connected { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .disconnected { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .calculation-verified {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid #00b4db;
        }
        
        .summary-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
    </style>
    """
