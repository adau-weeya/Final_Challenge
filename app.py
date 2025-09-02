from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# In-memory task storage
tasks = []
next_id = 1

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks"""
    logger.info("Fetching all tasks")
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add a new task"""
    global next_id
    data = request.get_json()
    
    if not data or 'description' not in data:
        logger.warning("Add task request missing description")
        return jsonify({'error': 'Description is required'}), 400
    
    description = data['description'].strip()
    
    # Validate description
    if not description:
        logger.warning("Add task request with empty description")
        return jsonify({'error': 'Description cannot be empty'}), 400
    
    # Prevent excessively long descriptions
    if len(description) > 500:
        logger.warning("Add task request with overly long description")
        return jsonify({'error': 'Description is too long'}), 400
    
    task = {
        'id': next_id,
        'description': description,
        'completed': False
    }
    tasks.append(task)
    next_id += 1
    
    logger.info(f"Added new task: {task}")
    return jsonify(task), 201

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Mark a task as complete"""
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        logger.warning(f"Complete task request for non-existent task: {task_id}")
        return jsonify({'error': 'Task not found'}), 404
    
    if task['completed']:
        logger.info(f"Task {task_id} is already completed")
        return jsonify({'message': 'Task was already completed', 'task': task})
    
    task['completed'] = True
    logger.info(f"Marked task {task_id} as complete")
    return jsonify(task)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        logger.warning(f"Delete task request for non-existent task: {task_id}")
        return jsonify({'error': 'Task not found'}), 404
    
    tasks = [t for t in tasks if t['id'] != task_id]
    logger.info(f"Deleted task: {task_id}")
    return jsonify({'message': 'Task deleted'})

if __name__ == '__main__':
    app.run(debug=True)