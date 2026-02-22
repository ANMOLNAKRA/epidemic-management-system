# generate_flowchart.py
import os

# Define the structure of the EpiShield UI as a dictionary
ui_structure = {
    "Login": ["Index (Home)"],
    "Index (Home)": ["View Patients", "Add Patient", "Resources", "Outbreaks", "Diseases", "Analysis", "Logout"],
    "View Patients": ["Index (Home)", "Add Patient", "Update Status", "Delete Patient"],
    "Add Patient": ["View Patients"],
    "Resources": ["Add Resource", "View Resources", "Resource Allocation"],
    "Add Resource": ["Resources"],
    "View Resources": ["Resources"],
    "Resource Allocation": ["Resources"],
    "Outbreaks": ["Add Outbreak", "View Outbreaks"],
    "Add Outbreak": ["Outbreaks"],
    "View Outbreaks": ["Outbreaks"],
    "Diseases": ["Report New Disease"],
    "Report New Disease": ["Diseases"],
    "Analysis": ["Index (Home)"],
    "Logout": ["Login"]
}

# HTML template with escaped curly braces in CSS
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EpiShield UI Flowchart</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .flowchart {{
            position: relative;
            width: 100%;
            max-width: 1200px;
        }}
        .box {{
            background-color: #28a745;
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            width: 200px;
            margin: 20px;
            position: absolute;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        .arrow {{
            position: absolute;
            border: 2px solid #218838;
            background-color: #218838;
        }}
        .label {{
            position: absolute;
            color: #333;
            font-size: 12px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 2px 5px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="flowchart">
        {boxes}
        {arrows}
    </div>
</body>
</html>
"""

# Define positions for each box
positions = {
    "Login": (100, 50),
    "Index (Home)": (400, 50),
    "View Patients": (700, 50),
    "Add Patient": (700, 150),
    "Resources": (400, 250),
    "Add Resource": (300, 350),
    "View Resources": (400, 350),
    "Resource Allocation": (500, 350),
    "Outbreaks": (400, 450),
    "Add Outbreak": (300, 550),
    "View Outbreaks": (400, 550),
    "Diseases": (400, 650),
    "Report New Disease": (400, 750),
    "Analysis": (700, 250),
    "Update Status": (900, 50),
    "Delete Patient": (900, 150),
    "Logout": (100, 150)
}

def generate_boxes():
    """Generate HTML for flowchart boxes."""
    boxes = ""
    for page, (x, y) in positions.items():
        boxes += f'<div class="box" style="left: {x}px; top: {y}px;">{page}</div>\n'
    return boxes

def generate_arrows():
    """Generate HTML for arrows between boxes."""
    arrows = ""
    for start_page, connections in ui_structure.items():
        start_x, start_y = positions[start_page]
        for end_page in connections:
            end_x, end_y = positions[end_page]
            dx = end_x - start_x
            dy = end_y - start_y
            length = ((dx ** 2) + (dy ** 2)) ** 0.5
            angle = (180 / 3.14159) * (dy / length)  # Simplified angle calculation
            
            if abs(dx) > abs(dy):
                arrows += f'<div class="arrow" style="left: {min(start_x, end_x) + 200}px; top: {start_y + 15}px; width: {abs(dx) - 200}px; height: 2px;"></div>\n'
                arrows += f'<div class="label" style="left: {(start_x + end_x) / 2}px; top: {start_y + 10}px;">to {end_page}</div>\n'
            else:
                arrows += f'<div class="arrow" style="left: {start_x + 90}px; top: {min(start_y, end_y) + 30}px; width: 2px; height: {abs(dy) - 30}px;"></div>\n'
                arrows += f'<div class="label" style="left: {start_x + 100}px; top: {(start_y + end_y) / 2}px;">to {end_page}</div>\n'
    return arrows

# Generate the HTML content
boxes = generate_boxes()
arrows = generate_arrows()
html_content = html_template.format(boxes=boxes, arrows=arrows)

# Write the HTML to a file
output_dir = "static"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "flowchart.html")
with open(output_file, "w") as f:
    f.write(html_content)

print(f"Flowchart generated successfully! Open {output_file} in a browser to view.")