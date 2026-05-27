"""
Cloud Task Manager API
A RESTful microservice built with Flask and MySQL,
deployed using Docker containers with Nginx reverse proxy.

Author: [Your Name]
"""

import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────────
# Database Configuration (from environment vars)
# ──────────────────────────────────────────────
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'taskuser'),
    'password': os.environ.get('DB_PASSWORD', 'taskpass123'),
    'database': os.environ.get('DB_NAME', 'taskmanager'),
    'port': int(os.environ.get('DB_PORT', 3306))
}


def get_db_connection():
    """Create and return a database connection with retry logic."""
    retries = 5
    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn
        except Error as e:
            if attempt < retries - 1:
                print(f"DB connection attempt {attempt + 1} failed: {e}. Retrying in 3s...")
                time.sleep(3)
            else:
                raise e


def init_db():
    """Initialize database tables on startup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
            priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample data if table is empty
    cursor.execute('SELECT COUNT(*) FROM tasks')
    count = cursor.fetchone()[0]
    if count == 0:
        sample_tasks = [
            ('Set up Docker environment', 'Configure Docker and Docker Compose for microservices deployment', 'completed', 'high'),
            ('Design REST API', 'Create RESTful endpoints for task management', 'completed', 'high'),
            ('Configure Nginx', 'Set up Nginx as reverse proxy with load balancing', 'in_progress', 'medium'),
            ('Write documentation', 'Document API endpoints and deployment steps', 'pending', 'medium'),
            ('Add monitoring', 'Integrate health checks and logging', 'pending', 'low'),
        ]
        cursor.executemany(
            'INSERT INTO tasks (title, description, status, priority) VALUES (%s, %s, %s, %s)',
            sample_tasks
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database initialized successfully!")


# ──────────────────────────────────────────────
# API Routes
# ──────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'service': 'task-manager-api',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'task-manager-api',
            'database': 'disconnected',
            'error': str(e)
        }), 503


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Retrieve all tasks with optional status filter."""
    status_filter = request.args.get('status')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if status_filter:
        cursor.execute('SELECT * FROM tasks WHERE status = %s ORDER BY created_at DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    
    tasks = cursor.fetchall()
    
    # Convert datetime objects to strings
    for task in tasks:
        task['created_at'] = task['created_at'].isoformat() if task['created_at'] else None
        task['updated_at'] = task['updated_at'].isoformat() if task['updated_at'] else None
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(tasks),
        'tasks': tasks
    }), 200


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retrieve a single task by ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if task:
        task['created_at'] = task['created_at'].isoformat() if task['created_at'] else None
        task['updated_at'] = task['updated_at'].isoformat() if task['updated_at'] else None
        return jsonify({'success': True, 'task': task}), 200
    
    return jsonify({'success': False, 'error': 'Task not found'}), 404


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'success': False, 'error': 'Title is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, status, priority) VALUES (%s, %s, %s, %s)',
        (
            data['title'],
            data.get('description', ''),
            data.get('status', 'pending'),
            data.get('priority', 'medium')
        )
    )
    conn.commit()
    task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task_id': task_id
    }), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task."""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check if task exists
    cursor.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()
    
    if not task:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    cursor.execute(
        '''UPDATE tasks SET title = %s, description = %s, 
           status = %s, priority = %s WHERE id = %s''',
        (
            data.get('title', task['title']),
            data.get('description', task['description']),
            data.get('status', task['status']),
            data.get('priority', task['priority']),
            task_id
        )
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Task {task_id} updated successfully'
    }), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
    if affected:
        return jsonify({
            'success': True,
            'message': f'Task {task_id} deleted successfully'
        }), 200
    
    return jsonify({'success': False, 'error': 'Task not found'}), 404


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get task statistics for dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority
        FROM tasks
    ''')
    stats = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'stats': stats}), 200


# ──────────────────────────────────────────────
# Application Entry Point
# ──────────────────────────────────────────────

if __name__ == '__main__':
    print("🚀 Starting Cloud Task Manager API...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
