from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mongoengine import MongoEngine
from loguru import logger
import os
from datetime import datetime, timedelta

# Import configuration
import config

# Import reporting modules
from reporting.report_generator import ReportGenerator
from reporting.visualizations import Visualizer

class Dashboard:
    """Dashboard class for creating and serving the web dashboard
    
    This class handles the creation and serving of the web-based dashboard
    for visualizing patient progress and treatment data.
    """
    
    def __init__(self, db):
        """Initialize the Dashboard
        
        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # Initialize report generator and visualizer
        self.report_generator = ReportGenerator(db)
        self.visualizer = Visualizer(db)
        
        # Register routes
        self._register_routes()
        
        logger.info("Dashboard initialized")
    
    def _register_routes(self):
        """Register Flask routes"""
        # Home route
        @self.app.route('/')
        def home():
            # Get all patients
            patients = list(self.db.patients.find())
            return render_template('index.html', patients=patients)
        
        # Patient dashboard route
        @self.app.route('/patient/<patient_id>')
        def patient_dashboard(patient_id):
            # Get patient data
            patient = self.db.patients.find_one({"_id": patient_id})
            if not patient:
                flash("Patient not found", "error")
                return redirect(url_for('home'))
            
            # Get recent sessions
            recent_sessions = list(self.db.sessions.find({
                "patient_id": patient_id
            }).sort("start_time", -1).limit(5))
            
            # Get recent reports
            recent_reports = list(self.db.reports.find({
                "patient_id": patient_id
            }).sort("creation_date", -1).limit(3))
            
            # Generate visualizations
            mood_chart = self.visualizer.generate_mood_trend(patient_id)
            emotion_chart = self.visualizer.generate_emotion_distribution(patient_id)
            engagement_chart = self.visualizer.generate_engagement_metrics(patient_id)
            progress_chart = self.visualizer.generate_treatment_progress(patient_id)
            
            # Get treatment stage and condition severity from latest report
            treatment_stage = "early_stage"
            condition_severity = "moderate"
            if recent_reports:
                content = recent_reports[0].get("content", {})
                treatment_stage = content.get("treatment_stage", treatment_stage)
                condition_severity = content.get("condition_severity", condition_severity)
            
            # Format treatment stage for display
            treatment_stage_display = treatment_stage.replace("_", " ").title()
            
            # Format condition severity for display
            condition_severity_display = condition_severity.replace("_", " ").title()
            
            return render_template(
                'patient_dashboard.html',
                patient=patient,
                recent_sessions=recent_sessions,
                recent_reports=recent_reports,
                mood_chart=mood_chart,
                emotion_chart=emotion_chart,
                engagement_chart=engagement_chart,
                progress_chart=progress_chart,
                treatment_stage=treatment_stage_display,
                condition_severity=condition_severity_display
            )
        
        # Generate report route
        @self.app.route('/patient/<patient_id>/generate_report', methods=['POST'])
        def generate_report(patient_id):
            report_type = request.form.get('report_type', 'progress')
            
            if report_type == 'progress':
                report = self.report_generator.generate_progress_report(patient_id)
            elif report_type == 'assessment':
                report = self.report_generator.generate_assessment_report(patient_id)
            else:
                flash("Invalid report type", "error")
                return redirect(url_for('patient_dashboard', patient_id=patient_id))
            
            if report:
                flash(f"{report_type.title()} report generated successfully", "success")
            else:
                flash("Error generating report", "error")
            
            return redirect(url_for('patient_dashboard', patient_id=patient_id))
        
        # View report route
        @self.app.route('/report/<report_id>')
        def view_report(report_id):
            # Get report data
            report = self.db.reports.find_one({"_id": report_id})
            if not report:
                flash("Report not found", "error")
                return redirect(url_for('home'))
            
            # Get patient data
            patient = self.db.patients.find_one({"_id": report["patient_id"]})
            
            return render_template('report.html', report=report, patient=patient)
        
        # Sessions history route
        @self.app.route('/patient/<patient_id>/sessions')
        def session_history(patient_id):
            # Get patient data
            patient = self.db.patients.find_one({"_id": patient_id})
            if not patient:
                flash("Patient not found", "error")
                return redirect(url_for('home'))
            
            # Get all sessions
            sessions = list(self.db.sessions.find({
                "patient_id": patient_id
            }).sort("start_time", -1))
            
            return render_template('sessions.html', patient=patient, sessions=sessions)
        
        # View session route
        @self.app.route('/session/<session_id>')
        def view_session(session_id):
            # Get session data
            session = self.db.sessions.find_one({"_id": session_id})
            if not session:
                flash("Session not found", "error")
                return redirect(url_for('home'))
            
            # Get patient data
            patient = self.db.patients.find_one({"_id": session["patient_id"]})
            
            return render_template('session_detail.html', session=session, patient=patient)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard web server
        
        Args:
            host (str): Host to run the server on
            port (int): Port to run the server on
            debug (bool): Whether to run in debug mode
        """
        # Create necessary directories
        os.makedirs('dashboard/static/images', exist_ok=True)
        os.makedirs('dashboard/templates', exist_ok=True)
        
        # Create template files if they don't exist
        self._create_templates()
        
        # Run the Flask app
        logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def _create_templates(self):
        """Create HTML templates for the dashboard"""
        # Create base template
        base_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block title %}AMIRA Dashboard{% endblock %}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                }
                .navbar {
                    background-color: #6c5ce7;
                }
                .navbar-brand {
                    font-weight: bold;
                    color: white;
                }
                .card {
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                .card-header {
                    background-color: #6c5ce7;
                    color: white;
                    font-weight: bold;
                    border-radius: 10px 10px 0 0 !important;
                }
                .btn-primary {
                    background-color: #6c5ce7;
                    border-color: #6c5ce7;
                }
                .btn-primary:hover {
                    background-color: #5b4bc4;
                    border-color: #5b4bc4;
                }
                .alert {
                    border-radius: 10px;
                }
                .status-badge {
                    font-size: 0.9rem;
                    padding: 0.5rem 0.75rem;
                    border-radius: 20px;
                }
                .status-improving {
                    background-color: #2ecc71;
                    color: white;
                }
                .status-stable {
                    background-color: #3498db;
                    color: white;
                }
                .status-early-stage {
                    background-color: #f39c12;
                    color: white;
                }
                .status-progressing {
                    background-color: #9b59b6;
                    color: white;
                }
                .status-worsening {
                    background-color: #e74c3c;
                    color: white;
                }
                .status-maintenance {
                    background-color: #1abc9c;
                    color: white;
                }
                .severity-mild {
                    background-color: #2ecc71;
                    color: white;
                }
                .severity-moderate {
                    background-color: #f39c12;
                    color: white;
                }
                .severity-severe {
                    background-color: #e74c3c;
                    color: white;
                }
                .severity-in-remission {
                    background-color: #3498db;
                    color: white;
                }
            </style>
            {% block head %}{% endblock %}
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark mb-4">
                <div class="container">
                    <a class="navbar-brand" href="/">AMIRA Dashboard</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <a class="nav-link" href="/">Home</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>

            <div class="container">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category if category != 'error' else 'danger' }} alert-dismissible fade show">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}

                {% block content %}{% endblock %}
            </div>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
            {% block scripts %}{% endblock %}
        </body>
        </html>
        """
        
        # Create index template
        index_template = """
        {% extends "base.html" %}

        {% block title %}AMIRA - Patient List{% endblock %}

        {% block content %}
        <div class="row mb-4">
            <div class="col">
                <h1>Patient List</h1>
            </div>
        </div>

        <div class="row">
            <div class="col">
                <div class="card">
                    <div class="card-header">Patients</div>
                    <div class="card-body">
                        {% if patients %}
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Condition</th>
                                            <th>Registration Date</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for patient in patients %}
                                            <tr>
                                                <td>{{ patient.name }}</td>
                                                <td>
                                                    {% if patient.condition == "depression" %}
                                                        Depression
                                                    {% elif patient.condition == "bipolar" %}
                                                        Bipolar Disorder
                                                    {% elif patient.condition == "ocd" %}
                                                        Obsessive-Compulsive Disorder
                                                    {% else %}
                                                        {{ patient.condition|title }}
                                                    {% endif %}
                                                </td>
                                                <td>{{ patient.registration_date.strftime('%Y-%m-%d') }}</td>
                                                <td>
                                                    <a href="{{ url_for('patient_dashboard', patient_id=patient._id) }}" class="btn btn-primary btn-sm">View Dashboard</a>
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-center">No patients found.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """
        
        # Create patient dashboard template
        patient_dashboard_template = """
        {% extends "base.html" %}

        {% block title %}{{ patient.name }}'s Dashboard{% endblock %}

        {% block content %}
        <div class="row mb-4">
            <div class="col-md-8">
                <h1>{{ patient.name }}'s Dashboard</h1>
                <p>
                    <span class="badge bg-secondary">
                        {% if patient.condition == "depression" %}
                            Depression
                        {% elif patient.condition == "bipolar" %}
                            Bipolar Disorder
                        {% elif patient.condition == "ocd" %}
                            Obsessive-Compulsive Disorder
                        {% else %}
                            {{ patient.condition|title }}
                        {% endif %}
                    </span>
                    <span class="badge status-badge status-{{ treatment_stage|lower|replace(' ', '-') }}">{{ treatment_stage }}</span>
                    <span class="badge status-badge severity-{{ condition_severity|lower|replace(' ', '-') }}">{{ condition_severity }}</span>
                </p>
            </div>
            <div class="col-md-4 text-end">
                <form action="{{ url_for('generate_report', patient_id=patient._id) }}" method="post" class="mb-2">
                    <input type="hidden" name="report_type" value="progress">
                    <button type="submit" class="btn btn-primary">Generate Progress Report</button>
                </form>
                <form action="{{ url_for('generate_report', patient_id=patient._id) }}" method="post">
                    <input type="hidden" name="report_type" value="assessment">
                    <button type="submit" class="btn btn-outline-primary">Generate Assessment Report</button>
                </form>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Mood Trend</div>
                    <div class="card-body text-center">
                        <img src="/static/images/mood_trend_{{ patient._id }}.png" class="img-fluid" alt="Mood Trend">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Emotion Distribution</div>
                    <div class="card-body text-center">
                        <img src="/static/images/emotion_distribution_{{ patient._id }}.png" class="img-fluid" alt="Emotion Distribution">
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Engagement Metrics</div>
                    <div class="card-body text-center">
                        <img src="/static/images/engagement_metrics_{{ patient._id }}.png" class="img-fluid" alt="Engagement Metrics">
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Treatment Progress</div>
                    <div class="card-body text-center">
                        <img src="/static/images/treatment_progress_{{ patient._id }}.png" class="img-fluid" alt="Treatment Progress">
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Recent Sessions</div>
                    <div class="card-body">
                        {% if recent_sessions %}
                            <div class="list-group">
                                {% for session in recent_sessions %}
                                    <a href="{{ url_for('view_session', session_id=session._id) }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h5 class="mb-1">Session on {{ session.start_time.strftime('%Y-%m-%d') }}</h5>
                                            <small>{{ session.interactions|length }} interactions</small>
                                        </div>
                                        <p class="mb-1">{{ session.start_time.strftime('%H:%M') }} - {{ session.end_time.strftime('%H:%M') }}</p>
                                    </a>
                                {% endfor %}
                            </div>
                            <div class="mt-3">
                                <a href="{{ url_for('session_history', patient_id=patient._id) }}" class="btn btn-outline-primary btn-sm">View All Sessions</a>
                            </div>
                        {% else %}
                            <p class="text-center">No sessions found.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Recent Reports</div>
                    <div class="card-body">
                        {% if recent_reports %}
                            <div class="list-group">
                                {% for report in recent_reports %}
                                    <a href="{{ url_for('view_report', report_id=report._id) }}" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h5 class="mb-1">{{ report.report_type|title }} Report</h5>
                                            <small>{{ report.creation_date.strftime('%Y-%m-%d') }}</small>
                                        </div>
                                        <p class="mb-1">
                                            {% if report.content.treatment_stage %}
                                                <span class="badge status-badge status-{{ report.content.treatment_stage|lower|replace('_', '-') }}">
                                                    {{ report.content.treatment_stage|replace('_', ' ')|title }}
                                                </span>
                                            {% endif %}
                                            {% if report.content.condition_severity %}
                                                <span class="badge status-badge severity-{{ report.content.condition_severity|lower|replace('_', '-') }}">
                                                    {{ report.content.condition_severity|replace('_', ' ')|title }}
                                                </span>
                                            {% endif %}
                                        </p>
                                    </a>
                                {% endfor %}
                            </div>
                        {% else %}
                            <p class="text-center">No reports found.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        {% endblock %}
        """
        
        # Create report template
        report_template = """
        {% extends "base.html" %}

        {% block title %}{{ report.report_type|title }} Report for {{ patient.name }}{% endblock %}

        {% block content %}
        <div class="row mb-4">
            <div class="col">
                <h1>{{ report.report_type|title }} Report</h1>
                <p>
                    <strong>Patient:</strong> {{ patient.name }}<br>
                    <strong>Date:</strong> {{ report.creation_date.strftime('%Y-%m-%d %H:%M') }}<br>
                    <strong>Condition:</strong> 
                    {% if patient.condition == "depression" %}
                        Depression
                    {% elif patient.condition == "bipolar" %}
                        Bipolar Disorder
                    {% elif patient.condition == "ocd" %}
                        Obsessive-Compulsive Disorder
                    {% else %}
                        {{ patient.condition|title }}
                    {% endif %}
                </p>
            </div>
            <div class="col text-end">
                <a href="{{ url_for('patient_dashboard', patient_id=patient._id) }}" class="btn btn-primary">Back to Dashboard</a>
            </div>
        </div>

        <div class="row">
            <div class="col">
                <div class="card mb-4">
                    <div class="card-header">Summary</div>
                    <div class="card-body">
                        <div class="d-flex justify-content-between mb-3">
                            <div>
                                <strong>Treatment Stage:</strong>
                                <span class="badge status-badge status-{{ report.content.treatment_stage|lower|replace('_', '-') }}">
                                    {{ report.content.treatment_stage|replace('_', ' ')|title }}
                                </span>
                            </div>
                            {% if report.content.condition_severity %}
                            <div>
                                <strong>Condition Severity:</strong>
                                <span class="badge status-badge severity-{{ report.content.condition_severity|lower|replace('_', '-') }}">
                                    {{ report.content.condition_severity|replace('_', ' ')|title }}
                                </span>
                            </div>
                            {% endif %}
                        </div>

                        {% if report.report_type == "progress" %}
                            <h5>Overall Assessment</h5>
                            <p>{{ report.content.overall_assessment }}</p>
                        {% elif report.report_type == "assessment" %}
                            <h5>Psychological Evaluation</h5>
                            <p>{{ report.content.psychological_evaluation }}</p>
                        {% endif %}
                    </div>
                </div>

                {% if report.report_type == "progress" %}
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Progress Indicators</div>
                            <div class="card-body">
                                <ul>
                                    {% for indicator in report.content.progress_indicators %}
                                        <li>{{ indicator }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Areas of Concern</div>
                            <div class="card-body">
                                <ul>
                                    {% for concern in report.content.areas_of_concern %}
                                        <li>{{ concern }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Emotional Patterns</div>
                            <div class="card-body">
                                <ul>
                                    {% for pattern in report.content.emotional_patterns %}
                                        <li>{{ pattern }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Intervention Effectiveness</div>
                            <div class="card-body">
                                <p>{{ report.content.intervention_effectiveness }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header">Recommendations</div>
                    <div class="card-body">
                        <p>{{ report.content.recommendations }}</p>
                    </div>
                </div>
                {% elif report.report_type == "assessment" %}
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Symptom Progression</div>
                            <div class="card-body">
                                <p>{{ report.content.symptom_progression }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Core Patterns</div>
                            <div class="card-body">
                                <ul>
                                    {% for pattern in report.content.core_patterns %}
                                        <li>{{ pattern }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Risk Factors</div>
                            <div class="card-body">
                                <ul>
                                    {% for factor in report.content.risk_factors %}
                                        <li>{{ factor }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Protective Factors</div>
                            <div class="card-body">
                                <ul>
                                    {% for factor in report.content.protective_factors %}
                                        <li>{{ factor }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Treatment Response</div>
                            <div class="card-body">
                                <p>{{ report.content.treatment_response }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Prognosis</div>
                            <div class="card-body">
                                <p>{{ report.content.prognosis }}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Treatment Recommendations</div>
                            <div class="card-body">
                                <ul>
                                    {% for recommendation in report.content.treatment_recommendations %}
                                        <li>{{ recommendation }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-4">
                            <div class="card-header">Effective Interventions</div>
                            <div class="card-body">
                                <p>{{ report.content.effective_interventions }}</p>
                            </div>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
        {% endblock %}
        """
        
        # Create sessions